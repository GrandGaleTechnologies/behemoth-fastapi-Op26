# pylint: disable=redefined-builtin
from datetime import datetime
from typing import cast

from sqlalchemy.orm import Query, Session

from app.common.encryption import EncryptionManager
from app.common.exceptions import InternalServerError
from app.common.paginators import paginate
from app.common.types import PaginationParamsType
from app.common.utils import find_all_matches, get_last_day_of_month, paginate_list
from app.core.settings import get_settings
from app.poi import models, utils
from app.poi.crud import (
    POICRUD,
    EducationalBackgroundCRUD,
    EmploymentHistoryCRUD,
    FrequentedSpotCRUD,
    GSMNumberCRUD,
    IDDocumentCRUD,
    KnownAssociateCRUD,
    OffenseCRUD,
    POIOffenseCRUD,
    ResidentialAddressCRUD,
    VeteranStatusCRUD,
)
from app.poi.exceptions import (
    EducationalBackgroundNotFound,
    EmploymentHistoryNotFound,
    FrequentedSpotNotFound,
    GSMNumberNotFound,
    IDDocumentNotFound,
    KnownAssociateNotFound,
    OffeseNotFound,
    POINotFound,
    POIOffenseNotFound,
    ResidentialAddressNotFound,
)

# Globals
settings = get_settings()
encryption_manager = EncryptionManager(key=settings.ENCRYPTION_KEY)


async def get_offense_by_id(id: int, db: Session, raise_exc: bool = True):
    """
    Get an offense using its ID

    Args:
        id (int): The ID of the offense
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        OffenseNotFound

    Returns:
        models.Offense | None
    """
    # init crud
    offense_crud = OffenseCRUD(db=db)

    # Get offense
    obj = await offense_crud.get(id=id)  # type: ignore
    if not obj and raise_exc:
        raise OffeseNotFound()

    return obj


async def get_paginated_offense_list(pagination: PaginationParamsType, db: Session):
    """
    Get paginated offense list

    Args:
        pagination (PaginationParamsType): The pagination details
        db (Session): The database session

    Returns:
        list[models.Offense]
    """
    # Init crud
    offense_crud = OffenseCRUD(db=db)

    # init qs
    qs = cast(Query[models.Offense], await offense_crud.get_all(return_qs=True))

    # order by
    if pagination.order_by == "asc":
        qs = qs.order_by(models.Offense.id.asc())
    else:
        qs = qs.order_by(models.Offense.id.desc())

    # Search
    if pagination.q:
        # Transformations
        # Decrypted list
        dec_all = qs.all()
        for obj in dec_all:
            obj.name = encryption_manager.decrypt_str(obj.name)  # type: ignore

        # Init objs
        objs: list[models.Offense] = []

        matches = await find_all_matches(
            query=pagination.q.capitalize(),  # Capitalize to normalize with db items
            options=[str(off.name) for off in dec_all],
        )
        for match in matches:
            # Get matching obj
            obj = [obj for obj in dec_all if bool(obj.name == match)][0]

            # encrypt name again
            obj.name = encryption_manager.encrypt_str(str(obj.name))  # type: ignore

            # Append to list
            objs.append(obj)

        # Paginate
        return paginate_list(
            items=objs, page=pagination.page, size=pagination.size
        ), len(objs)  # noqa

    # Paginate qs
    results: list[models.Offense] = paginate(
        qs=qs, page=pagination.page, size=pagination.size
    )

    return results, qs.count()


