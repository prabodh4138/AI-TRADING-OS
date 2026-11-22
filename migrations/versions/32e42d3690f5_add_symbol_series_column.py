"""add symbol series column

Revision ID: 32e42d3690f5
Revises: 1a9e7d8c5f20
Create Date: 2026-09-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "32e42d3690f5"
down_revision: Union[str, Sequence[str], None] = "1a9e7d8c5f20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add NSE Symbol Master series column."""

    op.add_column(
        "symbol",
        sa.Column(
            "series",
            sa.String(length=10),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove NSE Symbol Master series column."""

    op.drop_column(
        "symbol",
        "series",
    )
