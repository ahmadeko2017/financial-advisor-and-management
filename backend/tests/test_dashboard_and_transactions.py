from datetime import datetime, date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app, seed_default_categories
from app.database import Base, engine
from app.routers import dashboard
from app import models

client = TestClient(app)


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_default_categories()
    dashboard._summary_cache.clear()  # type: ignore[attr-defined]


def teardown_module():
    Base.metadata.drop_all(bind=engine)


def _auth_headers(email: str | None = None) -> dict[str, str]:
    email = email or f"user_{uuid4().hex}@example.com"
    payload = {"email": email, "password": "secret123"}
    client.post("/auth/register", json=payload)
    res = client.post("/auth/login", json=payload)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _make_account(headers: dict[str, str]) -> str:
    res = client.post("/accounts", json={"name": "Cash", "type": "cash", "currency": "IDR"}, headers=headers)
    return res.json()["id"]


def test_dashboard_summary_totals_and_top_category():
    headers = _auth_headers()
    account_id = _make_account(headers)

    # Create expense category and transactions
    res = client.post("/categories", json={"name": "Food", "type": "expense"}, headers=headers)
    category_id = res.json()["id"]
    now_iso = datetime.utcnow().isoformat()

    client.post(
        "/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "type": "income",
            "amount": 50000,
            "currency": "IDR",
            "description": "Salary",
            "occurred_at": now_iso,
            "status": models.TransactionStatus.confirmed,
            "source": "manual",
        },
        headers=headers,
    )

    client.post(
        "/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "type": "expense",
            "amount": 20000,
            "currency": "IDR",
            "description": "Lunch",
            "occurred_at": now_iso,
            "status": models.TransactionStatus.confirmed,
            "source": "manual",
        },
        headers=headers,
    )

    today = date.today().isoformat()
    res = client.get(
        "/dashboard/summary",
        params={"start_date": today, "end_date": today},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    to_dec = lambda v: Decimal(str(v))
    assert to_dec(data["totals"]["income"]) == Decimal("50000.00")
    assert to_dec(data["totals"]["expense"]) == Decimal("20000.00")
    assert to_dec(data["totals"]["balance"]) == Decimal("30000.00")
    assert data["currency"] == "IDR"
    assert data["top_categories"]
    top = data["top_categories"][0]
    assert top["category_id"] == category_id
    assert to_dec(top["amount"]) == Decimal("20000.00")


def test_transactions_pagination_warnings_and_filter():
    headers = _auth_headers(email="pager@example.com")
    account_id = _make_account(headers)

    # Create category and one transaction
    res = client.post("/categories", json={"name": "Coffee", "type": "expense"}, headers=headers)
    category_id = res.json()["id"]
    now_iso = datetime.utcnow().isoformat()
    client.post(
        "/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "type": "expense",
            "amount": 15000,
            "currency": "IDR",
            "description": "Coffee Morning",
            "occurred_at": now_iso,
            "status": models.TransactionStatus.confirmed,
            "source": "manual",
        },
        headers=headers,
    )

    res = client.get(
        "/transactions",
        params={"page": 0, "page_size": 150, "q": "Coffee"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 100
    assert data["pagination"]["total_items"] == 1
    assert data["pagination"]["total_pages"] == 1
    assert data["pagination"]["warnings"]
    assert any("page_size capped" in w for w in data["pagination"]["warnings"])
    assert len(data["items"]) == 1
    assert data["items"][0]["description"] == "Coffee Morning"


def test_dashboard_invalid_period_returns_validation_error():
    headers = _auth_headers(email="period@example.com")
    res = client.get(
        "/dashboard/summary",
        params={"start_date": "2025-02-10", "end_date": "2025-02-01"},
        headers=headers,
    )
    assert res.status_code == 400
    data = res.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "start_date" in data["message"]
    # trace_id should be present for debugging
    assert "trace_id" in data
