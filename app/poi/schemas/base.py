from datetime import date, datetime, time
from pydantic import BaseModel, Field


class Offense(BaseModel):
    """
    Base schema for offenses
    """

    id: int = Field(description="Unique identifier for the offense")
    name: str = Field(description="Name of the offense")
    description: str = Field(description="Description of the offense")
    created_at: datetime = Field(description="Creation timestamp")


class OffenseSummary(BaseModel):
    """
    Base schema for offense summaries
    """

    id: int = Field(description="Unique identifier for the offense")
    name: str = Field(description="Name of the offense")


class POI(BaseModel):
    """
    Base schema for POI's
    """

    id: int = Field(description="Unique identifier for the POI")
    pfp_url: str | None = Field(default=None, description="Profile picture URL")
    full_name: str = Field(description="Full name of the POI")
    alias: str = Field(description="Alias of the POI")
    dob: date | None = Field(default=None, description="Date of birth")
    pob: str | None = Field(default=None, description="Place of birth")
    nationality: str | None = Field(default=None, description="Nationality")
    religion: str | None = Field(default=None, description="Religion")
    political_affiliation: str | None = Field(
        default=None, description="Political affiliation"
    )
    tribal_union: str | None = Field(default=None, description="Tribal union")
    last_seen_date: date | None = Field(default=None, description="Last seen date")
    last_seen_time: time | None = Field(default=None, description="Last seen time")
    notes: str | None = Field(default=None, description="Additional notes")

    is_completed: bool = Field(description="Completion status")
    is_pinned: bool = Field(description="Pinned status")


class POISummary(BaseModel):
    """
    Base schema for poi summary
    """

    id: int = Field(description="The ID of the poi")
    full_name: str = Field(description="The fullname of the poi")
    convictions: list[OffenseSummary] = Field(
        description="The list of the poi's convictions"
    )
    is_pinned: bool = Field(description="If the poi is pinned")
    created_at: date = Field(description="The date the poi was created")


class IDDocument(BaseModel):
    """
    Base schema for ID Documents
    """

    id: int = Field(description="Unique identifier for the ID document")
    type: str = Field(description="Type of ID document")
    id_number: str = Field(description="ID number")


class GSMNumber(BaseModel):
    """
    Base schema for GSM Numbers
    """

    id: int = Field(description="Unique identifier for the GSM number")
    service_provider: str = Field(description="Service provider name")
    number: str = Field(description="GSM number")
    last_call_date: date | None = Field(default=None, description="Last call date")
    last_call_time: time | None = Field(default=None, description="Last call time")


class ResidentialAddress(BaseModel):
    """
    Base schema for poi residential addresses
    """

    id: int = Field(description="Unique identifier for the address")
    country: str = Field(description="Country of the address")
    state: str = Field(description="State of the address")
    city: str = Field(description="City of the address")
    address: str | None = Field(default=None, description="Street address")


class KnownAssociate(BaseModel):
    """
    Base schema for known poi associates
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


class EmploymentHistory(BaseModel):
    """
    Base schema for poi employment histories
    """

    id: int = Field(description="Unique identifier for employment history")
    company: str = Field(description="Company name")
    employment_type: str = Field(description="Type of employment")
    from_date: date | None = Field(default=None, description="Employment start date")
    to_date: date | None = Field(default=None, description="Employment end date")
    current_job: bool = Field(description="Is this the current job")
    description: str | None = Field(default=None, description="Job description")


class VeteranStatus(BaseModel):
    """
    Base schema for poi veteran status
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


class EducationalBackground(BaseModel):
    """
    Base schema for poi educational background
    """

    id: int = Field(description="Unique identifier for educational background")
    type: str = Field(description="Type of education")
    institute_name: str = Field(description="Name of the institute")
    country: str = Field(description="Country of the institute")
    state: str = Field(description="State of the institute")
    from_date: date | None = Field(default=None, description="Start date of education")
    to_date: date | None = Field(default=None, description="End date of education")
    current_institute: bool = Field(description="Is this the current institute")


class POIOffense(BaseModel):
    """
    Base schema for POI offenses
    """

    id: int = Field(description="Unique identifier for POI offense")
    offense_id: Offense = Field(description="Offense details")
    case_id: str | None = Field(default=None, description="Case ID")
    date_convicted: date | None = Field(default=None, description="Date of conviction")
    notes: str | None = Field(default=None, description="Additional notes")


class FrequentedSpot(BaseModel):
    """
    Base schema for poi frequented spots
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


class Fingerprint(BaseModel):
    """
    Base schema for POI fingerprints
    """

    id: int = Field(description="Unique identifier for fingerprint record")
    left_thumb: str = Field(description="Left thumb fingerprint data")
    right_thumb: str = Field(description="Right thumb fingerprint data")
    left_pointer: str = Field(description="Left pointer finger fingerprint data")
    right_pointer: str = Field(description="Right pointer finger fingerprint data")


class TopPOIOffense(BaseModel):
    """
    Base schema for top poi offenses
    """

    offense: str = Field(description="The name of the offense")
    value: int = Field(description="The number of pois convicted")


class TopPOIAge(BaseModel):
    """
    Base schema for top poi ages
    """

    range: str = Field(description="The age range of the pois")
    value: int = Field(description="The number of pois")


class TopPOIState(BaseModel):
    """
    Base schema for top poi states
    """

    state: str = Field(description="The state pois")
    value: int = Field(description="The number of pois")


class POIStatistics(BaseModel):
    """
    Base schema for poi statistics
    """

    tno_pois: int = Field(description="The total number of pois")
    tno_pois_last_month: int = Field(
        description="The total number of pois reported last month"
    )
    tno_pois_curr_month: int = Field(description="The total number of pois this month")
    poi_report_conviction: list[TopPOIOffense] = Field(
        max_length=4, description="The highest poi based on conviction"
    )
    poi_report_age: list[TopPOIAge] = Field(
        max_length=4, description="The top poi based on age"
    )
    poi_range_state: list[TopPOIState] = Field(
        max_length=4, description="The top poi based on state"
    )
