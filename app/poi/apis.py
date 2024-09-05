from datetime import datetime
from typing import cast

from fastapi import APIRouter, status

from app.common.annotations import DatabaseSession
from app.common.encryption import EncryptionManager
from app.common.exceptions import NotFound
from app.core.settings import get_settings
from app.core.tags import get_tags
from app.poi import models, selectors, services
from app.poi.formatters import (
    format_gsm,
    format_id_document,
    format_known_associate,
    format_poi_application,
    format_poi_base,
    format_residential_address,
)
from app.poi.routes.offense import router as poi_offense_router
from app.poi.schemas import create, edit, response
from app.user.annotated import CurrentUser
from app.user.services import create_log

# Globals
router = APIRouter()
tags = get_tags()
settings = get_settings()
encrypt_man = EncryptionManager(key=settings.ENCRYPTION_KEY)

# Include routers
router.include_router(poi_offense_router, prefix="/offense", tags=["Offense Endpoints"])


@router.get(
    "/{poi_id}/application",
    summary="Get POI Application Progress",
    response_description="The details of the application process",
    status_code=status.HTTP_200_OK,
    response_model=response.POIApplicationProcessResponse,
)
async def route_poi_application_process(
    poi_id: int, _: CurrentUser, db: DatabaseSession
):
    """
    This endpoint returns the poi's application process
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    if not poi.application:
        raise NotFound("POI Application not found")

    return {"data": await format_poi_application(application=poi.application)}


@router.post(
    "",
    summary="Create POI",
    response_description="The created poi's base details",
    status_code=status.HTTP_201_CREATED,
    response_model=response.POIBaseInformationResponse,
)
async def route_poi_create(
    poi_in: create.POICreate,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint creates a poi
    """

    # Create poi base information
    poi = await services.create_poi(user=curr_user, data=poi_in, db=db)

    # Start application process
    # await services.create_poi_application_process(poi=poi, db=db)

    return {"data": await format_poi_base(poi=poi)}


