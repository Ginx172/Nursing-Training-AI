"""Add organizations, teams, org_memberships tables

Revision ID: 005
Revises: 004
Create Date: 2026-03-31 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('subscription', sa.String(20), server_default='free'),
        sa.Column('max_members', sa.Integer(), server_default='5'),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('nhs_trust_name', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('settings', JSON, nullable=True),
    )
    op.create_index('ix_org_slug', 'organizations', ['slug'])

    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('specialty', sa.String(100), nullable=True),
        sa.Column('nhs_band_focus', sa.String(20), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_team_org', 'teams', ['organization_id'])

    op.create_table(
        'org_memberships',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('team_id', sa.Integer(), sa.ForeignKey('teams.id', ondelete='SET NULL'), nullable=True),
        sa.Column('role', sa.String(20), server_default='member'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
    )
    op.create_index('ix_orgmem_user', 'org_memberships', ['user_id'])
    op.create_index('ix_orgmem_org', 'org_memberships', ['organization_id'])
    op.create_index('ix_orgmem_team', 'org_memberships', ['team_id'])
    op.create_index('ix_orgmem_user_org', 'org_memberships', ['user_id', 'organization_id'], unique=True)


def downgrade() -> None:
    op.drop_table('org_memberships')
    op.drop_table('teams')
    op.drop_table('organizations')
