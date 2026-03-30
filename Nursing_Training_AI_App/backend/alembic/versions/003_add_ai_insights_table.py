"""Add ai_insights table for Ollama Brain reports

Revision ID: 003
Revises: 002
Create Date: 2026-03-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ai_insights',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('report_type', sa.String(50), nullable=False, index=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending', index=True),
        sa.Column('model_used', sa.String(100), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('generation_time_seconds', sa.Float(), nullable=True),
        sa.Column('analysis_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('analysis_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('insights', JSON, nullable=True),
        sa.Column('recommendations', JSON, nullable=True),
        sa.Column('raw_response', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table('ai_insights')
