"""
Unit Test Suite for Specification Baseline v3.1:
Master Final Consolidated System Specification v3.1 (16 October 2026).

Covers:
- Canonical Enums & Contracts (core/system_spec.py)
- Live Trading Boundary Enforcement (core/system_spec.py)
- Source Governance Registry & Preflight Gate (core/governance.py)
- Priority Alerts & Exceptions Engine (core/alerts.py)
- Independent Risk Gate & Canonical Decisions (risk/risk_gate.py)
- Fundamental Multi-Family Coverage Matrix (analytics/fundamental_coverage.py)
- Release Gate Verifier & Paper-Only Route Scan (core/release_verifier.py)
- 12-Stage Pipeline Orchestrator (core/orchestrator.py)
"""

from datetime import date, datetime
from pathlib import Path
import pytest
import pandas as pd

from core.alerts import AlertManager
from core.governance import GovernanceStatus, PermittedUse, SourceRegistry
from core.orchestrator import PipelineOrchestrator
from core.release_verifier import ReleaseGateVerifier
from core.system_spec import (
    AlertPriority,
    AlertStatus,
    DecisionStatus,
    FundamentalCoverageStatus,
    FundamentalMetricFamily,
    LiveTradingBoundaryPolicy,
    LiveTradingBoundaryViolation,
    PipelineRunState,
    PipelineStage,
    QualityState,
    ReleaseGate,
)
from analytics.fundamental_coverage import FundamentalCoverageEngine
from risk.risk_gate import IndependentRiskGate


# =============================================================================
# 1. Canonical Contracts & Live Trading Boundary
# =============================================================================

def test_canonical_decision_statuses():
    """Verify all 6 canonical decision statuses mandated by Section 8 exist."""
    assert DecisionStatus.FOCUS.value == "FOCUS"
    assert DecisionStatus.PAPER_PLAN_APPROVED.value == "PAPER PLAN APPROVED"
    assert DecisionStatus.DEFER.value == "DEFER"
    assert DecisionStatus.EXCLUDED.value == "EXCLUDED"
    assert DecisionStatus.NO_TRADE.value == "NO TRADE"
    assert DecisionStatus.INSUFFICIENT_DATA.value == "INSUFFICIENT DATA"
    assert len(DecisionStatus) == 6


def test_quality_and_pipeline_states():
    """Verify quality states and pipeline run states."""
    assert QualityState.READY.value == "READY"
    assert QualityState.DEGRADED.value == "DEGRADED"
    assert QualityState.INSUFFICIENT_DATA.value == "INSUFFICIENT DATA"
    assert QualityState.QUARANTINED.value == "QUARANTINED"

    assert PipelineRunState.SUCCEEDED.value == "Succeeded"
    assert PipelineRunState.BLOCKED.value == "Blocked"
    assert len(PipelineStage) == 12  # Stages 0 to 11


def test_live_trading_boundary_prohibition():
    """Verify strict prohibition on live order placement and credentials."""
    # When simulated, passes cleanly
    LiveTradingBoundaryPolicy.prohibit_live_order_routing(
        action_name="PAPER_SIMULATION",
        is_live_broker_connected=False,
    )
    LiveTradingBoundaryPolicy.assert_paper_only("paper trade simulation")

    # When live broker attempt is made, must raise LiveTradingBoundaryViolation
    with pytest.raises(LiveTradingBoundaryViolation) as exc_info:
        LiveTradingBoundaryPolicy.prohibit_live_order_routing(
            action_name="LIVE_ORDER_ROUTING",
            is_live_broker_connected=True,
        )
    assert "PROHIBITED" in str(exc_info.value)


# =============================================================================
# 2. Source Governance Registry (Stage 0)
# =============================================================================

