from functools import lru_cache

from pydantic import BaseModel


class RouteTags(BaseModel):
    """
    Base model for app route tags
    """

    # POI Modules
    POI: str = "POI APIs"
    POI_BASE_INFORMATION: str = "POI Base Information Endpoints"
    POI_OTHER_PROFILE: str = "POI Other Profile Endpoints"
    POI_ID_DOCUMENT: str = "POI ID Document Endpoints"
    POI_GSM_NUMBER: str = "POI GSM Number Endpoints"


@lru_cache
def get_tags():
    """
    Get app rotue tags
    """
    return RouteTags()
