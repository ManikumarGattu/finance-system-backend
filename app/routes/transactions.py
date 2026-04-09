from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TxnType
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate,
    TransactionOut, PaginatedTransactions
)
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(
    payload:      TransactionCreate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(require_admin)
):
    txn = Transaction(
        user_id  = current_user.id,
        amount   = payload.amount,
        txn_type = payload.txn_type,
        category = payload.category,
        txn_date = payload.txn_date,
        notes    = payload.notes,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


@router.get("", response_model=PaginatedTransactions)
def get_transactions(
    page:      int            = Query(1,   ge=1),
    size:      int            = Query(10,  ge=1, le=100),
    txn_type:  Optional[TxnType] = Query(None),
    category:  Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to:   Optional[date] = Query(None),
    db:        Session        = Depends(get_db),
    _:         User           = Depends(get_current_user)
):
    q = db.query(Transaction).filter(Transaction.is_deleted == False)
    if txn_type:  q = q.filter(Transaction.txn_type == txn_type)
    if category:  q = q.filter(Transaction.category.ilike(f"%{category}%"))
    if date_from: q = q.filter(Transaction.txn_date >= date_from)
    if date_to:   q = q.filter(Transaction.txn_date <= date_to)

    total = q.count()
    data  = q.order_by(Transaction.txn_date.desc()).offset((page-1)*size).limit(size).all()
    return {"total": total, "page": page, "size": size, "data": data}


@router.get("/{txn_id}", response_model=TransactionOut)
def get_transaction(txn_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    txn = db.query(Transaction).filter(Transaction.id == txn_id, Transaction.is_deleted == False).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.patch("/{txn_id}", response_model=TransactionOut)
def update_transaction(txn_id: int, payload: TransactionUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    txn = db.query(Transaction).filter(Transaction.id == txn_id, Transaction.is_deleted == False).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(txn, k, v)
    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/{txn_id}", status_code=200)
def soft_delete(txn_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    txn = db.query(Transaction).filter(Transaction.id == txn_id, Transaction.is_deleted == False).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    txn.is_deleted = True
    db.commit()
    return {"message": "Transaction deleted successfully"}