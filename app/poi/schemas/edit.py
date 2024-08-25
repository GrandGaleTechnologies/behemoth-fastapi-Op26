from pydantic import BaseModel, Field


class OffenseEdit(BaseModel):
    """
    Create schema for offenses
    """

    name: str = Field(description="Name of the offense")
    description: str = Field(description="Description of the offense")
