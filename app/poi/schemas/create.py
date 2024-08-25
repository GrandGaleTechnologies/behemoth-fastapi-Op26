from datetime import date, datetime, time
from pydantic import BaseModel, Field


class CreateOffense(BaseModel):
    """
    Create schema for offenses
    """

    id: int = Field(description="Unique identifier for the offense")
    name: str = Field(description="Name of the offense")
    description: str = Field(description="Description of the offense")
    created_at: datetime = Field(description="Creation timestamp")


class CreatePOI(BaseModel):
    """
    Create schema for POI's
    """

    # Basic Information
    pfp: bytes | None = Field(default=None, description="Profile picture URL")
    full_name: str = Field(description="Full name of the POI")
    alias: str = Field(description="Alias of the POI")
    dob: date | None = Field(default=None, description="Date of birth")
    pob: str | None = Field(default=None, description="Place of birth")
    nationality: str | None = Field(default=None, description="Nationality")
    religion: str | None = Field(default=None, description="Religion")
    id_documents: list["CreateIDDocument"] | None = Field(
        default=None, description="The list of ID Documents"
    )

    # Other Profiles
    email_addresses: str | None = Field(
        default=None, description="The list of the known poi email addresses"
    )
    political_affiliation: str | None = Field(
        default=None, description="Political affiliation"
    )
    tribal_union: str | None = Field(default=None, description="Tribal union")
    last_seen_date: date | None = Field(default=None, description="Last seen date")
    last_seen_time: time | None = Field(default=None, description="Last seen time")
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
    veteran_status: list["CreateVeteranStatus"] = Field(
        description="The poi's veteran status"
    )

    # Educational Background
    educational_background: list["CreateEducationalBackground"] | None = Field(
        default=None, description="The poi's educational background"
    )

    # Case report
    convictions: list["CreateOffense"] | None = Field(
        default=None, description="The poi's convictions"
    )
    frequented_spots: list["CreateFrequentedSpot"] | None = Field(
        default=None, description="The poi's frequented spots"
    )

    # Notes
    notes: str | None = Field(default=None, description="additional notes on the poi")

    # Fingerprint
    fingerprints: "CreateFingerprint" = Field(description="The poi's fingerprints")


class CreateIDDocument(BaseModel):
    """
    Create schema for ID Documents
    """

    id: int = Field(description="Unique identifier for the ID document")
    type: str = Field(description="Type of ID document")
    id_number: str = Field(description="ID number")


class CreateGSMNumber(BaseModel):
    """
    Create schema for GSM Numbers
    """

    id: int = Field(description="Unique identifier for the GSM number")
    service_provider: str = Field(description="Service provider name")
    number: str = Field(description="GSM number")
    last_call_date: date | None = Field(default=None, description="Last call date")
    last_call_time: time | None = Field(default=None, description="Last call time")


class CreateResidentialAddress(BaseModel):
    """
    Create schema for poi residential addresses
    """

    id: int = Field(description="Unique identifier for the address")
    country: str = Field(description="Country of the address")
    state: str = Field(description="State of the address")
    city: str = Field(description="City of the address")
    address: str | None = Field(default=None, description="Street address")


class CreateKnownAssociate(BaseModel):
    """
    Create schema for known poi associates
    """

    id: int = Field(description="Unique identifier for the associate")
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

    id: int = Field(description="Unique identifier for employment history")
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

    id: int = Field(description="Unique identifier for veteran status")
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

    id: int = Field(description="Unique identifier for educational background")
    type: str = Field(description="Type of education")
    institute_name: str = Field(description="Name of the institute")
    country: str = Field(description="Country of the institute")
    state: str = Field(description="State of the institute")
    from_date: date | None = Field(default=None, description="Start date of education")
    to_date: date | None = Field(default=None, description="End date of education")
    current_institute: bool = Field(description="Is this the current institute")


class CreateFrequentedSpot(BaseModel):
    """
    Create schema for poi frequented spots
    """

    id: int = Field(description="Unique identifier for frequented spot")
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

    id: int = Field(description="Unique identifier for fingerprint record")
    left_thumb: str = Field(description="Left thumb fingerprint data")
    right_thumb: str = Field(description="Right thumb fingerprint data")
    left_pointer: str = Field(description="Left pointer finger fingerprint data")
    right_pointer: str = Field(description="Right pointer finger fingerprint data")