def test_source_governance_registry_and_preflight():
    """Verify Source Registry tracks authorized sources and passes preflight."""
    reg = SourceRegistry()
    sources = reg.list_all_sources()
    assert len(sources) >= 2

    source_ids = [s.source_id for s in sources]
    assert "SRC_NSE_BHAVCOPY" in source_ids
    assert "SRC_YAHOO_FINANCE" in source_ids

    # Check permitted uses
    assert reg.is_source_permitted("SRC_NSE_BHAVCOPY", PermittedUse.ACQUISITION)
    assert reg.is_source_permitted("SRC_NSE_BHAVCOPY", PermittedUse.PAPER_SIMULATION)
    assert reg.is_permitted("SRC_YAHOO_FINANCE", PermittedUse.CANONICAL_NORMALISATION)

    # Run Stage 0 preflight check
    preflight = reg.execute_preflight_check()
    assert preflight.passed is True
    assert preflight.quality_state == QualityState.READY
    assert len(preflight.checked_sources) >= 2


# =============================================================================
# 3. P0-P3 Priority Alerts Framework
# =============================================================================

def test_alerts_manager_dispatch_and_deduplication(tmp_path):
    """Verify alert priority dispatch, deduplication, and resolution."""
    alerts_file = tmp_path / "test_alerts.json"
    mgr = AlertManager(persistence_path=alerts_file)

    # 1. Emit P0 Critical Alert
    a0 = mgr.emit_alert(
        priority=AlertPriority.P0_CRITICAL,
        category="SECURITY",
        title="Unauthorized Broker Endpoint Access Attempt",
        description="Blocked live route attempt.",
        source_component="BoundaryChecker",
    )
    assert a0.alert_id.startswith("ALT-")
    assert a0.status == AlertStatus.ACTIVE
    assert a0.priority == AlertPriority.P0_CRITICAL

    # 2. Emit duplicate within 24h -> returns same alert object (deduplicated)
    a0_dup = mgr.emit_alert(
        priority=AlertPriority.P0_CRITICAL,
        category="SECURITY",
        title="Unauthorized Broker Endpoint Access Attempt",
        description="Duplicate event.",
        source_component="BoundaryChecker",
    )
    assert a0_dup.alert_id == a0.alert_id

    # 3. Emit P1 High and P3 Informational alerts
    a1 = mgr.emit_alert(
        priority=AlertPriority.P1_HIGH,
        category="DATA_QUALITY",
        title="Stale Data Feed Warning",
        description="Feed lag detected.",
        source_component="DataIngest",
    )
    a3 = mgr.emit_alert(
        priority=AlertPriority.P3_INFORMATIONAL,
        category="OPERATIONS",
        title="Daily Scan Completed",
        description="500 symbols scanned.",
        source_component="Scanner",
    )

    # 4. Filter active alerts
    active = mgr.get_active_alerts()
    assert len(active) == 3

    p0_active = mgr.get_active_alerts(min_priority=AlertPriority.P0_CRITICAL)
    assert len(p0_active) == 1
    assert p0_active[0].priority == AlertPriority.P0_CRITICAL

    # 5. Acknowledge and Resolve
    assert mgr.acknowledge_alert(a0.alert_id, acknowledged_by="RiskOfficer") is True
    assert mgr.resolve_alert(a1.alert_id, resolution_notes="Feed caught up.") is True

    # 6. Verify persistence
    mgr2 = AlertManager(persistence_path=alerts_file)
    all_reloaded = mgr2.get_all_alerts()
    assert len(all_reloaded) == 3


# =============================================================================
# 4. Independent Risk Gate (Section 8)
# =============================================================================

def test_risk_gate_evaluation_dimensions():
    """Verify independent risk gate checks across 7 dimensions and emits canonical statuses."""
    gate = IndependentRiskGate(capital=1_000_000.0, risk_per_trade_pct=1.0)
    today = date(2026, 10, 16)

    # Case A: Quarantined Data -> INSUFFICIENT DATA
    d_quar = gate.evaluate_candidate(
        symbol="STALE_STOCK",
        trading_date=today,
        current_price=100.0,
        entry_price=100.0,
        stop_loss=90.0,
        target_price=130.0,
        quality_state=QualityState.QUARANTINED,
    )
    assert d_quar.decision_status == DecisionStatus.INSUFFICIENT_DATA
    assert d_quar.is_paper_approved is False

    # Case B: Penny Stock / Low Volume -> EXCLUDED
    d_penny = gate.evaluate_candidate(
        symbol="PENNY_STOCK",
        trading_date=today,
        current_price=2.50,
        entry_price=2.50,
        stop_loss=2.00,
        target_price=3.50,
        daily_volume=5000,
    )
    assert d_penny.decision_status == DecisionStatus.EXCLUDED
    assert d_penny.is_paper_approved is False

    # Case C: Unfavorable R:R (< 1.8) -> NO TRADE
    d_bad_rr = gate.evaluate_candidate(
        symbol="BAD_RR",
        trading_date=today,
        current_price=100.0,
        entry_price=100.0,
        stop_loss=95.0,  # risk = 5.0
        target_price=105.0,  # reward = 5.0 -> R:R = 1.0 < 1.8
        daily_volume=100000,
    )
    assert d_bad_rr.decision_status == DecisionStatus.NO_TRADE
    assert d_bad_rr.reward_to_risk < 1.8

    # Case D: High Model Uncertainty (> 85%) -> DEFER
    d_uncert = gate.evaluate_candidate(
        symbol="UNCERTAIN_STOCK",
        trading_date=today,
        current_price=500.0,
        entry_price=500.0,
        stop_loss=480.0,
        target_price=560.0,
        daily_volume=100000,
        model_uncertainty_score=92.0,  # exceeds 85.0
    )
    assert d_uncert.decision_status == DecisionStatus.DEFER

    # Case E: Pending Pullback (not at zone) -> DEFER
    d_pullback = gate.evaluate_candidate(
        symbol="PULLBACK_STOCK",
        trading_date=today,
        current_price=550.0,
        entry_price=500.0,
        stop_loss=480.0,
        target_price=560.0,
        daily_volume=100000,
        is_at_or_approaching_zone=False,
    )
    assert d_pullback.decision_status == DecisionStatus.DEFER

    # Case F: Portfolio Full (20/20 positions) -> FOCUS
    d_focus = gate.evaluate_candidate(
        symbol="FOCUS_STOCK",
        trading_date=today,
        current_price=500.0,
        entry_price=500.0,
        stop_loss=480.0,
        target_price=560.0,
        daily_volume=100000,
        current_open_positions=20,
    )
    assert d_focus.decision_status == DecisionStatus.FOCUS

    # Case G: Valid Setup Passing All Checks -> PAPER PLAN APPROVED
    d_approved = gate.evaluate_candidate(
        symbol="RELIANCE",
        trading_date=today,
        current_price=2500.0,
        entry_price=2500.0,
        stop_loss=2450.0,  # risk per share = 50.0
        target_price=2650.0,  # reward = 150.0 -> R:R = 3.0
        daily_volume=150000,
        history_bars_count=200,
        model_uncertainty_score=28.0,
        current_open_positions=2,
        current_sector_exposure_pct=5.0,
    )
    assert d_approved.decision_status == DecisionStatus.PAPER_PLAN_APPROVED
    assert d_approved.is_paper_approved is True
    # Capital: 1,000,000, Max stock exp: 10% = 100,000 max value; 100,000 // 2500 = 40 shares
    assert d_approved.approved_shares == 40
    assert d_approved.position_value == 100000.0
    assert d_approved.risk_amount == 2000.0
    assert d_approved.policy_version == "v3.1-ConsolidatedRiskPolicy"


# =============================================================================
# 5. Fundamental Multi-Family Coverage Matrix (Section 6 & 13)
# =============================================================================

