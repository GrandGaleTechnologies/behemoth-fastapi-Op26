import base64
import binascii
import os
import random
from datetime import datetime

import aiofiles
from sqlalchemy.orm import Session

from app.common.encryption import EncryptionManager
from app.common.exceptions import BadRequest, InternalServerError
from app.common.utils import dict_to_string
from app.core.settings import get_settings
from app.poi import models, selectors
from app.poi.crud import (
    POICRUD,
    EducationalBackgroundCRUD,
    EmploymentHistoryCRUD,
    FrequentedSpotCRUD,
    GSMNumberCRUD,
    IDDocumentCRUD,
    KnownAssociateCRUD,
    OffenseCRUD,
    POIApplicationProcess,
    POIOffenseCRUD,
    ResidentialAddressCRUD,
    VeteranStatusCRUD,
)
from app.poi.schemas import create, edit
from app.user import models as user_models
from app.user.crud import AuditLogCRUD
from app.user.services import create_log

# Global
settings = get_settings()
encryption_manager = EncryptionManager(key=settings.ENCRYPTION_KEY)
encrypt_man_dict = {
    "str": {
        "enc": encryption_manager.encrypt_str,
        "dec": encryption_manager.decrypt_str,
    },
    "date": {
        "enc": encryption_manager.encrypt_date,
        "dec": encryption_manager.decrypt_date,
    },
    "time": {
        "enc": encryption_manager.encrypt_time,
        "dec": encryption_manager.decrypt_time,
    },
    "bool": {
        "enc": encryption_manager.encrypt_boolean,
        "dec": encryption_manager.decrypt_boolean,
    },
}


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


async def create_poi(user: user_models.User, data: create.POICreate, db: Session):
    """
    Create poi

    Args:
        user (user_models.User): The user obj
        data (create.POIBaseInformationCreate): The poi data
        db (Session): The database session

    Raises:
        BadRequest: Invalid pfp bytes string

    Returns:
        models.POI
    """
    # Init crud
    poi_crud = POICRUD(db=db)

    # list for del
    created_objs = []

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
        "political_affiliation": encryption_manager.encrypt_str(
            data.political_affiliation
        )
        if data.political_affiliation
        else None,
        "tribal_union": encryption_manager.encrypt_str(data.tribal_union)
        if data.tribal_union
        else None,
        "last_seen_date": encryption_manager.encrypt_date(data.last_seen_date)
        if data.last_seen_date
        else None,
        "last_seen_time": encryption_manager.encrypt_time(data.last_seen_time)
        if data.last_seen_time
        else None,
        "is_completed": encryption_manager.encrypt_boolean(data=False),
        "notes": encryption_manager.encrypt_str(data.notes) if data.notes else None,
    }

    try:
        # Create poi
        poi = await poi_crud.create(data=encrypted_poi)
        created_objs.append(poi)

        # Create veteran status
        created_objs.append(
            await create_veteran_status(
                user=user, poi=poi, data=data.veteran_status, db=db
            )
        )

        # Create file for pfp
        if data.pfp:
            # Decode string
            try:
                img_data = base64.b64decode(data.pfp)
            except binascii.Error:
                raise BadRequest("Invalid pfp url bytes", loc=["body", "pfp"])

            # Save data to file
            loc = f"{settings.UPLOAD_DIR}/poi/{poi.id}/pfp/pfp_{random.randint(1, 50)}.jpeg"
            os.makedirs(os.path.dirname(loc), exist_ok=True)

            async with aiofiles.open(loc, "wb") as file:
                await file.write(img_data)

            # Set url
            poi.pfp_url = encryption_manager.encrypt_str(file.name)  # type: ignore
            db.commit()

        # Create ID documents
        if data.id_documents:
            for doc in data.id_documents:
                created_objs.append(
                    await create_id_doc(user=user, poi=poi, data=doc, db=db)
                )

        # Create GSM
        if data.gsm_numbers:
            for gsm in data.gsm_numbers:
                created_objs.append(
                    await create_gsm_number(user=user, poi=poi, data=gsm, db=db)
                )

        # Create Residential addresses
        if data.residential_addresses:
            for address in data.residential_addresses:
                created_objs.append(
                    await create_residential_address(
                        user=user, poi=poi, data=address, db=db
                    )
                )

        # Create known associates
        if data.known_associates:
            for associate in data.known_associates:
                created_objs.append(
                    await create_known_associates(
                        user=user, poi=poi, data=associate, db=db
                    )
                )

        # Create employment history
        if data.employment_history:
            for history in data.employment_history:
                created_objs.append(
                    await create_employment_history(
                        user=user, poi=poi, data=history, db=db
                    )
                )

        # Create educational background
        if data.educational_background:
            for background in data.educational_background:
                created_objs.append(
                    created_objs.append(
                        await create_educational_background(
                            user=user, poi=poi, data=background, db=db
                        )
                    )
                )

        # Create convictions
        if data.convictions:
            for conv in data.convictions:
                offense = await selectors.get_offense_by_id(id=conv.offense_id, db=db)
                created_objs.append(
                    await create_poi_offense(
                        user=user, poi=poi, offense=offense, data=conv, db=db
                    )
                )

        # Create frequented spots
        if data.frequented_spots:
            for spot in data.frequented_spots:
                created_objs.append(
                    await create_frequented_spot(user=user, poi=poi, data=spot, db=db)
                )
    except Exception as e:
        for obj in created_objs[:-1]:
            db.delete(obj)
        db.commit()

        raise e

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

    # init changelog
    changelog = ""

    # edit info
    poi_dict = poi.__dict__
    for field, value in data.model_dump(exclude=["pfp"], exclude_none=True).items():  # type: ignore
        enc = encrypt_man_dict[str(type(value).__name__)]["enc"]
        dec = encrypt_man_dict[str(type(value).__name__)]["dec"]

        if poi_dict[field] and dec(poi_dict[field]) != value:
            changelog += f"- {dec(poi_dict[field])} -> {value}\n"

            setattr(poi, field, enc(value))
        elif not poi_dict[field] and value:
            changelog += f"- {poi_dict[field]} -> {value}\n"

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


