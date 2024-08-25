from sqlalchemy.orm import Session

from app.common.crud import CRUDBase
from app.poi import models


class OffenseCRUD(CRUDBase[models.Offense]):
    """
    CRUD Class for offenses
    """

    def __init__(self, db: Session):
        super().__init__(models.Offense, db)
