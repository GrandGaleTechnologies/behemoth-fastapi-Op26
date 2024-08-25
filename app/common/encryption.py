from datetime import datetime

from cryptography.fernet import Fernet


class EncryptionManager:
    """
    Common encryption manager for datatypes
    """

    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())

    def encrypt_str(self, data: str):
        """
        Encrypt string
        """
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_str(self, encrypted_data: str):
        """
        Decrypt string
        """
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def encrypt_boolean(self, value: bool):
        """
        Encrypt boolean
        """
        bool_str = str(value)  # Convert boolean to string ("True" or "False")
        return self.encrypt_str(bool_str)

    def decrypt_boolean(self, encrypted_data: str):
        """
        Decrypt boolean
        """
        bool_str = self.decrypt_str(encrypted_data)  # Decrypt to string
        return bool_str == "True"  # Convert string back to boolean

    def encrypt_datetime(self, dt: datetime):
        """
        Encrypt datetime
        """
        dt_str = dt.isoformat()  # Convert datetime to ISO 8601 string format
        return self.encrypt_str(dt_str)

    def decrypt_datetime(self, encrypted_data: str):
        """
        Decrypt datetime
        """
        dt_str = self.decrypt_str(encrypted_data)  # Decrypt to ISO 8601 string
        return datetime.fromisoformat(dt_str)  # Convert string back to datetime
