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
