from datetime import date

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


class IDDocumentEdit(BaseModel):
    """
    Create schema for ID Documents
    """

    type: str = Field(description="Type of ID document")
    id_number: str = Field(description="ID number")
