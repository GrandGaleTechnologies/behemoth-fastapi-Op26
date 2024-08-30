from app.core.settings import get_settings
from app.poi import models
from app.common.encryption import EncryptionManager

# Globals
settings = get_settings()
encrypt_man = EncryptionManager(key=settings.ENCRYPTION_KEY)


async def format_offense(offense: models.Offense):
    """
    Format offense obj to dict
    """

    return {
        "id": offense.id,
        "name": encrypt_man.decrypt_str(data=offense.name),
        "description": encrypt_man.decrypt_str(data=offense.description),
        "created_at": encrypt_man.decrypt_datetime(data=offense.created_at),
    }


async def format_poi_application(application: models.POIApplicationProcess):
    """
    Format poi application to dict
    """
    return {
        "id": application.id,
        "other_profile": encrypt_man.decrypt_boolean(application.other_profile),
        "employment": encrypt_man.decrypt_boolean(application.employment),
        "veteran_status": encrypt_man.decrypt_boolean(application.veteran_status),
        "education": encrypt_man.decrypt_boolean(application.education),
        "case_file": encrypt_man.decrypt_boolean(application.case_file),
        "fingerprints": encrypt_man.decrypt_boolean(application.fingerprints),
    }


async def format_poi_base(poi: models.POI):
    """
    Format poi obj to poi base dict
    """

    return {
        "id": poi.id,
        "pfp": encrypt_man.decrypt_str(poi.pfp_url) if bool(poi.pfp_url) else None,
        "full_name": encrypt_man.decrypt_str(poi.full_name),
        "alias": encrypt_man.decrypt_str(poi.alias),
        "dob": encrypt_man.decrypt_date(poi.dob) if bool(poi.dob) else None,
        "pob": encrypt_man.decrypt_str(poi.pob) if bool(poi.pob) else None,
        "nationality": encrypt_man.decrypt_str(poi.nationality)
        if bool(poi.nationality)
        else None,
        "religion": encrypt_man.decrypt_str(poi.religion)
        if bool(poi.religion)
        else None,
        "political_affiliation": encrypt_man.decrypt_str(poi.political_affiliation)
        if bool(poi.political_affiliation)
        else None,
        "tribal_union": encrypt_man.decrypt_str(poi.tribal_union)
        if bool(poi.tribal_union)
        else None,
        "last_seen_date": encrypt_man.decrypt_date(poi.last_seen_date)
        if bool(poi.last_seen_date)
        else None,
        "last_seen_time": encrypt_man.decrypt_time(poi.last_seen_time)
        if bool(poi.last_seen_time)
        else None,
        "is_completed": encrypt_man.decrypt_boolean(poi.is_completed),
        "is_pinned": encrypt_man.decrypt_boolean(poi.is_pinned),
        "notes": encrypt_man.decrypt_str(poi.notes) if bool(poi.notes) else None,
        "id_documents": [
            await format_id_document(doc=doc)
            for doc in poi.id_documents
            if not encrypt_man.decrypt_boolean(doc.is_deleted)
        ]
        if poi.id_documents
        else None,
        "created_at": encrypt_man.decrypt_datetime(poi.created_at),
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
            await format_known_associates(associate=associate)
            for associate in poi.known_associates
        ],
    }


async def format_id_document(doc: models.IDDocument):
    """
    Format ID Doc object to dict
    """

    return {
        "id": doc.id,
        "type": encrypt_man.decrypt_str(doc.type),
        "id_number": encrypt_man.decrypt_str(doc.id_number),
    }


async def format_gsm(gsm: models.GSMNumber):
    """
    Format gsm obj to dict
    """
    return {
        "id": gsm.id,
        "service_provider": encrypt_man.decrypt_str(gsm.service_provider),
        "number": encrypt_man.decrypt_str(gsm.number),
        "last_call_date": encrypt_man.decrypt_date(gsm.last_call_date)
        if bool(gsm.last_call_date)
        else None,
        "last_call_time": encrypt_man.decrypt_time(gsm.last_call_time)
        if bool(gsm.last_call_time)
        else None,
    }


async def format_residential_address(address: models.ResidentialAddress):
    """
    Format residential address obj to dict
    """
    dec = encrypt_man.decrypt_str
    return {
        "id": address.id,
        "country": dec(address.country),
        "state": dec(address.state),
        "city": dec(address.city),
        "address": dec(address.address) if bool(address.address) else None,
    }


async def format_known_associates(associate: models.KnownAssociate):
    """
    Format known associate obj to dict
    """
    dec = encrypt_man.decrypt_str
    return {
        "id": associate.id,
        "full_name": dec(associate.full_name),
        "known_gsm_numbers": dec(associate.known_gsm_numbers)
        if bool(associate.known_gsm_numbers)
        else None,
        "relationship": dec(associate.relationship),
        "occupation": dec(associate.occupation) if bool(associate.occupation) else None,
        "residential_address": dec(associate.residential_address)
        if bool(associate.residential_address)
        else None,
        "last_seen_date": encrypt_man.decrypt_date(associate.last_seen_date)
        if bool(associate.last_seen_date)
        else None,
        "last_seen_time": encrypt_man.decrypt_time(associate.last_seen_time)
        if bool(associate.last_seen_time)
        else None,
    }
