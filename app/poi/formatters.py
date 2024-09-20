from app.core.settings import get_settings
from app.poi import models

# Globals
settings = get_settings()


async def format_offense(offense: models.Offense):
    """
    Format offense obj to dict
    """

    return {
        "id": offense.id,
        "name": offense.name,
        "description": offense.description,
        "created_at": offense.created_at,
    }


async def format_offense_summary(offense: models.Offense):
    """
    Format offense obj to offense summary dict
    """

    return {
        "id": offense.id,
        "name": offense.name,
    }


async def format_poi_base(poi: models.POI):
    """
    Format poi obj to poi base dict
    """

    return {
        "id": poi.id,
        "pfp": poi.pfp_url,
        "full_name": poi.full_name,
        "alias": poi.alias,
        "dob": poi.dob,
        "pob": poi.pob,
        "nationality": poi.nationality,
        "religion": poi.religion,
        "political_affiliation": poi.political_affiliation,
        "tribal_union": poi.tribal_union,
        "last_seen_date": poi.last_seen_date,
        "last_seen_time": poi.last_seen_time,
        "is_pinned": poi.is_pinned,
        "notes": poi.notes,
        "id_documents": [
            await format_id_document(doc=doc)
            for doc in poi.id_documents
            if not bool(doc.is_deleted)
        ],
        "created_at": poi.created_at,
    }


async def format_poi_summary(poi: models.POI):
    """
    Format poi obj to poi summary
    """

    return {
        "id": poi.id,
        "full_name": poi.full_name,
        "convictions": [await format_poi_offense(conv=conv) for conv in poi.offenses],
        "is_pinned": poi.is_pinned,
        "created_at": poi.created_at,
    }


async def format_poi_offense(conv: models.POIOffense):
    """
    Format poi offense to dict
    """
    return {
        "id": conv.id,
        "offense": await format_offense_summary(offense=conv.offense),
        "case_id": conv.case_id,
        "date_convicted": conv.date_convicted,
        "notes": conv.notes,
    }


async def format_poi_other_profile(poi: models.POI):
    """
    Format poi to poi other profile obj
    """
    return {
        "gsm_numbers": [await format_gsm(gsm=gsm) for gsm in poi.gsm_numbers],
        "residential_addresses": [
            await format_residential_address(address=address)
            for address in poi.residential_addresses
        ],
        "known_associates": [
            await format_known_associate(associate=associate)
            for associate in poi.known_associates
        ],
    }


async def format_id_document(doc: models.IDDocument):
    """
    Format ID Doc object to dict
    """

    return {
        "id": doc.id,
        "type": doc.type,
        "id_number": doc.id_number,
    }


async def format_gsm(gsm: models.GSMNumber):
    """
    Format gsm obj to dict
    """
    return {
        "id": gsm.id,
        "service_provider": gsm.service_provider,
        "number": gsm.number,
        "last_call_date": gsm.last_call_date,
        "last_call_time": gsm.last_call_time,
    }


async def format_residential_address(address: models.ResidentialAddress):
    """
    Format residential address obj to dict
    """
    return {
        "id": address.id,
        "country": address.country,
        "state": address.state,
        "city": address.city,
        "address": address.address,
    }


async def format_known_associate(associate: models.KnownAssociate):
    """
    Format known associate obj to dict
    """
    return {
        "id": associate.id,
        "full_name": associate.full_name,
        "known_gsm_numbers": associate.known_gsm_numbers,
        "relationship": associate.relationship,
        "occupation": associate.occupation,
        "residential_address": associate.residential_address,
        "last_seen_date": associate.last_seen_date,
        "last_seen_time": associate.last_seen_time,
    }


async def format_employment_history(history: models.EmploymentHistory):
    """
    Format employment history obj to dict
    """
    return {
        "id": history.id,
        "company": history.company,
        "employment_type": history.employment_type,
        "from_date": history.from_date,
        "to_date": history.to_date,
        "current_job": history.current_job,
        "description": history.description,
    }


async def format_veteran_status(status: models.VeteranStatus):
    """
    Format veteran status obj to dict
    """
    return {
        "id": status.id,
        "is_veteran": status.is_veteran,
        "section": status.section,
        "location": status.location,
        "id_card": status.id_card,
        "id_card_issuer": status.id_card_issuer,
        "from_date": status.from_date,
        "to_date": status.to_date,
        "notes": status.notes,
    }


async def format_educational_background(education: models.EducationalBackground):
    """
    Format educational background obj to dict
    """
    return {
        "id": education.id,
        "type": education.type,
        "institute_name": education.institute_name,
        "country": education.country,
        "state": education.state,
        "from_date": education.from_date,
        "to_date": education.to_date,
        "current_institute": education.current_institute,
    }


async def format_frequented_spot(spot: models.FrequentedSpot):
    """
    Format frequented spot obj to dict
    """
    return {
        "id": spot.id,
        "country": spot.country,
        "state": spot.state,
        "lga": spot.lga,
        "address": spot.address,
        "from_date": spot.from_date,
        "to_date": spot.to_date,
        "notes": spot.notes,
    }
