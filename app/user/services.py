from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.orm import Session

from app.common.encryption import EncryptionManager
from app.common.exceptions import Unauthorized
from app.common.security import verify_password
from app.core.settings import get_settings
from app.user import models
from app.user.crud import AuditLogCRUD, LoginAttemptCRUD, UserCRUD
from app.user.schemas import base

# Globals
settings = get_settings()
encryption_manager = EncryptionManager(key=settings.ENCRYPTION_KEY)


async def create_log(
    user: models.User,
    resource: str,
    action: str,
    db: Session,
    notes: str | Column[str] | None = None,
):
    """
    Create audit log

    Args:
        user (models.User): The user obj
        resource (str): The resource
        action (str): The action
        notes (str | Column[str] | None): The notes
        db (Session): The database session

    Returns:
        models.AuditLog
    """
    # Init crud
    audit_crud = AuditLogCRUD(db=db)

    # Create log
    log = await audit_crud.create(
        data={
            "user_id": user.id,
            "resource": encryption_manager.encrypt_str(data=resource),
            "action": encryption_manager.encrypt_str(data=action),
            "notes": encryption_manager.encrypt_str(data=str(notes))
            if bool(notes)
            else None,
            "created_at": encryption_manager.encrypt_datetime(dt=datetime.now()),
        }
    )

    return log


async def login_user(credential: base.UserLoginCredential, db: Session):
    """
    Login user
    Args:
        credential (base.UserLoginCredential): The user's login credentials
        db (Session): The database session

    Raises:
        Unauthorized

    Returns:
        models.User
    """
    # Init Crud
    user_crud = UserCRUD(db=db)
    attempt_crud = LoginAttemptCRUD(db=db)

    # Create Login Attempt
    login_attempt = await attempt_crud.create(
        data={
            "badge_num": encryption_manager.encrypt_str(data=credential.badge_num),
            "is_success": encryption_manager.encrypt_boolean(data=False),
            "attempted_at": encryption_manager.encrypt_datetime(dt=datetime.now()),
        }
    )

    # Get user obj
    obj = await user_crud.get(badge_num=credential.badge_num)
    if not obj:
        raise Unauthorized("Invalid Login Credentials")

    # Verify password
    if not await verify_password(raw=credential.password, hashed=obj.password):
        raise Unauthorized("Invalid Login Credentials")

    # Update login attempt
    login_attempt.is_success = encryption_manager.encrypt_boolean(data=True)  # type: ignore
    db.commit()

    return obj
