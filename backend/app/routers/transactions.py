from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[schemas.TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
):
    q = db.query(models.Transaction).filter(models.Transaction.user_id == user.id)
    if start_date:
        q = q.filter(models.Transaction.occurred_at >= start_date)
    if end_date:
        q = q.filter(models.Transaction.occurred_at <= end_date)
    return q.order_by(models.Transaction.occurred_at.desc()).all()


@router.post("", response_model=schemas.TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    account = (
        db.query(models.Account)
        .filter(models.Account.user_id == user.id, models.Account.id == payload.account_id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account")

    if payload.category_id:
        category = (
            db.query(models.Category)
            .filter(
                (models.Category.user_id == None) | (models.Category.user_id == user.id),  # noqa: E711
                models.Category.id == payload.category_id,
            )
            .first()
        )
        if not category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category")

    tx = models.Transaction(
        user_id=user.id,
        account_id=payload.account_id,
        category_id=payload.category_id,
        type=payload.type,
        amount=payload.amount,
        currency=payload.currency,
        description=payload.description,
        occurred_at=payload.occurred_at,
        source=payload.source,
        status=payload.status,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
