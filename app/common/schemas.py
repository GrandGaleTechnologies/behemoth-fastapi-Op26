from typing import Any

from pydantic import BaseModel, Field


class ResponseSchema(BaseModel):
    """This is the generic base response schema"""

    status: str = Field(description="The response status", default="success")
    msg: str = Field(default="Request Successful", description="The response message")
    data: Any = Field(description="The response data")
