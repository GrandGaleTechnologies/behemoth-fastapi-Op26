from typing import Literal
from app.common.types import PaginationParamsType
from app.core.database import SessionLocal


def get_session():
    """This function creates a db session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def pagination_params(
    q: str | None = None,
    page: int = 1,
    size: int = 10,
    order_by: Literal["asc", "desc"] = "desc",
):
    """Helper Dependency for pagination"""
    return PaginationParamsType(q=q, page=page, size=size, order_by=order_by)
