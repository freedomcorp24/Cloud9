from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Create bases for different databases
MainBase = declarative_base()
PaymentBase = declarative_base()
AnalyticsBase = declarative_base()

# Create async engines
main_engine = create_async_engine(settings.MAIN_DATABASE_URL, echo=True)
payment_engine = create_async_engine(settings.PAYMENT_DATABASE_URL, echo=True)
analytics_engine = create_async_engine(settings.ANALYTICS_DATABASE_URL, echo=True)

# Create async sessions
AsyncMainSession = sessionmaker(
    main_engine, class_=AsyncSession, expire_on_commit=False
)
AsyncPaymentSession = sessionmaker(
    payment_engine, class_=AsyncSession, expire_on_commit=False
)
AsyncAnalyticsSession = sessionmaker(
    analytics_engine, class_=AsyncSession, expire_on_commit=False
)
