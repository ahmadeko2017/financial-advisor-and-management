from datetime import date, datetime, time, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.rate_limit import check_rate_limit

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
JAKARTA_TZ = ZoneInfo("Asia/Jakarta")
TWO_PLACES = Decimal("0.01")


def _to_decimal(value: Decimal | None) -> Decimal:
    return (value or Decimal("0")).quantize(TWO_PLACES)


def _resolve_period(
    start_date: Optional[date],
    end_date: Optional[date],
) -> tuple[datetime, datetime, date, date]:
    now_local = datetime.now(JAKARTA_TZ)
    start_date_local = start_date or now_local.replace(day=1).date()
    end_date_local = end_date or now_local.date()

    if start_date_local > end_date_local:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before or equal to end_date",
        )

    start_dt = datetime.combine(start_date_local, time.min, tzinfo=JAKARTA_TZ).astimezone(timezone.utc)
    end_dt = datetime.combine(end_date_local, time(23, 59, 59), tzinfo=JAKARTA_TZ).astimezone(timezone.utc)
    return start_dt, end_dt, start_date_local, end_date_local


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(
    start_date: date | None = Query(default=None, description="YYYY-MM-DD (Asia/Jakarta)"),
    end_date: date | None = Query(default=None, description="YYYY-MM-DD (Asia/Jakarta)"),
    top_limit: int = Query(default=5, ge=1, le=10, description="Max top categories to return"),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    check_rate_limit(user.id, "dashboard:summary")
    start, end, start_date_local, end_date_local = _resolve_period(start_date, end_date)

    base_q = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == user.id,
            models.Transaction.occurred_at >= start,
            models.Transaction.occurred_at <= end,
        )
    )

    income = (
        base_q.filter(models.Transaction.type == models.TransactionType.income)
        .with_entities(func.coalesce(func.sum(models.Transaction.amount), 0))
        .scalar()
    )
    expense = (
        base_q.filter(models.Transaction.type == models.TransactionType.expense)
        .with_entities(func.coalesce(func.sum(models.Transaction.amount), 0))
        .scalar()
    )

    top_q = (
        db.query(
            models.Transaction.category_id,
            func.coalesce(models.Category.name, "Uncategorized").label("name"),
            func.coalesce(func.sum(models.Transaction.amount), 0).label("total"),
            func.coalesce(models.Category.type, models.Transaction.type).label("type"),
        )
        .join(models.Category, models.Category.id == models.Transaction.category_id, isouter=True)
        .filter(
            models.Transaction.user_id == user.id,
            models.Transaction.occurred_at >= start,
            models.Transaction.occurred_at <= end,
            models.Transaction.type == models.TransactionType.expense,
        )
        .group_by(
            models.Transaction.category_id,
            models.Category.name,
            models.Category.type,
            models.Transaction.type,
        )
        .order_by(func.sum(models.Transaction.amount).desc())
        .limit(top_limit)
        .all()
    )

    income_dec = _to_decimal(income)
    expense_dec = _to_decimal(expense)
    balance_dec = _to_decimal(income_dec - expense_dec)

    return schemas.DashboardSummary(
        period=schemas.DashboardPeriod(start_date=start_date_local, end_date=end_date_local),
        totals=schemas.DashboardTotals(
            income=income_dec,
            expense=expense_dec,
            balance=balance_dec,
        ),
        top_categories=[
            schemas.DashboardTopCategory(
                category_id=row.category_id,
                name=row.name,
                amount=_to_decimal(row.total),
                type=row.type,
            )
            for row in top_q
        ],
        currency="IDR",
    )
