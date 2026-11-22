"""
AI Trading Operating System (AI-TOS)
Pipeline Governance & Automated Run Routes.
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter
from backend.schemas import GenericApiResponse
from backend.services.data_service import DataService
from core.orchestrator import PipelineOrchestrator
from core.release_verifier import ReleaseGateVerifier

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline Governance"])


@router.get("/preflight")
def get_preflight_audit():
    """Executes Stage 0 governance preflight check."""
    orchestrator = PipelineOrchestrator()
    preflight = orchestrator.governance.run_preflight_checks()
    return {
        "passed": preflight.passed,
        "active_sources": preflight.active_sources,
        "blocked_sources": preflight.blocked_sources,
        "expired_credentials": preflight.expired_credentials,
        "unresolved_quarantines": preflight.unresolved_quarantines,
        "details": preflight.details,
    }


@router.post("/run", response_model=GenericApiResponse)
def run_pipeline():
    """Triggers end-to-end institutional pipeline execution."""
    ds = DataService.get_instance()
    df = ds.get_dataframe()
    orchestrator = PipelineOrchestrator()
    manifest = orchestrator.execute_pipeline(initial_df=df)

    return GenericApiResponse(
        success=manifest.overall_state.value in {"SUCCEEDED", "SUCCEEDED_WITH_WARNINGS"},
        message=f"Pipeline execution finished with state: {manifest.overall_state.value}",
        data={
            "run_id": manifest.run_id,
            "overall_state": manifest.overall_state.value,
            "start_time": str(manifest.start_time),
            "end_time": str(manifest.end_time),
            "total_duration_seconds": manifest.total_duration_seconds,
            "stages_completed": len(manifest.stages),
        },
    )
