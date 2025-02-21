from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.payment import TransactionType, CryptoType

class TransactionCreate(BaseModel):
    amount: float
    transaction_type: TransactionType
    crypto_type: CryptoType
    tx_hash: Optional[str] = None

class Transaction(TransactionCreate):
    id: str
    user_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
