from pydantic import BaseModel, Field

from app.poi.schemas import base as bps


class Token(BaseModel):
    """
    Base schema for user access tokens
    """

    token: str = Field(description="The user's access token")


class UserLoginCredential(BaseModel):
    """
    Base schema for user login credentials
    """

    badge_num: str = Field(min_length=1, description="The user's badge number")
    password: str = Field(min_length=1, description="The user's password")


class UserDashboard(BaseModel):
    """
    Base schema for the user's dashboard
    """

    statistics: bps.POIStatistics = Field(description="The poi statistics")
    pinned_pois: list[bps.POISummary] = Field(description="The pinned poi's")
    recently_added_pois: list[bps.POISummary] = Field(
        max_length=10, description="The last 10 added pois"
    )