########################################################################
# ID Document
########################################################################
async def create_id_doc(
    user: user_models.User, poi: models.POI, data: create.CreateIDDocument, db: Session
):
    """
    Create ID Doc

    Args:
        user (user_models.User): The user obj
        poi (models.POI): The poi obj
        data (create.CreateIDDocument): The doc's data
        db (Session): The database session

    Returns:
        models.IDDocument
    """
    # Init crud
    doc_crud = IDDocumentCRUD(db=db)

    # Create ID Doc
    enc = encrypt_man_dict["str"]["enc"]

    doc = await doc_crud.create(
        data={
            "poi_id": poi.id,
            "type": enc(data.type),
            "id_number": enc(data.id_number),
        }
    )

    # Create logs
    await create_log(
        user=user,
        resource="id-doc",
        action=f"create:{doc.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return doc


async def edit_id_doc(
    user: user_models.User,
    doc: models.IDDocument,
    data: edit.IDDocumentEdit,
    db: Session,
):
    """
    Edit ID Document

    Args:
        user (user_models.User): The user obj
        doc (models.IDDocument): The id doc obj
        data (edit.IDDocumentEdit): The doc edit data
        db (Session): The database session

    Returns:
        models.IDDocument
    """
    changelog = ""

    doc_dict = doc.__dict__
    for field, value in data.model_dump().items():
        enc = encrypt_man_dict[str(type(value).__name__)]["enc"]
        dec = encrypt_man_dict[str(type(value).__name__)]["dec"]

        if dec(doc_dict[field]) != value:
            changelog += f"- {dec(doc_dict[field])} -> {value}\n"

            setattr(doc, field, enc(value))

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="iddoc",
        action=f"edit:{doc.id}",
        notes=changelog,
        db=db,
    )

    return doc


#################################################
# GSM NUMBERS
#################################################
async def create_gsm_number(
    user: user_models.User, poi: models.POI, data: create.CreateGSMNumber, db: Session
):
    """
    Create gsm number

    Args:
        user (user_models.User): The user obj
        poi (models.POI): The poi obj
        data (create.CreateGSMNumber): The details of the gsm number
        db (Session): The database session

    Returns:
        models.GSMNumber
    """
    # Init crud
    gsm_crud = GSMNumberCRUD(db=db)

    # Create gsm number
    enc = encrypt_man_dict["str"]["enc"]
    obj = await gsm_crud.create(
        data={
            "poi_id": poi.id,
            "service_provider": enc(data.service_provider),
            "number": enc(data.number),
            "last_call_date": encryption_manager.encrypt_date(data.last_call_date)
            if data.last_call_date
            else None,
            "last_call_time": encryption_manager.encrypt_time(data.last_call_time)
            if data.last_call_time
            else None,
        }
    )

    # Create logs
    await create_log(
        user=user,
        resource="gsm-number",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


async def edit_gsm(
    user: user_models.User, gsm: models.GSMNumber, data: edit.GSMNumberEdit, db: Session
):
    """
    Edit gsm number

    Args:
        user (user_models.User): The user obj
        gsm (models.GSMNumber): The gsm number obj
        data (edit.GSMNumberEdit): The details of the gsm number
        db (Session): The database session

    Returns:
        models.GSMNumber
    """
    changelog = ""

    gsm_dict = gsm.__dict__
    for field, value in data.model_dump(exclude=["pfp"], exclude_none=True).items():  # type: ignore
        enc = encrypt_man_dict[str(type(value).__name__)]["enc"]
        dec = encrypt_man_dict[str(type(value).__name__)]["dec"]

        if gsm_dict[field] and dec(gsm_dict[field]) != value:
            changelog += f"- {dec(gsm_dict[field])} -> {value}\n"

            setattr(gsm, field, enc(value))
        elif not gsm_dict[field] and value:
            changelog += f"- {gsm_dict[field]} -> {value}\n"

            setattr(gsm, field, enc(value))

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="gsm-number",
        action=f"edit:{gsm.id}",
        notes=changelog,
        db=db,
    )

    return gsm


