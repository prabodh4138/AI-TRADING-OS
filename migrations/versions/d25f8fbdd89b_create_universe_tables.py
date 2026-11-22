"""create universe tables

Revision ID: d25f8fbdd89b
Revises: 32e42d3690f5
Create Date: 2026-09-28 21:05:27.510512
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision: str = "d25f8fbdd89b"
down_revision: Union[str, Sequence[str], None] = "32e42d3690f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "universe",
        sa.Column("universe_id", sa.UUID(), nullable=False),
        sa.Column("universe_code", sa.String(length=50), nullable=False),
        sa.Column("universe_name", sa.String(length=150), nullable=False),
        sa.Column(
            "universe_type",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column("provider", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("universe_id"),
    )

    op.create_index(
        op.f("ix_universe_universe_code"),
        "universe",
        ["universe_code"],
        unique=True,
    )

    op.create_index(
        op.f("ix_universe_universe_type"),
        "universe",
        ["universe_type"],
        unique=False,
    )

    op.create_table(
        "universe_constituent",
        sa.Column(
            "universe_constituent_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column("universe_id", sa.UUID(), nullable=False),
        sa.Column("symbol_id", sa.UUID(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["symbol_id"],
            ["symbol.symbol_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["universe_id"],
            ["universe.universe_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("universe_constituent_id"),
        sa.UniqueConstraint(
            "universe_id",
            "symbol_id",
            "effective_from",
            name="uq_universe_constituent_period",
        ),
    )

    op.create_index(
        "ix_universe_constituent_symbol_date",
        "universe_constituent",
        ["symbol_id", "effective_from", "effective_to"],
        unique=False,
    )

    op.create_index(
        op.f("ix_universe_constituent_symbol_id"),
        "universe_constituent",
        ["symbol_id"],
        unique=False,
    )

    op.create_index(
        "ix_universe_constituent_universe_date",
        "universe_constituent",
        ["universe_id", "effective_from", "effective_to"],
        unique=False,
    )

    op.create_index(
        op.f("ix_universe_constituent_universe_id"),
        "universe_constituent",
        ["universe_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_universe_constituent_universe_id"),
        table_name="universe_constituent",
    )

    op.drop_index(
        "ix_universe_constituent_universe_date",
        table_name="universe_constituent",
    )

    op.drop_index(
        op.f("ix_universe_constituent_symbol_id"),
        table_name="universe_constituent",
    )

    op.drop_index(
        "ix_universe_constituent_symbol_date",
        table_name="universe_constituent",
    )

    op.drop_table("universe_constituent")

    op.drop_index(
        op.f("ix_universe_universe_type"),
        table_name="universe",
    )

    op.drop_index(
        op.f("ix_universe_universe_code"),
        table_name="universe",
    )

    op.drop_table("universe")
