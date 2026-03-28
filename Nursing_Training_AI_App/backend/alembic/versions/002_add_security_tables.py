"""Add security tables: audit_logs, security_events, token_blacklist

Revision ID: 002
Revises: 001
Create Date: 2026-03-28 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Audit Logs (immutable, blockchain-style hash chain) ---
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('entry_id', sa.String(36), unique=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('action', sa.String(60), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('user_id', sa.String(50), nullable=True),
        sa.Column('organization_id', sa.String(50), nullable=True),
        sa.Column('resource_type', sa.String(100), nullable=True),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('details', JSON(), nullable=True),
        sa.Column('previous_hash', sa.String(64), nullable=False),
        sa.Column('hash', sa.String(64), nullable=False, unique=True),
    )
    op.create_index('ix_audit_logs_entry_id', 'audit_logs', ['entry_id'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_severity', 'audit_logs', ['severity'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_org_id', 'audit_logs', ['organization_id'])
    op.create_index('ix_audit_user_action', 'audit_logs', ['user_id', 'action'])
    op.create_index('ix_audit_org_timestamp', 'audit_logs', ['organization_id', 'timestamp'])
    op.create_index('ix_audit_severity_timestamp', 'audit_logs', ['severity', 'timestamp'])

    # --- Security Events (threat detection) ---
    op.create_table('security_events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_type', sa.String(60), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('source_ip', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('endpoint', sa.String(500), nullable=True),
        sa.Column('details', JSON(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
    )
    op.create_index('ix_security_events_timestamp', 'security_events', ['timestamp'])
    op.create_index('ix_security_events_event_type', 'security_events', ['event_type'])
    op.create_index('ix_security_events_severity', 'security_events', ['severity'])
    op.create_index('ix_security_events_source_ip', 'security_events', ['source_ip'])
    op.create_index('ix_secevt_severity_timestamp', 'security_events', ['severity', 'timestamp'])
    op.create_index('ix_secevt_ip_timestamp', 'security_events', ['source_ip', 'timestamp'])
    op.create_index('ix_secevt_type_timestamp', 'security_events', ['event_type', 'timestamp'])

    # --- Token Blacklist (persistent JWT revocation) ---
    op.create_table('token_blacklist',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('token_hash', sa.String(64), unique=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('blacklisted_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_token_blacklist_hash', 'token_blacklist', ['token_hash'])
    op.create_index('ix_token_blacklist_user_id', 'token_blacklist', ['user_id'])
    op.create_index('ix_token_blacklist_expires', 'token_blacklist', ['expires_at'])


def downgrade() -> None:
    op.drop_table('token_blacklist')
    op.drop_table('security_events')
    op.drop_table('audit_logs')
