from datetime import date, datetime, time, timezone
from math import ceil
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])
JAKARTA_TZ = ZoneInfo("Asia/Jakarta")
MAX_PAGE_SIZE = 100


def _sanitize_search(term: str | None) -> str | None:
    if not term:
        return None
    term = term.strip()
    if not term:
        return None
    if len(term) > 100:
        term = term[:100]
    return term


def _build_bounds(start_date: date | None, end_date: date | None) -> tuple[datetime | None, datetime | None]:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before or equal to end_date")

    start_dt = (
        datetime.combine(start_date, time.min, tzinfo=JAKARTA_TZ).astimezone(timezone.utc)
        if start_date
        else None
    )
    end_dt = (
        datetime.combine(end_date, time(23, 59, 59), tzinfo=JAKARTA_TZ).astimezone(timezone.utc)
        if end_date
        else None
    )
    return start_dt, end_dt


@router.get("", response_model=schemas.TransactionsPage)
def list_transactions(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
    start_date: date | None = Query(default=None, description="YYYY-MM-DD (Asia/Jakarta, inclusive)"),
    end_date: date | None = Query(default=None, description="YYYY-MM-DD (Asia/Jakarta, inclusive)"),
    category_id: str | None = Query(default=None),
    type: models.TransactionType | None = Query(default=None),
    q: str | None = Query(default=None, description="search in description"),
    page: int = Query(default=1, description="Page number (default 1)"),
    page_size: int = Query(default=20, description="Page size (default 20, max 100)"),
):
    warnings: list[str] = []
    if page < 1:
        page = 1
        warnings.append("page reset to 1")
    if page_size < 1:
        page_size = 20
        warnings.append("page_size reset to default 20")
    if page_size > MAX_PAGE_SIZE:
        page_size = MAX_PAGE_SIZE
        warnings.append(f"page_size capped at {MAX_PAGE_SIZE}")

    start_dt, end_dt = _build_bounds(start_date, end_date)
    search_term = _sanitize_search(q)

    tx_query = db.query(models.Transaction).filter(models.Transaction.user_id == user.id)
    if start_dt:
        tx_query = tx_query.filter(models.Transaction.occurred_at >= start_dt)
    if end_dt:
        tx_query = tx_query.filter(models.Transaction.occurred_at <= end_dt)
    if category_id:
        tx_query = tx_query.filter(models.Transaction.category_id == category_id)
    if type:
        tx_query = tx_query.filter(models.Transaction.type == type)
    if search_term:
        like = f"%{search_term}%"
        tx_query = tx_query.filter(models.Transaction.description.ilike(like))

    total_items = tx_query.count()
    total_pages = ceil(total_items / page_size) if total_items else 0
    items = (
        tx_query.order_by(models.Transaction.occurred_at.desc())
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
            "warnings": warnings or None,
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
