from datetime import date, time

from pydantic import BaseModel, Field


class CreateOffense(BaseModel):
    """
    Create schema for offenses
    """

    name: str = Field(description="Name of the offense")
    description: str = Field(description="Description of the offense")


class POICreate(BaseModel):
    """
    Create schema for POI
    """

    # Basic Information
    pfp: str | None = Field(default=None, description="Profile picture URL")
    full_name: str = Field(description="Full name of the POI")
    alias: str = Field(description="Alias of the POI")
    dob: date | None = Field(default=None, description="Date of birth")
    state_of_origin: str | None = Field(default=None, description="The state of origin")
    lga_of_origin: str | None = Field(default=None, description="The lga of the poi")
    district_of_origin: str | None = Field(
        default=None, description="The district of the poi"
    )
    pob: str | None = Field(default=None, description="Place of birth")
    nationality: str | None = Field(default=None, description="Nationality")
    religion: str | None = Field(default=None, description="Religion")
    political_affiliation: str | None = Field(
        default=None, description="Political affiliation"
    )
    tribal_union: str | None = Field(default=None, description="Tribal union")
    last_seen_date: date | None = Field(default=None, description="Last seen date")
    last_seen_time: time | None = Field(default=None, description="Last seen time")
    notes: str | None = Field(default=None, description="additional notes on the poi")
    id_documents: list["CreateIDDocument"] | None = Field(
        default=None, description="The list of ID Documents"
    )

    gsm_numbers: list["CreateGSMNumber"] | None = Field(
        default=None, description="The list of the poi's gsm numbers"
    )
    residential_addresses: list["CreateResidentialAddress"] | None = Field(
        default=None, description="The poi's residential addresses"
    )
    known_associates: list["CreateKnownAssociate"] | None = Field(
        default=None, description="The list of the poi's known associates"
    )

    # Employment history
    employment_history: list["CreateEmploymentHistory"] | None = Field(
        default=None, description="The poi's employment history"
    )

    # Veteran Status
    veteran_status: "CreateVeteranStatus" = Field(
        description="The poi's veteran status"
    )

    # Educational Background
    educational_background: list["CreateEducationalBackground"] | None = Field(
        default=None, description="The poi's educational background"
    )

    # Case report
    convictions: list["POIOffenseCreate"] | None = Field(
        default=None, description="The poi's convictions"
    )
    frequented_spots: list["CreateFrequentedSpot"] | None = Field(
        default=None, description="The poi's frequented spots"
    )

    # # Fingerprint
    # fingerprints: "CreateFingerprint" = Field(description="The poi's fingerprints")


class CreatePOIBaseInformation(BaseModel):
    """
    Create schema for poi base information
    """

    # Basic Information
    pfp: str | None = Field(default=None, description="Profile picture URL")
    full_name: str = Field(description="Full name of the POI")
    alias: str = Field(description="Alias of the POI")
    dob: date | None = Field(default=None, description="Date of birth")
    state_of_origin: str | None = Field(default=None, description="The state of origin")
    lga_of_origin: str | None = Field(default=None, description="The lga of the poi")
    district_of_origin: str | None = Field(
        default=None, description="The district of the poi"
    )
    pob: str | None = Field(default=None, description="Place of birth")
    nationality: str | None = Field(default=None, description="Nationality")
    religion: str | None = Field(default=None, description="Religion")
    political_affiliation: str | None = Field(
        default=None, description="Political affiliation"
    )
    tribal_union: str | None = Field(default=None, description="Tribal union")
    last_seen_date: date | None = Field(default=None, description="Last seen date")
    last_seen_time: time | None = Field(default=None, description="Last seen time")
    notes: str | None = Field(default=None, description="additional notes on the poi")
    id_documents: list["CreateIDDocument"] | None = Field(
        default=None, description="The list of ID Documents"
    )


class CreateIDDocument(BaseModel):
    """
    Create schema for ID Documents
    """

    type: str = Field(description="Type of ID document")
    id_number: str = Field(description="ID number")


