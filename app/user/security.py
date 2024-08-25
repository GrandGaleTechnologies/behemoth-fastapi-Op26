from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.common.auth import TokenGenerator
from app.common.dependencies import get_session
from app.common.exceptions import Unauthorized
from app.core.settings import get_settings
from app.user import selectors

# Globals
settings = get_settings()
token_generator = TokenGenerator(
    secret_key=settings.SECRET_KEY, expire_in=settings.ACCESS_TOKEN_EXPIRE_MIN
)


async def get_current_user(
    token: str = Header(alias="Authorization"), db: Session = Depends(get_session)
):
    """
    This function returns the current logged in user

    Args:
        token (str, optional): The Authorization header. Defaults to Header(alias="Authorization
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        models.Ward: The current ward
    """
    try:
        token_type, token = token.split(" ")

    except ValueError:
        raise Unauthorized("Invalid Token")

    if token_type != "Bearer":
        raise Unauthorized("Invalid Token")

    badge_num = await token_generator.verify(sub_head="USER", token=token)

    if user := await selectors.get_user(badge_num=badge_num, db=db, raise_exc=False):
        return user

    raise Unauthorized("Invalid Token")
