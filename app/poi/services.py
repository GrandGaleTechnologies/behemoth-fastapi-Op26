from datetime import datetime

from sqlalchemy.orm import Session

from app.common.encryption import EncryptionManager
from app.common.exceptions import BadRequest
from app.core.settings import get_settings
from app.poi import models
from app.poi.crud import OffenseCRUD
from app.poi.schemas import create, edit
from app.user import models as user_models
from app.user.crud import AuditLogCRUD
from app.user.services import create_log

# Global
settings = get_settings()
encryption_manager = EncryptionManager(key=settings.ENCRYPTION_KEY)


async def create_offense(
    user: user_models.User, data: create.CreateOffense, db: Session
):
    """
    Create offense

    Args:
        user (user_models.User): The user obj
        data (create.CreateOffense): The data of the offense,
        db (Session): The database session

    Raises:
        BadRequest: Offense already exists

    Returns:
        models.Offense
    """
    # Init CRUD
    offense_crud = OffenseCRUD(db=db)
    audit_crud = AuditLogCRUD(db=db)

    # Transformations
    data.name = data.name.capitalize()

    # Check: unique offense
    if data.name in [
        encryption_manager.decrypt_str(data=off.name)
        for off in await offense_crud.get_all()
    ]:
        raise BadRequest("Offense already exists")

    # Create offense
    obj = await offense_crud.create(
        data={
            "name": encryption_manager.encrypt_str(data=data.name),
            "description": encryption_manager.encrypt_str(data=data.description),
            "created_at": encryption_manager.encrypt_datetime(dt=datetime.now()),
        }
    )

    # Create log
    await audit_crud.create(
        data={
            "user_id": user.id,
            "resource": encryption_manager.encrypt_str(data="offenses"),
            "action": encryption_manager.encrypt_str(data="create"),
            "notes": encryption_manager.encrypt_str(data=data.name),
            "created_at": encryption_manager.encrypt_datetime(dt=datetime.now()),
        }
    )

    return obj


# NOTE
# - Add a check to make sure new name is unique
async def edit_offense(
    user: user_models.User, offense: models.Offense, data: edit.OffenseEdit, db: Session
):
    """
    Edit offense

    Args:
        user (user_models.User): The user obj
        offense (models.Offense): The offense obj
        data (edit.OffenseEdit): The edit data,
        db (Session): The database session

    Returns:
        models.Offense
    """

    # Init changelog
    changelog = ""

    # Check: name change
    offense_name = encryption_manager.decrypt_str(data=offense.name)
    if offense_name != data.name:
        changelog += f"- {offense_name} -> {data.name}\n"
        offense.name = encryption_manager.encrypt_str(data.name)  # type: ignore

    # Check: description change
    offense_description = encryption_manager.decrypt_str(data=offense.description)
    if offense_description != data.description:
        changelog += f"- {offense_description} -> {data.description}"
        offense.description = encryption_manager.encrypt_str(data.description)  # type: ignore

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="offense",
        action=f"edit:{offense.id}",
        notes=changelog if changelog != "" else None,
        db=db,
    )

    return offense
