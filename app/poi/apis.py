from datetime import datetime
from typing import cast

from fastapi import APIRouter, status

from app.common.annotations import DatabaseSession, PaginationParams
from app.common.encryption import EncryptionManager
from app.common.exceptions import NotFound
from app.common.paginators import get_pagination_metadata
from app.core.settings import get_settings
from app.core.tags import get_tags
from app.poi import models, selectors, services
from app.poi.formatters import (
    format_educational_background,
    format_employment_history,
    format_frequented_spot,
    format_gsm,
    format_id_document,
    format_known_associate,
    format_poi_application,
    format_poi_base,
    format_poi_offense,
    format_poi_summary,
    format_residential_address,
    format_veteran_status,
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


@router.get(
    "",
    summary="Get POI List",
    response_description="The paginated list of poi's",
    status_code=status.HTTP_200_OK,
    response_model=response.PaginatedPOISummaryListResponse,
)
async def route_poi_list(
    pagination: PaginationParams,
    curr_user: CurrentUser,
    db: DatabaseSession,
    gsm: str | None = None,
    is_pinned: bool | None = None,
):
    """
    This endpoint returns the paginated list of pois
    """

    # Create log
    await create_log(
        user=curr_user,
        resource="poi",
        action="get-paginated-list",
        notes=f"Q: {pagination.q}, P: {pagination.page}, S: {pagination.size}, OB: {pagination.order_by}",
        db=db,
    )

    # get offenses
    pois, tnoi = await selectors.get_paginated_poi_list(
        gsm=gsm, is_pinned=is_pinned, pagination=pagination, db=db
    )

    return {
        "data": [await format_poi_summary(poi=poi) for poi in pois],
        "meta": get_pagination_metadata(
            tno_items=tnoi,
            count=len(pois),
            page=pagination.page,
            size=pagination.size,
        ),
    }


@router.put(
    "/{poi_id}/pin/toggle",
    summary="Toggle POI Pin Status",
    response_description="POI Pinned/Unpinned successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.POIPinResponse,
    tags=[tags.POI],
)
async def route_poi_pin_toggle(
    poi_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint toggles the poi's pin status
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Toggle pin
    if encrypt_man.decrypt_boolean(poi.is_pinned):
        stat = "POI Successfully Unpinned"
    else:
        stat = "POI Succcessfully Pinned"

    poi.is_pinned = encrypt_man.encrypt_boolean(  # type: ignore
        not encrypt_man.decrypt_boolean(poi.is_pinned)
    )
    db.commit()

    # Create logs
    await create_log(
        user=curr_user,
        resource="poi",
        action=f"edit-pin:{poi.id}",
        notes=stat,
        db=db,
    )

    return {"msg": stat}


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


@router.delete(
    "/{poi_id}/",
    summary="Delete POI",
    response_description="POI Deleted Successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.POIDeleteRequestResponse,
)
async def route_poi_delete(poi_id: int, curr_user: CurrentUser, db: DatabaseSession):
    """
    This endpoint deletes the poi
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Delete doc
    poi.is_deleted = encrypt_man.encrypt_boolean(True)  # type: ignore
    poi.deleted_at = encrypt_man.encrypt_datetime(datetime.now())  # type: ignore
    db.commit()

    # NOTE: Mark other items like id-doc, etc as deleted

    # Create logs
    await create_log(
        user=curr_user,
        resource="poi",
        action=f"delete:{poi.id}",
        db=db,
    )

    return {}


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


@router.get(
    "/{poi_id}/id-doc",
    summary="Get POI ID Documents",
    response_description="The list of the poi's id documents",
    status_code=status.HTTP_200_OK,
    response_model=response.IDDocumentListResponse,
    tags=[tags.POI_ID_DOCUMENT],
)
async def route_poi_id_doc_list(
    poi_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint returns the list of the poi's id documents
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create logs
    await create_log(
        user=curr_user,
        resource="id-doc",
        action=f"get-list:{poi.id}",
        db=db,
    )

    return {
        "data": [
            await format_id_document(doc=doc)
            for doc in await selectors.get_id_documents(poi=poi, db=db)
        ]
    }


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


@router.get(
    "/{poi_id}/gsm",
    summary="Get POI ID GSM Numbers",
    response_description="The list of the poi's gsm numbers",
    status_code=status.HTTP_200_OK,
    response_model=response.GSMNumberListResponse,
    tags=[tags.POI_GSM_NUMBER],
)
async def route_poi_gsm_list(poi_id: int, curr_user: CurrentUser, db: DatabaseSession):
    """
    This endpoint returns the list of the poi's gsm numbers
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create logs
    await create_log(
        user=curr_user,
        resource="gsm-numbers",
        action=f"get-list:{poi.id}",
        db=db,
    )

    return {
        "data": [
            await format_gsm(gsm=gsm)
            for gsm in await selectors.get_gsm_numbers(poi=poi, db=db)
        ]
    }


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
    tags=[tags.POI_RESIDENTIAL_ADDRESS],
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


@router.get(
    "/{poi_id}/address",
    summary="Get POI Residential addresses",
    response_description="The poi's residential addresses",
    status_code=status.HTTP_200_OK,
    response_model=response.ResidentialAddressListResponse,
    tags=[tags.POI_RESIDENTIAL_ADDRESS],
)
async def route_poi_address_list(
    poi_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint returns the list of the poi's addresses
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create logs
    await create_log(
        user=curr_user,
        resource="residential-address",
        action=f"get-list:{poi.id}",
        db=db,
    )

    return {
        "data": [
            await format_residential_address(address=address)
            for address in await selectors.get_residential_addresses(poi=poi, db=db)
        ]
    }


@router.put(
    "/address/{address_id}/",
    summary="Edit POI residential addresses",
    response_description="The new details of the residential address",
    status_code=status.HTTP_200_OK,
    response_model=response.ResidentialAddressResponse,
    tags=[tags.POI_RESIDENTIAL_ADDRESS],
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
    tags=[tags.POI_RESIDENTIAL_ADDRESS],
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
    tags=[tags.POI_KNOWN_ASSOCIATE],
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


@router.get(
    "/{poi_id}/associate",
    summary="Get POI known associates",
    response_description="The list of poi known associates",
    status_code=status.HTTP_200_OK,
    response_model=response.KnownAssociateListResponse,
    tags=[tags.POI_KNOWN_ASSOCIATE],
)
async def route_poi_associate_list(
    poi_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint returns the list of the poi's known associates
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create logs
    await create_log(
        user=curr_user,
        resource="known-associate",
        action=f"get-list:{poi.id}",
        db=db,
    )

    return {
        "data": [
            await format_known_associate(associate=associate)
            for associate in await selectors.get_known_associates(poi=poi, db=db)
        ]
    }


@router.put(
    "/associate/{associate_id}/",
    summary="Edit known associate",
    response_description="The new details of the known associate",
    status_code=status.HTTP_200_OK,
    response_model=response.KnownAssociateResponse,
    tags=[tags.POI_KNOWN_ASSOCIATE],
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
    tags=[tags.POI_KNOWN_ASSOCIATE],
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
@router.post(
    "/{poi_id}/employment",
    summary="Add POI Employment History",
    response_description="The details of the employment history",
    status_code=status.HTTP_201_CREATED,
    response_model=response.EmploymentHistoryResponse,
    tags=[tags.POI_EMPLOYMENT_HISTORY],
)
async def route_poi_employment_create(
    poi_id: int,
    history_in: create.CreateEmploymentHistory,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint creates an employment history
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create employment history
    history = await services.create_employment_history(
        user=curr_user, poi=poi, data=history_in, db=db
    )

    return {"data": await format_employment_history(history=history)}


@router.get(
    "/{poi_id}/employment",
    summary="Get POI employment history",
    response_description="The list of the poi's employment history",
    status_code=status.HTTP_200_OK,
    response_model=response.EmploymentHistoryListResponse,
    tags=[tags.POI_EMPLOYMENT_HISTORY],
)
async def route_poi_employment_list(
    poi_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint returns the list of the poi's employment history
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create logs
    await create_log(
        user=curr_user,
        resource="employment-history",
        action=f"get-list:{poi.id}",
        db=db,
    )

    return {
        "data": [
            await format_employment_history(history=history)
            for history in await selectors.get_employment_history(poi=poi, db=db)
        ]
    }


@router.put(
    "/employment/{history_id}/",
    summary="Edit employment history",
    response_description="The new details of the employment history",
    status_code=status.HTTP_200_OK,
    response_model=response.EmploymentHistoryResponse,
    tags=[tags.POI_EMPLOYMENT_HISTORY],
)
async def route_poi_employment_edit(
    history_id: int,
    history_in: edit.EmploymentHistoryEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint edits an employment history
    """

    # Get employment history
    history = cast(
        models.EmploymentHistory,
        await selectors.get_employment_history_by_id(id=history_id, db=db),
    )

    # Edit history
    new_history = await services.edit_employment_history(
        user=curr_user, history=history, data=history_in, db=db
    )

    return {"data": await format_employment_history(history=new_history)}


@router.delete(
    "/employment/{history_id}/",
    summary="Delete employment history",
    response_description="Employment history deleted successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.EmploymentHistoryDeleteResponse,
    tags=[tags.POI_EMPLOYMENT_HISTORY],
)
async def route_poi_employment_delete(
    history_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint deletes an employment history
    """

    # Get employment history
    history = cast(
        models.EmploymentHistory,
        await selectors.get_employment_history_by_id(id=history_id, db=db),
    )

    # Delete employment history
    history.is_deleted = encrypt_man.encrypt_boolean(True)  # type: ignore
    history.deleted_at = encrypt_man.encrypt_datetime(datetime.now())  # type: ignore
    db.commit()

    # Create logs
    await create_log(
        user=curr_user,
        resource="employment-history",
        action=f"delete:{history.id}",
        db=db,
    )

    return {}


#########################################################################
# VETERAN STATUS
#########################################################################
@router.get(
    "/{poi_id}/vetstatus",
    summary="Get POI Veteran Status",
    response_description="The poi's veteran status",
    status_code=status.HTTP_200_OK,
    response_model=response.VeteranStatusResponse,
    tags=[tags.POI_VETERAN_STATUS],
)
async def route_poi_veteran_status_get(
    poi_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint the poi's veteran status
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create logs
    await create_log(
        user=curr_user,
        resource="veteran-status",
        action=f"get-list:{poi.id}",
        db=db,
    )

    return {
        "data": await format_veteran_status(
            status=await selectors.get_veteran_status_by_poi(poi=poi, db=db)
        )
    }


@router.put(
    "/{poi_id}/vetstatus",
    summary="Edit POI Veteran Status",
    response_description="The POI's veteran status details",
    status_code=status.HTTP_200_OK,
    response_model=response.VeteranStatusResponse,
    tags=[tags.POI_VETERAN_STATUS],
)
async def route_poi_veteran_status_edit(
    poi_id: int,
    status_in: edit.VeteranStatusEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint edits a poi's veteran status
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Get veteran status
    vet_status = cast(
        models.VeteranStatus, await selectors.get_veteran_status_by_poi(poi=poi, db=db)
    )

    # Edit veteran status
    new_vet_status = await services.edit_veteran_status(
        user=curr_user, status=vet_status, data=status_in, db=db
    )

    return {"data": await format_veteran_status(status=new_vet_status)}


#########################################################################
# EDUCATIONAL BACKGROUND
#########################################################################
@router.post(
    "/{poi_id}/education",
    summary="Add POI Educational Background",
    response_description="The details of the educational background",
    status_code=status.HTTP_201_CREATED,
    response_model=response.EducationalBackgroundResponse,
    tags=[tags.POI_EDUCATIONAL_BACKGROUND],
)
async def route_poi_education_create(
    poi_id: int,
    education_in: create.CreateEducationalBackground,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint creates an educational background
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create educational background
    education = await services.create_educational_background(
        user=curr_user, poi=poi, data=education_in, db=db
    )

    return {"data": await format_educational_background(education=education)}


@router.get(
    "/{poi_id}/education",
    summary="Get POI Educational Background",
    response_description="The list of the poi's educational background",
    status_code=status.HTTP_200_OK,
    response_model=response.EducationalBackgroundListResponse,
    tags=[tags.POI_EDUCATIONAL_BACKGROUND],
)
async def route_poi_education_list(
    poi_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint returns the poi's educational background
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create logs
    await create_log(
        user=curr_user,
        resource="educational-background",
        action=f"get-list:{poi.id}",
        db=db,
    )

    return {
        "data": [
            await format_educational_background(education=education)
            for education in await selectors.get_educational_background(poi=poi, db=db)
        ]
    }


@router.put(
    "/education/{education_id}/",
    summary="Edit POI Educational Background",
    response_description="The details of the educational background",
    status_code=status.HTTP_200_OK,
    response_model=response.EducationalBackgroundResponse,
    tags=[tags.POI_EDUCATIONAL_BACKGROUND],
)
async def route_poi_education_edit(
    education_id: int,
    education_in: edit.EducationalBackgroundEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint edits the poi's education background
    """

    # Get educational background
    education = cast(
        models.EducationalBackground,
        await selectors.get_educational_background_by_id(id=education_id, db=db),
    )

    # Edit educational background
    new_education = await services.edit_educational_background(
        user=curr_user, education=education, data=education_in, db=db
    )

    return {"data": await format_educational_background(education=new_education)}


@router.delete(
    "/education/{education_id}/",
    summary="Delete educational background",
    response_description="Educational background deleted successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.EducationalBackgroundDeleteResponse,
    tags=[tags.POI_EDUCATIONAL_BACKGROUND],
)
async def route_poi_education_delete(
    education_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint deletes an educational background
    """

    # Get educational background
    education = cast(
        models.EducationalBackground,
        await selectors.get_educational_background_by_id(id=education_id, db=db),
    )

    # Delete educational background
    education.is_deleted = encrypt_man.encrypt_boolean(True)  # type: ignore
    education.deleted_at = encrypt_man.encrypt_datetime(datetime.now())  # type: ignore
    db.commit()

    # Create logs
    await create_log(
        user=curr_user,
        resource="educational-background",
        action=f"delete:{education.id}",
        db=db,
    )

    return {}


#########################################################################
# POI OFFENSE
#########################################################################
@router.post(
    "/{poi_id}/conviction",
    summary="Add POI Offense",
    response_description="The details of the poi offense",
    status_code=status.HTTP_201_CREATED,
    response_model=response.POIOffenseResponse,
    tags=[tags.POI_CONVICTION],
)
async def route_poi_conviction_create(
    poi_id: int,
    offense_in: create.POIOffenseCreate,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint creates a poi offense
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Get offense
    offense = cast(
        models.Offense,
        await selectors.get_offense_by_id(id=offense_in.offense_id, db=db),
    )

    # Create offense
    poi_offense = await services.create_poi_offense(
        user=curr_user, poi=poi, offense=offense, data=offense_in, db=db
    )

    return {"data": await format_poi_offense(conv=poi_offense)}


@router.get(
    "/{poi_id}/conviction",
    summary="Get POI Offenses",
    response_description="The list of the poi's offenses",
    status_code=status.HTTP_200_OK,
    response_model=response.POIOffenseListResponse,
    tags=[tags.POI_CONVICTION],
)
async def route_poi_conviction_list(
    poi_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint returns the list of the poi's offenses
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create logs
    await create_log(
        user=curr_user,
        resource="poi-offense",
        action=f"get-list:{poi.id}",
        db=db,
    )

    return {
        "data": [
            await format_poi_offense(conv=conv)
            for conv in await selectors.get_poi_offenses(poi=poi, db=db)
        ]
    }


@router.put(
    "/conviction/{poi_offense_id}/",
    summary="Edit POI Offense",
    response_description="The new details of the poi offense",
    status_code=status.HTTP_200_OK,
    response_model=response.POIOffenseResponse,
    tags=[tags.POI_CONVICTION],
)
async def route_poi_conviction_edit(
    poi_offense_id: int,
    offense_in: edit.POIOffenseEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint edits the poi offense
    """

    # Get poi offense
    poi_offense = cast(
        models.POIOffense,
        await selectors.get_poi_offense_by_id(id=poi_offense_id, db=db),
    )

    # Edit poi offense
    new_poi_offense = await services.edit_poi_offense(
        user=curr_user, poi_offense=poi_offense, data=offense_in, db=db
    )

    return {"data": await format_poi_offense(conv=new_poi_offense)}


@router.delete(
    "/conviction/{poi_offense_id}/",
    summary="Delete POI Offense",
    response_description="POI Offense deleted successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.POIOffenseDeleteResponse,
    tags=[tags.POI_CONVICTION],
)
async def route_poi_conviction_delete(
    poi_offense_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint deletes a poi offense
    """

    # Get poi offense
    poi_offense = cast(
        models.POIOffense,
        await selectors.get_poi_offense_by_id(id=poi_offense_id, db=db),
    )

    # Delete poi offense
    poi_offense.is_deleted = encrypt_man.encrypt_boolean(True)  # type: ignore
    poi_offense.deleted_at = encrypt_man.encrypt_datetime(datetime.now())  # type: ignore
    db.commit()

    # Create logs
    await create_log(
        user=curr_user,
        resource="poi-offense",
        action=f"delete:{poi_offense.id}",
        db=db,
    )

    return {}


#########################################################################
# FREQUENTED SPOTS
#########################################################################
@router.post(
    "/{poi_id}/spot",
    summary="Add POI Frequented Spot",
    response_description="The details of the poi's frequented spot",
    status_code=status.HTTP_201_CREATED,
    response_model=response.FrequentedSpotResponse,
    tags=[tags.POI_FREQUENTED_SPOT],
)
async def route_poi_spot_create(
    poi_id: int,
    spot_in: create.CreateFrequentedSpot,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint creates a poi frequented spot
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create spot
    spot = await services.create_frequented_spot(
        user=curr_user, poi=poi, data=spot_in, db=db
    )

    return {"data": await format_frequented_spot(spot=spot)}


@router.get(
    "/{poi_id}/spot",
    summary="Get POI Frequented Spots",
    response_description="The list of the poi's frequented spots",
    status_code=status.HTTP_200_OK,
    response_model=response.FrequentedSpotListResponse,
    tags=[tags.POI_FREQUENTED_SPOT],
)
async def route_poi_spot_list(poi_id: int, curr_user: CurrentUser, db: DatabaseSession):
    """
    This endpoint returns the poi's frequented spots
    """

    # Get poi
    poi = cast(models.POI, await selectors.get_poi_by_id(id=poi_id, db=db))

    # Create logs
    await create_log(
        user=curr_user,
        resource="frequented-spot",
        action=f"get-list:{poi.id}",
        db=db,
    )

    return {
        "data": [
            await format_frequented_spot(spot=spot)
            for spot in await selectors.get_frequented_spots(poi=poi, db=db)
        ]
    }


@router.put(
    "/spot/{spot_id}/",
    summary="Edit Frequented Spot",
    response_description="The new details of the frequented spot",
    status_code=status.HTTP_200_OK,
    response_model=response.FrequentedSpotResponse,
    tags=[tags.POI_FREQUENTED_SPOT],
)
async def route_poi_spot_edit(
    spot_id: int,
    spot_in: edit.FrequentedSpotEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint edits a frequented spot
    """

    # Get frequented spot
    spot = cast(
        models.FrequentedSpot,
        await selectors.get_frequented_spot_by_id(id=spot_id, db=db),
    )

    # Edit frequented spot
    new_spot = await services.edit_frequented_spot(
        user=curr_user, spot=spot, data=spot_in, db=db
    )

    return {"data": await format_frequented_spot(spot=new_spot)}


@router.delete(
    "/spot/{spot_id}/",
    summary="Delete Frequented Spot",
    response_description="Frequented spot deleted successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.FrequentedSpotDeleteResponse,
    tags=[tags.POI_FREQUENTED_SPOT],
)
async def route_poi_spot_delete(
    spot_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint deletes a frequented spot
    """

    # Get frequented spot
    spot = cast(
        models.FrequentedSpot,
        await selectors.get_frequented_spot_by_id(id=spot_id, db=db),
    )

    # Delete frequented spot
    spot.is_deleted = encrypt_man.encrypt_boolean(True)  # type: ignore
    spot.deleted_at = encrypt_man.encrypt_datetime(datetime.now())  # type: ignore
    db.commit()

    # Create logs
    await create_log(
        user=curr_user,
        resource="frequented-spot",
        action=f"delete:{spot.id}",
        db=db,
    )

    return {}
