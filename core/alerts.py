"""
AI Trading Operating System (AI-TOS)
Module: core/alerts.py
Specification Baseline: Master Final Consolidated System Specification v3.1 (Section 13)

Alerts & Exceptions Framework:
- P0 Critical: Security/permission compromise, paper boundary breach, severe data integrity incident.
- P1 High: Material source failure, risk-policy issue, repeated run failures, significant model drift.
- P2 Medium: Degraded coverage, persistent reconciliation conflict, delayed recoverable process.
- P3 Informational: Daily digest, completed run, routine research notifications.
- Manages deduplication, acknowledgement, and persistent audit history.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from core.system_spec import AlertPriority, AlertStatus, SystemAlert


class AlertManager:
    """
    Central alert dispatch, deduplication, and persistence manager.
    """

    def __init__(self, persistence_path: Optional[str | Path] = None) -> None:
        self.persistence_path = Path(persistence_path or "data/system_alerts.json")
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        self.alerts: List[SystemAlert] = []
        self._load_alerts()

    def _load_alerts(self) -> None:
        if self.persistence_path.exists():
            try:
                data = json.loads(self.persistence_path.read_text(encoding="utf-8"))
                for d in data:
                    self.alerts.append(
                        SystemAlert(
                            alert_id=d["alert_id"],
                            priority=AlertPriority(d["priority"]),
                            category=d["category"],
                            title=d["title"],
                            description=d["description"],
                            source_component=d["source_component"],
                            created_at=datetime.fromisoformat(d["created_at"]),
                            status=AlertStatus(d["status"]),
                            acknowledged_by=d.get("acknowledged_by"),
                            acknowledged_at=datetime.fromisoformat(d["acknowledged_at"]) if d.get("acknowledged_at") else None,
                            resolution_notes=d.get("resolution_notes"),
                        )
                    )
            except Exception:
                self.alerts = []

    def _save_alerts(self) -> None:
        try:
            raw = [a.to_dict() for a in self.alerts]
            self.persistence_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        except Exception:
            pass

    def emit_alert(
        self,
        priority: AlertPriority,
        category: str,
        title: str,
        description: str,
        source_component: str,
    ) -> SystemAlert:
        """Emits an alert with automated deduplication against active alerts."""
        # Deduplication check: if active alert exists with same category & title in last 24h, skip duplicate
        for a in self.alerts:
            if (
                a.status == AlertStatus.ACTIVE
                and a.category == category
                and a.title == title
                and (datetime.now() - a.created_at).total_seconds() < 86400
            ):
                return a

        alert = SystemAlert(
            alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
            priority=priority,
            category=category,
            title=title,
            description=description,
            source_component=source_component,
            created_at=datetime.now(),
            status=AlertStatus.ACTIVE,
        )
        self.alerts.append(alert)
        self._save_alerts()
        return alert

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "Operator") -> bool:
        for a in self.alerts:
            if a.alert_id == alert_id and a.status == AlertStatus.ACTIVE:
                a.status = AlertStatus.ACKNOWLEDGED
                a.acknowledged_by = acknowledged_by
                a.acknowledged_at = datetime.now()
                self._save_alerts()
                return True
        return False

    def resolve_alert(self, alert_id: str, resolution_notes: str = "Resolved by system") -> bool:
        for a in self.alerts:
            if a.alert_id == alert_id:
                a.status = AlertStatus.RESOLVED
                a.resolution_notes = resolution_notes
                self._save_alerts()
                return True
        return False

    def get_active_alerts(self, min_priority: Optional[AlertPriority] = None) -> List[SystemAlert]:
        active = [a for a in self.alerts if a.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]]
        if min_priority == AlertPriority.P0_CRITICAL:
            active = [a for a in active if a.priority == AlertPriority.P0_CRITICAL]
        elif min_priority == AlertPriority.P1_HIGH:
            active = [a for a in active if a.priority in [AlertPriority.P0_CRITICAL, AlertPriority.P1_HIGH]]
        return sorted(active, key=lambda a: (a.priority.value, a.created_at), reverse=True)

    def get_all_alerts(self) -> List[SystemAlert]:
        return sorted(self.alerts, key=lambda a: a.created_at, reverse=True)
