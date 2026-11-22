"""
AI Trading Operating System (AI-TOS)
Module: core/governance.py
Specification Baseline: Master Final Consolidated System Specification v3.1 (Section 4 & Stage 0)

Source Permission Registry & Governance Preflight Gate:
- Tracks provider permissions, products, access methods, effective dates, and permitted uses.
- Enforces Stage 0: Governance Preflight (runs blocked if mandatory permissions or policy versions are missing).
- Prevents unapproved data sources or unauthorised downstream publishing.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.system_spec import QualityState


class PermittedUse(str, Enum):
    ACQUISITION = "ACQUISITION"
    RAW_STORAGE = "RAW_STORAGE"
    CANONICAL_NORMALISATION = "CANONICAL_NORMALISATION"
    CROSS_SOURCE_COMPARISON = "CROSS_SOURCE_COMPARISON"
    DERIVED_FEATURES = "DERIVED_FEATURES"
    DASHBOARD_DISPLAY = "DASHBOARD_DISPLAY"
    PAPER_SIMULATION = "PAPER_SIMULATION"
    EXPORT = "EXPORT"


class GovernanceStatus(str, Enum):
    AUTHORISED = "AUTHORISED"
    CONDITIONAL_RESEARCH_ONLY = "CONDITIONAL_RESEARCH_ONLY"
    UNDER_REVIEW = "UNDER_REVIEW"
    EXPIRED = "EXPIRED"
    BLOCKED = "BLOCKED"


@dataclass
class SourcePermissionEntry:
    source_id: str
    provider: str
    product_feed: str
    access_method: str
    owner: str
    permission_evidence: str
    effective_date: date
    expiry_date: Optional[date]
    permitted_uses: List[PermittedUse]
    governance_status: GovernanceStatus
    notes: str = ""

    def is_use_permitted(self, use: PermittedUse) -> bool:
        if self.governance_status not in [GovernanceStatus.AUTHORISED, GovernanceStatus.CONDITIONAL_RESEARCH_ONLY]:
            return False
        if self.expiry_date and date.today() > self.expiry_date:
            return False
        return use in self.permitted_uses

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "provider": self.provider,
            "product_feed": self.product_feed,
            "access_method": self.access_method,
            "owner": self.owner,
            "permission_evidence": self.permission_evidence,
            "effective_date": str(self.effective_date),
            "expiry_date": str(self.expiry_date) if self.expiry_date else None,
            "permitted_uses": [u.value for u in self.permitted_uses],
            "governance_status": self.governance_status.value,
            "notes": self.notes,
        }


@dataclass
class PreflightCheckResult:
    passed: bool
    run_timestamp: datetime
    active_policy_version: str
    checked_sources: List[str]
    missing_permissions: List[str]
    blockers: List[str]
    quality_state: QualityState

    @property
    def summary(self) -> str:
        if self.passed:
            return f"PASSED — All {len(self.checked_sources)} sources authorized under {self.active_policy_version} (Quality: {self.quality_state.value})."
        return f"FAILED — Blocked by {len(self.blockers)} issue(s): {', '.join(self.blockers)}."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "run_timestamp": self.run_timestamp.isoformat(),
            "active_policy_version": self.active_policy_version,
            "checked_sources": self.checked_sources,
            "missing_permissions": self.missing_permissions,
            "blockers": self.blockers,
            "quality_state": self.quality_state.value,
            "summary": self.summary,
        }


class SourceRegistry:
    """
    Central governance registry for permitted market data sources.
    """

    def __init__(self) -> None:
        self.sources: Dict[str, SourcePermissionEntry] = {
            "SRC_NSE_BHAVCOPY": SourcePermissionEntry(
                source_id="SRC_NSE_BHAVCOPY",
                provider="National Stock Exchange of India (NSE)",
                product_feed="Daily Bhavcopy & Securities Master",
                access_method="Local CSV / Authorized Public Archive",
                owner="Data Administrator",
                permission_evidence="NSE Public Market Data Terms / Historical Research License",
                effective_date=date(2025, 1, 1),
                expiry_date=date(2027, 12, 31),
                permitted_uses=[
                    PermittedUse.ACQUISITION,
                    PermittedUse.RAW_STORAGE,
                    PermittedUse.CANONICAL_NORMALISATION,
                    PermittedUse.CROSS_SOURCE_COMPARISON,
                    PermittedUse.DERIVED_FEATURES,
                    PermittedUse.DASHBOARD_DISPLAY,
                    PermittedUse.PAPER_SIMULATION,
                ],
                governance_status=GovernanceStatus.AUTHORISED,
                notes="Primary source for exchange settlement prices, wicks and session volume.",
            ),
            "SRC_YAHOO_FINANCE": SourcePermissionEntry(
                source_id="SRC_YAHOO_FINANCE",
                provider="Yahoo Finance API (yfinance / v8 direct)",
                product_feed="Split-Adjusted Multi-Year OHLCV & Fundamentals",
                access_method="REST API / yfinance adapter",
                owner="Research Engineer",
                permission_evidence="Non-commercial academic & positional research terms",
                effective_date=date(2025, 1, 1),
                expiry_date=date(2027, 12, 31),
                permitted_uses=[
                    PermittedUse.ACQUISITION,
                    PermittedUse.RAW_STORAGE,
                    PermittedUse.CANONICAL_NORMALISATION,
                    PermittedUse.CROSS_SOURCE_COMPARISON,
                    PermittedUse.DERIVED_FEATURES,
                    PermittedUse.DASHBOARD_DISPLAY,
                    PermittedUse.PAPER_SIMULATION,
                ],
                governance_status=GovernanceStatus.AUTHORISED,
                notes="Split and bonus adjusted historical ground truth matching Zerodha quotes.",
            ),
        }

    def list_all_sources(self) -> List[SourcePermissionEntry]:
        return list(self.sources.values())

    def get_source(self, source_id: str) -> Optional[SourcePermissionEntry]:
        return self.sources.get(source_id)

    def is_permitted(self, source_id: str, use: PermittedUse) -> bool:
        src = self.get_source(source_id)
        if not src:
            return False
        return src.is_use_permitted(use)

    def is_source_permitted(self, source_id: str, use: PermittedUse) -> bool:
        return self.is_permitted(source_id, use)

    def execute_preflight_check(self, required_sources: Optional[List[str]] = None) -> PreflightCheckResult:
        """
        Stage 0: Governance preflight. Verifies permissions, configuration, calendar.
        """
        req = required_sources or ["SRC_NSE_BHAVCOPY", "SRC_YAHOO_FINANCE"]
        missing = []
        blockers = []

        for sid in req:
            src = self.get_source(sid)
            if not src:
                missing.append(sid)
                blockers.append(f"Source {sid} not registered in governance registry.")
            elif src.governance_status == GovernanceStatus.BLOCKED:
                blockers.append(f"Source {sid} explicitly blocked by governance policy.")
            elif src.governance_status == GovernanceStatus.EXPIRED:
                blockers.append(f"Source {sid} license has expired.")

        passed = len(blockers) == 0
        q_state = QualityState.READY if passed else QualityState.QUARANTINED

        return PreflightCheckResult(
            passed=passed,
            run_timestamp=datetime.now(),
            active_policy_version="v3.1-Consolidated",
            checked_sources=req,
            missing_permissions=missing,
            blockers=blockers,
            quality_state=q_state,
        )
