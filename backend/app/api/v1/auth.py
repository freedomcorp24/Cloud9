from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta

from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import User, UserType
from app.api.deps import get_main_db

router = APIRouter()

@router.post("/register")
async def register(
    *,
    db: AsyncSession = Depends(get_main_db),
    public_username: str,
    private_username: str,
    password: str,
    user_type: UserType,
    country: str,
    welcome_phrase: str = None,
    pgp_key: str = None,
    preferred_fiat: str = "USD"
):
    # Check if usernames are taken
    existing_public = await db.execute(
        select(User).where(User.public_username == public_username)
    )
    existing_private = await db.execute(
        select(User).where(User.private_username == private_username)
    )
    
    if existing_public.scalar_one_or_none() or existing_private.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    user = User(
        public_username=public_username,
        private_username=private_username,
        hashed_password=get_password_hash(password),
        user_type=user_type,
        country=country,
        welcome_phrase=welcome_phrase,
        pgp_key=pgp_key,
        preferred_fiat=preferred_fiat,
        vendor_bond_paid=False if user_type == UserType.VENDOR else None
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {"message": "User registered successfully"}

@router.post("/token")
async def login(
    db: AsyncSession = Depends(get_main_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await db.execute(
        select(User).where(User.private_username == form_data.username)
    )
    user = user.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.private_username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "welcome_phrase": user.welcome_phrase
    }
