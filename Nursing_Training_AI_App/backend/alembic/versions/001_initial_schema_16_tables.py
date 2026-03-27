"""Initial schema - 16 tables

Revision ID: 001
Revises:
Create Date: 2026-03-27 19:32:56.751239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Users (core) ---
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('nhs_band', sa.String(20), nullable=True),
        sa.Column('specialization', sa.String(100), nullable=True),
        sa.Column('years_experience', sa.Integer(), server_default='0'),
        sa.Column('subscription_tier', sa.String(20), server_default='demo'),
        sa.Column('subscription_expires_at', sa.DateTime(), nullable=True),
        sa.Column('demo_questions_used', sa.Integer(), server_default='0'),
        sa.Column('demo_questions_limit', sa.Integer(), server_default='3'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('role', sa.String(20), server_default='student'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('preferred_language', sa.String(10), server_default='en'),
        sa.Column('timezone', sa.String(50), server_default='UTC'),
    )

    op.create_table('user_progress',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('current_band', sa.String(20), nullable=False),
        sa.Column('band_progress_percentage', sa.Integer(), server_default='0'),
        sa.Column('total_questions_answered', sa.Integer(), server_default='0'),
        sa.Column('correct_answers', sa.Integer(), server_default='0'),
        sa.Column('total_study_time_minutes', sa.Integer(), server_default='0'),
        sa.Column('clinical_skills_score', sa.Integer(), server_default='0'),
        sa.Column('management_skills_score', sa.Integer(), server_default='0'),
        sa.Column('communication_skills_score', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('session_token', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('last_activity', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- Training ---
    op.create_table('questions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(30), nullable=False),
        sa.Column('difficulty_level', sa.String(20), nullable=False),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('correct_answer', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('nhs_band', sa.String(20), nullable=False),
        sa.Column('specialization', sa.String(100), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('calculation_formula', sa.Text(), nullable=True),
        sa.Column('calculation_units', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_demo', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('user_answers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('question_id', sa.Integer(), sa.ForeignKey('questions.id'), nullable=False),
        sa.Column('user_answer', sa.Text(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('confidence_level', sa.Integer(), nullable=True),
        sa.Column('time_taken_seconds', sa.Integer(), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('improvement_suggestions', sa.Text(), nullable=True),
        sa.Column('answered_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('training_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('session_name', sa.String(200), nullable=True),
        sa.Column('nhs_band', sa.String(20), nullable=False),
        sa.Column('specialization', sa.String(100), nullable=True),
        sa.Column('question_count', sa.Integer(), server_default='10'),
        sa.Column('total_questions', sa.Integer(), server_default='0'),
        sa.Column('correct_answers', sa.Integer(), server_default='0'),
        sa.Column('score_percentage', sa.Float(), server_default='0.0'),
        sa.Column('duration_minutes', sa.Integer(), server_default='0'),
        sa.Column('started_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), server_default='false'),
        sa.Column('is_demo', sa.Boolean(), server_default='false'),
    )

    op.create_table('learning_paths',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('nhs_band', sa.String(20), nullable=False),
        sa.Column('specialization', sa.String(100), nullable=True),
        sa.Column('modules', sa.JSON(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.Column('estimated_hours', sa.Integer(), server_default='0'),
        sa.Column('difficulty_level', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_demo', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('user_learning_paths',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('learning_path_id', sa.Integer(), sa.ForeignKey('learning_paths.id'), nullable=False),
        sa.Column('current_module', sa.Integer(), server_default='0'),
        sa.Column('completed_modules', sa.JSON(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), server_default='0.0'),
        sa.Column('started_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), server_default='false'),
        sa.Column('is_paused', sa.Boolean(), server_default='false'),
    )

    # --- Nursing / Interview ---
    op.create_table('specialities',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('bands',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('band_number', sa.Integer(), nullable=False, unique=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('focus_areas', sa.JSON(), nullable=True),
        sa.Column('management_level', sa.String(50), nullable=True),
        sa.Column('min_experience_years', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('question_categories',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('applies_from_band', sa.Integer(), server_default='5'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('interview_questions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('model_answer', sa.Text(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('speciality_id', sa.Integer(), sa.ForeignKey('specialities.id'), nullable=True),
        sa.Column('band_id', sa.Integer(), sa.ForeignKey('bands.id'), nullable=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('question_categories.id'), nullable=True),
        sa.Column('difficulty', sa.String(20), server_default='medium'),
        sa.Column('max_score', sa.Integer(), server_default='10'),
        sa.Column('is_intro', sa.Boolean(), server_default='false'),
        sa.Column('is_generic', sa.Boolean(), server_default='false'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('trusts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(200), nullable=False, unique=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('region', sa.String(100), nullable=True),
        sa.Column('values', sa.JSON(), nullable=True),
        sa.Column('custom_questions_enabled', sa.Boolean(), server_default='false'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('trust_questions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('trust_id', sa.Integer(), sa.ForeignKey('trusts.id'), nullable=False),
        sa.Column('question_id', sa.Integer(), sa.ForeignKey('interview_questions.id'), nullable=False),
        sa.Column('custom_text', sa.Text(), nullable=True),
        sa.Column('custom_model_answer', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), server_default='0'),
        sa.Column('is_additional', sa.Boolean(), server_default='false'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('interview_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(100), nullable=False, index=True),
        sa.Column('speciality_id', sa.Integer(), sa.ForeignKey('specialities.id'), nullable=True),
        sa.Column('band_id', sa.Integer(), sa.ForeignKey('bands.id'), nullable=True),
        sa.Column('trust_id', sa.Integer(), sa.ForeignKey('trusts.id'), nullable=True),
        sa.Column('mode', sa.String(30), server_default='practice'),
        sa.Column('total_questions', sa.Integer(), server_default='0'),
        sa.Column('status', sa.String(20), server_default='in_progress'),
        sa.Column('total_score', sa.Float(), server_default='0'),
        sa.Column('max_possible_score', sa.Float(), server_default='0'),
        sa.Column('score_percentage', sa.Float(), server_default='0'),
        sa.Column('passed', sa.Boolean(), nullable=True),
        sa.Column('pass_threshold', sa.Float(), server_default='70.0'),
        sa.Column('overall_feedback', sa.Text(), nullable=True),
        sa.Column('strengths_summary', sa.JSON(), nullable=True),
        sa.Column('weaknesses_summary', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    op.create_table('interview_answers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', sa.Integer(), sa.ForeignKey('interview_questions.id'), nullable=False),
        sa.Column('question_order', sa.Integer(), nullable=False),
        sa.Column('user_answer', sa.Text(), nullable=True),
        sa.Column('audio_url', sa.String(500), nullable=True),
        sa.Column('score', sa.Float(), server_default='0'),
        sa.Column('max_score', sa.Float(), server_default='10'),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('weaknesses', sa.JSON(), nullable=True),
        sa.Column('keywords_matched', sa.JSON(), nullable=True),
        sa.Column('keywords_missed', sa.JSON(), nullable=True),
        sa.Column('follow_up_question', sa.Text(), nullable=True),
        sa.Column('follow_up_answer', sa.Text(), nullable=True),
        sa.Column('follow_up_score', sa.Float(), nullable=True),
        sa.Column('answered_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('time_taken_seconds', sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('interview_answers')
    op.drop_table('interview_sessions')
    op.drop_table('trust_questions')
    op.drop_table('trusts')
    op.drop_table('interview_questions')
    op.drop_table('question_categories')
    op.drop_table('bands')
    op.drop_table('specialities')
    op.drop_table('user_learning_paths')
    op.drop_table('learning_paths')
    op.drop_table('training_sessions')
    op.drop_table('user_answers')
    op.drop_table('questions')
    op.drop_table('user_sessions')
    op.drop_table('user_progress')
    op.drop_table('users')
