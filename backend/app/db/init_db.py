from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.base import MainBase, PaymentBase, AnalyticsBase
from app.models.base import main_engine, payment_engine, analytics_engine

async def init_db():
    """Initialize database schemas"""
    async with main_engine.begin() as conn:
        await conn.run_sync(MainBase.metadata.create_all)
    
    async with payment_engine.begin() as conn:
        await conn.run_sync(PaymentBase.metadata.create_all)
    
    async with analytics_engine.begin() as conn:
        await conn.run_sync(AnalyticsBase.metadata.create_all)
