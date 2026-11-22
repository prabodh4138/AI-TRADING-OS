"""
AI Trading Operating System
Module: portfolio/automated_pipeline.py (Sections 1, 8, 9, 10)

Complete Automated Paper Trading Pipeline:
1. Download from NSE website (with resilient local Bhavcopy fallback).
2. Inject/Update PostgreSQL database (symbol master and market_data).
3. Execute Market-Index and Sector Intelligence Scan (Layers A through E).
4. Automated Paper Trading:
   - Auto-exit: Stop-loss and target triggers net of slippage/costs.
   - Auto-entry: Executes approved Risk-Gated trade plans into active paper positions.
5. Save state to ledger and generate comprehensive Section 9/10 executive report.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from sqlalchemy import text

from core.logger import get_logger
from database.connection import database
from database.models.market_data import MarketData
from database.models.symbol import Symbol
from data_engine.downloader.download_manager import DownloadManager
from data_engine.market_data import read_market_csv
from portfolio.paper_trader import PaperPosition, PaperTradeRecord, PaperTradingManager
from scanner.engine import ScanReport, Scanner


@dataclass
class DailyPipelineExecutionResult:
    """Summary of daily automated paper trading pipeline run."""
    run_timestamp: str
    trading_date: str
    data_source: str
    rows_ingested: int
    market_regime: str
    regime_confidence: float
    total_screened: int
    approved_plans_count: int
    rejected_plans_count: int
    exits_executed: int
    entries_executed: int
    open_positions_count: int
    current_cash: float
    total_equity: float
    total_return_pct: float
    report_path: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AutomatedPaperTradingPipeline:
    """
    World-Class Automated End-to-End Paper Trading Pipeline.
    """

    def __init__(
        self,
        capital: float = 1_000_000.0,
        slippage_bps: float = 10.0,
        brokerage_bps: float = 5.0,
        ledger_path: str = "data/paper_trading_ledger.json",
        reports_dir: str = "reports",
    ) -> None:
        self.logger = get_logger()
        self.capital = capital
        self.slippage_bps = slippage_bps
        self.brokerage_bps = brokerage_bps
        self.ledger_path = Path(ledger_path)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.paper_trader = PaperTradingManager(
            initial_capital=capital,
            slippage_bps=slippage_bps,
            brokerage_bps=brokerage_bps,
            ledger_path=self.ledger_path,
        )
        self.scanner = Scanner(capital=capital)

    def run_daily_pipeline(
        self,
        target_date: Optional[date] = None,
        csv_file: Optional[str | Path] = None,
    ) -> DailyPipelineExecutionResult:
        """
        Executes the full automated paper trading lifecycle:
        Download -> Inject DB -> Scan -> Auto Exit -> Auto Entry -> Report
        """
        run_ts = datetime.now().isoformat()
        self.logger.info("Starting Daily Automated Paper Trading Pipeline...")

        # -------------------------------------------------------------
        # STAGE 1: Acquire Market Data (NSE Download or Fallback)
        # -------------------------------------------------------------
        market_df, source_desc, effective_date = self._acquire_market_data(target_date, csv_file)
        self.logger.info(f"Data acquired: {len(market_df)} records from {source_desc} for date {effective_date}")

        # -------------------------------------------------------------
        # STAGE 2: Inject / Persist into PostgreSQL Database
        # -------------------------------------------------------------
        rows_ingested = self._inject_to_database(market_df)

        # -------------------------------------------------------------
        # STAGE 3: Multi-Layer Quantitative Scan (Layers A-E)
        # -------------------------------------------------------------
        scan_report = self.scanner.scan(market_df, reference_date=effective_date)
        self.logger.info(f"Scan complete. Regime: {scan_report.regime.regime}. Approved plans: {len(scan_report.trade_plans)}")

        # -------------------------------------------------------------
        # STAGE 4: Automated Paper Trading Lifecycle
        # -------------------------------------------------------------
        # 4A. Auto-Exits: Check Stop-Loss and Targets on current day bars
        today_bars = market_df[market_df["trading_date"] == effective_date]
        if today_bars.empty:
            today_bars = market_df.groupby("symbol").last().reset_index()

        closed_trades = self.paper_trader.on_daily_market_data(today_bars)
        exits_count = len(closed_trades)

        # 4B. Auto-Entries: Execute approved trade plans
        approved_plans = [p for p in scan_report.trade_plans if p.risk_gate_outcome in {"APPROVED", "RESIZED"}]
        sector_lookup = {}
        for _, row in today_bars.iterrows():
            sector_lookup[str(row["symbol"]).upper()] = str(row.get("sector", "OTHER"))

        new_positions = self.paper_trader.execute_trade_plans(
            approved_plans,
            sector_lookup=sector_lookup,
        )
        entries_count = len(new_positions)

        # -------------------------------------------------------------
        # STAGE 5: Persist Ledger & Generate Rich Audit Report
        # -------------------------------------------------------------
        summary = self.paper_trader.get_portfolio_summary()
        report_file = self._generate_markdown_report(
            scan_report=scan_report,
            closed_trades=closed_trades,
            new_positions=new_positions,
            summary=summary,
            effective_date=effective_date,
            source_desc=source_desc,
        )

        result = DailyPipelineExecutionResult(
            run_timestamp=run_ts,
            trading_date=str(effective_date),
            data_source=source_desc,
            rows_ingested=rows_ingested,
            market_regime=scan_report.regime.regime,
            regime_confidence=scan_report.regime.confidence_score,
            total_screened=len(scan_report.ranked_candidates) + len(scan_report.rejected_candidates),
            approved_plans_count=len(approved_plans),
            rejected_plans_count=len(scan_report.rejected_candidates),
            exits_executed=exits_count,
            entries_executed=entries_count,
            open_positions_count=summary["open_positions_count"],
            current_cash=summary["current_cash"],
            total_equity=summary["total_equity"],
            total_return_pct=summary["total_return_pct"],
            report_path=str(report_file),
        )

        self._print_terminal_summary(result, scan_report, closed_trades, new_positions, summary)
        return result

    def _acquire_market_data(
        self,
        target_date: Optional[date],
        csv_file: Optional[str | Path],
    ) -> Tuple[pd.DataFrame, str, date]:
        """Acquires market data via live NSE download, specified CSV, or cumulative dataset."""
        if csv_file and Path(csv_file).exists():
            df = read_market_csv(csv_file)
            df["trading_date"] = pd.to_datetime(df["trading_date"]).dt.date
            eff_date = df["trading_date"].max()
            return df, f"Custom CSV ({csv_file})", eff_date

        # Attempt download from NSE
        eff_date = target_date or date.today()
        download_mgr = DownloadManager()

        # Try up to 3 previous business days if today is weekend or holiday
        trial_dates = [eff_date]
        for days_back in range(1, 4):
            trial_dates.append(eff_date - timedelta(days=days_back))

        downloaded_df = None
        source_desc = None
        resolved_date = eff_date

        for d in trial_dates:
            try:
                res = download_mgr.download(d)
                if res.success and res.file_path and res.file_path.exists():
                    downloaded_df = read_market_csv(res.file_path)
                    downloaded_df["trading_date"] = d
                    resolved_date = d
                    source_desc = f"Live NSE Bhavcopy Download ({res.file_path.name})"
                    self.logger.info(f"Downloaded live NSE data for {d}: {len(downloaded_df)} records")
                    break
            except Exception as e:
                self.logger.warning(f"Could not fetch NSE data for {d}: {e}")

        # Check existing cumulative historical dataset
        hist_csv = Path("downloads/raw/historical_nifty500_dataset.csv")
        base_hist_df = pd.DataFrame()
        if hist_csv.exists():
            base_hist_df = read_market_csv(hist_csv)
            base_hist_df["trading_date"] = pd.to_datetime(base_hist_df["trading_date"]).dt.date

        if downloaded_df is not None and not downloaded_df.empty:
            # Combine newly downloaded live day with historical dataset to maintain multi-horizon context
            if not base_hist_df.empty:
                combined_df = pd.concat([
                    base_hist_df[base_hist_df["trading_date"] != resolved_date],
                    downloaded_df
                ], ignore_index=True).sort_values(["trading_date", "symbol"]).reset_index(drop=True)
                combined_df.to_csv(hist_csv, index=False)
                return combined_df, f"{source_desc} (Combined with 1-Year History)", resolved_date
            return downloaded_df, source_desc, resolved_date

        if not base_hist_df.empty:
            eff_date = base_hist_df["trading_date"].max()
            return base_hist_df, "Historical Multi-Session NIFTY 500 Dataset", eff_date

        # Fallback to local Bhavcopy
        bhav_csv = Path("downloads/raw/market_data_2026-09-25.csv")
        if bhav_csv.exists():
            df = read_market_csv(bhav_csv)
            df["trading_date"] = pd.to_datetime(df["trading_date"]).dt.date
            eff_date = df["trading_date"].max()
            return df, "Local NSE Bhavcopy (2026-09-25)", eff_date

        return pd.DataFrame(), "None", date.today()

    def _inject_to_database(self, df: pd.DataFrame) -> int:
        """Injects symbol records and OHLCV market data into PostgreSQL."""
        if df.empty or "symbol" not in df.columns:
            return 0

        ingested = 0
        try:
            with database.engine.connect() as conn:
                # 1. Update/insert unique symbols
                symbols = df["symbol"].str.strip().str.upper().unique()
                for sym in symbols:
                    conn.execute(
                        text("""
                            INSERT INTO public.symbol (symbol_id, symbol_code, symbol_name, exchange, instrument_type, lot_size, tick_size, created_at, updated_at, is_fno, is_active)
                            VALUES (gen_random_uuid(), :code, :code, 'NSE', 'EQUITY', 1, 0.05, NOW(), NOW(), TRUE, TRUE)
                            ON CONFLICT (symbol_code) DO NOTHING
                        """),
                        {"code": sym},
                    )

                # 2. Bulk insert market_data
                sym_map = dict(conn.execute(text("SELECT symbol_code, symbol_id FROM public.symbol")).fetchall())

                # Sample up to last session bars
                latest_date = df["trading_date"].max()
                latest_rows = df[df["trading_date"] == latest_date]

                for _, r in latest_rows.iterrows():
                    code = str(r["symbol"]).strip().upper()
                    if code not in sym_map:
                        continue
                    sid = sym_map[code]
                    t_date = r["trading_date"]
                    conn.execute(
                        text("""
                            INSERT INTO public.market_data (
                                market_data_id, symbol_id, trading_date,
                                open_price, high_price, low_price, close_price, adjusted_close, volume, is_active, created_at, updated_at
                            )
                            VALUES (
                                gen_random_uuid(), :sid, :tdate,
                                :open, :high, :low, :close, :close, :vol, true, NOW(), NOW()
                            )
                            ON CONFLICT (symbol_id, trading_date) DO UPDATE
                            SET close_price = EXCLUDED.close_price, volume = EXCLUDED.volume, is_active = true, updated_at = NOW()
                        """),
                        {
                            "sid": sid,
                            "tdate": t_date,
                            "open": float(r["open"]),
                            "high": float(r["high"]),
                            "low": float(r["low"]),
                            "close": float(r["close"]),
                            "vol": int(r.get("volume", 1000)),
                        },
                    )
                    ingested += 1

                conn.commit()
        except Exception as e:
            self.logger.warning(f"Database injection notice: {e}")

        return ingested

    def _generate_markdown_report(
        self,
        scan_report: ScanReport,
        closed_trades: List[PaperTradeRecord],
        new_positions: List[PaperPosition],
        summary: Dict[str, Any],
        effective_date: date,
        source_desc: str,
    ) -> Path:
        """Generates comprehensive daily paper trading executive report."""
        report_path = self.reports_dir / f"paper_trading_daily_report_{effective_date}.md"

        lines = [
            "# AI Trading OS -- Daily Automated Paper Trading Report",
            f"**Execution Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Trading Date**: {effective_date} | **Data Source**: {source_desc}  ",
            "",
            "## 1. Portfolio Ledger Summary",
            f"- **Initial Capital**: ₹{summary['initial_capital']:,.2f}",
            f"- **Current Cash**: ₹{summary['current_cash']:,.2f}",
            f"- **Total Portfolio Equity**: ₹{summary['total_equity']:,.2f}",
            f"- **Total Return**: {summary['total_return_pct']:+.2f}%",
            f"- **Active Open Positions**: {summary['open_positions_count']}",
            f"- **Total Closed Trades**: {summary['total_closed_trades']} (Win Rate: {summary['win_rate_pct']}%, Profit Factor: {summary['profit_factor']})",
            "",
            "## 2. Automated Paper Trading Executions",
        ]

        if closed_trades:
            lines.append("### Automated Exits (Today)")
            lines.append("| Symbol | Entry Date | Exit Date | Entry Price | Exit Price | Qty | Net P&L (₹) | P&L % | Reason |")
            lines.append("|---|---|---|---|---|---|---|---|---|")
            for t in closed_trades:
                lines.append(f"| {t.symbol} | {t.entry_date} | {t.exit_date} | {t.entry_price:,.2f} | {t.exit_price:,.2f} | {t.quantity} | {t.net_pnl:+,.2f} | {t.pnl_pct:+.2f}% | {t.exit_reason} |")
        else:
            lines.append("*(No positions exited today - all active positions within risk bounds)*")

        lines.append("")
        if new_positions:
            lines.append("### Automated Entries (Today)")
            lines.append("| Symbol | Sector | Fill Price (with slippage) | Qty | Stop Loss | Target | Capital Allocated |")
            lines.append("|---|---|---|---|---|---|---|")
            for p in new_positions:
                val = p.quantity * p.entry_price
                lines.append(f"| {p.symbol} | {p.sector_id} | ₹{p.entry_price:,.2f} | {p.quantity} | ₹{p.stop_loss:,.2f} | ₹{p.target:,.2f} | ₹{val:,.2f} |")
        else:
            lines.append("*(No new entries approved by Risk Gate under current market regime constraints)*")

        lines.append("")
        lines.append("## 3. Active Open Paper Positions")
        if summary["open_positions"]:
            lines.append("| Symbol | Sector | Entry Date | Entry Price | Current Price | Unrealized P&L | Return % | Stop Loss | Target | Days Held |")
            lines.append("|---|---|---|---|---|---|---|---|---|---|")
            for pos in summary["open_positions"]:
                lines.append(
                    f"| {pos['symbol']} | {pos['sector_id']} | {pos['entry_date']} | "
                    f"₹{pos['entry_price']:,.2f} | ₹{pos['current_price']:,.2f} | "
                    f"₹{pos['unrealized_pnl']:+,.2f} | {pos['unrealized_pnl_pct']:+.2f}% | "
                    f"₹{pos['stop_loss']:,.2f} | ₹{pos['target']:,.2f} | {pos['days_held']}d |"
                )
        else:
            lines.append("*(No open paper positions currently active)*")

        lines.append("")
        lines.append("## 4. Market-Index & Sector Intelligence Context (Section 9)")
        lines.append("```")
        lines.append(scan_report.format_section_9_output())
        lines.append("```")

        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path

    def _print_terminal_summary(
        self,
        res: DailyPipelineExecutionResult,
        scan_report: ScanReport,
        closed: List[PaperTradeRecord],
        entries: List[PaperPosition],
        summary: Dict[str, Any],
    ) -> None:
        """Prints clean, world-class executive output to terminal."""
        sep = "=" * 80
        subsep = "-" * 80

        print(sep)
        print("  AI TRADING OPERATING SYSTEM (AI-TOS) -- AUTOMATED DAILY PIPELINE")
        print(f"  Session Date: {res.trading_date} | Source: {res.data_source}")
        print(sep)
        print(f"  [1] PIPELINE INGESTION & MARKET REGIME")
        print(f"      * Database Rows Ingested : {res.rows_ingested}")
        print(f"      * Market Regime State     : {res.market_regime} ({res.regime_confidence:.1f}% confidence)")
        print(f"      * Breadth & Sector State  : AD Ratio {scan_report.breadth.ad_ratio:.2f} ({scan_report.breadth.breadth_regime})")
        print(subsep)

        print(f"  [2] AUTOMATED PAPER EXECUTIONS (AUTO-EXIT & AUTO-ENTRY)")
        print(f"      * Automated Exits Triggered : {len(closed)}")
        for c in closed:
            print(f"        -> EXIT {c.symbol}: Net P&L Rs. {c.net_pnl:+,.2f} ({c.pnl_pct:+.2f}%) via [{c.exit_reason}]")
        print(f"      * Automated Entries Filled   : {len(entries)}")
        for e in entries:
            print(f"        -> ENTRY {e.symbol} ({e.sector_id}): Qty {e.quantity} @ Rs. {e.entry_price:,.2f} | Stop: {e.stop_loss:,.2f} | Target: {e.target:,.2f}")
        print(subsep)

        print(f"  [3] CURRENT PAPER PORTFOLIO LEDGER STATUS")
        print(f"      * Initial Capital  : Rs. {summary['initial_capital']:,.2f}")
        print(f"      * Available Cash   : Rs. {summary['current_cash']:,.2f}")
        print(f"      * Total Equity     : Rs. {summary['total_equity']:,.2f} ({summary['total_return_pct']:+.2f}%)")
        print(f"      * Active Positions : {summary['open_positions_count']}")
        print(f"      * Closed Trades    : {summary['total_closed_trades']} (Win Rate: {summary['win_rate_pct']}%, Profit Factor: {summary['profit_factor']})")

        if summary["open_positions"]:
            print("      * Open Positions Ledger:")
            for p in summary["open_positions"]:
                print(f"        - {p['symbol']:<10} {p['sector_id']:<15} Qty: {p['quantity']:<4} Price: {p['current_price']:<9.2f} P&L: Rs. {p['unrealized_pnl']:<+9.2f} ({p['unrealized_pnl_pct']:+.2f}%)")

        print(subsep)
        print(f"  Full Markdown Report Saved: {res.report_path}")
        print(sep)
