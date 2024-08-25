from sqlalchemy.orm import Session

from app.user.crud import UserCRUD
from app.user.exceptions import UserNotFound


async def get_user(badge_num: str, db: Session, raise_exc: bool = True):
    """
    Get user using the user's badge num

    Args:
        badge_num (str): The user's badge num
        db (Session): The database session
        raise_exc (bool = True): raise 404 exception if user is not found

    Raises:
        UserNotFound

    Returns:
        models.User | None
    """
    # Init crud
    user_crud = UserCRUD(db=db)

    # Get user
    user = await user_crud.get(badge_num=badge_num)

    # Check: user exists
    if not user and raise_exc:
        raise UserNotFound()

    return user
