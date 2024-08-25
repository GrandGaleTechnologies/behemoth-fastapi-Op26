from typing import Annotated

from fastapi import Depends

from app.user import models, security

CurrentUser = Annotated[models.User, Depends(security.get_current_user)]
