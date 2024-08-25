from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.common.dependencies import get_session, pagination_params
from app.common.types import PaginationParamsType

DatabaseSession = Annotated[Session, Depends(get_session)]
PaginationParams = Annotated[PaginationParamsType, Depends(pagination_params)]
