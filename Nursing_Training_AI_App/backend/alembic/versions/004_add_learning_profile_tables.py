"""Add user_learning_profiles and learning_events tables

Revision ID: 004
Revises: 003
Create Date: 2026-03-30 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_learning_profiles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('baseline_accuracy_pct', sa.Float(), nullable=True),
        sa.Column('baseline_established_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('baseline_questions', sa.Integer(), server_default='0'),
        sa.Column('current_accuracy_pct', sa.Float(), server_default='0'),
        sa.Column('total_questions_answered', sa.Integer(), server_default='0'),
        sa.Column('total_correct', sa.Integer(), server_default='0'),
        sa.Column('strongest_specialty', sa.String(100), nullable=True),
        sa.Column('weakest_specialty', sa.String(100), nullable=True),
        sa.Column('strongest_competency', sa.String(100), nullable=True),
        sa.Column('weakest_competency', sa.String(100), nullable=True),
        sa.Column('specialty_scores', JSON, nullable=True),
        sa.Column('competency_scores', JSON, nullable=True),
        sa.Column('trend', sa.String(20), server_default='stable'),
        sa.Column('learning_velocity', sa.Float(), server_default='0'),
        sa.Column('last_recommendation_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recommendations', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_ulp_user_id', 'user_learning_profiles', ['user_id'])

    op.create_table(
        'learning_events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('time_taken_seconds', sa.Integer(), nullable=True),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_le_user_id', 'learning_events', ['user_id'])
    op.create_index('ix_le_event_type', 'learning_events', ['event_type'])
    op.create_index('ix_le_created_at', 'learning_events', ['created_at'])
    op.create_index('ix_le_user_type', 'learning_events', ['user_id', 'event_type'])
    op.create_index('ix_le_user_date', 'learning_events', ['user_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('learning_events')
    op.drop_table('user_learning_profiles')
