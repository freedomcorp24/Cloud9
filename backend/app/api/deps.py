from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.base import AsyncMainSession, AsyncPaymentSession, AsyncAnalyticsSession
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_main_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncMainSession() as session:
        yield session

async def get_payment_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncPaymentSession() as session:
        yield session

async def get_analytics_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncAnalyticsSession() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_main_db)
) -> Optional[dict]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await db.execute(
        select(User).where(User.private_username == username)
    )
    user = user.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user