@router.put(
    "/{poi_id}/base",
    summary="Edit POI Base information",
    response_description="The poi's edited base information",
    status_code=status.HTTP_200_OK,
    response_model=response.POIBaseInformationResponse,
    tags=[tags.POI_BASE_INFORMATION],
)
async def route_poi_base_info_edit(
    poi_id: int,
    poi_in: edit.POIBaseInformationEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint returns the poi's base information
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Edit poi
    edited_poi = await services.edit_poi(user=curr_user, poi=poi, data=poi_in, db=db)

    # Create logs
    await create_log(
        user=curr_user,
        resource="poi",
        action=f"get:{poi.id}-base",
        db=db,
    )

    return {"data": await format_poi_base(poi=edited_poi)}


@router.get(
    "/{poi_id}/base",
    summary="Get POI Base information",
    response_description="The poi's base information",
    status_code=status.HTTP_200_OK,
    response_model=response.POIBaseInformationResponse,
    tags=[tags.POI_BASE_INFORMATION],
)
async def route_poi_base_info(poi_id: int, curr_user: CurrentUser, db: DatabaseSession):
    """
    This endpoint returns the poi's base information
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create logs
    await create_log(
        user=curr_user,
        resource="poi",
        action=f"get:{poi.id}-base",
        db=db,
    )

    return {"data": await format_poi_base(poi=poi)}


#################################################################
# Other profile
#################################################################
# @router.post(
#     "/{poi_id}/other",
#     summary="Get POI other profile",
#     response_description="The POIs other profile",
#     status_code=status.HTTP_200_OK,
#     response_model=response.POIOtherInformationResponse,
#     tags=[tags.POI_OTHER_PROFILE],
# )
# async def route_poi_other_create(
#     poi_id: int,
#     data_in: create.POIOtherProfileCreate,
#     curr_user: CurrentUser,
#     db: DatabaseSession,
# ):
#     """
#     This endpoint adds the poi's other profile information
#     """

#     # Get poi
#     poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

#     # Create gsm numbers
#     if data_in.gsm_numbers:
#         for gsm in data_in.gsm_numbers:
#             await services.create_gsm_number(user=curr_user, poi=poi, data=gsm, db=db)

#     # Create residential addresses
#     if data_in.residential_addresses:
#         for address in data_in.residential_addresses:
#             await services.create_residential_address(
#                 user=curr_user, poi=poi, data=address, db=db
#             )

#     # Create known associates
#     if data_in.known_associates:
#         for associate in data_in.known_associates:
#             await services.create_known_associates(
#                 user=curr_user, poi=poi, data=associate, db=db
#             )

#     # Refresh poi
#     db.refresh(poi)

#     return {"data": await format_poi_other_profile(poi=poi)}


######################################################################
# ID Document
######################################################################
@router.post(
    "/{poi_id}/id-doc",
    summary="Create/Add ID Document",
    response_description="The created Id doc obj",
    status_code=status.HTTP_201_CREATED,
    response_model=response.IDDocumentResponse,
    tags=[tags.POI_ID_DOCUMENT],
)
async def route_poi_id_doc_create(
    poi_id: int,
    doc_in: create.CreateIDDocument,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint creates/adds an ID Doc to a poi
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # create id doc
    doc = await services.create_id_doc(user=curr_user, poi=poi, data=doc_in, db=db)

    return {"data": await format_id_document(doc=doc)}


@router.put(
    "/id-doc/{doc_id}/",
    summary="Edit ID Document",
    response_description="The edited ID Doc",
    status_code=status.HTTP_200_OK,
    response_model=response.IDDocumentResponse,
    tags=[tags.POI_ID_DOCUMENT],
)
async def route_poi_id_doc_edit(
    doc_id: int,
    doc_in: edit.IDDocumentEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint is used to edit ID Documents
    """

    # Get document
    doc = await selectors.get_id_doc_by_id(id=doc_id, db=db)

    edited_doc = await services.edit_id_doc(user=curr_user, doc=doc, data=doc_in, db=db)

    return {"data": await format_id_document(doc=edited_doc)}


@router.delete(
    "/id-doc/{doc_id}/",
    summary="Delete ID Document",
    response_description="ID Document Deleted Successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.IDDocumentDeleteResponse,
    tags=[tags.POI_ID_DOCUMENT],
)
async def route_poi_id_doc_delete(
    doc_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint deletes an ID Document
    """

    # Get ID Document
    doc = cast(models.IDDocument, await selectors.get_id_doc_by_id(id=doc_id, db=db))

    # Delete doc
    doc.is_deleted = encrypt_man.encrypt_boolean(True)  # type: ignore
    doc.deleted_at = encrypt_man.encrypt_datetime(datetime.now())  # type: ignore
    db.commit()

    # Create logs
    await create_log(
        user=curr_user,
        resource="id-doc",
        action=f"delete:{doc.id}",
        db=db,
    )

    return {}


###################################################################
# GSM NUMBERS
###################################################################
@router.post(
    "/{poi_id}/gsm",
    summary="Create GSM Number",
    response_description="The details of the created gsm number",
    status_code=status.HTTP_201_CREATED,
    response_model=response.GSMNumberResponse,
    tags=[tags.POI_GSM_NUMBER],
)
async def route_poi_gsm_create(
    poi_id: int,
    gsm_in: create.CreateGSMNumber,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint creates a gsm number
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # create gsm
    gsm = await services.create_gsm_number(user=curr_user, poi=poi, data=gsm_in, db=db)

    return {"data": await format_gsm(gsm=gsm)}


@router.put(
    "/gsm/{gsm_id}",
    summary="Edit GSM Number",
    response_description="The edited gsm number",
    status_code=status.HTTP_200_OK,
    response_model=response.GSMNumberResponse,
    tags=[tags.POI_GSM_NUMBER],
)
async def route_poi_gsm_edit(
    gsm_id: int,
    data_in: edit.GSMNumberEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint edits a poi's gsm number
    """

    # Get gsm
    gsm = await selectors.get_gsm_by_id(id=gsm_id, db=db)

    # Edit gsm
    edited_gsm = await services.edit_gsm(user=curr_user, gsm=gsm, data=data_in, db=db)

    return {"data": await format_gsm(gsm=edited_gsm)}


@router.delete(
    "/gsm/{gsm_id}/",
    summary="Delete GSM Number",
    response_description="GSM Number Deleted Successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.GSMNumberDeleteResponse,
    tags=[tags.POI_GSM_NUMBER],
)
async def route_poi_gsm_delete(
    gsm_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint deletes a gsm number
    """

    # Get gsm
    gsm = cast(models.GSMNumber, await selectors.get_gsm_by_id(id=gsm_id, db=db))

    # Delete gsm
    gsm.is_deleted = encrypt_man.encrypt_boolean(True)  # type: ignore
    gsm.deleted_at = encrypt_man.encrypt_datetime(datetime.now())  # type: ignore
    db.commit()

    # Create logs
    await create_log(
        user=curr_user,
        resource="gsm-number",
        action=f"delete:{gsm.id}",
        db=db,
    )

    return {}


#########################################################################
# RESIDENTIAL ADDRESS
#########################################################################
@router.post(
    "/{poi_id}/address",
    summary="Add POI residential address",
    response_description="The details of the residential address",
    status_code=status.HTTP_201_CREATED,
    response_model=response.ResidentialAddressResponse,
)
async def route_poi_address_create(
    poi_id: int,
    address_in: create.CreateResidentialAddress,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint creates a residential address
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create address
    address = await services.create_residential_address(
        user=curr_user, poi=poi, data=address_in, db=db
    )

    return {"data": await format_residential_address(address=address)}


@router.put(
    "/address/{address_id}/",
    summary="Edit POI residential addresses",
    response_description="The new details of the residential address",
    status_code=status.HTTP_200_OK,
    response_model=response.ResidentialAddressResponse,
)
async def route_poi_address_edit(
    address_id: int,
    address_in: edit.ResidentialAddressEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint is used to edit the poi's residential address
    """

    # Get address
    address = await selectors.get_residential_address_by_id(id=address_id, db=db)

    # edit address
    new_address = await services.edit_residential_address(
        user=curr_user, address=address, data=address_in, db=db
    )

    return {"data": await format_residential_address(address=new_address)}


@router.delete(
    "/address/{address_id}/",
    summary="Delete Residential Address",
    response_description="Residential Address Deleted Successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.ResidentialAddressDeleteResponse,
)
async def route_poi_address_delete(
    address_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint deletes a residential address
    """

    # Get address
    address = cast(
        models.ResidentialAddress,
        await selectors.get_residential_address_by_id(id=address_id, db=db),
    )

    # Delete address
    address.is_deleted = encrypt_man.encrypt_boolean(True)  # type: ignore
    address.deleted_at = encrypt_man.encrypt_datetime(datetime.now())  # type: ignore
    db.commit()

    # Create logs
    await create_log(
        user=curr_user,
        resource="residential-address",
        action=f"delete:{address.id}",
        db=db,
    )

    return {}


#########################################################################
# KNOWN ASSOCIATES
#########################################################################
@router.post(
    "/{poi_id}/associate",
    summary="Add POI Known associate",
    response_description="The details of the poi's known associate",
    status_code=status.HTTP_201_CREATED,
    response_model=response.KnownAssociateResponse,
)
async def route_poi_associate_create(
    poi_id: int,
    associate_in: create.CreateKnownAssociate,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint creates a known associate
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create associate
    associate = await services.create_known_associate(
        user=curr_user, poi=poi, data=associate_in, db=db
    )

    return {"data": await format_known_associate(associate=associate)}


@router.put(
    "/associate/{associate_id}/",
    summary="Edit known associate",
    response_description="The new details of the known associate",
    status_code=status.HTTP_200_OK,
    response_model=response.KnownAssociateResponse,
)
async def route_poi_associate_edit(
    associate_id: int,
    associate_in: edit.KnownAssociateEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint edits the known associate
    """

    # Get associate
    associate = cast(
        models.KnownAssociate,
        await selectors.get_known_associate_by_id(id=associate_id, db=db),
    )

    # Edit associate
    new_associate = await services.edit_known_associate(
        user=curr_user, associate=associate, data=associate_in, db=db
    )

    return {"data": await format_known_associate(associate=new_associate)}


@router.delete(
    "/associate/{associate_id}/",
    summary="Delete known associate",
    response_description="Known associate deleted successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.KnownAssociateDeleteResponse,
)
async def route_poi_assicate_delete(
    associate_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint is used to delete known associates
    """

    # Get associate
    associate = cast(
        models.KnownAssociate,
        await selectors.get_known_associate_by_id(id=associate_id, db=db),
    )

    # Delete address
    associate.is_deleted = encrypt_man.encrypt_boolean(True)  # type: ignore
    associate.deleted_at = encrypt_man.encrypt_datetime(datetime.now())  # type: ignore
    db.commit()

    # Create logs
    await create_log(
        user=curr_user,
        resource="known-associate",
        action=f"delete:{associate.id}",
        db=db,
    )

    return {}


#########################################################################
# EMPLOYMENT HISTORY
#########################################################################

#########################################################################
# VETERAN STATUS
#########################################################################

#########################################################################
# EDUCATIONAL BACKGROUND
#########################################################################

#########################################################################
# POI OFFENSE
#########################################################################

#########################################################################
# FREQUENTED SPOTS
#########################################################################
