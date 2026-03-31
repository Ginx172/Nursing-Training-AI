"""
Organization Models - Organizations, Teams, Memberships
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class OrgSubscription(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class MemberRole(str, enum.Enum):
    MEMBER = "member"
    TEAM_LEADER = "team_leader"
    MANAGER = "manager"
    ADMIN = "admin"
    OWNER = "owner"


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)

    subscription = Column(Enum(OrgSubscription), default=OrgSubscription.FREE)
    max_members = Column(Integer, default=5)

    contact_email = Column(String(255), nullable=True)
    nhs_trust_name = Column(String(200), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    settings = Column(JSON, nullable=True)

    # Relationships
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")
    memberships = relationship("OrgMembership", back_populates="organization", cascade="all, delete-orphan")


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    specialty = Column(String(100), nullable=True)
    nhs_band_focus = Column(String(20), nullable=True)
    description = Column(String(500), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="teams")
    members = relationship("OrgMembership", back_populates="team")


class OrgMembership(Base):
    """Legatura User <-> Organization + optional Team"""
    __tablename__ = "org_memberships"
    __table_args__ = (
        Index('ix_orgmem_user_org', 'user_id', 'organization_id', unique=True),
        {'extend_existing': True},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)

    role = Column(Enum(MemberRole), default=MemberRole.MEMBER)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    organization = relationship("Organization", back_populates="memberships")
    team = relationship("Team", back_populates="members")
