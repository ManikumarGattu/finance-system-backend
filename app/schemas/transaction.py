from pydantic import BaseModel, Field
from datetime import datetime
from datetime import date as Date
from typing import Optional
import enum


class TxnType(str, enum.Enum):
    income  = "income"
    expense = "expense"


class TransactionCreate(BaseModel):
    amount:   float
    txn_type: TxnType
    category: str     = Field(..., min_length=2, max_length=100)
    txn_date: Date
    notes:    Optional[str] = None


class TransactionUpdate(BaseModel):
    amount:   Optional[float]   = None
    txn_type: Optional[TxnType] = None
    category: Optional[str]     = None
    txn_date: Optional[Date]    = None
    notes:    Optional[str]     = None


class TransactionOut(BaseModel):
    id:         int
    user_id:    int
    amount:     float
    txn_type:   TxnType
    category:   str
    txn_date:   Date
    notes:      Optional[str]
    is_deleted: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTransactions(BaseModel):
    total: int
    page:  int
    size:  int
    data:  list[TransactionOut]


class SummaryOut(BaseModel):
    total_income:       float
    total_expenses:     float
    net_balance:        float
    total_transactions: int


class CategoryBreakdown(BaseModel):
    category: str
    txn_type: TxnType
    total:    float


class MonthlyTrend(BaseModel):
    month:    str
    income:   float
    expenses: float


class WeeklySummary(BaseModel):
    income:   float
    expenses: float
    net:      float