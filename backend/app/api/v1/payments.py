from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_user, get_payment_db, get_rate_limiter, get_double_spend_preventer
from app.core.rate_limit import PaymentRateLimiter, DoubleSpendingPreventer
from app.models.user import User
from app.models.payment import Transaction
from app.schemas.payment import TransactionCreate

router = APIRouter()

@router.post("/transaction", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_payment_db),
    rate_limiter: PaymentRateLimiter = Depends(get_rate_limiter),
    double_spend_preventer: DoubleSpendingPreventer = Depends(get_double_spend_preventer)
):
    """Create a new transaction with rate limiting and security checks"""
    # Check rate limits
    await rate_limiter.check_transaction_limit(
        current_user.private_username,
        transaction.transaction_type,
        transaction.amount
    )
    
    # Prevent double-spending
    if transaction.tx_hash:
        if not await double_spend_preventer.check_and_lock_transaction(
            transaction.tx_hash,
            current_user.private_username
        ):
            raise HTTPException(
                status_code=400,
                detail="Transaction already processed"
            )
    
    # Create transaction
    db_transaction = Transaction(
        user_id=current_user.private_username,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        crypto_type=transaction.crypto_type,
        status="pending",
        tx_hash=transaction.tx_hash
    )
    
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    
    return db_transaction

@router.get("/transactions")
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_payment_db)
):
    """Get user's transactions"""
    transactions = await db.execute(
        select(Transaction).where(
            Transaction.user_id == current_user.private_username
        )
    )
    return transactions.scalars().all()