async def get_poi_statistics(db: Session):
    """
    Get POI Statistics

    Args:
        db (Session): The database session

    Returns:
        dict: {
        "tno_pois": the total number of pois,
        "tno_pois_last_month": the total number of pois last month,
        "tno_pois_curr_month": the total number of pois this month,
        "poi_report_conviction": the list of the top poi convictions,
        "poi_report_age": the list of the top poi age ranges
    }
    """
    # Init crud
    poi_crud = POICRUD(db=db)

    # Init qs
    qs = cast(Query[models.POI], await poi_crud.get_all(return_qs=True))

    # Decrypted poi list
    objs: list[models.POI] = []
    for poi in qs.all():
        # Check: poi was not deleted
        if encryption_manager.decrypt_boolean(data=poi.is_deleted):
            continue

        objs.append(poi)

    # Get tno_pois
    tno_pois = qs.count()

    # Edge Check: last month is in last year
    year = datetime.now().year
    last_month = datetime.now().month - 1

    if datetime.now().month < last_month:
        year = year - 1

    # Get last month range
    last_month_start = datetime(year=year, month=last_month, day=1)
    last_month_end = datetime(
        year=year,
        month=last_month,
        day=await get_last_day_of_month(year=year, month=last_month),
    )

    # Get tno pois last month
    tno_pois_last_month = 0
    for poi in objs:
        created_at = encryption_manager.decrypt_datetime(poi.created_at)

        if last_month_start <= created_at <= last_month_end:
            tno_pois_last_month += 1

    # Get curr month range
    year = datetime.now().year
    month = datetime.now().month

    curr_month_start = datetime(year=year, month=month, day=1)

    # Get tno pois last month
    tno_pois_curr_month = len(
        [
            poi
            for poi in objs
            if encryption_manager.decrypt_datetime(poi.created_at) > curr_month_start
        ]
    )

    # Get poi report on convictions
    top_convictions: list[dict[str, str | int]] = []

    top_offenses = await utils.get_top_offenses(db=db)
    for offense_name, value in top_offenses:
        top_convictions.append(
            {
                "offense": encryption_manager.decrypt_str(offense_name),
                "value": value,
            }
        )

    # Get poi report on age range
    top_age_range = await utils.get_top_poi_age_ranges(
        dob_list=[
            encryption_manager.decrypt_date(data=str(poi.dob))
            for poi in objs
            if bool(poi.dob)
        ]
    )

    return {
        "tno_pois": tno_pois,
        "tno_pois_last_month": tno_pois_last_month,
        "tno_pois_curr_month": tno_pois_curr_month,
        "poi_report_conviction": top_convictions,
        "poi_report_age": [
            {"range": report[0], "value": report[1]} for report in top_age_range
        ],
    }


async def get_pinned_pois(db: Session):
    """
    Get all pinned pois

    Args:
        db (Session): The database session

    Returns:
        list[models.POI]
    """
    # Init crud
    poi_crud = POICRUD(db=db)

    # init qs
    qs = cast(list[models.POI], await poi_crud.get_all())

    # decrypt pin status
    data = []
    for obj in qs:
        if encryption_manager.decrypt_boolean(obj.is_pinned):
            data.append(obj)

    return data


async def get_recently_added_pois(db: Session):
    """
    Get recently added pois

    Args:
        db (Session): The database session

    Returns:
        list[models.POI]
    """
    # Init crud
    poi_crud = POICRUD(db=db)

    # init qs
    qs = cast(Query[models.POI], await poi_crud.get_all(return_qs=True))

    return qs.order_by(models.POI.id.desc()).all()


async def get_poi_by_id(id: int, db: Session, raise_exc: bool = True):
    """
    Get poi obj using its ID

    Args:
        id (int): The ID of the poi
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if obj is not found

    Raises:
        POINotFound

    Returns:
        models.POI | None
    """
    # Init crud
    poi_crud = POICRUD(db=db)

    # Get poi
    obj = await poi_crud.get(id=id)
    if not obj and raise_exc:
        raise POINotFound()

    # Check if deleted
    if obj and encryption_manager.decrypt_boolean(obj.is_deleted):
        raise POINotFound()

    return obj


async def get_poi_offense_by_id(id: int, db: Session, raise_exc: bool = True):
    """
    Get poi offense by id

    Args:
        id (int): The ID of the poi offense
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        POIOffenseNotFound

    Returns:
        models.POIOffense | None
    """
    # Init crud
    poi_offense_crud = POIOffenseCRUD(db=db)

    # Get obj
    obj = await poi_offense_crud.get(id=id)
    if not obj and raise_exc:
        raise POIOffenseNotFound()

    # Check if deleted
    if obj and encryption_manager.decrypt_boolean(obj.is_deleted):
        raise POIOffenseNotFound()

    return obj


async def get_poi_offenses(poi: models.POI, db: Session):
    """
    Get POI Offenses

    Args:
        poi (models.POI): The poi obj
        db (Session): The database session

    Returns:
        list[models.POIOffense]
    """
    # Init crud
    poi_offense_crud = POIOffenseCRUD(db=db)

    qs = cast(list[models.POIOffense], await poi_offense_crud.get_all())

    return [
        obj
        for obj in qs
        if not encryption_manager.decrypt_boolean(obj.is_deleted)
        and bool(obj.poi_id == poi.id)
    ]


