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


class GSMNumberCRUD(CRUDBase[models.GSMNumber]):
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


class EmploymentHistoryCRUD(CRUDBase[models.EmploymentHistory]):
    """
    CRUD Class for employment history
    """

    def __init__(self, db: Session):
        super().__init__(models.EmploymentHistory, db)


class VeteranStatusCRUD(CRUDBase[models.VeteranStatus]):
    """
    CRUD Class for veteran status
    """

    def __init__(self, db: Session):
        super().__init__(models.VeteranStatus, db)


class EducationalBackgroundCRUD(CRUDBase[models.EducationalBackground]):
    """
    CRUD Class for educational background
    """

    def __init__(self, db: Session):
        super().__init__(models.EducationalBackground, db)


class FrequentedSpotCRUD(CRUDBase[models.FrequentedSpot]):
    """
    CRUD Class for frequented spot
    """

    def __init__(self, db: Session):
        super().__init__(models.FrequentedSpot, db)
