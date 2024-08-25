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