async def get_id_doc_by_id(id: int, db: Session, raise_exc: bool = True):
    """
    Get ID Document using its iD

    Args:
        id (int): The id of the document
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Returns:
        models.IDDocument | None
    """
    # Init crud
    doc_crud = IDDocumentCRUD(db=db)

    # Get id doc
    obj = await doc_crud.get(id=id)
    if not obj and raise_exc:
        raise IDDocumentNotFound()

    # Check if deleted
    if obj and encryption_manager.decrypt_boolean(obj.is_deleted):
        raise IDDocumentNotFound()

    return obj


async def get_id_documents(poi: models.POI, db: Session):
    """
    Get POI ID Documents

    Args:
        poi (mdoels.POI): The poi obj
        db (Session): The database session

    Returns:
        list[models.IDDocument]
    """
    # Init crud
    doc_crud = IDDocumentCRUD(db=db)

    qs = cast(list[models.IDDocument], await doc_crud.get_all())

    return [
        obj
        for obj in qs
        if not encryption_manager.decrypt_boolean(obj.is_deleted)
        and bool(obj.poi_id == poi.id)
    ]


async def get_gsm_by_id(id: int, db: Session, raise_exc: bool = True):
    """
    Get GSM Number using ID

    Args:
        id (int): The ID of the gsm number
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        GSMNumberNotFound

    Returns:
        models.GSMNumber | None
    """
    # Init crud
    gsm_crud = GSMNumberCRUD(db=db)

    # Get gsm
    obj = await gsm_crud.get(id=id)
    if not obj and raise_exc:
        raise GSMNumberNotFound()

    # Check if deleted
    if obj and encryption_manager.decrypt_boolean(obj.is_deleted):
        raise GSMNumberNotFound()

    return obj


async def get_gsm_numbers(poi: models.POI, db: Session):
    """
    Get gsm numbers

    Args:
        poi (models.POI): The poi obj
        db (Session): The database session

    Returns:
        list[models.GSMNumber]
    """
    # Init crud
    gsm_crud = GSMNumberCRUD(db=db)

    qs = cast(list[models.GSMNumber], await gsm_crud.get_all())

    return [
        obj
        for obj in qs
        if not encryption_manager.decrypt_boolean(obj.is_deleted)
        and bool(obj.poi_id == poi.id)
    ]


async def get_residential_address_by_id(id: int, db: Session, raise_exc: bool = True):
    """
    Get residential address using its ID

    Args:
        id (int): The ID of the address
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        ResidentialAddressNotFound

    Returns:
        models.ResidentialAddress | None
    """
    # Init crud
    address_crud = ResidentialAddressCRUD(db=db)

    # get obj
    obj = await address_crud.get(id=id)
    if not obj and raise_exc:
        raise ResidentialAddressNotFound()

    # Check deleted
    if obj and encryption_manager.decrypt_boolean(obj.is_deleted):
        raise ResidentialAddressNotFound()

    return obj


async def get_residential_addresses(poi: models.POI, db: Session):
    """
    Get poi residential addresses

    Args:
        poi (models.POI): The poi obj
        db (Session): The database session

    Returns:
        list[models.ResidentialAddress]
    """
    # Init crud
    address_crud = ResidentialAddressCRUD(db=db)

    qs = cast(list[models.ResidentialAddress], await address_crud.get_all())

    return [
        obj
        for obj in qs
        if not encryption_manager.decrypt_boolean(obj.is_deleted)
        and bool(obj.poi_id == poi.id)
    ]


async def get_known_associate_by_id(id: int, db: Session, raise_exc: bool = True):
    """
    Get known associate using its ID

    Args:
        id (int): The ID of the associate
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        KnownAssociateNotFound

    Returns:
        models.KnownAssociate | None
    """
    # Init crud
    address_crud = KnownAssociateCRUD(db=db)

    # get obj
    obj = await address_crud.get(id=id)
    if not obj and raise_exc:
        raise KnownAssociateNotFound()

    # Check if deleted
    if obj and encryption_manager.decrypt_boolean(obj.is_deleted):
        raise KnownAssociateNotFound()

    return obj


async def get_known_associates(poi: models.POI, db: Session):
    """
    Get poi known associates

    Args:
        poi (models.POI): The poi obj
        db (Session): The database session

    Returns:
        list[models.KnownAssociate]
    """
    # Init crud
    associate_crud = KnownAssociateCRUD(db=db)

    qs = cast(list[models.KnownAssociate], await associate_crud.get_all())

    return [
        obj
        for obj in qs
        if not encryption_manager.decrypt_boolean(obj.is_deleted)
        and bool(obj.poi_id == poi.id)
    ]


