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
        "is_completed": encrypt_man.decrypt_boolean(poi.is_completed),
        "is_pinned": encrypt_man.decrypt_boolean(poi.is_pinned),
        "id_documents": [await format_id_document(doc=doc) for doc in poi.id_documents]
        if poi.id_documents
        else None,
        "created_at": encrypt_man.decrypt_datetime(poi.created_at),
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
