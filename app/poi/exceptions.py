from app.common.exceptions import NotFound


class OffeseNotFound(NotFound):
    """
    Exception for 404 Offense Not Found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Offense Not Found", loc=loc)
