from datetime import datetime, timezone
import calendar
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _month_bounds(period: Optional[str]) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month
    if period:
        try:
            parts = period.split("-")
            if len(parts) == 2:
                year = int(parts[0])
                month = int(parts[1])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid period format, expected YYYY-MM")
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    last_day = calendar.monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    return start, end


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(
    period: str | None = Query(default=None, description="YYYY-MM"),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if start_date or end_date:
        if not start_date or not end_date:
            raise HTTPException(status_code=400, detail="start_date and end_date both required if one is provided")
        start, end = start_date, end_date
    else:
        start, end = _month_bounds(period)

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
        )
        .join(models.Category, models.Category.id == models.Transaction.category_id, isouter=True)
        .filter(
            models.Transaction.user_id == user.id,
            models.Transaction.occurred_at >= start,
            models.Transaction.occurred_at <= end,
            models.Transaction.type == models.TransactionType.expense,
        )
        .group_by(models.Transaction.category_id, models.Category.name)
        .order_by(func.sum(models.Transaction.amount).desc())
        .limit(5)
        .all()
    )

    return schemas.DashboardSummary(
        period=period or f"{start.year}-{start.month:02d}",
        start_date=start,
        end_date=end,
        income=float(income or 0),
        expense=float(expense or 0),
        balance=float((income or 0) - (expense or 0)),
        top_categories=[
          schemas.CategoryTotal(category_id=row.category_id, name=row.name, total=float(row.total or 0))
          for row in top_q
        ],
    )
