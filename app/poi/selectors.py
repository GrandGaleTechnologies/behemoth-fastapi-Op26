# pylint: disable=redefined-builtin
from typing import cast
from sqlalchemy.orm import Session, Query

from app.common.encryption import EncryptionManager
from app.common.paginators import paginate
from app.common.types import PaginationParamsType
from app.common.utils import find_all_matches, paginate_list
from app.core.settings import get_settings
from app.poi import models
from app.poi.crud import OffenseCRUD
from app.poi.exceptions import OffeseNotFound

# Globals
settings = get_settings()
encryption_manager = EncryptionManager(key=settings.ENCRYPTION_KEY)


async def get_offense_by_id(id: int, db: Session, raise_exc: bool = True):
    """
    Get an offense using its ID

    Args:
        id (int): The ID of the offense
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        OffenseNotFound

    Returns:
        models.Offense | None
    """
    # init crud
    offense_crud = OffenseCRUD(db=db)

    # Get offense
    obj = await offense_crud.get(id=id)  # type: ignore
    if not obj and raise_exc:
        raise OffeseNotFound()

    return obj


async def get_paginated_offense_list(pagination: PaginationParamsType, db: Session):
    """
    Get paginated offense list

    Args:
        pagination (PaginationParamsType): The pagination details
        db (Session): The database session

    Returns:
        list[models.Offense]
    """
    # Init crud
    offense_crud = OffenseCRUD(db=db)

    # init qs
    qs = cast(Query[models.Offense], await offense_crud.get_all(return_qs=True))

    # order by
    if pagination.order_by == "asc":
        qs = qs.order_by(models.Offense.id.asc())
    else:
        qs = qs.order_by(models.Offense.id.desc())

    # Search
    if pagination.q:
        # Transformations
        # Decrypted list
        dec_all = qs.all()
        for obj in dec_all:
            obj.name = encryption_manager.decrypt_str(obj.name)  # type: ignore

        # Init objs
        objs: list[models.Offense] = []

        matches = await find_all_matches(
            query=pagination.q.capitalize(),  # Capitalize to normalize with db items
            options=[str(off.name) for off in dec_all],
        )
        for match in matches:
            # Get matching obj
            obj = [obj for obj in dec_all if bool(obj.name == match)][0]

            # encrypt name again
            obj.name = encryption_manager.encrypt_str(str(obj.name))  # type: ignore

            # Append to list
            objs.append(obj)

        # Paginate
        return paginate_list(
            items=objs, page=pagination.page, size=pagination.size
        ), len(objs)  # noqa

    # Paginate qs
    results: list[models.Offense] = paginate(
        qs=qs, page=pagination.page, size=pagination.size
    )

    return results, qs.count()
