from sqlalchemy.orm import Session

from app.common.crud import CRUDBase
from app.poi import models


class OffenseCRUD(CRUDBase[models.Offense]):
    """
    CRUD Class for offenses
    """

    def __init__(self, db: Session):
        super().__init__(models.Offense, db)


class POICRUD(CRUDBase[models.POI]):
    """
    CRUD Class for pois
    """

    def __init__(self, db: Session):
        super().__init__(models.POI, db)


class POIApplicationProcess(CRUDBase[models.POIApplicationProcess]):
    """
    CRUD Class for poi application processes
    """

    def __init__(self, db: Session):
        super().__init__(models.POIApplicationProcess, db)


class IDDocumentCRUD(CRUDBase[models.IDDocument]):
    """
    CRUD Class for ID Documents
    """

    def __init__(self, db: Session):
        super().__init__(models.IDDocument, db)


class POIOffenseCRUD(CRUDBase[models.POIOffense]):
    """
    CRUD Class for poi offenses
    """

    def __init__(self, db: Session):
        super().__init__(models.POIOffense, db)


class GSMNumber(CRUDBase[models.GSMNumber]):
    """
    CRUD Class for gsm numbers
    """

    def __init__(self, db: Session):
        super().__init__(models.GSMNumber, db)


class ResidentialAddressCRUD(CRUDBase[models.ResidentialAddress]):
    """
    CRUD Class for residential addresses
    """

    def __init__(self, db: Session):
        super().__init__(models.ResidentialAddress, db)


class KnownAssociateCRUD(CRUDBase[models.KnownAssociate]):
    """
    CRUD Class for known associates
    """

    def __init__(self, db: Session):
        super().__init__(models.KnownAssociate, db)
