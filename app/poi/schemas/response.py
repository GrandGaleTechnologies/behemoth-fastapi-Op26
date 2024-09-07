from pydantic import Field

from app.common.schemas import PaginatedResponseSchema, ResponseSchema
from app.poi.schemas.base import (
    EducationalBackground,
    EmploymentHistory,
    FrequentedSpot,
    GSMNumber,
    IDDocument,
    KnownAssociate,
    Offense,
    POIApplicationProcess,
    POIBaseInformation,
    POIOffense,
    POIOtherInformation,
    ResidentialAddress,
    VeteranStatus,
)


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


class POIOtherInformationResponse(ResponseSchema):
    """
    Response schema for poi other profile info
    """

    msg: str = Field(default="POI other profile retreieved successfully")
    data: POIOtherInformation = Field(description="The poi's other profile info")


class IDDocumentResponse(ResponseSchema):
    """
    Response schema for id documents
    """

    msg: str = Field(default="ID Document retrieved successfully")
    data: IDDocument = Field(description="The details of the ID Document")


class IDDocumentDeleteResponse(ResponseSchema):
    """
    Response schema for id document delete request
    """

    msg: str = Field(default="ID Document deleted successfully")
    data: None = None


class GSMNumberResponse(ResponseSchema):
    """
    Response schema for poi gsm number
    """

    msg: str = Field(default="GSM retrieved successfully")
    data: GSMNumber = Field(description="The details of the gsm number")


class GSMNumberDeleteResponse(ResponseSchema):
    """
    Response schema for gsm number delete requests
    """

    msg: str = Field(default="GSM Number deleted successfully")
    data: None = None


class ResidentialAddressResponse(ResponseSchema):
    """
    Response schema for poi residential address
    """

    msg: str = Field(default="Residential address retreived successfully")
    data: ResidentialAddress = Field(
        description="The details of the residential address"
    )


class ResidentialAddressDeleteResponse(ResponseSchema):
    """
    Response schema for residential address delete requests
    """

    msg: str = Field(default="Residential address deleted successfully")
    data: None = None


class KnownAssociateResponse(ResponseSchema):
    """
    Response schema for known associates responses
    """

    msg: str = Field(default="Known associate retreived successfully")
    data: KnownAssociate = Field(description="The details of the known associate")


class KnownAssociateDeleteResponse(ResponseSchema):
    """
    Response schema for known associate delete request
    """

    msg: str = Field(default="Known associate deleted successfully")
    data: None = None


class EmploymentHistoryResponse(ResponseSchema):
    """
    Response schema for employment history responses
    """

    msg: str = Field(default="Employment history retreived successfully")
    data: EmploymentHistory = Field(description="The details of the employment history")


class EmploymentHistoryDeleteResponse(ResponseSchema):
    """
    Response schema for employment history delete request
    """

    msg: str = Field(default="Employment history deleted successfully")
    data: None = None


class VeteranStatusResponse(ResponseSchema):
    """
    Response schema for poi veteran status
    """

    msg: str = Field(default="Veteran status retreieved successfully")
    data: VeteranStatus = Field(description="The details of the poi's veteran status")


class EducationalBackgroundResponse(ResponseSchema):
    """
    Response schema for educational background responses
    """

    msg: str = Field(default="Educational background retreived successfully")
    data: EducationalBackground = Field(
        description="The details of the educational background"
    )


class EducationalBackgroundDeleteResponse(ResponseSchema):
    """
    Response schema for educational background delete request
    """

    msg: str = Field(default="Educational background deleted successfully")
    data: None = None


class POIOffenseResponse(ResponseSchema):
    """
    Response schema for poi offense responses
    """

    msg: str = Field(default="POI offense retreived successfully")
    data: POIOffense = Field(description="The details of the poi offense conviction")


class POIOffenseDeleteResponse(ResponseSchema):
    """
    Response schema for poi offense delete request
    """

    msg: str = Field(default="POI offense deleted successfully")
    data: None = None


class FrequentedSpotResponse(ResponseSchema):
    """
    Response schema for poi frequented spot responses
    """

    msg: str = Field(default="Frequented spot retreived successfully")
    data: FrequentedSpot = Field(description="The details of the frequented spot")


class FrequentedSpotDeleteResponse(ResponseSchema):
    """
    Response schema for frequented spot delete request
    """

    msg: str = Field(default="Frequented spot deleted successfully")
    data: None = None
