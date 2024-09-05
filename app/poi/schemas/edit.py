from datetime import date, time

from pydantic import BaseModel, Field


class OffenseEdit(BaseModel):
    """
    Create schema for offenses
    """

    name: str = Field(description="Name of the offense")
    description: str = Field(description="Description of the offense")


class POIBaseInformationEdit(BaseModel):
    """
    Edit schema for base POI information
    """

    # Basic Information
    pfp: str | None = Field(default=None, description="Profile picture URL")
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
    notes: str | None = Field(default=None, description="additional notes on the poi")


class POIOtherProfileEdit(BaseModel):
    """
    Edit schema for other profile poi information
    """

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


class IDDocumentEdit(BaseModel):
    """
    Create schema for ID Documents
    """

    type: str = Field(description="Type of ID document")
    id_number: str = Field(description="ID number")


class GSMNumberEdit(BaseModel):
    """
    Edit schema for GSM Numbers
    """

    service_provider: str = Field(description="Service provider name")
    number: str = Field(description="GSM number")
    last_call_date: date | None = Field(default=None, description="Last call date")
    last_call_time: time | None = Field(default=None, description="Last call time")


class ResidentialAddressEdit(BaseModel):
    """
    Edit schema for poi residential addresses
    """

    country: str = Field(description="Country of the address")
    state: str = Field(description="State of the address")
    city: str = Field(description="City of the address")
    address: str | None = Field(default=None, description="Street address")


class KnownAssociateEdit(BaseModel):
    """
    Edit schema for known poi associates
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


class EmploymentHistoryEdit(BaseModel):
    """
    Edit schema for poi employment histories
    """

    company: str = Field(description="Company name")
    employment_type: str = Field(description="Type of employment")
    from_date: date | None = Field(default=None, description="Employment start date")
    to_date: date | None = Field(default=None, description="Employment end date")
    current_job: bool = Field(description="Is this the current job")
    description: str | None = Field(default=None, description="Job description")
