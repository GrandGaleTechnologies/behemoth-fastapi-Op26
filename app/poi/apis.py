from datetime import datetime
from typing import cast

from fastapi import APIRouter, status

from app.common.annotations import DatabaseSession
from app.common.encryption import EncryptionManager
from app.common.exceptions import NotFound
from app.core.settings import get_settings
from app.poi import models, selectors, services
from app.poi.formatters import (
    format_id_document,
    format_poi_application,
    format_poi_base,
)
from app.poi.routes.offense import router as poi_offense_router
from app.poi.schemas import create, edit, response
from app.user.annotated import CurrentUser
from app.user.services import create_log

# Globals
router = APIRouter()
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
    poi_in: create.POIBaseInformationCreate,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint creates a poi
    """

    # Create poi base information
    poi = await services.create_poi(user=curr_user, data=poi_in, db=db)

    # Start application process
    await services.create_poi_application_process(poi=poi, db=db)

    return {"data": await format_poi_base(poi=poi)}


@router.put(
    "/{poi_id}/base",
    summary="Edit POI Base information",
    response_description="The poi's edited base information",
    status_code=status.HTTP_200_OK,
    response_model=response.POIBaseInformationResponse,
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
