class CustomHTTPException(Exception):
    """
    Common base class for all http exceptions
    """

    def __init__(self, msg: str, *, status_code: int, loc: list | None = None):
        self.status_code = status_code
        self.msg = msg
        self.loc = loc
