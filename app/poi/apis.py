from fastapi import APIRouter, status

from app.common.annotations import DatabaseSession
from app.poi import services
from app.poi.formatters import format_poi_base
from app.poi.routes.offense import router as poi_offense_router
from app.poi.schemas import create, response
from app.user.annotated import CurrentUser

router = APIRouter()

# Include routers
router.include_router(poi_offense_router, prefix="/offense", tags=["Offense Endpoints"])


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

    return {"data": await format_poi_base(poi=poi)}
