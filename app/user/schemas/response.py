from pydantic import Field

from app.common.schemas import ResponseSchema
from app.user.schemas.base import Token, UserDashboard


class LoginResponse(ResponseSchema):
    """
    Response schema for user login
    """

    msg: str = Field(default="User successfully logged in")
    data: Token = Field(description="The user's access token")


class UserDashboardResponse(ResponseSchema):
    """
    Response schema for user dashboard
    """

    msg: str = Field(default="User dashboard request successful")
    data: UserDashboard = Field(description="The user's dashboard details")
