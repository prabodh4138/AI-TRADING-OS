"""AI-TOS command-line entry point."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from app.application import Application
from portfolio.automated_pipeline import AutomatedPaperTradingPipeline
from portfolio.oos_paper_trading import OutOfSamplePaperTrader
from portfolio.paper_trader import PaperTradingManager


def main() -> None:
    p = argparse.ArgumentParser(description="AI Trading Operating System (AI-TOS)")
    p.add_argument("--scan", type=Path, help="Scan a local OHLCV/NSE Bhavcopy CSV")
    p.add_argument("--top", type=int, default=50, help="Maximum candidate ranking count (default: 50)")
    p.add_argument("--paper-trade", action="store_true", help="Automatically execute approved scan trade plans in paper portfolio")
    p.add_argument("--paper-portfolio", action="store_true", help="Display current active paper trading portfolio and performance")
    p.add_argument("--run-daily-pipeline", action="store_true", help="Execute daily automated end-to-end paper trading loop (Download -> Ingest DB -> Scan -> Auto Exit -> Auto Entry -> Report)")
    p.add_argument("--run-oos-paper", action="store_true", help="Execute multi-session Out-of-Sample automated paper trading simulation (Section 10 Mandate)")
    p.add_argument("--gtf-scan", action="store_true", help="Execute Pure GTF Institutional Demand & Supply Zone Trade Scanner with dedicated ML models")
    p.add_argument("--stock-thesis", type=str, help="Generate institutional 360-degree stock thesis (Why to Buy, Why to Hold, Why Not to Buy, Fundamentals & News)")
    p.add_argument("--date", type=str, help="Target date for daily pipeline (format: YYYY-MM-DD)")
    p.add_argument("--data-health", action="store_true", help="Audit database presence, check CMP mismatches, and diagnose price discrepancies")
    p.add_argument("--sync-db", action="store_true", help="Reconcile and sync latest Bhavcopy quotes into PostgreSQL database")
    p.add_argument("--fetch-yahoo", action="store_true", help="Fetch clean split-adjusted historical and live quotes from Yahoo Finance and sync to DB")
    p.add_argument("--fetch-yahoo-symbol", type=str, help="Fetch Yahoo Finance historical OHLCV data for a specific stock (e.g. RELIANCE, TCS)")
    p.add_argument("--period", type=str, default="2y", help="Historical period for Yahoo Finance download (1mo, 3mo, 6mo, 1y, 2y, 5y, max. Default: 2y)")
    p.add_argument("--mtf-zones", type=str, help="Generate dynamic Multi-Timeframe Demand Zone list (Yearly, Half-Yearly, Quarterly, Monthly, Daily) for a symbol")
    p.add_argument("--mtf-scan", action="store_true", help="Scan entire universe for dynamic demand zones and nested super-confluence")
    p.add_argument("--thesis", type=str, dest="stock_thesis", help="Generate institutional 360-degree stock thesis (alias for --stock-thesis)")
    p.add_argument("--run-pipeline", action="store_true", help="Execute 12-stage automated lifecycle from Governance Preflight to Dashboard Publication (Specification v3.1)")
    p.add_argument("--release-gates", action="store_true", help="Audit Release Gates RG-0 to RG-9 and certify paper-only boundary security")
    p.add_argument("--alerts", action="store_true", help="Display active P0-P3 system alerts and exceptions")
    p.add_argument("--fundamental-coverage", type=str, help="Evaluate 7-family fundamental coverage matrix for a symbol (Section 6 & 13)")
    p.add_argument("--run-all", action="store_true", help="One-Click Master Command: Simultaneously executes entire system across all modules end-to-end")
    p.add_argument("--reset-paper-ledger", action="store_true", help="Reset paper trading ledger to clean Rs. 1,000,000.00 cash and clear legacy test trades")
    p.add_argument("--dashboard", action="store_true", help="Launch Streamlit Command Center UI")
    args = p.parse_args()

    if args.reset_paper_ledger:
        pt = PaperTradingManager()
        pt.reset_ledger(capital=1_000_000.0)
        print("\n" + "=" * 75)
        print("  AI-TOS PAPER TRADING LEDGER RESET SUCCESSFUL")
        print("=" * 75)
        print("  Available Cash      : Rs. 1,000,000.00")
        print("  Active Positions    : 0")
        print("  Closed Trades Audit : 0")
        print("  Cash Reserve Buffer : 20.0% protected (Rs. 200,000.00)")
        print("  Max Positions Cap   : 12 high-conviction positions")
        print("=" * 75 + "\n")
        return

    if args.run_all:
        from core.master_pipeline import MasterOneClickPipeline
        master = MasterOneClickPipeline()
        target_d = None
        if args.date:
            target_d = datetime.strptime(args.date, "%Y-%m-%d").date()
        master.execute_complete_system(target_date=target_d, launch_dashboard=args.dashboard)
        return

    if args.dashboard:
        import subprocess
        import sys
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py"], check=True)
        return

    if args.run_pipeline:
        from core.orchestrator import PipelineOrchestrator
        orch = PipelineOrchestrator()
        target_d = None
        if args.date:
            target_d = datetime.strptime(args.date, "%Y-%m-%d").date()
        manifest = orch.execute_full_pipeline(target_date=target_d, csv_file=args.scan)
        print(manifest.format_terminal_summary())
        return

    if args.release_gates:
        from core.release_verifier import ReleaseGateVerifier
        verifier = ReleaseGateVerifier()
        report = verifier.audit_all_gates()
        print(report.format_terminal_report())
        return

    if args.alerts:
        from core.alerts import AlertManager
        mgr = AlertManager()
        active = mgr.get_active_alerts()
        print("\n" + "=" * 80)
        print("  ACTIVE SYSTEM ALERTS & EXCEPTIONS (P0–P3)")
        print("=" * 80)
        if not active:
            print("  No active alerts or exceptions. System status: NORMAL.")
        else:
            for a in active:
                print(f"  [{a.priority.value.upper()}] {a.title} ({a.created_at.strftime('%Y-%m-%d %H:%M')})")
                print(f"    Component: {a.source_component} | Category: {a.category}")
                print(f"    Details  : {a.description}")
                print("-" * 80)
        print("=" * 80 + "\n")
        return

    if args.fundamental_coverage:
        from analytics.fundamental_coverage import FundamentalCoverageEngine
        engine = FundamentalCoverageEngine()
        sym = args.fundamental_coverage.strip().upper()
        cov = engine.evaluate_stock_coverage(sym)
        print("\n" + "=" * 85)
        print(f"  FUNDAMENTAL COVERAGE MATRIX: {cov.company_name} ({cov.symbol})")
        print(f"  Sector: {cov.sector} | Coverage: {cov.overall_coverage_pct:.0f}% ({cov.available_families_count}/7 Families)")
        print(f"  Decision Readiness: {'SUFFICIENT' if cov.is_sufficient_for_decision else 'INCOMPLETE'}")
        print("=" * 85)
        print(f"  {'Metric':<25} {'Family':<20} {'Value':<12} {'Period':<12} {'Status':<12}")
        print("-" * 85)
        for m in cov.metrics:
            v_str = f"{m.value} {m.unit}" if m.value is not None else "N/A"
            print(f"  {m.metric_name:<25} {m.family.value:<20} {v_str:<12} {m.fiscal_period:<12} {m.coverage_status.value:<12}")
        print("=" * 85 + "\n")
        return

    if args.data_health:
        from data_engine.data_health import DataHealthEngine
        engine = DataHealthEngine(
            historical_csv_path=args.scan or "downloads/raw/historical_nifty500_dataset.csv"
        )
        report = engine.run_health_check()
        print(report.format_terminal_report())
        return

    if args.sync_db:
        from data_engine.data_health import DataHealthEngine
        engine = DataHealthEngine()
        result = engine.sync_bhavcopy_to_database()
        print("\n" + "=" * 70)
        print("  DATABASE RECONCILIATION RESULT")
        print("=" * 70)
        print(f"  Status       : {result['status']}")
        print(f"  Message      : {result['message']}")
        if "session_date" in result:
            print(f"  Session Date : {result['session_date']}")
            print(f"  Total Symbols: {result['total_symbols']}")
        print("=" * 70 + "\n")
        return

    if args.fetch_yahoo:
        from data_engine.yahoo_finance_pipeline import YahooFinanceDataPipeline
        pipeline = YahooFinanceDataPipeline()
        print(f"\n[YAHOO FINANCE PIPELINE] Downloading clean split-adjusted data (Period: {args.period})...")
        target_syms = None
        if args.scan and Path(args.scan).exists():
            import pandas as pd
            s_df = pd.read_csv(args.scan)
            if "symbol" in s_df.columns:
                target_syms = s_df["symbol"].unique().tolist()[:25]
        df, summary = pipeline.fetch_universe(symbols=target_syms, period=args.period, save_csv=True, sync_db=True)
        print(summary.format_terminal_report())
        return

    if args.fetch_yahoo_symbol:
        from data_engine.yahoo_finance_pipeline import YahooFinanceDataPipeline
        pipeline = YahooFinanceDataPipeline()
        sym = args.fetch_yahoo_symbol.strip().upper()
        print(f"\n[YAHOO FINANCE PIPELINE] Fetching {sym} with period={args.period}...")
        df = pipeline.fetch_symbol_ohlcv(sym, period=args.period)
        if df.empty:
            print(f"Error: Unable to fetch data for {sym} from Yahoo Finance.")
            return
        pipeline.sync_dataframe_to_database(df)
        print(f"Successfully fetched {len(df)} bars for {sym} ({df['trading_date'].min()} to {df['trading_date'].max()}). Latest Close: Rs. {df.iloc[-1]['close']:,.2f}")
        print(df.tail(5))
        return

    if args.mtf_zones:
        from analytics.dynamic_mtf_zones import DynamicMTFZoneEngine
        from data_engine.market_data import read_market_csv
        sym = args.mtf_zones.strip().upper()
        csv_file = args.scan or Path("downloads/raw/historical_nifty500_dataset.csv")
        if not Path(csv_file).exists():
            print(f"Error: Dataset {csv_file} not found.")
            return
        df = read_market_csv(csv_file)
        sym_df = df[df["symbol"] == sym]
        if sym_df.empty:
            print(f"Symbol {sym} not found in {csv_file}.")
            return
        engine = DynamicMTFZoneEngine()
        mat = engine.evaluate_symbol_zones(symbol=sym, daily_df=sym_df)
        print(mat.format_terminal_matrix())
        return

    if args.mtf_scan:
        from analytics.dynamic_mtf_zones import DynamicMTFZoneEngine
        from data_engine.market_data import read_market_csv
        csv_file = args.scan or Path("downloads/raw/historical_nifty500_dataset.csv")
        if not Path(csv_file).exists():
            print(f"Error: Dataset {csv_file} not found.")
            return
        df = read_market_csv(csv_file)
        engine = DynamicMTFZoneEngine()
        res = engine.scan_universe_dynamic_zones(df)
        print("\n" + "=" * 90)
        print("  DYNAMIC MULTI-TIMEFRAME DEMAND ZONE UNIVERSE SCAN")
        print("=" * 90)
        print(f"  Total Active Zones Found   : {len(res['all_zones_records'])}")
        print(f"  Yearly Demand Zones        : {len(res['yearly_demand_stocks'])}")
        print(f"  Half-Yearly Demand Zones   : {len(res['half_yearly_demand_stocks'])}")
        print(f"  Quarterly Demand Zones     : {len(res['quarterly_demand_stocks'])}")
        print(f"  Monthly Demand Zones       : {len(res['monthly_demand_stocks'])}")
        print(f"  Daily Demand Zones         : {len(res['daily_demand_stocks'])}")
        print(f"  Nested Super-Confluence    : {len(res['nested_super_zone_stocks'])}")
        print("-" * 90)
        if res["nested_super_zone_stocks"]:
            print("  TOP NESTED SUPER-ZONES (HIGHEST INSTITUTIONAL CONFLUENCE):")
            for nz in res["nested_super_zone_stocks"][:10]:
                print(f"  * {nz.symbol:<11} {nz.timeframe} @ Rs. {nz.proximal_line:<9.2f} nested in {nz.nested_parent_timeframe} (Rs. {nz.nested_parent_proximal:<9.2f}) | ML Win: {nz.ml_bounce_probability:.1f}%")
        print("=" * 90 + "\n")
        return

    if args.stock_thesis:
        from analytics.stock_thesis_engine import StockThesisEngine
        from data_engine.market_data import read_market_csv
        sym = args.stock_thesis.strip().upper()
        engine = StockThesisEngine()
        csv_file = args.scan or Path("downloads/raw/historical_nifty500_dataset.csv")
        df = None
        if Path(csv_file).exists():
            df = read_market_csv(csv_file)
        thesis = engine.generate_stock_thesis(sym, price_history=df)
        print(thesis.format_terminal_report())
        return

    if args.run_daily_pipeline:
        target_d = None
        if args.date:
            target_d = datetime.strptime(args.date, "%Y-%m-%d").date()
        pipeline = AutomatedPaperTradingPipeline()
        pipeline.run_daily_pipeline(target_date=target_d, csv_file=args.scan)
        return

    if args.run_oos_paper:
        csv_file = args.scan or Path("downloads/raw/historical_nifty500_dataset.csv")
        if not Path(csv_file).exists():
            print(f"Error: Dataset {csv_file} not found. Generate or specify historical dataset.")
            return
        import pandas as pd
        df = pd.read_csv(csv_file)
        trader = OutOfSamplePaperTrader(initial_capital=1_000_000.0, train_ratio=0.70)
        report = trader.run_oos_simulation(df)
        print(report.format_terminal_report())
        return

    if args.gtf_scan:
        csv_file = args.scan or Path("downloads/raw/historical_nifty500_dataset.csv")
        if not Path(csv_file).exists():
            csv_file = Path("downloads/raw/bhavcopy/bhavcopy_20261015.csv")
        from data_engine.market_data import read_market_csv
        from scanner.gtf_scanner import GTFTradeScanner
        from ai.hierarchical_engine import TradePlan
        df = read_market_csv(csv_file)
        scanner = GTFTradeScanner()
        res = scanner.scan_universe(df)
        print(res.format_terminal_report())

        if args.paper_trade:
            pt = PaperTradingManager()
            plans = []
            for c in res.actionable_candidates:
                # Size trade based on 1% risk
                risk_amt = pt.total_equity * 0.01
                risk_per_share = max(1.0, c.proximal_line - c.distal_line)
                qty = max(1, int(risk_amt // risk_per_share))
                plan = TradePlan(
                    symbol=c.symbol,
                    trading_date=res.as_of_date,
                    action="BUY",
                    entry_trigger=c.proximal_line,
                    stop_loss=c.distal_line,
                    target_zone=c.target_supply,
                    reward_to_risk=c.reward_to_risk,
                    position_size_shares=qty,
                    position_value=round(qty * c.proximal_line, 2),
                    risk_amount=round(qty * risk_per_share, 2),
                    risk_gate_outcome="APPROVED",
                    gate_reason=f"GTF {c.zone_type} Zone | Score {c.odds_enhancer_score}/10 | ML Prob {c.ml_success_probability:.1f}%",
                )
                plans.append(plan)
            if plans:
                new_pos = pt.execute_trade_plans(plans)
                print(f"\n[GTF PAPER EXECUTION] Executed {len(new_pos)} high-conviction Demand Zone paper orders into ledger.")
                print(f"Remaining Cash: Rs. {pt.current_cash:,.2f} | Total Equity: Rs. {pt.total_equity:,.2f}")
            else:
                print("\n[GTF PAPER EXECUTION] No Demand Zone setups currently meet actionable criteria.")
        return

    if args.paper_portfolio:
        pt = PaperTradingManager()
        summary = pt.get_portfolio_summary()
        print("\n" + "=" * 70)
        print("  AI-TOS AUTOMATED PAPER TRADING PORTFOLIO LEDGER")
        print("=" * 70)
        print(f"  Initial Capital  : Rs. {summary['initial_capital']:,.2f}")
        print(f"  Current Cash     : Rs. {summary['current_cash']:,.2f}")
        print(f"  Total Equity     : Rs. {summary['total_equity']:,.2f}")
        print(f"  Total Return     : {summary['total_return_pct']:+.2f}%")
        print(f"  Open Positions   : {summary['open_positions_count']}")
        print(f"  Closed Trades    : {summary['total_closed_trades']} (Win Rate: {summary['win_rate_pct']:.1f}%)")
        print("-" * 70)
        if summary["open_positions"]:
            print("  ACTIVE OPEN POSITIONS:")
            for pos in summary["open_positions"]:
                print(f"  * {pos['symbol']:<10} Qty: {pos['quantity']:<5} Entry: Rs. {pos['entry_price']:<8.2f} Current: Rs. {pos['current_price']:<8.2f} P&L: Rs. {pos['unrealized_pnl']:+8.2f} ({pos['unrealized_pnl_pct']:+.2f}%)")
        else:
            print("  No open paper positions currently active.")
        print("=" * 70 + "\n")
        return

    if args.scan:
        report = Application().scan_file(str(args.scan), top_n=args.top)
        print(report.format_section_9_output())

        if args.paper_trade:
            pt = PaperTradingManager()
            if report.trade_plans:
                new_pos = pt.execute_trade_plans(list(report.trade_plans))
                print(f"\n[PAPER EXECUTION] Executed {len(new_pos)} new paper orders into active portfolio.")
                print(f"Remaining Cash: Rs. {pt.current_cash:,.2f} | Total Equity: Rs. {pt.total_equity:,.2f}")
            else:
                print("\n[PAPER EXECUTION] No trade plans approved for execution by Risk Gate.")
        return

    p.print_help()


if __name__ == "__main__":
    main()
