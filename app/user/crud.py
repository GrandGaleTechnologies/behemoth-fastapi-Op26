from sqlalchemy.orm import Session

from app.common.crud import CRUDBase
from app.user import models


class UserCRUD(CRUDBase[models.User]):
    """
    CRUD Class for user model
    """

    def __init__(self, db: Session):
        super().__init__(models.User, db)


class LoginAttemptCRUD(CRUDBase[models.LoginAttempt]):
    """
    CRUD Class for login attempts
    """

    def __init__(self, db: Session):
        super().__init__(models.LoginAttempt, db)
