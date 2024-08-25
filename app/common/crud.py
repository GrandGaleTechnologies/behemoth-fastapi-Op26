from typing import Any, Generic, Type, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class CRUDBase(Generic[T]):
    """
    CRUD object with default methods to Create, Read, Update, Delete (CRUD).
    """

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db
        self.qs = db.query(model)

    async def create(self, *, data: dict[str, Any]):
        """
        Create object
        """
        db_obj = self.model(**data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)

        return db_obj

    async def get(self, **kwargs):
        """
        Retrieve object
        """

        return self.qs.filter_by(**kwargs).first()

    async def get_all(self, return_qs: bool = False):
        """
        Get all objects
        """

        if return_qs:
            return self.qs
        return self.qs.all()
