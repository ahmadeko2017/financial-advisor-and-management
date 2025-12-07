from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app, seed_default_categories
from app.database import Base, engine


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_default_categories()


def teardown_module():
    Base.metadata.drop_all(bind=engine)


async def _auth_headers(client: AsyncClient, email: str | None = None) -> dict[str, str]:
    email = email or f"neg_{uuid4().hex}@example.com"
    payload = {"email": email, "password": "secret123"}
    await client.post("/auth/register", json=payload)
    res = await client.post("/auth/login", json=payload)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_unauthorized_transactions_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/transactions")
        assert res.status_code == 401
        body = res.json()
        assert body["code"] == "UNAUTHORIZED"


@pytest.mark.anyio
async def test_login_wrong_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        email = f"wrong_{uuid4().hex}@example.com"
        await client.post("/auth/register", json={"email": email, "password": "secret123"})

        res = await client.post("/auth/login", json={"email": email, "password": "badpass"})
        assert res.status_code == 401
        body = res.json()
        assert body["code"] == "UNAUTHORIZED"
        assert "Invalid credentials" in body["message"]


@pytest.mark.anyio
async def test_create_transaction_invalid_account():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        headers = await _auth_headers(client)

        payload = {
            "account_id": "non-existent",
            "category_id": None,
            "type": "expense",
            "amount": 1000,
            "currency": "IDR",
            "description": "Invalid account test",
            "occurred_at": datetime.utcnow().isoformat(),
            "status": "confirmed",
            "source": "manual",
        }
        res = await client.post("/transactions", json=payload, headers=headers)
        assert res.status_code == 400
        body = res.json()
        assert body["code"] == "VALIDATION_ERROR"
        assert "Invalid account" in body["message"]
