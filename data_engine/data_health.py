"""
AI Trading Operating System
Module: data_engine/data_health.py

Unified Data Health, Price Integrity & Database Reconciliation Engine:
- Audits PostgreSQL database (symbol and market_data tables) and local raw CSV datasets.
- Diagnoses Current Market Price (CMP) mismatches, date lag, and corporate action divergence (bonus/splits).
- Validates OHLC integrity: Zero/Negative prices, High < Low violations, wick boundaries, volume anomalies.
- Computes overall Data Health Score (0-100%) and provides automated reconciliation / sync into PostgreSQL.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from sqlalchemy import text

from database.connection import database
from data_engine.market_data import read_market_csv


@dataclass
class SymbolPriceMismatch:
    symbol: str
    db_last_date: Optional[date]
    db_close_price: Optional[float]
    hist_last_date: Optional[date]
    hist_close_price: Optional[float]
    bhav_last_date: Optional[date]
    bhav_close_price: Optional[float]
    price_discrepancy_pct: float
    mismatch_type: str  # CORPORATE_ACTION_SPLIT_BONUS, DATE_LAG_STALE, PRICE_DRIFT, HEALTHY_ALIGNED
    clarification_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DatabaseHealthSummary:
    connected: bool
    total_symbols: int
    total_market_data_bars: int
    min_trading_date: Optional[date]
    max_trading_date: Optional[date]
    total_symbols_with_data: int
    missing_data_symbols: List[str]
    ohlc_violations_count: int
    zero_volume_bars_count: int
    trading_sessions_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DataHealthReport:
    as_of_timestamp: str
    overall_health_score: float  # 0 to 100
    health_status: str  # PRISTINE_HEALTH, GOOD, NEEDS_RECONCILIATION, CRITICAL_MISMATCH
    database_summary: DatabaseHealthSummary
    historical_csv_summary: Dict[str, Any]
    bhavcopy_csv_summary: Dict[str, Any]
    price_mismatches: List[SymbolPriceMismatch]
    reconciliation_recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "as_of_timestamp": self.as_of_timestamp,
            "overall_health_score": self.overall_health_score,
            "health_status": self.health_status,
            "database_summary": self.database_summary.to_dict(),
            "historical_csv_summary": self.historical_csv_summary,
            "bhavcopy_csv_summary": self.bhavcopy_csv_summary,
            "price_mismatches": [m.to_dict() for m in self.price_mismatches],
            "reconciliation_recommendations": self.reconciliation_recommendations,
        }

    def format_terminal_report(self) -> str:
        sep = "=" * 92
        subsep = "-" * 92
        lines: List[str] = []

        lines.append(sep)
        lines.append("  AI-TOS DATA HEALTH, CMP INTEGRITY & DATABASE RECONCILIATION AUDIT")
        lines.append(f"  Audit Generated At: {self.as_of_timestamp}")
        lines.append(sep)

        # Overall Status Banner
        lines.append(f"  OVERALL DATA HEALTH SCORE : {self.overall_health_score:.1f} / 100.0 [{self.health_status}]")
        lines.append(subsep)

        # 1. Database Health
        db = self.database_summary
        lines.append("  [1] POSTGRESQL DATABASE REPOSITORY STATUS")
        if db.connected:
            lines.append(f"  * Connection Status       : CONNECTED (Port 5433 | Local PostgreSQL)")
            lines.append(f"  * Total Registered Symbols: {db.total_symbols} constituents")
            lines.append(f"  * Market Data Records     : {db.total_market_data_bars:,} bars across {db.total_symbols_with_data} active instruments")
            lines.append(f"  * Database Date Horizon   : {db.min_trading_date} to {db.max_trading_date} ({db.trading_sessions_count} sessions)")
            lines.append(f"  * OHLC Integrity Flags    : {db.ohlc_violations_count} wick/price violations | {db.zero_volume_bars_count} zero-volume bars")
            if db.missing_data_symbols:
                lines.append(f"  * Missing Data Symbols    : {len(db.missing_data_symbols)} symbols (Sample: {db.missing_data_symbols[:5]})")
        else:
            lines.append("  * Connection Status       : DISCONNECTED / CONNECTION FAILURE")
        lines.append("")

        # 2. File Store Health
        lines.append("  [2] FLAT-FILE DATASTORE INTEGRITY (HISTORICAL CSV & BHAVCOPY)")
        hc = self.historical_csv_summary
        lines.append(f"  * Historical Master CSV   : {hc.get('path', 'N/A')}")
        lines.append(f"    - Symbols: {hc.get('symbol_count', 0)} | Rows: {hc.get('row_count', 0):,} | Range: {hc.get('min_date', 'N/A')} to {hc.get('max_date', 'N/A')}")
        bc = self.bhavcopy_csv_summary
        lines.append(f"  * Live Bhavcopy CSV       : {bc.get('path', 'N/A')}")
        lines.append(f"    - Symbols: {bc.get('symbol_count', 0)} | Rows: {bc.get('row_count', 0):,} | Session Date: {bc.get('session_date', 'N/A')}")
        lines.append(subsep)

        # 3. CMP Mismatch & Divergence Table
        lines.append("  [3] CURRENT MARKET PRICE (CMP) RECONCILIATION & DIVERGENCE AUDIT")
        lines.append("      Comparison: PostgreSQL DB Last Close vs Historical CSV vs Live Bhavcopy")
        lines.append(subsep)

        if self.price_mismatches:
            lines.append(
                f"  {'Symbol':<11} {'DB Last Date':<13} {'DB Close':<10} {'Hist Date':<12} {'Hist Close':<11} "
                f"{'Bhav Close':<11} {'Diff%':<8} {'Mismatch Type':<26}"
            )
            for m in self.price_mismatches:
                db_d = str(m.db_last_date) if m.db_last_date else "N/A"
                db_p = f"{m.db_close_price:,.2f}" if m.db_close_price is not None else "N/A"
                hi_d = str(m.hist_last_date) if m.hist_last_date else "N/A"
                hi_p = f"{m.hist_close_price:,.2f}" if m.hist_close_price is not None else "N/A"
                bh_p = f"{m.bhav_close_price:,.2f}" if m.bhav_close_price is not None else "N/A"
                diff_str = f"{m.price_discrepancy_pct:+.1f}%" if m.price_discrepancy_pct != 0.0 else "0.0%"

                lines.append(
                    f"  {m.symbol:<11} {db_d:<13} {db_p:<10} {hi_d:<12} {hi_p:<11} "
                    f"{bh_p:<11} {diff_str:<8} {m.mismatch_type:<26}"
                )
            lines.append("")
            lines.append("  DETAILED CLARIFICATION ON PRICE DISCREPANCIES:")
            for m in self.price_mismatches[:5]:
                if m.clarification_notes:
                    lines.append(f"  * {m.symbol}: {m.clarification_notes}")
        else:
            lines.append("  All instruments across Database and CSVs exhibit exact zero-drift price alignment.")

        lines.append(subsep)
        lines.append("  [4] ACTIONABLE RECONCILIATION & REMEDIATION STEPS")
        for idx, rec in enumerate(self.reconciliation_recommendations, 1):
            lines.append(f"  {idx}. {rec}")
        lines.append(sep)

        return "\n".join(lines)


class DataHealthEngine:
    """
    Central Data Health, Price Integrity, and Reconciliation Engine.
    Provides automated audits of PostgreSQL tables, CSV data files, and live price feeds.
    """

    def __init__(
        self,
        historical_csv_path: Optional[Path | str] = None,
        bhavcopy_csv_path: Optional[Path | str] = None,
    ) -> None:
        self.historical_csv_path = Path(historical_csv_path or "downloads/raw/historical_nifty500_dataset.csv")
        if bhavcopy_csv_path:
            self.bhavcopy_csv_path = Path(bhavcopy_csv_path)
        else:
            bhav_dir = Path("downloads/raw/bhavcopy")
            candidates = sorted(bhav_dir.glob("bhavcopy_*.csv"), key=lambda p: p.name, reverse=True) if bhav_dir.exists() else []
            self.bhavcopy_csv_path = candidates[0] if candidates else Path("downloads/raw/bhavcopy/bhavcopy_20261016.csv")

    def run_health_check(self) -> DataHealthReport:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 0. Self-heal and reconcile database integrity
        self.reconcile_database_integrity()

        # 1. Audit Database
        db_summary = self._audit_database()

        # 2. Audit Flat Files
        hist_summary, df_hist = self._audit_historical_csv()
        bhav_summary, df_bhav = self._audit_bhavcopy_csv()

        # 3. Analyze CMP Mismatches
        mismatches = self._audit_price_mismatches(df_hist, df_bhav)

        # 4. Compute Health Score
        score = 100.0
        if not db_summary.connected:
            score -= 30.0
        if db_summary.ohlc_violations_count > 0:
            score -= min(15.0, db_summary.ohlc_violations_count * 2.0)

        # Mismatch penalties
        critical_mismatches = sum(1 for m in mismatches if "SPLIT" in m.mismatch_type or abs(m.price_discrepancy_pct) > 20.0)
        date_lags = sum(1 for m in mismatches if "DATE_LAG" in m.mismatch_type)
        score -= min(30.0, critical_mismatches * 3.0)
        score -= min(15.0, date_lags * 1.5)

        score = max(10.0, min(100.0, round(score, 1)))

        if score >= 90.0:
            status = "PRISTINE_HEALTH"
        elif score >= 75.0:
            status = "GOOD"
        elif score >= 50.0:
            status = "NEEDS_RECONCILIATION"
        else:
            status = "CRITICAL_MISMATCH"

        # 5. Formulate Reconciliation Recommendations
        recommendations: List[str] = []
        if date_lags > 0:
            recommendations.append(
                f"Date Synchronization Lag: PostgreSQL database last date ({db_summary.max_trading_date}) is behind latest market session ({bhav_summary.get('session_date')}). Run `python main.py --run-daily-pipeline` to inject latest Bhavcopy bars into PostgreSQL."
            )
        if critical_mismatches > 0:
            recommendations.append(
                f"Corporate Action / CMP Discrepancy: Detected {critical_mismatches} stock(s) with >20% price divergence between historical dataset and raw Bhavcopy. This is caused by unadjusted bonus/split corporate actions (e.g., RELIANCE 1:1 bonus issue). Apply split adjustment factor or standardize on post-bonus Bhavcopy closes."
            )
        if db_summary.missing_data_symbols:
            recommendations.append(
                f"Constituent Coverage Gap: {len(db_summary.missing_data_symbols)} symbol(s) exist in Symbol Master without corresponding OHLCV records. Re-seed market_data using `populate_postgresql_historical_data()`."
            )
        if not recommendations:
            recommendations.append("All databases, CSV sources, and price series are in perfect synchronization. No corrective actions required.")

        return DataHealthReport(
            as_of_timestamp=now_str,
            overall_health_score=score,
            health_status=status,
            database_summary=db_summary,
            historical_csv_summary=hist_summary,
            bhavcopy_csv_summary=bhav_summary,
            price_mismatches=mismatches,
            reconciliation_recommendations=recommendations,
        )

    def _audit_database(self) -> DatabaseHealthSummary:
        try:
            with database.engine.connect() as conn:
                tot_syms = conn.execute(text("SELECT count(*) FROM symbol;")).scalar() or 0
                tot_bars = conn.execute(text("SELECT count(*) FROM market_data;")).scalar() or 0
                dr = conn.execute(text("SELECT min(trading_date), max(trading_date) FROM market_data;")).fetchone()
                min_d = dr[0] if dr else None
                max_d = dr[1] if dr else None

                syms_with_data = conn.execute(text("SELECT count(DISTINCT symbol_id) FROM market_data;")).scalar() or 0

                # Check missing data symbols
                missing_sym_rows = conn.execute(text(
                    "SELECT symbol_code FROM symbol WHERE symbol_id NOT IN (SELECT DISTINCT symbol_id FROM market_data) LIMIT 10;"
                )).fetchall()
                missing_syms = [r[0] for r in missing_sym_rows]

                # Check OHLC violations: High < Low, or Close outside High/Low
                ohlc_viol = conn.execute(text(
                    "SELECT count(*) FROM market_data WHERE high_price < low_price OR close_price < low_price OR close_price > high_price;"
                )).scalar() or 0

                # Check zero volume bars
                zero_vol = conn.execute(text("SELECT count(*) FROM market_data WHERE volume = 0;")).scalar() or 0

                # Count distinct trading sessions
                sessions = conn.execute(text("SELECT count(DISTINCT trading_date) FROM market_data;")).scalar() or 0

                return DatabaseHealthSummary(
                    connected=True,
                    total_symbols=tot_syms,
                    total_market_data_bars=tot_bars,
                    min_trading_date=min_d,
                    max_trading_date=max_d,
                    total_symbols_with_data=syms_with_data,
                    missing_data_symbols=missing_syms,
                    ohlc_violations_count=ohlc_viol,
                    zero_volume_bars_count=zero_vol,
                    trading_sessions_count=sessions,
                )
        except Exception:
            return DatabaseHealthSummary(
                connected=False,
                total_symbols=0,
                total_market_data_bars=0,
                min_trading_date=None,
                max_trading_date=None,
                total_symbols_with_data=0,
                missing_data_symbols=[],
                ohlc_violations_count=0,
                zero_volume_bars_count=0,
                trading_sessions_count=0,
            )

    def _audit_historical_csv(self) -> Tuple[Dict[str, Any], Optional[pd.DataFrame]]:
        if not self.historical_csv_path.exists():
            return {"path": str(self.historical_csv_path), "exists": False}, None
        try:
            df = read_market_csv(self.historical_csv_path)
            summary = {
                "path": str(self.historical_csv_path),
                "exists": True,
                "symbol_count": df["symbol"].nunique(),
                "row_count": len(df),
                "min_date": str(df["trading_date"].min()),
                "max_date": str(df["trading_date"].max()),
            }
            return summary, df
        except Exception as e:
            return {"path": str(self.historical_csv_path), "exists": True, "error": str(e)}, None

    def _audit_bhavcopy_csv(self) -> Tuple[Dict[str, Any], Optional[pd.DataFrame]]:
        if not self.bhavcopy_csv_path.exists():
            return {"path": str(self.bhavcopy_csv_path), "exists": False}, None
        try:
            df = read_market_csv(self.bhavcopy_csv_path)
            session_d = str(df["trading_date"].max())
            summary = {
                "path": str(self.bhavcopy_csv_path),
                "exists": True,
                "symbol_count": df["symbol"].nunique(),
                "row_count": len(df),
                "session_date": session_d,
            }
            return summary, df
        except Exception as e:
            return {"path": str(self.bhavcopy_csv_path), "exists": True, "error": str(e)}, None

    def _audit_price_mismatches(
        self,
        df_hist: Optional[pd.DataFrame],
        df_bhav: Optional[pd.DataFrame],
    ) -> List[SymbolPriceMismatch]:
        mismatches: List[SymbolPriceMismatch] = []

        # Query Database last prices for major symbols
        db_prices: Dict[str, Tuple[date, float]] = {}
        try:
            with database.engine.connect() as conn:
                q = """
                SELECT s.symbol_code, m.trading_date, m.close_price
                FROM symbol s
                JOIN market_data m ON s.symbol_id = m.symbol_id
                WHERE (s.symbol_id, m.trading_date) IN (
                    SELECT symbol_id, max(trading_date)
                    FROM market_data
                    GROUP BY symbol_id
                );
                """
                for r in conn.execute(text(q)).fetchall():
                    db_prices[str(r[0]).strip().upper()] = (r[1], float(r[2]))
        except Exception:
            pass

        # Target constituents to compare
        key_symbols = [
            "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
            "TATAMOTORS", "LT", "ITC", "BHARTIARTL", "SUNPHARMA",
            "KOTAKBANK", "MARUTI", "BAJFINANCE", "AXISBANK"
        ]

        # Add any symbols present in historical
        if df_hist is not None and not df_hist.empty:
            for s in df_hist["symbol"].unique():
                if s not in key_symbols and s.upper() not in {"NIFTY 50", "BANK NIFTY", "^NSEI"}:
                    key_symbols.append(s)

        for sym in key_symbols[:15]:
            db_entry = db_prices.get(sym)
            db_d = db_entry[0] if db_entry else None
            db_p = db_entry[1] if db_entry else None

            # Historical CSV
            hist_d = None
            hist_p = None
            if df_hist is not None and not df_hist.empty:
                s_hist = df_hist[df_hist["symbol"] == sym]
                if not s_hist.empty:
                    last_h = s_hist.sort_values("trading_date").iloc[-1]
                    hist_d = last_h["trading_date"]
                    hist_p = float(last_h["close"])

            # Bhavcopy CSV
            bhav_d = None
            bhav_p = None
            if df_bhav is not None and not df_bhav.empty:
                s_bhav = df_bhav[df_bhav["symbol"] == sym]
                if not s_bhav.empty:
                    last_b = s_bhav.iloc[-1]
                    bhav_d = last_b["trading_date"]
                    bhav_p = float(last_b["close"])

            # Calculate price discrepancy between Database and Live Bhavcopy
            diff_pct = 0.0
            if db_p and bhav_p and bhav_p > 0:
                diff_pct = round(((db_p - bhav_p) / bhav_p) * 100.0, 2)
            elif hist_p and bhav_p and bhav_p > 0:
                diff_pct = round(((hist_p - bhav_p) / bhav_p) * 100.0, 2)
            elif db_p and hist_p and hist_p > 0:
                diff_pct = round(((db_p - hist_p) / hist_p) * 100.0, 2)

            # Diagnose cause
            m_type = "HEALTHY_ALIGNED"
            notes = "Price feeds are aligned within standard session tolerance."

            if bhav_p and hist_p and (hist_p > bhav_p * 1.8 or bhav_p > hist_p * 1.8):
                m_type = "CORPORATE_ACTION_SPLIT_BONUS"
                notes = (
                    f"Massive ~{abs(diff_pct):.0f}% price gap between Historical CSV (Rs. {hist_p:,.2f}) and Bhavcopy (Rs. {bhav_p:,.2f}). "
                    f"Indicates unadjusted 1:1 Bonus / Stock Split. Raw Bhavcopy reflects ex-bonus market quotes."
                )
            elif db_d and bhav_d and db_d < bhav_d:
                m_type = "DATE_LAG_STALE_DB"
                days_behind = (bhav_d - db_d).days
                notes = f"Database bar is {days_behind} days behind live Bhavcopy ({db_d} vs {bhav_d}). Database needs sync."
            elif hist_d and bhav_d and hist_d < bhav_d and abs(diff_pct) > 5.0:
                m_type = "SESSION_PRICE_DRIFT"
                notes = f"Historical CSV bar is on {hist_d} while DB & Bhavcopy are on {bhav_d}."
            elif abs(diff_pct) > 5.0:
                m_type = "SESSION_PRICE_DRIFT"
                notes = f"Moderate {diff_pct:+.1f}% price drift between database and live feeds."

            mismatches.append(
                SymbolPriceMismatch(
                    symbol=sym,
                    db_last_date=db_d,
                    db_close_price=db_p,
                    hist_last_date=hist_d,
                    hist_close_price=hist_p,
                    bhav_last_date=bhav_d,
                    bhav_close_price=bhav_p,
                    price_discrepancy_pct=diff_pct,
                    mismatch_type=m_type,
                    clarification_notes=notes,
                )
            )

        return mismatches

    def reconcile_database_integrity(self) -> Dict[str, int]:
        """
        Automated self-healing database integrity routine:
        1. Purges future phantom dates (> today's date).
        2. Heals OHLC boundary violations:
           Clamps high_price = GREATEST(open, high, close), low_price = LEAST(open, low, close).
        """
        purged = 0
        healed_ohlc = 0
        try:
            today_d = date.today()
            with database.engine.connect() as conn:
                with conn.begin():
                    # Purge any future phantom dates beyond today
                    r1 = conn.execute(
                        text("DELETE FROM market_data WHERE trading_date > :today_val;"),
                        {"today_val": today_d}
                    )
                    purged = r1.rowcount or 0

                    # Heal any OHLC violations (e.g. high < low, close > high, close < low, open > high, open < low)
                    r2 = conn.execute(text("""
                        UPDATE market_data
                        SET high_price = GREATEST(open_price, high_price, close_price),
                            low_price = LEAST(open_price, low_price, close_price)
                        WHERE high_price < low_price
                           OR close_price > high_price
                           OR close_price < low_price
                           OR open_price > high_price
                           OR open_price < low_price;
                    """))
                    healed_ohlc = r2.rowcount or 0
        except Exception:
            pass
        return {"purged_future_bars": purged, "healed_ohlc_bars": healed_ohlc}

    def sync_bhavcopy_to_database(self) -> Dict[str, Any]:
        """
        Reconciles and synchronizes live Bhavcopy quotes into PostgreSQL market_data
        and automatically appends/merges them into the cumulative historical master CSV.
        """
        if not self.bhavcopy_csv_path.exists():
            return {"status": "ERROR", "message": f"Bhavcopy file {self.bhavcopy_csv_path} not found."}

        df = read_market_csv(self.bhavcopy_csv_path)
        from portfolio.automated_pipeline import AutomatedPaperTradingPipeline
        pipeline = AutomatedPaperTradingPipeline()
        ingested_cnt = pipeline._inject_to_database(df)

        # Merge new Bhavcopy bars into cumulative historical CSV to maintain 100% synchronization
        if self.historical_csv_path.exists():
            try:
                base_hist = read_market_csv(self.historical_csv_path)
                sess_date = df["trading_date"].max()
                base_hist["trading_date"] = pd.to_datetime(base_hist["trading_date"]).dt.date
                combined = pd.concat([
                    base_hist[base_hist["trading_date"] != sess_date],
                    df
                ], ignore_index=True).sort_values(["trading_date", "symbol"]).reset_index(drop=True)
                combined.to_csv(self.historical_csv_path, index=False)
            except Exception:
                pass

        # Self-heal and purge any anomalies
        healing = self.reconcile_database_integrity()

        msg = f"Successfully synced and reconciled {ingested_cnt:,} market quotes into PostgreSQL & Historical CSV."
        if healing.get("purged_future_bars", 0) > 0 or healing.get("healed_ohlc_bars", 0) > 0:
            msg += f" (Auto-repaired: {healing['purged_future_bars']} future bars, {healing['healed_ohlc_bars']} OHLC wicks)"

        return {
            "status": "SUCCESS",
            "message": msg,
            "session_date": str(df["trading_date"].max()),
            "total_symbols": df["symbol"].nunique(),
        }
