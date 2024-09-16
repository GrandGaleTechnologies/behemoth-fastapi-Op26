from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.common.encryption import EncryptionManager
from app.core.database import DBBase
from app.core.settings import get_settings

# Globals
settings = get_settings()
encryption_manager = EncryptionManager(key=settings.ENCRYPTION_KEY)


class Offense(DBBase):
    """
    Database model for offenses
    """

    __tablename__ = "offenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(String, nullable=False)


class POI(DBBase):
    """
    Database model for persons of interest
    """

    __tablename__ = "pois"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pfp_url = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    alias = Column(String, nullable=False)
    dob = Column(String, nullable=True)
    state_of_origin = Column(String, nullable=True)
    lga_of_origin = Column(String, nullable=True)
    district_of_origin = Column(String, nullable=True)
    pob = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    religion = Column(String, nullable=True)
    political_affiliation = Column(String, nullable=True)
    tribal_union = Column(String, nullable=True)
    last_seen_date = Column(String, nullable=True)
    last_seen_time = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    is_completed = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    is_pinned = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )

    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(
        String,
        nullable=False,
        default=encryption_manager.encrypt_datetime(datetime.now()),
    )
    deleted_at = Column(String, nullable=True)

    application: Mapped["POIApplicationProcess"] = relationship(
        "POIApplicationProcess", backref="pois"
    )
    veteran_status: Mapped["VeteranStatus"] = relationship(
        "VeteranStatus", backref="pois"
    )
    fingerprint: Mapped["Fingerprint"] = relationship("Fingerprint", backref="pois")

    id_documents: Mapped[list["IDDocument"]] = relationship(
        "IDDocument", backref="pois"
    )
    gsm_numbers: Mapped[list["GSMNumber"]] = relationship("GSMNumber", backref="pois")
    residential_addresses: Mapped[list["ResidentialAddress"]] = relationship(
        "ResidentialAddress", backref="pois"
    )
    known_associates: Mapped[list["KnownAssociate"]] = relationship(
        "KnownAssociate", backref="pois"
    )
    employment_history: Mapped[list["EmploymentHistory"]] = relationship(
        "EmploymentHistory", backref="pois"
    )
    educational_background: Mapped[list["EducationalBackground"]] = relationship(
        "EducationalBackground", backref="pois"
    )
    offenses: Mapped[list["POIOffense"]] = relationship("POIOffense", backref="pois")
    frequented_spots: Mapped[list["FrequentedSpot"]] = relationship(
        "FrequentedSpot", backref="pois"
    )


class IDDocument(DBBase):
    """
    Database model for ID Documents
    """

    __tablename__ = "id_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(Integer, ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    id_number = Column(String, nullable=False)

    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(
        String,
        nullable=False,
        default=encryption_manager.encrypt_datetime(datetime.now()),
    )
    deleted_at = Column(String, nullable=True)


class GSMNumber(DBBase):
    """
    Database model for known poi gsm numbers
    """

    __tablename__ = "gsm_numbers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(Integer, ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    service_provider = Column(String, nullable=False)
    number = Column(String, nullable=False)
    last_call_date = Column(String, nullable=True)
    last_call_time = Column(String, nullable=True)
    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(
        String,
        nullable=False,
        default=encryption_manager.encrypt_datetime(datetime.now()),
    )
    deleted_at = Column(String, nullable=True)


class ResidentialAddress(DBBase):
    """
    Database model for residential addresses
    """

    __tablename__ = "residential_addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(Integer, ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    city = Column(String, nullable=False)
    address = Column(String, nullable=True)
    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(
        String,
        nullable=False,
        default=encryption_manager.encrypt_datetime(datetime.now()),
    )
    deleted_at = Column(String, nullable=True)


class KnownAssociate(DBBase):
    """
    Database model for known associates of the poi
    """

    __tablename__ = "known_associates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(Integer, ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String, nullable=False)
    known_gsm_numbers = Column(String, nullable=True)
    relationship = Column(String, nullable=False)
    occupation = Column(String, nullable=True)
    residential_address = Column(String, nullable=True)
    last_seen_date = Column(String, nullable=True)
    last_seen_time = Column(String, nullable=True)

    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(
        String,
        nullable=False,
        default=encryption_manager.encrypt_datetime(datetime.now()),
    )
    deleted_at = Column(String, nullable=True)


