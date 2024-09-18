from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.core.database import DBBase


class User(DBBase):
    """
    Database model for users
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    badge_num = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(), nullable=False)


class LoginAttempt(DBBase):
    """
    Database model for login attempts
    """

    __tablename__ = "login_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    badge_num = Column(String, nullable=False)
    is_success = Column(Boolean, default=False, nullable=False)
    attempted_at = Column(
        DateTime(timezone=True), default=datetime.now(), nullable=False
    )


class AuditLog(DBBase):
    """
    Database model for audit logs
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    resource = Column(String, nullable=False)
    action = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
