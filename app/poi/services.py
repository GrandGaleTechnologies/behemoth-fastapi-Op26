import base64
import binascii
import os
import random

import aiofiles
from sqlalchemy.orm import Session

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
    POIOffenseCRUD,
    ResidentialAddressCRUD,
    VeteranStatusCRUD,
)
from app.poi.schemas import create, edit
from app.user import models as user_models
from app.user.services import create_log

# Global
settings = get_settings()


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

    # Transformations
    data.name = data.name.capitalize()

    # Check: unique offense
    if await offense_crud.get(name=data.name):
        raise BadRequest("Offense already exists")

    # Create offense
    obj = await offense_crud.create(
        data={
            "name": data.name,
            "description": data.description,
        }
    )

    # Create log
    await create_log(
        user=user, resource="offense", action=f"create:{obj.id}", notes=data.name, db=db
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
    if bool(offense.name != data.name):
        changelog += f"- {offense.name} -> {data.name}\n"
        offense.name = data.name  # type: ignore

    # Check: description change
    if bool(offense.description != data.description):
        changelog += f"- {offense.description} -> {data.description}"
        offense.description = data.description  # type: ignore

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

    try:
        # Create poi
        poi = await poi_crud.create(
            data=create.CreatePOIBaseInformation(**data.model_dump()).model_dump(
                exclude=["pfp", "id_documents"]  # type: ignore
            )
        )
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
                base64_str = data.pfp.split(",", 1)[1]
                img_data = base64.b64decode(base64_str)
            except (binascii.Error, Exception):
                raise BadRequest("Invalid pfp format", loc=["body", "pfp"])

            # Save data to file
            loc = f"{settings.UPLOAD_DIR}/poi/{poi.id}/pfp/pfp_{random.randint(1, 50)}.jpeg"
            os.makedirs(os.path.dirname(loc), exist_ok=True)

            async with aiofiles.open(loc, "wb") as file:
                await file.write(img_data)

            # Set url
            poi.pfp_url = file.name  # type: ignore
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
                    await create_known_associate(
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
        for obj in created_objs[::-1]:
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

    # Transformation
    data.full_name = data.full_name.capitalize()
    data.alias = data.alias.capitalize()

    # init changelog
    changelog = ""

    # edit info
    poi_dict = poi.__dict__
    for field, value in data.model_dump(exclude=["pfp"], exclude_none=True).items():  # type: ignore
        if poi_dict[field] and poi_dict[field] != value:
            changelog += f"- {poi_dict[field]} -> {value}\n"

            setattr(poi, field, value)

        elif not poi_dict[field] and value:
            changelog += f"- {poi_dict[field]} -> {value}\n"

            setattr(poi, field, value)

    # Create file for pfp
    if data.pfp:
        try:
            base64_str = data.pfp.split(",", 1)[1]
            img_data = base64.b64decode(base64_str)
        except (binascii.Error, Exception):
            raise BadRequest("Invalid pfp format", loc=["body", "pfp"])

        # Save data to file
        loc = f"{settings.UPLOAD_DIR}/poi/{poi.id}/pfp/pfp.jpeg"
        os.makedirs(os.path.dirname(loc), exist_ok=True)

        async with aiofiles.open(loc, "wb") as file:
            await file.write(img_data)

        # Set url
        poi.pfp_url = file.name  # type: ignore

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

    doc = await doc_crud.create(data={"poi_id": poi.id, **data.model_dump()})

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
        if doc_dict[field] != value:
            changelog += f"- {doc_dict[field]} -> {value}\n"

            setattr(doc, field, value)

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
    obj = await gsm_crud.create(data={"poi_id": poi.id, **data.model_dump()})

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
        if gsm_dict[field] and gsm_dict[field] != value:
            changelog += f"- {gsm_dict[field]} -> {value}\n"

            setattr(gsm, field, value)

        elif not gsm_dict[field] and value:
            changelog += f"- {gsm_dict[field]} -> {value}\n"

            setattr(gsm, field, value)

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
    obj = await address_crud.create(data={"poi_id": poi.id, **data.model_dump()})

    # Create logs
    await create_log(
        user=user,
        resource="address",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


async def edit_residential_address(
    user: user_models.User,
    address: models.ResidentialAddress,
    data: edit.ResidentialAddressEdit,
    db: Session,
):
    """
    Edit residential address

    Args:
        user (user_models.User): The user obj
        address (models.ResidentialAddress): The address obj
        data (edit.ResidentialAddressEdit): The details of the residential address
        db (Session): The database session

    Returns:
        models.ResidentialAddress
    """
    changelog = ""

    address_dict = address.__dict__
    for field, value in data.model_dump(exclude_none=True).items():  # type: ignore
        if address_dict[field] and address_dict[field] != value:
            changelog += f"- {address_dict[field]} -> {value}\n"

            setattr(address, field, value)

        elif not address_dict[field] and value:
            changelog += f"- {address_dict[field]} -> {value}\n"

            setattr(address, field, value)

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="residential-address",
        action=f"edit:{address.id}",
        notes=changelog,
        db=db,
    )

    return address


############################################################
# KNOWN ASSOCIATES
############################################################
async def create_known_associate(
    user: user_models.User,
    poi: models.POI,
    data: create.CreateKnownAssociate,
    db: Session,
):
    """
    Create known associate

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
    obj = await associate_crud.create(data={"poi_id": poi.id, **data.model_dump()})

    # Create logs
    await create_log(
        user=user,
        resource="known-associates",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


async def edit_known_associate(
    user: user_models.User,
    associate: models.KnownAssociate,
    data: edit.KnownAssociateEdit,
    db: Session,
):
    """
    Edit known associate

    Args:
        user (user_models.User): The user obj
        associate (models.KnownAssociate): The associate obj
        data (edit.KnownAssociateEdit): The details of the known associate
        db (Session): The database session

    Return:
        models.KnownAssociate
    """
    changelog = ""

    address_dict = associate.__dict__
    for field, value in data.model_dump(exclude_none=True).items():  # type: ignore
        if address_dict[field] and address_dict[field] != value:
            changelog += f"- {address_dict[field]} -> {value}\n"

            setattr(associate, field, value)
        elif not address_dict[field] and value:
            changelog += f"- {address_dict[field]} -> {value}\n"

            setattr(associate, field, value)

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="known-associate",
        action=f"edit:{associate.id}",
        notes=changelog,
        db=db,
    )

    return associate


###############################################################################
# EMPLOYMENT HISTORY
###############################################################################


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
    obj = await employment_crud.create(data={"poi_id": poi.id, **data.model_dump()})

    # Create logs
    await create_log(
        user=user,
        resource="employment-history",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


async def edit_employment_history(
    user: user_models.User,
    history: models.EmploymentHistory,
    data: edit.EmploymentHistoryEdit,
    db: Session,
):
    """
    Edit employment history

    Args:
        user (user_models.User): The user obj
        history (models.EmploymentHistory): The history obj
        data (edit.EmploymentHistoryEdit): The details of the employment history
        db (Session): The database session

    Returns:
        models.EmploymentHistory
    """
    changelog = ""

    history_dict = history.__dict__
    for field, value in data.model_dump(exclude_none=True).items():  # type: ignore
        if history_dict[field] and history_dict[field] != value:
            changelog += f"- {history_dict[field]} -> {value}\n"

            setattr(history, field, value)

        elif not history_dict[field] and value:
            changelog += f"- {history_dict[field]} -> {value}\n"

            setattr(history, field, value)

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="employment-history",
        action=f"edit:{history.id}",
        notes=changelog,
        db=db,
    )

    return history


#############################################################################
# VETERAN STATUS
#############################################################################


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
    obj = await veteran_crud.create(data={"poi_id": poi.id, **data.model_dump()})

    # Create logs
    await create_log(
        user=user,
        resource="veteran-status",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


async def edit_veteran_status(
    user: user_models.User,
    status: models.VeteranStatus,
    data: edit.VeteranStatusEdit,
    db: Session,
):
    """
    Edit veteran status

    Args:
        user (user_models.User): The user obj
        status (models.VeteranStatus): The poi obj
        data (edit.VeteranStatusEdit): The details of the veteran status
        db (Session): The database session

    Returns:
        models.VeteranStatus
    """
    changelog = ""

    status_dict = status.__dict__
    for field, value in data.model_dump(exclude_none=True).items():  # type: ignore
        if status_dict[field] and status_dict[field] != value:
            changelog += f"- {status_dict[field]} -> {value}\n"

            setattr(status, field, value)

        elif not status_dict[field] and value:
            changelog += f"- {status_dict[field]} -> {value}\n"

            setattr(status, field, value)

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="veteran-status",
        action=f"edit:{status.id}",
        notes=changelog,
        db=db,
    )

    return status


#############################################################################
# EDUCATIONAL BACKGROUND
#############################################################################
async def create_educational_background(
    user: user_models.User,
    poi: models.POI,
    data: create.CreateEducationalBackground,
    db: Session,
):
    """
    Create educational background

    Args:
        user (user_models.User): The user obj
        poi (models.POI): The poi obj
        data (create.CreateEducationalBackground): The details of the educational background
        db (Session): The database session

    Returns:
        models.EducationalBackground
    """
    # Init crud
    background_crud = EducationalBackgroundCRUD(db=db)

    # create educatonal background
    obj = await background_crud.create(data={"poi_id": poi.id, **data.model_dump()})

    # Create logs
    await create_log(
        user=user,
        resource="veteran-status",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )
    return obj


async def edit_educational_background(
    user: user_models.User,
    education: models.EducationalBackground,
    data: edit.EducationalBackgroundEdit,
    db: Session,
):
    """
    Edit educational background

    Args:
        user (user_models.User): The user obj
        education (models.EducationalBackground): The educational background obj
        data (edit.EducationalBackgroundEdit): The details of the educational background
        db (Session): The database session

    Returns:
        models.EducationalBackground
    """
    changelog = ""

    education_dict = education.__dict__
    for field, value in data.model_dump(exclude_none=True).items():  # type: ignore
        if education_dict[field] and education_dict[field] != value:
            changelog += f"- {education_dict[field]} -> {value}\n"

            setattr(education, field, value)

        elif not education_dict[field] and value:
            changelog += f"- {education_dict[field]} -> {value}\n"

            setattr(education, field, value)

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="educational-background",
        action=f"edit:{education.id}",
        notes=changelog,
        db=db,
    )

    return education


##############################################################################
# POI OFFENSE
##############################################################################
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
    obj = await poi_offense_crud.create(
        data={"poi_id": poi.id, "offense_id": offense.id, **data.model_dump()}
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


async def edit_poi_offense(
    user: user_models.User,
    poi_offense: models.POIOffense,
    data: edit.POIOffenseEdit,
    db: Session,
):
    """
    Edit poi offense

    Args:
        user (user_models.User): The user obj
        poi_offense (models.POIOffense): The poi offense obj
        data (edit.POIOffenseEdit): The details of the poi
        db (Session): The database session

    Returns:
        models.POIOffense
    """
    changelog = ""

    poi_offense_dict = poi_offense.__dict__
    for field, value in data.model_dump(exclude_none=True).items():  # type: ignore
        if poi_offense_dict[field] and poi_offense_dict[field] != value:
            changelog += f"- {poi_offense_dict[field]} -> {value}\n"

            setattr(poi_offense, field, value)

        elif not poi_offense_dict[field] and value:
            changelog += f"- {poi_offense_dict[field]} -> {value}\n"

            setattr(poi_offense, field, value)

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="poi-offense",
        action=f"edit:{poi_offense.id}",
        notes=changelog,
        db=db,
    )

    return poi_offense


#################################################################################
# FREQUENTED SPOT
#################################################################################
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
    obj = await spot_crud.create(data={"poi_id": poi.id, **data.model_dump()})

    # Create logs
    await create_log(
        user=user,
        resource="frequented-spot",
        action=f"create:{obj.id}",
        notes=await dict_to_string(data.model_dump()),
        db=db,
    )

    return obj


async def edit_frequented_spot(
    user: user_models.User,
    spot: models.FrequentedSpot,
    data: edit.FrequentedSpotEdit,
    db: Session,
):
    """
    Edit frequented spot

    Args:
        user (user_models.User): The user obj
        spot (models.FrequentedSpot): The frequented spot obj
        data (edit.FrequentedSpotEdit): The details of the frequented spot
        db (Session): The database session

    Returns:
        models.FrequentedSpot
    """
    changelog = ""

    spot_dict = spot.__dict__
    for field, value in data.model_dump(exclude_none=True).items():  # type: ignore
        if spot_dict[field] and spot_dict[field] != value:
            changelog += f"- {spot_dict[field]} -> {value}\n"

            setattr(spot, field, value)
        elif not spot_dict[field] and value:
            changelog += f"- {spot_dict[field]} -> {value}\n"

            setattr(spot, field, value)

    # Save changes
    db.commit()

    # Create logs
    await create_log(
        user=user,
        resource="frequented-spot",
        action=f"edit:{spot.id}",
        notes=changelog,
        db=db,
    )

    return spot
