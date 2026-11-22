"""add supertrend persistence columns

Revision ID: 1a9e7d8c5f20
Revises: b066194363c3
"""
from alembic import op
import sqlalchemy as sa

revision='1a9e7d8c5f20'
down_revision='b066194363c3'
branch_labels=None
depends_on=None

def upgrade() -> None:
    op.add_column('indicator_data', sa.Column('supertrend', sa.Numeric(18,4), nullable=True))
    op.add_column('indicator_data', sa.Column('supertrend_direction', sa.Integer(), nullable=True))

def downgrade() -> None:
    op.drop_column('indicator_data','supertrend_direction')
    op.drop_column('indicator_data','supertrend')
