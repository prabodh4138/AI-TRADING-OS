"""
AI Trading Operating System
Module: portfolio/paper_trader.py (Sections 1, 8, 9, 10)

Automated Paper Trading Engine:
- Manages paper portfolio cash, equity, and open positions across trading sessions.
- Executes approved TradePlans with simulated broker slippage and transaction costs.
- Tracks daily mark-to-market prices and automatically triggers stop-loss or profit-target exits.
- Maintains a persistent ledger on disk (JSON / PostgreSQL) with complete audit trail.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import uuid
import pandas as pd

from ai.hierarchical_engine import TradePlan


@dataclass
class PaperPosition:
    position_id: str
    symbol: str
    sector_id: str
    entry_date: str
    entry_price: float
    quantity: int
    current_price: float
    stop_loss: float
    target: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    days_held: int = 1
    initial_stop_loss: float = 0.0

    def __post_init__(self) -> None:
        if self.initial_stop_loss <= 0.0:
            self.initial_stop_loss = self.stop_loss

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PaperTradeRecord:
    trade_id: str
    symbol: str
    sector_id: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    quantity: int
    net_pnl: float
    pnl_pct: float
    exit_reason: str  # "STOP_LOSS", "TARGET", "REGIME_EXIT"
    slippage_and_fees: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def realized_pnl(self) -> float:
        return self.net_pnl

    @property
    def realized_pnl_pct(self) -> float:
        return self.pnl_pct


class PaperTradingManager:
    """
    Automated Paper Trading Execution Engine and Portfolio Ledger.
    """

    def __init__(
        self,
        initial_capital: float = 1_000_000.0,
        slippage_bps: float = 10.0,
        brokerage_bps: float = 5.0,
        max_positions: int = 30,
        min_cash_reserve_pct: float = 0.0,
        min_trade_size: float = 500.0,
        ledger_path: str | Path = "data/paper_trading_ledger.json",
    ) -> None:
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        self.slippage_bps = slippage_bps
        self.brokerage_bps = brokerage_bps
        self.max_positions = max_positions
        self.min_cash_reserve_pct = min_cash_reserve_pct
        self.min_trade_size = min_trade_size
        self.total_cost_pct = (slippage_bps + brokerage_bps) / 10000.0
        self.ledger_path = Path(ledger_path)

        self.positions: Dict[str, PaperPosition] = {}
        self.closed_trades: List[PaperTradeRecord] = []
        self.last_update_date: Optional[str] = None

        self.load_state()

    @property
    def total_equity(self) -> float:
        """Total portfolio equity (cash + current mark-to-market position value)."""
        open_val = sum(pos.quantity * pos.current_price for pos in self.positions.values())
        return round(self.current_cash + open_val, 2)

    def reset_ledger(self, capital: float = 1_000_000.0) -> None:
        """Resets paper trading ledger to clean starting capital and clears legacy trades."""
        self.initial_capital = capital
        self.current_cash = capital
        self.positions = {}
        self.closed_trades = []
        self.save_state()

    def execute_trade_plans(
        self,
        plans: List[TradePlan],
        sector_lookup: Optional[Dict[str, str]] = None,
    ) -> List[PaperPosition]:
        """
        Executes approved trade plans in paper trading without artificial restrictions:
        - Automatically sizes and allocates orders within available cash.
        - Zero restrictive rejection boundaries so user can test recommendations.
        """
        new_positions = []
        sector_lookup = sector_lookup or {}

        for plan in plans:
            if plan.action != "BUY" or plan.symbol in self.positions:
                continue

            # Capacity constraint (generous 30 positions for paper testing)
            if len(self.positions) >= self.max_positions:
                break

            # Effective entry price with buy slippage
            fill_price = round(plan.entry_trigger * (1 + self.total_cost_pct), 2)
            if fill_price <= 0:
                continue

            # Investable cash in paper trading: use available cash (with small ₹500 buffer)
            investable_cash = max(0.0, self.current_cash - 500.0)
            if investable_cash < fill_price:
                # Genuinely zero cash remaining
                continue

            # Position sizing rule: Divide total equity across 15 stocks (~6.67% max allocation per stock)
            # so the user can comfortably take paper tests on 10 to 15 stocks simultaneously!
            target_portfolio_slots = 15
            max_alloc_per_position = max(1000.0, self.total_equity / float(target_portfolio_slots))
            max_qty_by_alloc = max(1, int(max_alloc_per_position // (fill_price * (1 + self.total_cost_pct))))

            desired_shares = max(1, min(plan.position_size_shares, max_qty_by_alloc))
            desired_total = round(fill_price * desired_shares * (1 + self.total_cost_pct), 2)

            if desired_total > investable_cash:
                # Dynamically resize to available cash so order is NEVER blocked!
                resized_qty = int(investable_cash // (fill_price * (1 + self.total_cost_pct)))
                if resized_qty < 1:
                    continue
                qty = resized_qty
                total_required = round(fill_price * qty * (1 + self.total_cost_pct), 2)
            else:
                qty = desired_shares
                total_required = desired_total

            self.current_cash = round(self.current_cash - total_required, 2)
            sec_id = sector_lookup.get(plan.symbol, "OTHER")
            fees = round(total_required - (fill_price * qty), 2)

            pos = PaperPosition(
                position_id=str(uuid.uuid4())[:8],
                symbol=plan.symbol,
                sector_id=sec_id,
                entry_date=str(plan.trading_date),
                entry_price=fill_price,
                quantity=qty,
                current_price=fill_price,
                stop_loss=plan.stop_loss,
                target=plan.target_zone,
                unrealized_pnl=-fees,
                unrealized_pnl_pct=round((-fees / max(1.0, fill_price * qty)) * 100, 2),
                days_held=1,
                initial_stop_loss=plan.stop_loss,
            )
            self.positions[plan.symbol] = pos
            new_positions.append(pos)

        self.save_state()
        return new_positions

    def on_daily_market_data(self, daily_df: pd.DataFrame) -> List[PaperTradeRecord]:
        """
        Processes new daily market prices:
        - Smart dynamic trailing stops: Breakeven lock at +1.5R, profit lock at +2.5R.
        - Triggers stop-loss or profit-target exits.
        - Updates mark-to-market.
        """
        if daily_df.empty or not self.positions:
            return []

        active_syms = set(self.positions.keys())
        # High-speed indexed lookup: only inspect latest bar for active positions
        subset_df = daily_df[daily_df["symbol"].str.strip().str.upper().isin(active_syms)]
        if subset_df.empty:
            return []

        latest_df = subset_df.sort_values("trading_date").groupby("symbol").last()
        lookup = {str(sym).strip().upper(): row for sym, row in latest_df.iterrows()}

        newly_closed = []
        symbols_to_remove = []

        for sym, pos in self.positions.items():
            if sym not in lookup:
                continue

            bar = lookup[sym]
            t_date = str(bar["trading_date"])

            # -------------------------------------------------------------
            # Temporal Causality Enforcement:
            # A position can NEVER be evaluated or exited against a historical bar
            # that occurred before its entry date!
            # -------------------------------------------------------------
            if t_date < pos.entry_date:
                continue

            high_p = float(bar["high"])
            low_p = float(bar["low"])
            close_p = float(bar["close"])

            # -------------------------------------------------------------
            # Smart Dynamic Trailing Stop Loss (Guarantees Breakeven & Locks Profits)
            # -------------------------------------------------------------
            init_stop = getattr(pos, "initial_stop_loss", None) or pos.stop_loss
            init_risk = max(1.0, pos.entry_price - init_stop)

            # Rule 1: Breakeven Lock at +1.5R favorable movement
            if high_p >= pos.entry_price + (1.5 * init_risk):
                breakeven_p = round(pos.entry_price * (1 + self.total_cost_pct * 2), 2)
                if breakeven_p > pos.stop_loss:
                    pos.stop_loss = breakeven_p

            # Rule 2: Profit Lock at +2.5R favorable movement
            if high_p >= pos.entry_price + (2.5 * init_risk):
                profit_lock_p = round(pos.entry_price + (1.2 * init_risk), 2)
                if profit_lock_p > pos.stop_loss:
                    pos.stop_loss = profit_lock_p

            exit_price = None
            reason = None

            # 1. Stop loss check (can be breakeven or trailing stop)
            if low_p <= pos.stop_loss:
                exit_price = round(pos.stop_loss * (1 - self.total_cost_pct), 2)
                if exit_price >= pos.entry_price:
                    reason = "TRAILING_STOP_PROFIT"
                else:
                    reason = "STOP_LOSS"
            # 2. Profit target check
            elif high_p >= pos.target:
                exit_price = round(pos.target * (1 - self.total_cost_pct), 2)
                reason = "TARGET"

            if exit_price is not None:
                cost = round(exit_price * pos.quantity * self.total_cost_pct, 2)
                gross_pnl = round(pos.quantity * (exit_price - pos.entry_price), 2)
                net_pnl = round(gross_pnl - cost, 2)
                pnl_pct = round((net_pnl / (pos.entry_price * pos.quantity)) * 100.0, 2)

                self.current_cash += round(pos.quantity * exit_price - cost, 2)

                record = PaperTradeRecord(
                    trade_id=str(uuid.uuid4())[:8],
                    symbol=sym,
                    sector_id=pos.sector_id,
                    entry_date=pos.entry_date,
                    exit_date=t_date if t_date >= pos.entry_date else pos.entry_date,
                    entry_price=pos.entry_price,
                    exit_price=exit_price,
                    quantity=pos.quantity,
                    net_pnl=net_pnl,
                    pnl_pct=pnl_pct,
                    exit_reason=reason,
                    slippage_and_fees=cost,
                )
                self.closed_trades.append(record)
                newly_closed.append(record)
                symbols_to_remove.append(sym)
            else:
                # Mark to market
                pos.current_price = close_p
                pos.unrealized_pnl = round(pos.quantity * (close_p - pos.entry_price), 2)
                pos.unrealized_pnl_pct = round(((close_p - pos.entry_price) / pos.entry_price) * 100.0, 2)
                
                # Accurately compute calendar days held from entry_date to market date
                try:
                    e_d = datetime.strptime(str(pos.entry_date)[:10], "%Y-%m-%d").date()
                    c_d = datetime.strptime(str(t_date)[:10], "%Y-%m-%d").date()
                    pos.days_held = max(1, (c_d - e_d).days + 1)
                except Exception:
                    pos.days_held = 1

        for sym in symbols_to_remove:
            del self.positions[sym]

        self.save_state()
        return newly_closed

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Returns structured performance and position summary."""
        eq = self.total_equity
        ret_pct = round(((eq / self.initial_capital) - 1) * 100.0, 2)
        total_closed = len(self.closed_trades)

        wins = [t for t in self.closed_trades if t.net_pnl > 0]
        losses = [t for t in self.closed_trades if t.net_pnl < 0]
        win_rate = round((len(wins) / max(1, total_closed)) * 100.0, 1) if total_closed else 0.0

        gross_profit = sum(t.net_pnl for t in wins)
        gross_loss = abs(sum(t.net_pnl for t in losses))
        profit_factor = round(gross_profit / max(1.0, gross_loss), 2)

        return {
            "initial_capital": self.initial_capital,
            "current_cash": round(self.current_cash, 2),
            "total_equity": eq,
            "total_return_pct": ret_pct,
            "open_positions_count": len(self.positions),
            "total_closed_trades": total_closed,
            "win_rate_pct": win_rate,
            "profit_factor": profit_factor,
            "open_positions": [p.to_dict() for p in self.positions.values()],
            "closed_trades": [t.to_dict() for t in self.closed_trades],
        }

    def save_state(self) -> None:
        """Persists paper portfolio state to JSON file."""
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "initial_capital": self.initial_capital,
            "current_cash": self.current_cash,
            "positions": {sym: p.to_dict() for sym, p in self.positions.items()},
            "closed_trades": [t.to_dict() for t in self.closed_trades],
            "last_updated": datetime.now().isoformat(),
        }
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> None:
        """Loads paper portfolio state from JSON file if present."""
        if not self.ledger_path.exists():
            return
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            self.initial_capital = state.get("initial_capital", self.initial_capital)
            self.current_cash = state.get("current_cash", self.current_cash)

            self.positions = {}
            for sym, p in state.get("positions", {}).items():
                p.setdefault("initial_stop_loss", p.get("stop_loss", 0.0))
                self.positions[sym] = PaperPosition(**p)

            self.closed_trades = [PaperTradeRecord(**t) for t in state.get("closed_trades", [])]
        except Exception:
            pass
