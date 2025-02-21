from sqlalchemy import Column, String, Float, JSON, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from app.models.base import MainBase
import enum

class DeliveryType(str, enum.Enum):
    INSTANT = "instant"
    MAIL = "mail"
    PICKUP = "pickup"

class MeasurementUnit(str, enum.Enum):
    ML = "ml"
    GRAMS = "g"
    OUNCES = "oz"
    KILOS = "kg"
    PARTS = "parts"

class Product(MainBase):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    vendor_id = Column(String, ForeignKey("users.private_username"))
    name = Column(String, index=True)
    category = Column(String, index=True)
    type = Column(String, index=True)
    description = Column(String)
    base_price = Column(Float)  # In vendor's preferred fiat
    bulk_discounts = Column(JSON, nullable=True)  # {"quantity": "discount_percentage"}
    measurement_value = Column(Float)
    measurement_unit = Column(Enum(MeasurementUnit))
    accepted_crypto = Column(JSON)  # List of accepted cryptocurrencies
    delivery_options = Column(JSON)  # {"type": {"price": float, "details": dict}}
    images = Column(JSON)  # List of image URLs
    is_active = Column(Boolean, default=True)
    
    vendor = relationship("User", back_populates="products")
