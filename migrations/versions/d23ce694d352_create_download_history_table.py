"""create download_history table

Revision ID: d23ce694d352
Revises: e6f8a1dab74a
Create Date: 2026-07-26 16:53:52.783109
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d23ce694d352"
down_revision: Union[str, Sequence[str], None] = "e6f8a1dab74a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "download_history",

        sa.Column(
            "download_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "provider",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "dataset",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "trading_date",
            sa.Date(),
            nullable=False,
        ),

        sa.Column(
            "filename",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "file_path",
            sa.String(length=500),
            nullable=False,
        ),

        sa.Column(
            "file_size",
            sa.BigInteger(),
            nullable=True,
        ),

        sa.Column(
            "checksum",
            sa.String(length=128),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "SUCCESS",
                "FAILED",
                "SKIPPED",
                name="download_status_enum",
            ),
            nullable=False,
        ),

        sa.Column(
            "retry_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),

        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("download_id"),

        sa.UniqueConstraint(
            "provider",
            "dataset",
            "trading_date",
            name="uq_download_history_provider_dataset_date",
        ),
    )

    op.create_index(
        "ix_download_history_provider",
        "download_history",
        ["provider"],
        unique=False,
    )

    op.create_index(
        "ix_download_history_trading_date",
        "download_history",
        ["trading_date"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_download_history_trading_date",
        table_name="download_history",
    )

    op.drop_index(
        "ix_download_history_provider",
        table_name="download_history",
    )

    op.drop_table("download_history")

    op.execute("DROP TYPE IF EXISTS download_status_enum")