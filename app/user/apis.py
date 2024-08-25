from fastapi import APIRouter, status

from app.common.annotations import DatabaseSession
from app.common.auth import TokenGenerator
from app.core.settings import get_settings
from app.poi import selectors as poi_selectors
from app.user import services
from app.user.annotated import CurrentUser
from app.user.schemas import base, response

router = APIRouter()


# Globals
settings = get_settings()
token_generator = TokenGenerator(
    secret_key=settings.SECRET_KEY, expire_in=settings.ACCESS_TOKEN_EXPIRE_MIN
)


@router.post(
    "/login",
    summary="Login User",
    response_description="The user's access token",
    status_code=status.HTTP_200_OK,
    response_model=response.LoginResponse,
)
async def route_user_login(
    credentials_in: base.UserLoginCredential, db: DatabaseSession
):
    """
    This endpoint logs in the user
    """

    # Login user
    user = await services.login_user(credential=credentials_in, db=db)

    # Generate access token
    token = await token_generator.generate(sub=f"USER-{user.badge_num}")

    return {"data": {"token": token}}


@router.get(
    "/dashboard",
    summary="The user's dashboard",
    response_description="The user's dashboard details",
    status_code=status.HTTP_200_OK,
    response_model=response.UserDashboardResponse,
)
async def route_user_dashboard(_: CurrentUser, db: DatabaseSession):
    """
    This endpoint returns the user's dashboard details
    """

    # return {
    #     "statistics": await poi_selectors.get_poi_statistics(db=db),
    #     "pinned_pois": await poi_selectors.get_pinned_pois(db=db),
    #     "recently_added_pois": await poi_selectors.get_recently_added_pois(db=db),
    # }
    return {
        "data": {
            "statistics": {
                "tno_pois": 463,
                "tno_pois_last_month": 33,
                "tno_pois_curr_month": 25,
                "poi_report_conviction": [
                    {"offense": "Robbery", "value": 50},
                    {"offense": "Arson", "value": 40},
                    {"offense": "Murder", "value": 30},
                    {"offense": "Homicide", "value": 20},
                ],
                "poi_report_age": [
                    {"range": "18-25", "value": 100},
                    {"range": "26-35", "value": 80},
                    {"range": "36-50", "value": 60},
                    {"range": "50+", "value": 40},
                ],
            },
            "pinned_pois": [],
            "recently_added_pois": [],
        }
    }
