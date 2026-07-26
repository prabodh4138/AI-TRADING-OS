"""
==============================================================
AI Trading Operating System
Enterprise Download History Repository
==============================================================

Repository for download_history table.

Responsibilities
----------------
- Create download history
- Check existing downloads
- Retrieve download history
- Update download status

Author : AI Trading OS
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import desc
from sqlalchemy.orm import Session

from database.models.download_history import DownloadHistory


class DownloadHistoryRepository:
    """
    Repository for DownloadHistory.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    # ==========================================================
    # Create
    # ==========================================================

    def add(
        self,
        history: DownloadHistory,
    ) -> DownloadHistory:
        """
        Insert a new download history record.
        """

        self.session.add(history)

        return history

    # ==========================================================
    # Read
    # ==========================================================

    def get_by_id(
        self,
        history_id,
    ) -> DownloadHistory | None:

        return self.session.get(
            DownloadHistory,
            history_id,
        )

    def get_by_date(
        self,
        provider: str,
        dataset: str,
        trading_date: date,
    ) -> DownloadHistory | None:

        return (
            self.session.query(DownloadHistory)
            .filter(
                DownloadHistory.provider == provider,
                DownloadHistory.dataset == dataset,
                DownloadHistory.trading_date == trading_date,
            )
            .first()
        )

    def exists(
        self,
        provider: str,
        dataset: str,
        trading_date: date,
    ) -> bool:

        return (
            self.get_by_date(
                provider,
                dataset,
                trading_date,
            )
            is not None
        )

    def get_latest(
        self,
        provider: str,
        dataset: str,
    ) -> DownloadHistory | None:

        return (
            self.session.query(DownloadHistory)
            .filter(
                DownloadHistory.provider == provider,
                DownloadHistory.dataset == dataset,
            )
            .order_by(
                desc(DownloadHistory.trading_date)
            )
            .first()
        )

    def list_failed(
        self,
    ) -> list[DownloadHistory]:

        return (
            self.session.query(DownloadHistory)
            .filter(
                DownloadHistory.status == "FAILED"
            )
            .order_by(
                DownloadHistory.trading_date
            )
            .all()
        )

    # ==========================================================
    # Update
    # ==========================================================

    def update_status(
        self,
        history: DownloadHistory,
        status: str,
    ) -> DownloadHistory:

        history.status = status

        return history

    # ==========================================================
    # Delete
    # ==========================================================

    def delete(
        self,
        history: DownloadHistory,
    ) -> None:

        self.session.delete(history)

    # ==========================================================
    # Utility
    # ==========================================================

    def count(self) -> int:

        return (
            self.session.query(DownloadHistory)
            .count()
        )

    def get_all(
        self,
    ) -> list[DownloadHistory]:

        return (
            self.session.query(DownloadHistory)
            .order_by(
                DownloadHistory.trading_date.desc()
            )
            .all()
        )