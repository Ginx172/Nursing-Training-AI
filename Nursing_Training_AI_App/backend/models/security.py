"""
Security Models - Audit Logs, Security Events, Token Blacklist
Persistenta datelor de securitate in PostgreSQL
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Index
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from core.database import Base


class AuditLog(Base):
    """Audit trail imutabil cu blockchain-style hash chain (SHA-256)"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(String(36), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    action = Column(String(60), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)

    user_id = Column(String(50), nullable=True, index=True)
    organization_id = Column(String(50), nullable=True, index=True)

    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    details = Column(JSON, nullable=True)

    previous_hash = Column(String(64), nullable=False)
    hash = Column(String(64), nullable=False, unique=True)

    __table_args__ = (
        Index('ix_audit_user_action', 'user_id', 'action'),
        Index('ix_audit_org_timestamp', 'organization_id', 'timestamp'),
        Index('ix_audit_severity_timestamp', 'severity', 'timestamp'),
    )


class SecurityEvent(Base):
    """Evenimente de securitate persistente (threat detection)"""
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String(60), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)

    source_ip = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(500), nullable=True)

    details = Column(JSON, nullable=True)
    risk_score = Column(Float, nullable=False, default=0.0)

    __table_args__ = (
        Index('ix_secevt_severity_timestamp', 'severity', 'timestamp'),
        Index('ix_secevt_ip_timestamp', 'source_ip', 'timestamp'),
        Index('ix_secevt_type_timestamp', 'event_type', 'timestamp'),
    )


class TokenBlacklist(Base):
    """Token-uri JWT revocate - supravietuiesc restart-ul serverului"""
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
