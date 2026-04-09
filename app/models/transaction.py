import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base


class TxnType(str, enum.Enum):
    income  = "income"
    expense = "expense"


class Transaction(Base):
    __tablename__ = "transactions"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount     = Column(Float,          nullable=False)
    txn_type   = Column(SAEnum(TxnType), nullable=False)
    category   = Column(String(100),    nullable=False)
    txn_date   = Column(Date,           nullable=False, default=date.today)
    notes      = Column(Text,           nullable=True)
    is_deleted = Column(Boolean,        default=False, nullable=False)
    created_at = Column(DateTime,       default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="transactions")