##############################################################
# RESIDENTIAL ADDRESSES
##############################################################
async def create_residential_address(
    user: user_models.User,
    poi: models.POI,
    data: create.CreateResidentialAddress,
    db: Session,
):
    """
    Create residential address

    Args:
        user (user_models.User): The user obj
        poi (models.POI): The poi obj
        data (create.CreateResidentialAddress): The details of the address
        db (Session): The database session

    Returns:
        models.ResidentialAddress
    """
    # Init crud
    address_crud = ResidentialAddressCRUD(db=db)

    # Create address
    enc = encrypt_man_dict["str"]["enc"]
    obj = await address_crud.create(
        data={
            "poi_id": poi.id,
            "country": enc(data.country),
            "state": enc(data.state),
            "city": enc(data.city),
            "address": enc(data.address) if data.address else None,
        }
    )

    # Create logs
    await create_log(
        user=user,
        resource="address",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


############################################################
# KNOWN ASSOCIATES
############################################################
async def create_known_associates(
    user: user_models.User,
    poi: models.POI,
    data: create.CreateKnownAssociate,
    db: Session,
):
    """
    Create known associates

    Args:
        user (user_models.User): The user obj
        poi (models.POI): The poi obj
        data (create.CreateKnownAssociate): The associate's details
        db (Session): The database session

    Returns:
        models.KnownAssociate
    """
    # Init crud
    associate_crud = KnownAssociateCRUD(db=db)

    # Create known associates
    enc_str = encrypt_man_dict["str"]["enc"]
    enc_date = encrypt_man_dict["date"]["enc"]
    enc_time = encrypt_man_dict["time"]["enc"]
    obj = await associate_crud.create(
        data={
            "poi_id": poi.id,
            "full_name": enc_str(data.full_name),
            "known_gsm_numbers": enc_str(data.known_gsm_numbers),
            "relationship": enc_str(data.relationship),
            "occupation": enc_str(data.occupation) if data.occupation else None,
            "residential_address": enc_str(data.residential_address)
            if data.residential_address
            else None,
            "last_seen_date": enc_date(data.last_seen_date)
            if data.last_seen_date
            else None,
            "last_seen_time": enc_time(data.last_seen_time)
            if data.last_seen_time
            else None,
        }
    )

    # Create logs
    await create_log(
        user=user,
        resource="known-associates",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


async def create_employment_history(
    user: user_models.User,
    poi: models.POI,
    data: create.CreateEmploymentHistory,
    db: Session,
):
    """
    Create employment history

    Args:
        user (user_models.User): The user obj
        poi (models.POI): The poi obj
        data (create.CreateEmploymentHistory): The poi's employment history
        db (Session): The database session

    Returns:
        models.EmploymentHistory
    """
    # Init crud
    employment_crud = EmploymentHistoryCRUD(db=db)

    # create obj
    enc_str = encrypt_man_dict["str"]["enc"]
    enc_date = encrypt_man_dict["date"]["enc"]
    enc_bool = encrypt_man_dict["bool"]["enc"]

    obj = await employment_crud.create(
        data={
            "poi_id": poi.id,
            "company": enc_str(data.company),
            "employment_type": enc_str(data.employment_type),
            "from_date": enc_date(data.from_date) if data.from_date else None,
            "to_date": enc_date(data.to_date) if data.to_date else None,
            "current_job": enc_bool(data.current_job),
            "description": enc_str(data.description) if data.description else None,
        }
    )

    # Create logs
    await create_log(
        user=user,
        resource="employment-history",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


async def create_veteran_status(
    user: user_models.User,
    poi: models.POI,
    data: create.CreateVeteranStatus,
    db: Session,
):
    """
    Create veteran status

    Args:
        user (user_models.User): The user obj
        poi (models.POI): The poi obj
        data (create.CreateVeteranStatus): The veteran status details
        db (Session): The database session

    Returns:
        models.VeteranStatus
    """
    # Init crud
    veteran_crud = VeteranStatusCRUD(db=db)

    # Check: Veteran status exists
    if await veteran_crud.get(poi_id=poi.id):
        raise InternalServerError(
            f"POI[{poi.id}] Already ha a veteran status",
            loc="app.poi.services.create_veteran_status",
        )

    # Create obj
    enc_str = encrypt_man_dict["str"]["enc"]
    enc_bool = encrypt_man_dict["bool"]["enc"]
    enc_date = encrypt_man_dict["date"]["enc"]

    obj = await veteran_crud.create(
        data={
            "poi_id": poi.id,
            "is_veteran": enc_bool(data.is_veteran),
            "section": enc_str(data.section),
            "location": enc_str(data.location),
            "id_card": enc_str(data.id_card) if data.id_card else None,
            "id_card_issuer": enc_str(data.id_card_issuer)
            if data.id_card_issuer
            else None,
            "from_date": enc_date(data.from_date) if data.from_date else None,
            "to_date": enc_date(data.to_date) if data.to_date else None,
            "notes": enc_str(data.notes) if data.notes else None,
        }
    )

    # Create logs
    await create_log(
        user=user,
        resource="veteran-status",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


async def create_educational_background(
    user: user_models.User,
    poi: models.POI,
    data: create.CreateEducationalBackground,
    db: Session,
):
    # Init crud
    background_crud = EducationalBackgroundCRUD(db=db)

    # create educatonal background
    enc_str = encrypt_man_dict["str"]["enc"]
    enc_date = encrypt_man_dict["date"]["enc"]
    enc_bool = encrypt_man_dict["bool"]["enc"]
    obj = await background_crud.create(
        data={
            "poi_id": poi.id,
            "type": enc_str(data.type),
            "institute_name": enc_str(data.institute_name),
            "country": enc_str(data.country),
            "state": enc_str(data.state),
            "from_date": enc_date(data.from_date) if data.from_date else None,
            "to_date": enc_date(data.to_date) if data.to_date else None,
            "current_institute": enc_bool(data.current_institute),
        }
    )

    # Create logs
    await create_log(
        user=user,
        resource="veteran-status",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )
    return obj


async def create_poi_offense(
    user: user_models.User,
    poi: models.POI,
    offense: models.Offense,
    data: create.POIOffenseCreate,
    db: Session,
):
    """
    Create poi offense

    Args:
        user (user_models.User): The user obj
        poi (models.POI): The poi obj
        offense (models.Offense): The offense obj
        data (create.POIOffenseCreate): The details of the conviction
        db (Session): The database session

    Returns:
        models.POIOffense
    """
    # Init crud
    poi_offense_crud = POIOffenseCRUD(db=db)

    # create conviction
    enc_str = encrypt_man_dict["str"]["enc"]
    enc_date = encrypt_man_dict["date"]["enc"]

    obj = await poi_offense_crud.create(
        data={
            "poi_id": poi.id,
            "offense_id": offense.id,
            "case_id": enc_str(data.case_id) if data.case_id else None,
            "date_convicted": enc_date(data.date_convicted)
            if data.date_convicted
            else None,
            "notes": enc_str(data.notes) if data.notes else None,
        }
    )

    # Create logs
    await create_log(
        user=user,
        resource="poi-offense",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


async def create_frequented_spot(
    user: user_models.User,
    poi: models.POI,
    data: create.CreateFrequentedSpot,
    db: Session,
):
    """
    Create frequented spot

    Args:
        user (user_models.User): The user obj
        poi (models.POI): The poi obj
        data (create.CreatedFrequentedSpot): The spot details
        db (Session): The database session

    Returns:
        models.FrequentedSpot
    """
    # Init crud
    spot_crud = FrequentedSpotCRUD(db=db)

    # create spot
    enc_str = encrypt_man_dict["str"]["enc"]
    enc_date = encrypt_man_dict["date"]["enc"]

    obj = await spot_crud.create(
        data={
            "poi_id": poi.id,
            "country": enc_str(data.country),
            "state": enc_str(data.state),
            "lga": enc_str(data.lga),
            "address": enc_str(data.address),
            "from_date": enc_date(data.from_date) if data.from_date else None,
            "to_date": enc_date(data.to_date) if data.to_date else None,
            "notes": enc_str(data.notes) if data.notes else None,
        }
    )

    # Create logs
    await create_log(
        user=user,
        resource="frequented-spot",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj
