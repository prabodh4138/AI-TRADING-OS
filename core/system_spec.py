"""
AI Trading Operating System (AI-TOS)
Module: core/system_spec.py
Specification Baseline: Master Final Consolidated System Specification v3.1 (16 October 2026)

Defines system-wide canonical enums, contracts, decision statuses, quality states,
pipeline stages, alert models, and release gates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# 1. Critical Boundary & Paper-Only Guarantee (Section 1, 9, 14)
# =============================================================================
class LiveTradingBoundaryViolation(Exception):
    """Raised if any component attempts live broker routing or real-money order placement."""
    pass


class LiveTradingBoundaryPolicy:
    """Enforces absolute separation: Research, Analytics & Simulated Paper Trading ONLY."""
    IS_LIVE_TRADING_PERMITTED: bool = False
    ALLOW_BROKER_ORDER_ROUTING: bool = False
    EXECUTION_MODE: str = "SIMULATED_PAPER_TRADING_ONLY"

    @classmethod
    def assert_paper_only(cls, action_description: str = "trade action") -> None:
        if cls.IS_LIVE_TRADING_PERMITTED or cls.ALLOW_BROKER_ORDER_ROUTING:
            raise LiveTradingBoundaryViolation(
                f"FATAL: Live order execution forbidden by System Specification v3.1. "
                f"Action '{action_description}' blocked."
            )

    @classmethod
    def prohibit_live_order_routing(cls, action_name: str, is_live_broker_connected: bool) -> None:
        if is_live_broker_connected:
            raise LiveTradingBoundaryViolation(
                f"PROHIBITED: Live order routing '{action_name}' is forbidden by Master Specification v3.1."
            )


# =============================================================================
# 2. Canonical Decision Statuses (Section 8)
# =============================================================================
class DecisionStatus(str, Enum):
    """
    Independent Risk Gate & Research Candidate Decision Statuses:
    - FOCUS: Eligible research candidate; not a trade instruction.
    - PAPER_PLAN_APPROVED: Passed configured research/risk gates for simulation only.
    - DEFER: Needs review or a specified condition before reconsideration.
    - EXCLUDED: Fails an eligibility or policy rule; reason recorded.
    - NO_TRADE: No acceptable setup or risk/reward under current conditions.
    - INSUFFICIENT_DATA: Required data, permissions, freshness or confidence is inadequate.
    """
    FOCUS = "FOCUS"
    PAPER_PLAN_APPROVED = "PAPER PLAN APPROVED"
    DEFER = "DEFER"
    EXCLUDED = "EXCLUDED"
    NO_TRADE = "NO TRADE"
    INSUFFICIENT_DATA = "INSUFFICIENT DATA"


# =============================================================================
# 3. Canonical Data Quality States (Section 4 & 5)
# =============================================================================
class QualityState(str, Enum):
    """
    Canonical Data Quality States:
    - READY: Data passed all freshness, completeness, duplicate and OHLC logic checks.
    - DEGRADED: Partial coverage or non-critical tolerance divergence; usable with caution.
    - INSUFFICIENT_DATA: Missing mandatory fields, history or warmup required for decision.
    - QUARANTINED: Cross-source conflict, wick/logic violation or stale-beyond-tolerance.
    """
    READY = "READY"
    DEGRADED = "DEGRADED"
    INSUFFICIENT_DATA = "INSUFFICIENT DATA"
    QUARANTINED = "QUARANTINED"


# =============================================================================
# 4. Pipeline Run States & 12 Workflow Stages (Section 3 & 10)
# =============================================================================
class PipelineRunState(str, Enum):
    CREATED = "Created"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    SUCCEEDED_WITH_WARNINGS = "Succeeded with warnings"
    FAILED = "Failed"
    BLOCKED = "Blocked"
    CANCELLED = "Cancelled"
    RECOVERY_REQUIRED = "Recovery required"


class PipelineStage(str, Enum):
    STAGE_0_PREFLIGHT = "0. Governance preflight"
    STAGE_1_RUN_CREATION = "1. Run creation"
    STAGE_2_ACQUISITION = "2. Source acquisition"
    STAGE_3_RAW_ARCHIVE = "3. Raw evidence archive"
    STAGE_4_CANONICALISATION = "4. Canonicalisation"
    STAGE_5_QUALITY_RECONCILIATION = "5. Quality and reconciliation"
    STAGE_6_FEATURE_BUILD = "6. Feature build"
    STAGE_7_SCANNER_RANKER = "7. Scanner and ranker"
    STAGE_8_RISK_GATE = "8. Independent risk gate"
    STAGE_9_PAPER_SIMULATION = "9. Paper simulation"
    STAGE_10_EVALUATION_ALERTS = "10. Evaluation and alerts"
    STAGE_11_DASHBOARD_PUBLICATION = "11. Dashboard publication"


# =============================================================================
# 5. Alert Priority Model (Section 13)
# =============================================================================
class AlertPriority(str, Enum):
    P0_CRITICAL = "P0 Critical"       # Security/source permission compromise, paper-only breach, severe integrity incident
    P1_HIGH = "P1 High"               # Material source failure, risk-policy issue, repeated run failures, significant drift
    P2_MEDIUM = "P2 Medium"           # Degraded coverage, persistent reconciliation conflict, delayed process
    P3_INFORMATIONAL = "P3 Informational" # Daily digest, completed run, non-critical status, research notification


class AlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


@dataclass
class SystemAlert:
    alert_id: str
    priority: AlertPriority
    category: str
    title: str
    description: str
    source_component: str
    created_at: datetime = field(default_factory=datetime.now)
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "priority": self.priority.value,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "source_component": self.source_component,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolution_notes": self.resolution_notes,
        }


# =============================================================================
# 6. Fundamental Metric Families (Section 6)
# =============================================================================
class FundamentalMetricFamily(str, Enum):
    VALUATION = "Valuation"             # P/E, P/B, EV/EBITDA, Dividend Yield
    GROWTH = "Growth"                   # Revenue, earnings, EPS, cash-flow growth
    PROFITABILITY = "Profitability"     # Margins, ROE, ROA, ROCE
    BALANCE_SHEET = "Balance Sheet"     # Debt, interest coverage, liquidity, working capital
    CASH_FLOW = "Cash Flow / Quality"   # Operating CF vs earnings, Free Cash Flow, Accrual quality
    OWNERSHIP = "Ownership / Governance"# Promoter/institutional holding, pledging
    EVENTS_SECTOR = "Events / Sector"   # Results dates, corporate actions


class FundamentalCoverageStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    STALE = "STALE"
    MISSING = "MISSING"
    CONFLICTED = "CONFLICTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


# =============================================================================
# 7. Release Gates (Section 15)
# =============================================================================
class ReleaseGate(str, Enum):
    RG_0_SCOPE = "RG-0 Scope"
    RG_1_PERMISSIONS = "RG-1 Permissions"
    RG_2_ARCHITECTURE = "RG-2 Architecture"
    RG_3_DATA_CONTRACTS = "RG-3 Data contracts"
    RG_4_SECURITY = "RG-4 Security"
    RG_5_PIPELINE = "RG-5 Pipeline"
    RG_6_ANALYTICS = "RG-6 Analytics"
    RG_7_RISK_PAPER = "RG-7 Risk/paper"
    RG_8_DASHBOARD = "RG-8 Dashboard"
    RG_9_RELEASE = "RG-9 Release"


@dataclass
class ReleaseGateAuditResult:
    gate: ReleaseGate
    passed: bool
    review_date: date
    evidence_description: str
    reviewer: str = "System Automated Verifier"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate": self.gate.value,
            "passed": self.passed,
            "review_date": str(self.review_date),
            "evidence_description": self.evidence_description,
            "reviewer": self.reviewer,
            "notes": self.notes,
        }
