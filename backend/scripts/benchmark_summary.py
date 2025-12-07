"""
Quick EXPLAIN/benchmark helper for dashboard summary queries.

Usage:
    DATABASE_URL=postgresql+psycopg2://user:pass@host/db python scripts/benchmark_summary.py <user_id> [start_date] [end_date]

Defaults:
    - start_date: first day of current month (local Jakarta)
    - end_date: today
Outputs:
    - EXPLAIN ANALYZE for expense aggregation by category
    - Total income/expense sums timing
"""

from __future__ import annotations

import sys
from datetime import datetime, date
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, text

from app.config import get_settings


def main():
    if len(sys.argv) < 2:
        print("usage: python scripts/benchmark_summary.py <user_id> [start_date] [end_date]")
        sys.exit(1)

    user_id = sys.argv[1]
    jakarta = ZoneInfo("Asia/Jakarta")
    today = datetime.now(jakarta).date()
    start_date = date.fromisoformat(sys.argv[2]) if len(sys.argv) >= 3 else today.replace(day=1)
    end_date = date.fromisoformat(sys.argv[3]) if len(sys.argv) >= 4 else today

    settings = get_settings()
    engine = create_engine(settings.database_url)

    start_ts = datetime.combine(start_date, datetime.min.time(), jakarta).astimezone(ZoneInfo("UTC"))
    end_ts = datetime.combine(end_date, datetime.max.time(), jakarta).astimezone(ZoneInfo("UTC"))

    with engine.connect() as conn:
        print("=== EXPLAIN top categories (expense) ===")
        explain = conn.execute(
            text(
                """
                EXPLAIN ANALYZE
                SELECT t.category_id, COALESCE(c.name, 'Uncategorized') AS name, SUM(t.amount) as total
                FROM transactions t
                LEFT JOIN categories c ON c.id = t.category_id
                WHERE t.user_id = :user_id
                  AND t.occurred_at BETWEEN :start AND :end
                  AND t.type = 'expense'
                GROUP BY t.category_id, c.name
                ORDER BY SUM(t.amount) DESC
                LIMIT 5;
                """
            ),
            {"user_id": user_id, "start": start_ts, "end": end_ts},
        )
        for row in explain:
            print(row[0])

        print("\n=== EXPLAIN totals income/expense ===")
        explain2 = conn.execute(
            text(
                """
                EXPLAIN ANALYZE
                SELECT
                  COALESCE(SUM(CASE WHEN type = 'income' THEN amount END), 0) AS income,
                  COALESCE(SUM(CASE WHEN type = 'expense' THEN amount END), 0) AS expense
                FROM transactions
                WHERE user_id = :user_id
                  AND occurred_at BETWEEN :start AND :end;
                """
            ),
            {"user_id": user_id, "start": start_ts, "end": end_ts},
        )
        for row in explain2:
            print(row[0])


if __name__ == "__main__":
    main()
