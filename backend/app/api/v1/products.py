from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_main_db, get_current_user
from app.models.product import Product, DeliveryType, MeasurementUnit
from app.models.user import User, UserType
from app.search.elastic import index_product, search_products

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    *,
    db: AsyncSession = Depends(get_main_db),
    current_user: User = Depends(get_current_user),
    name: str,
    category: str,
    type: str,
    description: str,
    base_price: float,
    measurement_value: float,
    measurement_unit: MeasurementUnit,
    accepted_crypto: List[str],
    delivery_options: dict,
    bulk_discounts: Optional[dict] = None,
    images: Optional[List[str]] = None
):
    if current_user.user_type != UserType.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can create products"
        )
    
    if not current_user.vendor_bond_paid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor bond must be paid before listing products"
        )
    
    product = Product(
        vendor_id=current_user.private_username,
        name=name,
        category=category,
        type=type,
        description=description,
        base_price=base_price,
        measurement_value=measurement_value,
        measurement_unit=measurement_unit,
        accepted_crypto=accepted_crypto,
        delivery_options=delivery_options,
        bulk_discounts=bulk_discounts,
        images=images
    )
    
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    # Index product in Elasticsearch
    await index_product({
        "id": product.id,
        "name": product.name,
        "vendor_id": product.vendor_id,
        "vendor_name": current_user.public_username,
        "category": product.category,
        "type": product.type,
        "description": product.description,
        "base_price": product.base_price,
        "measurement_unit": product.measurement_unit,
        "delivery_options": list(product.delivery_options.keys()),
        "country": current_user.country,
        "is_active": product.is_active
    })
    
    return product

@router.get("/search")
async def search(
    query: Optional[str] = None,
    category: Optional[str] = None,
    type: Optional[str] = None,
    delivery_method: Optional[DeliveryType] = None,
    country: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius: Optional[int] = 10
):
    filters = {
        "category": category,
        "type": type,
        "delivery_options": delivery_method,
        "country": country
    }
    
    location = None
    if lat and lon:
        location = {
            "lat": lat,
            "lon": lon,
            "radius": radius
        }
    
    results = await search_products(query, filters, location)
    return results
