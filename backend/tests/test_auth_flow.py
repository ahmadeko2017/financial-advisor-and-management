from datetime import datetime

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app, seed_default_categories
from app.database import Base, SessionLocal, engine
from app import models


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_default_categories()


@pytest.mark.anyio
async def test_register_login_and_crud_accounts_transactions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
    # Register
        register_payload = {"email": "user@example.com", "password": "secret123"}
        res = await client.post("/auth/register", json=register_payload)
        assert res.status_code == 201

        # Login
        res = await client.post("/auth/login", json=register_payload)
        assert res.status_code == 200
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create account
        res = await client.post("/accounts", json={"name": "Cash", "type": "cash", "currency": "IDR"}, headers=headers)
        assert res.status_code == 201
        account_id = res.json()["id"]

        # List categories (should include defaults if seeded in future; currently empty)
        res = await client.get("/categories", headers=headers)
        assert res.status_code == 200

        # Create category
        res = await client.post("/categories", json={"name": "Makan", "type": "expense"}, headers=headers)
        assert res.status_code == 201
        category_id = res.json()["id"]

        # Create transaction
        tx_payload = {
            "account_id": account_id,
            "category_id": category_id,
            "type": "expense",
            "amount": 15000,
            "currency": "IDR",
            "description": "Lunch",
            "occurred_at": datetime.utcnow().isoformat(),
            "status": "confirmed",
            "source": "manual",
        }
        res = await client.post("/transactions", json=tx_payload, headers=headers)
        assert res.status_code == 201

        # List transactions
        res = await client.get("/transactions", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["pagination"]["total_items"] == 1
        assert data["items"][0]["description"] == "Lunch"
