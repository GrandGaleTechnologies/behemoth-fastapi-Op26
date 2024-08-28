from typing import cast

from fastapi import APIRouter, status

from app.common.annotations import DatabaseSession
from app.common.exceptions import NotFound
from app.poi import models, selectors, services
from app.poi.formatters import format_poi_application, format_poi_base
from app.poi.routes.offense import router as poi_offense_router
from app.poi.schemas import create, edit, response
from app.user.annotated import CurrentUser
from app.user.services import create_log

router = APIRouter()

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
