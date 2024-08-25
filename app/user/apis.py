from fastapi import APIRouter, status

from app.common.annotations import DatabaseSession
from app.common.auth import TokenGenerator
from app.user import services
from app.user.schemas import base, response
from app.core.settings import get_settings

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
async def route_user_dashboard():
    """
    This endpoint returns the user's dashboard details
    """
