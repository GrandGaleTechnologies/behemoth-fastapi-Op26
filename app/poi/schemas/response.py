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
    POIBaseInformation,
    POIOffense,
    POIOtherInformation,
    POISummary,
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


class POIPinResponse(ResponseSchema):
    """
    Response schema for poi pin
    """

    msg: str = Field(default="Succesfully Pinned/Unpinned poi")
    data: None = None


class POIDeleteRequestResponse(ResponseSchema):
    """
    Response schema for poi delete
    """

    msg: str = Field(default="Succesfully Deleted Poi")
    data: None = None


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


class PaginatedPOISummaryListResponse(PaginatedResponseSchema):
    """
    Response schema for pagianted poi list response
    """

    msg: str = Field(default="POIs retreieved successfully")
    data: list[POISummary] = Field(description="The poi's other profile info")


class IDDocumentResponse(ResponseSchema):
    """
    Response schema for id documents
    """

    msg: str = Field(default="ID Document retrieved successfully")
    data: IDDocument = Field(description="The details of the ID Document")


class IDDocumentListResponse(ResponseSchema):
    """
    Response schema for id document list
    """

    msg: str = Field(default="ID Documents retrieved successfully")
    data: list[IDDocument] = Field(description="The details of the ID Document")


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


class GSMNumberListResponse(ResponseSchema):
    """
    Response schema for poi gsm numbers
    """

    msg: str = Field(default="GSM Numbers retrieved successfully")
    data: list[GSMNumber] = Field(description="The list of gsm numbers")


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


class ResidentialAddressListResponse(ResponseSchema):
    """
    Response schema for poi residential address list
    """

    msg: str = Field(default="Residential addresses retreived successfully")
    data: list[ResidentialAddress] = Field(
        description="The details of the residential addresses"
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


class KnownAssociateListResponse(ResponseSchema):
    """
    Response schema for poi known associates responses
    """

    msg: str = Field(default="Known associates retreived successfully")
    data: list[KnownAssociate] = Field(
        description="The details of the poi's known associates"
    )


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


class EmploymentHistoryListResponse(ResponseSchema):
    """
    Response schema for poi employment history responses
    """

    msg: str = Field(default="POI Employment history retreived successfully")
    data: list[EmploymentHistory] = Field(
        description="The details of the poi's employment history"
    )


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


class EducationalBackgroundListResponse(ResponseSchema):
    """
    Response schema for the poi's educational background responses
    """

    msg: str = Field(default="POI educational background retreived successfully")
    data: list[EducationalBackground] = Field(
        description="The poi's educational background"
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


class POIOffenseListResponse(ResponseSchema):
    """
    Response schema for poi offense list responses
    """

    msg: str = Field(default="POI offenses retreived successfully")
    data: list[POIOffense] = Field(
        description="The details of the poi offenses conviction"
    )


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


class FrequentedSpotListResponse(ResponseSchema):
    """
    Response schema for poi frequented spot list responses
    """

    msg: str = Field(default="POI Frequented spots retreived successfully")
    data: list[FrequentedSpot] = Field(
        description="The details of the poi's frequented spots"
    )


class FrequentedSpotDeleteResponse(ResponseSchema):
    """
    Response schema for frequented spot delete request
    """

    msg: str = Field(default="Frequented spot deleted successfully")
    data: None = None
