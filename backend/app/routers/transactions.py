from datetime import datetime
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("")
def list_transactions(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    category_id: str | None = Query(default=None),
    type: models.TransactionType | None = Query(default=None),
    q: str | None = Query(default=None, description="search in description"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    q = db.query(models.Transaction).filter(models.Transaction.user_id == user.id)
    if start_date:
        q = q.filter(models.Transaction.occurred_at >= start_date)
    if end_date:
        q = q.filter(models.Transaction.occurred_at <= end_date)
    if category_id:
        q = q.filter(models.Transaction.category_id == category_id)
    if type:
        q = q.filter(models.Transaction.type == type)
    if q:
        like = f"%{q}%"
        q = q.filter(models.Transaction.description.ilike(like))

    total_items = q.count()
    total_pages = ceil(total_items / page_size) if total_items else 1
    items = (
        q.order_by(models.Transaction.occurred_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    }


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
