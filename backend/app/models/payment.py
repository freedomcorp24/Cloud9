from sqlalchemy import Column, String, Float, JSON, ForeignKey, DateTime, Enum
from app.models.base import PaymentBase
import enum
from datetime import datetime

class CryptoType(str, enum.Enum):
    BTC = "btc"
    XMR = "xmr"
    USDT = "usdt"

class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    VENDOR_BOND = "vendor_bond"

class Transaction(PaymentBase):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.private_username"))
    transaction_type = Column(Enum(TransactionType))
    crypto_type = Column(Enum(CryptoType))
    amount = Column(Float)
    status = Column(String)  # pending, completed, failed
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON)  # Additional transaction details
    address = Column(String)  # Crypto address used
    tx_hash = Column(String, nullable=True)  # Blockchain transaction hash
