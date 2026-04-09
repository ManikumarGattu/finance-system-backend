from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TxnType
from app.schemas.transaction import SummaryOut, CategoryBreakdown, MonthlyTrend, WeeklySummary
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.is_deleted == False,
        Transaction.txn_type == TxnType.income
    ).scalar() or 0.0

    expenses = db.query(func.sum(Transaction.amount)).filter(
        Transaction.is_deleted == False,
        Transaction.txn_type == TxnType.expense
    ).scalar() or 0.0

    count = db.query(Transaction).filter(Transaction.is_deleted == False).count()

    return {
        "total_income":       round(income, 2),
        "total_expenses":     round(expenses, 2),
        "net_balance":        round(income - expenses, 2),
        "total_transactions": count,
    }


@router.get("/category-breakdown", response_model=list[CategoryBreakdown])
def category_breakdown(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(
        Transaction.category,
        Transaction.txn_type,
        func.sum(Transaction.amount).label("total")
    ).filter(Transaction.is_deleted == False
    ).group_by(Transaction.category, Transaction.txn_type).all()

    return [{"category": r.category, "txn_type": r.txn_type, "total": round(r.total, 2)} for r in rows]


@router.get("/monthly-trends", response_model=list[MonthlyTrend])
def monthly_trends(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(
        func.date_format(Transaction.txn_date, "%Y-%m").label("month"),
        Transaction.txn_type,
        func.sum(Transaction.amount).label("total")
    ).filter(Transaction.is_deleted == False
    ).group_by("month", Transaction.txn_type).order_by("month").all()

    result = {}
    for r in rows:
        if r.month not in result:
            result[r.month] = {"month": r.month, "income": 0.0, "expenses": 0.0}
        if r.txn_type == TxnType.income:
            result[r.month]["income"] = round(r.total, 2)
        else:
            result[r.month]["expenses"] = round(r.total, 2)
    return list(result.values())


@router.get("/recent-activity")
def recent_activity(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(Transaction).filter(
        Transaction.is_deleted == False
    ).order_by(Transaction.txn_date.desc(), Transaction.created_at.desc()).limit(10).all()
    return [
        {"id": t.id, "amount": t.amount, "txn_type": t.txn_type,
         "category": t.category, "txn_date": str(t.txn_date), "notes": t.notes}
        for t in rows
    ]


@router.get("/weekly-summary", response_model=WeeklySummary)
def weekly_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    since = date.today() - timedelta(days=7)

    income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.is_deleted == False,
        Transaction.txn_type == TxnType.income,
        Transaction.txn_date >= since
    ).scalar() or 0.0

    expenses = db.query(func.sum(Transaction.amount)).filter(
        Transaction.is_deleted == False,
        Transaction.txn_type == TxnType.expense,
        Transaction.txn_date >= since
    ).scalar() or 0.0

    return {"income": round(income, 2), "expenses": round(expenses, 2), "net": round(income - expenses, 2)}