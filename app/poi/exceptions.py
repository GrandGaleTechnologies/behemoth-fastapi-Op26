from app.common.exceptions import NotFound


class OffeseNotFound(NotFound):
    """
    Exception for 404 Offense Not Found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Offense Not Found", loc=loc)


class POINotFound(NotFound):
    """
    Exception for 404 POI Not Found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("POI Not Found", loc=loc)


class IDDocumentNotFound(NotFound):
    """
    Exception for 404 ID Document Not Found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("ID Document Not Found", loc=loc)


class GSMNumberNotFound(NotFound):
    """
    Exception for 404 GSM Number Not Found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("GSM Number Not Found", loc=loc)