class EmploymentHistory(DBBase):
    """
    Database model for poi employment history
    """

    __tablename__ = "employment_histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(Integer, ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    company = Column(String, nullable=False)
    employment_type = Column(String, nullable=False)
    from_date = Column(String, nullable=True)
    to_date = Column(String, nullable=True)
    current_job = Column(String, nullable=False)
    description = Column(String, nullable=True)

    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(
        String,
        nullable=False,
        default=encryption_manager.encrypt_datetime(datetime.now()),
    )
    deleted_at = Column(String, nullable=True)


class VeteranStatus(DBBase):
    """
    Database model for the poi's veteran status details
    """

    __tablename__ = "veteran_statuses"

    id = Column(Integer, primary_key=True, nullable=False)
    poi_id = Column(
        Integer, ForeignKey("pois.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    is_veteran = Column(String, nullable=False)
    section = Column(String, nullable=False)
    location = Column(String, nullable=False)
    id_card = Column(String, nullable=True)
    id_card_issuer = Column(String, nullable=True)
    from_date = Column(String, nullable=True)
    to_date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(
        String,
        nullable=False,
        default=encryption_manager.encrypt_datetime(datetime.now()),
    )
    deleted_at = Column(String, nullable=True)


class EducationalBackground(DBBase):
    """
    Database model for the poi's educational background
    """

    __tablename__ = "educational_backgrounds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(Integer, ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    institute_name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    from_date = Column(String, nullable=True)
    to_date = Column(String, nullable=True)
    current_institute = Column(String, nullable=False)

    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(
        String,
        nullable=False,
        default=encryption_manager.encrypt_datetime(datetime.now()),
    )
    deleted_at = Column(String, nullable=True)


class POIOffense(DBBase):
    """
    Database model for the poi's offense
    """

    __tablename__ = "poi_offenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(Integer, ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    offense_id = Column(
        Integer, ForeignKey("offenses.id", ondelete="CASCADE"), nullable=False
    )
    case_id = Column(String, nullable=True)
    date_convicted = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    offense: Mapped[Offense] = relationship("Offense", backref="poi_offenses")
    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(
        String,
        nullable=False,
        default=encryption_manager.encrypt_datetime(datetime.now()),
    )
    deleted_at = Column(String, nullable=True)


class FrequentedSpot(DBBase):
    """
    Database model for poi frequented spots
    """

    __tablename__ = "frequented_spots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(Integer, ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    country = Column(String, nullable=False)
    state = Column(String, nullable=False)
    lga = Column(String, nullable=False)
    address = Column(String, nullable=False)
    from_date = Column(String, nullable=True)
    to_date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(
        String,
        nullable=False,
        default=encryption_manager.encrypt_datetime(datetime.now()),
    )
    deleted_at = Column(String, nullable=True)


class Fingerprint(DBBase):
    """
    Database model for poi fingerprints
    """

    __tablename__ = "fingerprints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(Integer, ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    left_thumb = Column(String, nullable=False)
    right_thumb = Column(String, nullable=False)
    left_pointer = Column(String, nullable=False)
    right_pointer = Column(String, nullable=False)

    is_deleted = Column(
        String, nullable=False, default=encryption_manager.encrypt_boolean(False)
    )
    edited_at = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
    deleted_at = Column(String, nullable=True)


class POIApplicationProcess(DBBase):
    """
    Database model for poi application process
    """

    __tablename__ = "poi_application_processes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poi_id = Column(Integer, ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    other_profile = Column(
        String, default=encryption_manager.encrypt_boolean(False), nullable=False
    )
    employment = Column(
        String, default=encryption_manager.encrypt_boolean(False), nullable=False
    )
    veteran_status = Column(
        String, default=encryption_manager.encrypt_boolean(False), nullable=False
    )
    education = Column(
        String, default=encryption_manager.encrypt_boolean(False), nullable=False
    )
    case_file = Column(
        String, default=encryption_manager.encrypt_boolean(False), nullable=False
    )
    fingerprints = Column(
        String, default=encryption_manager.encrypt_boolean(False), nullable=False
    )