def test_fundamental_coverage_matrix():
    """Verify evaluation of 7 metric families and explicit missingness reporting."""
    engine = FundamentalCoverageEngine()

    # 1. Known stock (e.g. RELIANCE)
    rel_cov = engine.evaluate_symbol_coverage("RELIANCE")
    assert rel_cov.symbol == "RELIANCE"
    assert rel_cov.available_families_count == 7
    assert rel_cov.missing_families_count == 0
    assert rel_cov.overall_coverage_pct == 100.0
    assert rel_cov.is_sufficient_for_decision is True

    # 2. Check metric families
    families_present = {m.family for m in rel_cov.metrics}
    assert FundamentalMetricFamily.VALUATION in families_present
    assert FundamentalMetricFamily.GROWTH in families_present
    assert FundamentalMetricFamily.PROFITABILITY in families_present
    assert FundamentalMetricFamily.BALANCE_SHEET in families_present
    assert FundamentalMetricFamily.CASH_FLOW in families_present
    assert FundamentalMetricFamily.OWNERSHIP in families_present
    assert FundamentalMetricFamily.EVENTS_SECTOR in families_present

    # 3. Stock without fundamentals -> NO SILENT IMPUTATION (Explicitly MISSING)
    unknown_cov = engine.evaluate_symbol_coverage("UNKNOWN_CORP")
    assert unknown_cov.symbol == "UNKNOWN_CORP"
    assert unknown_cov.overall_coverage_pct < 50.0
    assert unknown_cov.is_sufficient_for_decision is False

    # Metrics must be explicitly marked MISSING
    for m in unknown_cov.metrics:
        assert m.coverage_status == FundamentalCoverageStatus.MISSING
        assert m.value is None

    # 4. Universe Coverage
    mock_df = pd.DataFrame({
        "symbol": ["RELIANCE", "TCS", "INFY", "UNKNOWN_CORP"],
        "close": [2500.0, 3500.0, 1600.0, 50.0],
    })
    summary = engine.evaluate_universe_coverage(mock_df)
    assert summary["total_symbols"] == 4
    assert summary["sufficient_coverage_count"] >= 3
    assert len(summary["family_breakdown"]) == 7


# =============================================================================
# 6. Release Gate Verifier & Paper-Only Assurance (Section 14 & 15)
# =============================================================================

def test_release_gates_verifier():
    """Verify RG-0 to RG-9 automated audit and paper-only route scanning."""
    verifier = ReleaseGateVerifier()
    report = verifier.audit_all_gates()

    # All 10 release gates must pass
    assert report.total_gates_audited == 10
    assert report.passed_gates_count == 10
    assert report.failed_gates_count == 0
    assert report.overall_status == "ALL_GATES_PASSED"

    # Paper-only boundary certification must confirm 0 live endpoints
    assert report.paper_only_boundary_certified is True
    assert "ZERO LIVE EXECUTION ROUTES" in report.live_trading_boundary_notes


# =============================================================================
# 7. 12-Stage Pipeline Orchestrator (Section 10 & 11)
# =============================================================================

def test_12_stage_pipeline_orchestrator(tmp_path):
    """Verify 12-stage pipeline execution from Stage 0 to Stage 11."""
    # Create small synthetic test CSV
    synth_csv = tmp_path / "test_synth_market.csv"
    rows = []
    for sym in ["RELIANCE", "TCS", "NIFTY 50", "BANK NIFTY"]:
        for d_int in range(1, 35):
            d_str = f"2026-09-{d_int:02d}" if d_int <= 30 else f"2026-10-{d_int-30:02d}"
            base = 2500.0 if sym == "RELIANCE" else (3500.0 if sym == "TCS" else 24000.0)
            rows.append({
                "trading_date": d_str,
                "symbol": sym,
                "open": base,
                "high": base + 20.0,
                "low": base - 10.0,
                "close": base + 10.0,
                "volume": 200000,
            })
    pd.DataFrame(rows).to_csv(synth_csv, index=False)

    orchestrator = PipelineOrchestrator(
        runs_dir=tmp_path / "runs",
        ledger_path=tmp_path / "paper_ledger.json",
    )
    manifest = orchestrator.run_pipeline(csv_path=synth_csv, top_n=5)

    assert manifest.run_state == PipelineRunState.SUCCEEDED
    assert manifest.total_symbols_scanned >= 2
    assert len(manifest.stages) == 12  # All 12 stages recorded
    assert (tmp_path / "runs" / f"{manifest.run_id}.json").exists()