class CreateGSMNumber(BaseModel):
    """
    Create schema for GSM Numbers
    """

    service_provider: str = Field(description="Service provider name")
    number: str = Field(description="GSM number")
    last_call_date: date | None = Field(default=None, description="Last call date")
    last_call_time: time | None = Field(default=None, description="Last call time")


class CreateResidentialAddress(BaseModel):
    """
    Create schema for poi residential addresses
    """

    country: str = Field(description="Country of the address")
    state: str = Field(description="State of the address")
    city: str = Field(description="City of the address")
    address: str | None = Field(default=None, description="Street address")


class CreateKnownAssociate(BaseModel):
    """
    Create schema for known poi associates
    """

    full_name: str = Field(description="Full name of the associate")
    known_gsm_numbers: str | None = Field(default=None, description="Known GSM numbers")
    relationship: str = Field(description="Relationship with the POI")
    occupation: str | None = Field(default=None, description="Occupation")
    residential_address: str | None = Field(
        default=None, description="Residential address"
    )
    last_seen_date: date | None = Field(default=None, description="Last seen date")
    last_seen_time: time | None = Field(default=None, description="Last seen time")


class CreateEmploymentHistory(BaseModel):
    """
    Create schema for poi employment histories
    """

    company: str = Field(description="Company name")
    employment_type: str = Field(description="Type of employment")
    from_date: date | None = Field(default=None, description="Employment start date")
    to_date: date | None = Field(default=None, description="Employment end date")
    current_job: bool = Field(description="Is this the current job")
    description: str | None = Field(default=None, description="Job description")


class CreateVeteranStatus(BaseModel):
    """
    Create schema for poi veteran status
    """

    is_veteran: bool = Field(description="Is the POI a veteran")
    section: str = Field(description="Section or unit")
    location: str = Field(description="Location of service")
    id_card: str | None = Field(default=None, description="ID card")
    id_card_issuer: str | None = Field(default=None, description="ID card issuer")
    from_date: date | None = Field(default=None, description="Service start date")
    to_date: date | None = Field(default=None, description="Service end date")
    notes: str | None = Field(default=None, description="Additional notes")


class CreateEducationalBackground(BaseModel):
    """
    Create schema for poi educational background
    """

    type: str = Field(description="Type of education")
    institute_name: str = Field(description="Name of the institute")
    country: str = Field(description="Country of the institute")
    state: str = Field(description="State of the institute")
    from_date: date | None = Field(default=None, description="Start date of education")
    to_date: date | None = Field(default=None, description="End date of education")
    current_institute: bool = Field(description="Is this the current institute")


class POIOffenseCreate(BaseModel):
    """
    Create schema for poi offenses
    """

    offense_id: int = Field(description="The ID of the offense")
    case_id: str | None = Field(default=None, description="The id of the case")
    date_convicted: date | None = Field(
        default=None, description="The date the poi was convicted"
    )
    notes: str | None = Field(default=None, description="Notes on the conviction")


class CreateFrequentedSpot(BaseModel):
    """
    Create schema for poi frequented spots
    """

    country: str = Field(description="Country of the spot")
    state: str = Field(description="State of the spot")
    lga: str = Field(description="Local Government Area (LGA) of the spot")
    address: str = Field(description="Address of the spot")
    from_date: date | None = Field(
        default=None, description="Start date of frequenting this spot"
    )
    to_date: date | None = Field(
        default=None, description="End date of frequenting this spot"
    )
    notes: str | None = Field(None, description="Additional notes")


class CreateFingerprint(BaseModel):
    """
    Create schema for POI fingerprints
    """

    left_thumb: str = Field(description="Left thumb fingerprint data")
    right_thumb: str = Field(description="Right thumb fingerprint data")
    left_pointer: str = Field(description="Left pointer finger fingerprint data")
    right_pointer: str = Field(description="Right pointer finger fingerprint data")