async def get_employment_history_by_id(id: int, db: Session, raise_exc: bool = True):
    """
    Get employment history by id

    Args:
        id (int): The ID of the employment history
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        EmploymentHistoryNotFound

    Returns:
        models.EmploymentHistory | None
    """
    # Init crud
    history_crud = EmploymentHistoryCRUD(db=db)

    # Get obj
    obj = await history_crud.get(id=id)
    if not obj and raise_exc:
        raise EmploymentHistoryNotFound()

    # Check if deleted
    if obj and encryption_manager.decrypt_boolean(obj.is_deleted):
        raise EmploymentHistoryNotFound()

    return obj


async def get_employment_history(poi: models.POI, db: Session):
    """
    Get poi employment history

    Args:
        poi (models.POI): The poi obj
        db (Session): The database session

    Returns:
        list[models.EmploymentHistory]
    """
    # Init crud
    history_crud = EmploymentHistoryCRUD(db=db)

    qs = cast(list[models.EmploymentHistory], await history_crud.get_all())

    return [
        obj
        for obj in qs
        if not encryption_manager.decrypt_boolean(obj.is_deleted)
        and bool(obj.poi_id == poi.id)
    ]


async def get_veteran_status_by_poi(
    poi: models.POI, db: Session, raise_exc: bool = True
):
    """
    Get veteran status by poi

    Args:
        poi (models.POI): The poi obj
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        InternalServerError

    Returns:
        models.VeteranStatus
    """
    # Init crud
    veteran_crud = VeteranStatusCRUD(db=db)

    # Get obj
    obj = await veteran_crud.get(poi_id=poi.id)
    if not obj and raise_exc:
        raise InternalServerError(
            f"Veteran status for poi {poi.id} not found",
            loc="app.poi.selectors.get_veteran_status_by_poi",
        )

    return obj


async def get_educational_background_by_id(
    id: int, db: Session, raise_exc: bool = True
):
    """
    Get educational background by id

    Args:
        id (int): The id of the educational background
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        EducationalBackgroundNotFound

    Returns:
        models.EducationalBackground | None
    """
    # Init crud
    education_crud = EducationalBackgroundCRUD(db=db)

    # Get obj
    obj = await education_crud.get(id=id)
    if not obj and raise_exc:
        raise EducationalBackgroundNotFound()

    # Check if deleted
    if obj and encryption_manager.decrypt_boolean(obj.is_deleted):
        raise EducationalBackgroundNotFound()

    return obj


async def get_educational_background(poi: models.POI, db: Session):
    """
    Get educational background

    Args:
        poi (models.POI): The poi obj
        db (Session): The database session

    Returns:
        list[models.EducationalBackground]
    """
    # Init crud
    education_crud = EducationalBackgroundCRUD(db=db)

    qs = cast(list[models.EducationalBackground], await education_crud.get_all())

    return [
        obj
        for obj in qs
        if not encryption_manager.decrypt_boolean(obj.is_deleted)
        and bool(obj.poi_id == poi.id)
    ]


async def get_frequented_spot_by_id(id: int, db: Session, raise_exc: bool = True):
    """
    Get frequented spot by id

    Args:
        id (int): The ID of the frequented spot
        db (Session): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        FrequentedSpotNotFound

    Returns:
        models.FrequentedSpot | None
    """
    # Init crud
    spot_crud = FrequentedSpotCRUD(db=db)

    # Get obj
    obj = await spot_crud.get(id=id)
    if not obj and raise_exc:
        raise FrequentedSpotNotFound()

    # Check if deleted
    if obj and encryption_manager.decrypt_boolean(obj.is_deleted):
        raise FrequentedSpotNotFound()

    return obj


async def get_frequented_spots(poi: models.POI, db: Session):
    """
    Get poi frequented spots

    Args:
        poi (models.POI): The poi obj
        db (Session): The database session

    Returns:
        list[models.FrequentedSpot]
    """
    # Init crud
    spot_crud = FrequentedSpotCRUD(db=db)

    qs = cast(list[models.FrequentedSpot], await spot_crud.get_all())

    return [
        obj
        for obj in qs
        if not encryption_manager.decrypt_boolean(obj.is_deleted)
        and bool(obj.poi_id == poi.id)
    ]
