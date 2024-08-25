from fastapi import APIRouter, status

from app.common.annotations import DatabaseSession, PaginationParams
from app.common.paginators import get_pagination_metadata
from app.poi import selectors, services
from app.poi.formatters import format_offense
from app.poi.schemas import create, edit, response
from app.user import services as user_services
from app.user.annotated import CurrentUser

router = APIRouter()


@router.post(
    "",
    summary="Create offense",
    response_description="The details of the offense",
    status_code=status.HTTP_201_CREATED,
    response_model=response.OffenseResponse,
)
async def route_poi_offense_create(
    offense_in: create.CreateOffense, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint creates a new offense
    """

    offense = await services.create_offense(user=curr_user, data=offense_in, db=db)

    return {"data": await format_offense(offense=offense)}


@router.get(
    "",
    summary="Get List of Offenses",
    response_description="The paginated list of offenses",
    status_code=status.HTTP_200_OK,
    response_model=response.PaginatedOffenseListResponse,
)
async def route_poi_offense_list(
    pagination: PaginationParams, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint returns the paginated list of offenses
    """
    # Create log
    await user_services.create_log(
        user=curr_user,
        resource="offenses",
        action="get-paginated-list",
        notes=pagination.q,
        db=db,
    )

    # get offenses
    offenses, tnoi = await selectors.get_paginated_offense_list(
        pagination=pagination, db=db
    )

    return {
        "data": [await format_offense(offense=offense) for offense in offenses],
        "meta": get_pagination_metadata(
            tno_items=tnoi,
            count=len(offenses),
            page=pagination.page,
            size=pagination.size,
        ),
    }


@router.get(
    "/{offense_id}/",
    summary="Get offense details",
    response_description="The details of the offense",
    status_code=status.HTTP_200_OK,
    response_model=response.OffenseResponse,
)
async def route_poi_offense_details(
    offense_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint returns the details of an offense
    """
    # Create log
    await user_services.create_log(
        user=curr_user,
        resource="offenses",
        action="get-offense",
        notes=str(offense_id),
        db=db,
    )

    # Get offense
    offense = await selectors.get_offense_by_id(id=offense_id, db=db)

    return {"data": await format_offense(offense=offense)}


@router.put(
    "/{offense_id}/",
    summary="Edit Offense",
    response_description="The details of the edited offense",
    status_code=status.HTTP_200_OK,
    response_model=response.OffenseResponse,
)
async def route_poi_offense_edit(
    offense_id: int,
    offense_in: edit.OffenseEdit,
    curr_user: CurrentUser,
    db: DatabaseSession,
):
    """
    This endpoint edits the details of an offense
    """

    # Get offense
    offense = await selectors.get_offense_by_id(id=offense_id, db=db)

    # Edit offense
    editted_offense = await services.edit_offense(
        user=curr_user, offense=offense, data=offense_in, db=db
    )

    return {"data": await format_offense(offense=editted_offense)}


@router.delete(
    "/{offense_id}/",
    summary="Delete offense",
    response_description="Offense deleted successfully",
    status_code=status.HTTP_200_OK,
    response_model=response.OffenseDeleteResponse,
)
async def route_poi_offense_delete(
    offense_id: int, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint deletes an offense
    """
    # Create log
    await user_services.create_log(
        user=curr_user,
        resource="offenses",
        action="delete",
        notes=str(offense_id),
        db=db,
    )

    # Get offense
    offense = await selectors.get_offense_by_id(id=offense_id, db=db)

    # Delete offense
    db.delete(offense)
    db.commit()

    return {}
