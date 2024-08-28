import base64
import binascii
import os
from datetime import datetime

import aiofiles
from sqlalchemy.orm import Session

from app.common.encryption import EncryptionManager
from app.common.exceptions import BadRequest
from app.common.utils import dict_to_string
from app.core.settings import get_settings
from app.poi import models
from app.poi.crud import POICRUD, IDDocumentCRUD, OffenseCRUD, POIApplicationProcess
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


async def create_poi(
    user: user_models.User, data: create.POIBaseInformationCreate, db: Session
):
    # Init crud
    poi_crud = POICRUD(db=db)
    id_crud = IDDocumentCRUD(db=db)

    # encrypt data
    encrypted_poi = {
        "full_name": encryption_manager.encrypt_str(data.full_name),
        "alias": encryption_manager.encrypt_str(data.alias),
        "dob": encryption_manager.encrypt_date(data.dob) if data.dob else None,
        "pob": encryption_manager.encrypt_str(data.pob) if data.pob else None,
        "nationality": encryption_manager.encrypt_str(data.nationality)
        if data.nationality
        else None,
        "religion": encryption_manager.encrypt_str(data.religion)
        if data.religion
        else None,
        "is_completed": encryption_manager.encrypt_boolean(data=False),
    }

    # Create poi
    poi = await poi_crud.create(data=encrypted_poi)

    # Create ID documents
    if data.id_documents:
        _ = [
            await id_crud.create(
                data={
                    "poi_id": poi.id,
                    "type": encryption_manager.encrypt_str(doc.type),
                    "id_number": encryption_manager.encrypt_str(doc.id_number),
                },
            )
            for doc in data.id_documents
        ]

    # Create file for pfp
    if data.pfp:
        # Decode string
        try:
            img_data = base64.b64decode(data.pfp)
        except binascii.Error:
            raise BadRequest("Invalid pfp url bytes", loc=["body", "pfp"])

        # Save data to file
        loc = f"{settings.UPLOAD_DIR}/poi/{poi.id}/pfp/pfp.jpeg"
        os.makedirs(os.path.dirname(loc), exist_ok=True)

        async with aiofiles.open(loc, "wb") as file:
            await file.write(img_data)

        # Set url
        poi.pfp_url = encryption_manager.encrypt_str(file.name)  # type: ignore
        db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="poi",
        action=f"create:{poi.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return poi


async def edit_poi(
    user: user_models.User,
    poi: models.POI,
    data: edit.POIBaseInformationEdit,
    db: Session,
):
    """
    Edit poi base information

    Args:
        user (user_models.User): The user obj
        poi (modes.POI): The poi obj
        data (edit.POIBaseInformationEdit): The poi's edit
        db (Session): The database session

    Returns:
        models.POI
    """
    # type mang:
    encrypt_man_dict = {
        "str": {
            "enc": encryption_manager.encrypt_str,
            "dec": encryption_manager.decrypt_str,
        },
        "date": {
            "enc": encryption_manager.encrypt_date,
            "dec": encryption_manager.decrypt_date,
        },
    }

    # init changelog
    changelog = ""

    # edit info
    poi_dict = poi.__dict__
    for field, value in data.model_dump(exclude=["pfp"]).items():  # type: ignore
        enc = encrypt_man_dict[str(type(value).__name__)]["enc"]
        dec = encrypt_man_dict[str(type(value).__name__)]["dec"]

        if dec(poi_dict[field]) != value:
            changelog += f"- {dec(poi_dict[field])} -> {value}\n"

            setattr(poi, field, enc(value))

    # Create file for pfp
    if data.pfp:
        # Decode string
        try:
            img_data = base64.b64decode(data.pfp)
        except binascii.Error:
            raise BadRequest("Invalid pfp url bytes", loc=["body", "pfp"])

        # Save data to file
        loc = f"{settings.UPLOAD_DIR}/poi/{poi.id}/pfp/pfp.jpeg"
        os.makedirs(os.path.dirname(loc), exist_ok=True)

        async with aiofiles.open(loc, "wb") as file:
            await file.write(img_data)

        # Set url
        poi.pfp_url = encryption_manager.encrypt_str(file.name)  # type: ignore

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="poi",
        action=f"create:{poi.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return poi


async def create_poi_application_process(poi: models.POI, db: Session):
    """
    Create poi application process

    Args:
        poi (models.POI): The poi obj
        db (Session): The database session

    Returns:
        models.POIApplicationProcess
    """
    # Init crud
    application_crud = POIApplicationProcess(db=db)

    # Create application process
    application_process = await application_crud.create(data={"poi_id": poi.id})

    return application_process
