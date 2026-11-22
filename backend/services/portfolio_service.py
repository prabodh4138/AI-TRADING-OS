"""
AI Trading Operating System (AI-TOS)
Portfolio Service: Manages Paper Trading Execution, MTM, and Ledger Persistence.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from ai.hierarchical_engine import TradePlan
from backend.schemas import (
    AutoTradeResultDTO,
    AutoTradeStatusDTO,
    ClosedTradeDTO,
    ExecuteTradeRequest,
    PortfolioSummaryDTO,
    PositionDTO,
)
from backend.services.data_service import DataService
from portfolio.paper_trader import PaperTradingManager


class PortfolioService:
    _instance: Optional[PortfolioService] = None

    def __init__(self) -> None:
        self.manager = PaperTradingManager()
        self.data_service = DataService.get_instance()
        self.auto_trading_enabled: bool = True
        self.last_auto_run_timestamp: Optional[str] = None
        self.update_mark_to_market()

    @classmethod
    def get_instance(cls) -> PortfolioService:
        if cls._instance is None:
            cls._instance = PortfolioService()
        return cls._instance

    def update_mark_to_market(self) -> None:
        df = self.data_service.get_dataframe()
        if not df.empty:
            self.manager.on_daily_market_data(df)

    def get_summary(self) -> PortfolioSummaryDTO:
        self.update_mark_to_market()
        s = self.manager.get_portfolio_summary()

        df = self.data_service.get_dataframe()
        curr_mkt_date = str(df["trading_date"].max()) if not df.empty else datetime.now().strftime("%Y-%m-%d")

        pos_dtos: List[PositionDTO] = []
        for p in self.manager.positions.values():
            # Robust calendar/trading days calculation
            try:
                e_d = datetime.strptime(str(p.entry_date)[:10], "%Y-%m-%d").date()
                c_d = datetime.strptime(str(curr_mkt_date)[:10], "%Y-%m-%d").date()
                computed_days = max(1, (c_d - e_d).days + 1)
            except Exception:
                computed_days = 1
            p.days_held = computed_days

            pos_dtos.append(PositionDTO(
                position_id=p.position_id,
                symbol=p.symbol,
                sector_id=p.sector_id,
                entry_date=p.entry_date,
                entry_price=p.entry_price,
                quantity=p.quantity,
                current_price=p.current_price,
                stop_loss=p.stop_loss,
                target=p.target,
                unrealized_pnl=p.unrealized_pnl,
                unrealized_pnl_pct=p.unrealized_pnl_pct,
                days_held=computed_days,
                initial_stop_loss=getattr(p, "initial_stop_loss", p.stop_loss),
            ))

        closed_dtos: List[ClosedTradeDTO] = []
        for t in self.manager.closed_trades[-20:]:
            closed_dtos.append(ClosedTradeDTO(
                trade_id=t.trade_id,
                symbol=t.symbol,
                sector_id=t.sector_id,
                entry_date=t.entry_date,
                exit_date=t.exit_date,
                entry_price=t.entry_price,
                exit_price=t.exit_price,
                quantity=t.quantity,
                net_pnl=t.net_pnl,
                pnl_pct=t.pnl_pct,
                exit_reason=t.exit_reason,
                slippage_and_fees=t.slippage_and_fees,
            ))

        return PortfolioSummaryDTO(
            total_equity=s["total_equity"],
            current_cash=s["current_cash"],
            open_positions_count=s["open_positions_count"],
            total_closed_trades=s["total_closed_trades"],
            win_rate_pct=s["win_rate_pct"],
            total_return_pct=s["total_return_pct"],
            positions=pos_dtos,
            recent_closed_trades=closed_dtos,
        )

    def execute_trade(self, req: ExecuteTradeRequest) -> Optional[PositionDTO]:
        import pandas as pd
        df = self.data_service.get_dataframe()
        global_max_date = str(df["trading_date"].max()) if not df.empty else "2026-11-20"

        # Check symbol's latest bar date
        sym_df = df[df["symbol"].str.upper() == req.symbol.upper()]
        sym_max_date = str(sym_df["trading_date"].max()) if not sym_df.empty else None

        # If symbol data is behind global market date, fetch latest bars on-demand from Yahoo Finance
        if sym_max_date is None or sym_max_date < global_max_date:
            try:
                from data_engine.yahoo_finance_pipeline import YahooFinanceDataPipeline
                pipe = YahooFinanceDataPipeline()
                fetched = pipe.fetch_symbol_ohlcv(req.symbol, period="1mo")
                if not fetched.empty:
                    fetched["trading_date"] = pd.to_datetime(fetched["trading_date"]).dt.date
                    merged = pd.concat([df, fetched], ignore_index=True)
                    merged = merged.dropna(subset=["close", "open", "high", "low"])
                    merged = merged[merged["close"] > 0]
                    merged = merged.drop_duplicates(subset=["trading_date", "symbol"], keep="last")
                    merged = merged.sort_values(["trading_date", "symbol"]).reset_index(drop=True)
                    merged.to_csv("downloads/raw/historical_nifty500_dataset.csv", index=False)
                    self.data_service.load_dataset()
                    df = self.data_service.get_dataframe()
                    sym_df = df[df["symbol"].str.upper() == req.symbol.upper()]
                    if not sym_df.empty:
                        sym_max_date = str(sym_df["trading_date"].max())
            except Exception as e:
                print(f"[PORTFOLIO] On-demand symbol fetch notice for {req.symbol}: {e}")

        effective_entry_date = sym_max_date or global_max_date

        # Determine latest CMP from available bars
        latest_cmp = None
        if not sym_df.empty:
            latest_cmp = float(sym_df.sort_values("trading_date").iloc[-1]["close"])

        # Entry price: use requested entry_trigger or live CMP
        entry_price = req.entry_trigger if req.entry_trigger > 0 else (latest_cmp or 100.0)

        # Dynamic Stop Loss & Target protection relative to entry price
        stop_loss = req.stop_loss
        if stop_loss <= 0 or stop_loss >= entry_price:
            stop_loss = round(entry_price * 0.96, 2) # 4% stop loss default below entry

        target_zone = req.target_zone
        if target_zone <= entry_price:
            target_zone = round(entry_price + (2.5 * max(1.0, entry_price - stop_loss)), 2)

        # Equal-weight portfolio division rule: Divide balance across 15 stocks (~6.67% max per position)
        # so at least 10 to 15 stocks can be held and tested concurrently in paper trading!
        target_portfolio_slots = 15
        max_alloc_per_stock = max(1000.0, self.manager.total_equity / float(target_portfolio_slots))
        capital_qty = max(1, int(max_alloc_per_stock // entry_price))

        risk_amt = self.manager.total_equity * 0.015 # 1.5% equity risk sizing
        risk_per_share = max(1.0, entry_price - stop_loss)
        risk_qty = max(1, int(risk_amt // risk_per_share))

        # Size by both capital allocation (1/15th of balance) and risk budget
        auto_calculated_qty = min(capital_qty, risk_qty)
        qty = req.position_size_shares if req.position_size_shares and req.position_size_shares > 0 else auto_calculated_qty

        # Ensure qty respects available cash
        investable_cash = max(0.0, self.manager.current_cash - 200.0)
        if (qty * entry_price) > investable_cash and investable_cash > 0:
            qty = max(1, int(investable_cash // entry_price))

        risk_rr = round(max(1.0, (target_zone - entry_price) / risk_per_share), 2)

        plan = TradePlan(
            symbol=req.symbol,
            trading_date=effective_entry_date,
            action=req.action or "BUY",
            entry_trigger=entry_price,
            stop_loss=stop_loss,
            target_zone=target_zone,
            reward_to_risk=risk_rr,
            position_size_shares=qty,
            position_value=round(qty * entry_price, 2),
            risk_amount=round(qty * risk_per_share, 2),
            risk_gate_outcome="APPROVED",
            gate_reason=req.gate_reason or "FastAPI Direct Execution",
        )

        new_pos = self.manager.execute_trade_plans([plan])
        if new_pos:
            p = new_pos[0]
            return PositionDTO(
                position_id=p.position_id,
                symbol=p.symbol,
                sector_id=p.sector_id,
                entry_date=p.entry_date,
                entry_price=p.entry_price,
                quantity=p.quantity,
                current_price=p.current_price,
                stop_loss=p.stop_loss,
                target=p.target,
                unrealized_pnl=p.unrealized_pnl,
                unrealized_pnl_pct=p.unrealized_pnl_pct,
                days_held=p.days_held,
                initial_stop_loss=p.initial_stop_loss,
            )
        return None

    def execute_batch(self, reqs: List[ExecuteTradeRequest]) -> List[PositionDTO]:
        res = []
        for r in reqs:
            p = self.execute_trade(r)
            if p:
                res.append(p)
        return res

    def reset_portfolio(self, capital: float = 1_000_000.0) -> None:
        self.manager.reset_ledger(capital=capital)

    def get_auto_trade_status(self) -> AutoTradeStatusDTO:
        return AutoTradeStatusDTO(
            enabled=self.auto_trading_enabled,
            max_positions=self.manager.max_positions,
            risk_per_trade_pct=1.5,
            min_cash_reserve_pct=self.manager.min_cash_reserve_pct,
            last_run_timestamp=self.last_auto_run_timestamp,
            active_rules=[
                "Rule 1: Portfolio balance divided across 15 stocks (~6.7% / ₹66.6K max allocation per stock)",
                "Rule 2: Minimum 2.0:1 Reward-to-Risk ratio mandatory",
                "Rule 3: Macro Curve Location at or below Equilibrium (<= 55%)",
                "Rule 4: Multi-Timeframe Alignment Grade A+ or A",
                "Rule 5: Maximum 1.5% Risk of Total Equity per position",
                "Rule 6: Trailing Stop: Breakeven lock at +1.5R, Profit lock at +2.5R",
                "Rule 7: Seamless execution across 10-15 simultaneous positions",
            ],
        )

    def toggle_auto_trading(self, enabled: Optional[bool] = None) -> bool:
        if enabled is not None:
            self.auto_trading_enabled = enabled
        else:
            self.auto_trading_enabled = not self.auto_trading_enabled
        return self.auto_trading_enabled

    def run_auto_trading(self, max_new_trades: int = 5) -> AutoTradeResultDTO:
        """
        Executes automated institutional paper trading cycle:
        1. Evaluates active positions for Dynamic Trailing Stop Loss (Breakeven at +1.5R, Profit lock at +2.5R)
        2. Closes positions that reached Target Supply or hit Buffered Stop Loss
        3. Scans GTF demand universe for Actionable & High-Conviction Setups
        4. Sizes positions automatically to 1.5% risk and enters trades
        """
        from backend.services.zone_service import ZoneService

        self.last_auto_run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details: List[str] = []

        # 1. Update mark to market & trailing stops
        initial_closed_count = len(self.manager.closed_trades)
        self.update_mark_to_market()
        newly_closed_count = len(self.manager.closed_trades) - initial_closed_count

        if newly_closed_count > 0:
            latest_exits = self.manager.closed_trades[-newly_closed_count:]
            for ex in latest_exits:
                details.append(f"EXIT TRIGGERED: {ex.symbol} closed at ₹{ex.exit_price:.2f} ({ex.exit_reason}) | P&L: ₹{ex.net_pnl:+.2f} ({ex.pnl_pct:+.2f}%)")
        else:
            details.append("Trailing stops evaluated: All active positions protected.")

        # 2. Check capacity
        slots_available = max(0, self.manager.max_positions - len(self.manager.positions))
        if slots_available == 0:
            details.append(f"Portfolio at maximum capacity ({self.manager.max_positions} active holdings). Preserving risk boundary.")
            summary = self.get_summary()
            return AutoTradeResultDTO(
                success=True,
                message="Portfolio capacity reached. No new entries.",
                new_positions_opened=0,
                positions_closed=newly_closed_count,
                stops_updated=len(summary.positions),
                open_positions=summary.positions,
                execution_details=details,
            )

        # 3. Scan universe for high conviction candidates
        zs = ZoneService.get_instance()
        scan = zs.scan_universe()
        candidates = scan.actionable_candidates + scan.watchlist_candidates + scan.best_aligned_candidates

        # Deduplicate & filter
        existing_symbols = set(self.manager.positions.keys())
        seen_cand = set()
        valid_candidates = []

        for c in candidates:
            if c.symbol in existing_symbols or c.symbol in seen_cand:
                continue
            seen_cand.add(c.symbol)

            # Strict institutional qualification audit
            if (
                c.touch_count <= 1
                and c.reward_to_risk >= 2.0
                and c.risk_pct <= 3.0
                and c.curve_location_pct <= 55.0
                and c.gate_passed
                and c.institutional_score_100 >= 60.0
            ):
                valid_candidates.append(c)

        # Sort by institutional score descending, then R:R descending
        valid_candidates.sort(key=lambda x: (x.institutional_score_100, x.reward_to_risk), reverse=True)

        newly_opened: List[PositionDTO] = []
        limit_to_open = min(slots_available, max_new_trades)

        for cand in valid_candidates[:limit_to_open]:
            # Equal-weight portfolio division rule: Divide balance across 15 stocks (~6.67% max per position)
            # so at least 10 to 15 stocks can be held and tested concurrently in paper trading!
            target_portfolio_slots = 15
            max_alloc = max(1000.0, self.manager.total_equity / float(target_portfolio_slots))
            capital_qty = max(1, int(max_alloc // cand.proximal_line))

            risk_amt = self.manager.total_equity * 0.015
            risk_per_share = max(1.0, cand.proximal_line - cand.buffered_stop_loss)
            risk_qty = max(1, int(risk_amt // risk_per_share))

            qty = min(capital_qty, risk_qty)

            # Cash availability check
            investable_cash = max(0.0, self.manager.current_cash - 200.0)
            if (qty * cand.proximal_line) > investable_cash:
                qty = int(investable_cash // cand.proximal_line)
                if qty < 1 or (qty * cand.proximal_line) < self.manager.min_trade_size:
                    details.append(f"SKIPPED {cand.symbol}: Insufficient available cash for entry.")
                    continue

            req = ExecuteTradeRequest(
                symbol=cand.symbol,
                entry_trigger=cand.proximal_line,
                stop_loss=cand.buffered_stop_loss,
                target_zone=cand.target_supply,
                position_size_shares=qty,
                gate_reason=f"AUTO_GTF_ENTRY: {cand.zone_type} | Score: {cand.institutional_score_100:.0f} | R:R: {cand.reward_to_risk:.1f}:1",
            )
            pos = self.execute_trade(req)
            if pos:
                newly_opened.append(pos)
                details.append(f"AUTO-ENTRY EXECUTED: Bought {pos.quantity} shares of {pos.symbol} @ Proximal ₹{pos.entry_price:.2f} | Buffered SL: ₹{pos.stop_loss:.2f} | Target: ₹{pos.target:.2f} (Allocated: ₹{pos.quantity * pos.entry_price:,.2f})")

        summary = self.get_summary()
        return AutoTradeResultDTO(
            success=True,
            message=f"Auto-trade cycle finished: {len(newly_opened)} new positions entered, {newly_closed_count} exited, {len(summary.positions)} active.",
            new_positions_opened=len(newly_opened),
            positions_closed=newly_closed_count,
            stops_updated=len(summary.positions),
            open_positions=summary.positions,
            execution_details=details,
        )
