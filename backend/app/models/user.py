from sqlalchemy import Boolean, Column, String, Enum, JSON
from app.models.base import MainBase
import enum

class UserType(str, enum.Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"

class User(MainBase):
    __tablename__ = "users"

    public_username = Column(String, unique=True, index=True)
    private_username = Column(String, unique=True, primary_key=True)
    hashed_password = Column(String)
    pgp_key = Column(String, nullable=True)
    welcome_phrase = Column(String, nullable=True)
    user_type = Column(Enum(UserType))
    country = Column(String)
    preferred_fiat = Column(String, default="USD")
    accepted_crypto = Column(JSON, nullable=True)  # For vendors only
    is_active = Column(Boolean, default=True)
    vendor_bond_paid = Column(Boolean, default=False)  # For vendors only
