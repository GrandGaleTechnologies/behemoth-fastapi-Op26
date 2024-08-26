from pydantic import Field

from app.common.schemas import PaginatedResponseSchema, ResponseSchema
from app.poi.schemas.base import Offense, POIApplicationProcess, POIBaseInformation


class OffenseResponse(ResponseSchema):
    """
    Response schema for offenses
    """

    msg: str = Field(default="Offense retrieved successfully")
    data: Offense = Field(description="The details of the offense")


class OffenseDeleteResponse(ResponseSchema):
    """
    Response schema for offense deletes
    """

    msg: str = Field(default="Offense deleted successfully")
    data: None = None


class PaginatedOffenseListResponse(PaginatedResponseSchema):
    """
    Paginated response schema for offense list
    """

    msg: str = Field(default="Successfully retrieved offenses")
    data: list[Offense] = Field(description="The list of offenses")


class POIApplicationProcessResponse(ResponseSchema):
    """
    Response schema for poi application process
    """

    msg: str = Field(default="Succesfully retreieved poi application process")
    data: POIApplicationProcess = Field(
        description="The detais of the application process"
    )


class POIBaseInformationResponse(ResponseSchema):
    """
    Response schema for poi's
    """

    msg: str = Field(default="POI successfully retreieved")
    data: POIBaseInformation = Field(description="The details of the poi")
