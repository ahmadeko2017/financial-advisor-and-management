import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app import models
from app.ai.category_classifier import PredictionResult


@pytest.mark.anyio
async def test_predict_category_no_model_returns_null():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # register + login
        cred = {"email": "aiuser@example.com", "password": "secret123"}
        await client.post("/auth/register", json=cred)
        res = await client.post("/auth/login", json=cred)
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = await client.post(
            "/ai/predict_category",
            headers=headers,
            json={"description": "Makan siang nasi padang", "amount": 45000, "type": "expense"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["category_id"] is None
        assert data["confidence"] == 0.0


@pytest.mark.anyio
async def test_transaction_auto_predict(monkeypatch):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        cred = {"email": "predict@example.com", "password": "secret123"}
        await client.post("/auth/register", json=cred)
        res = await client.post("/auth/login", json=cred)
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create account
        res = await client.post("/accounts", json={"name": "Cash", "type": "cash", "currency": "IDR"}, headers=headers)
        account_id = res.json()["id"]

        # Create category to satisfy FK when auto-assigning prediction
        res = await client.post("/categories", json={"name": "AI Food", "type": "expense"}, headers=headers)
        category_id = res.json()["id"]

        # Patch predict to return deterministic result
        dummy_result = PredictionResult(category_id=category_id, confidence=0.9, top_k=[(category_id, 0.9)], model_version="vtest")

        def fake_load_model():
            return object()

        def fake_predict(description, model=None):
            return dummy_result

        monkeypatch.setattr("app.routers.transactions.load_model", fake_load_model)
        monkeypatch.setattr("app.routers.transactions.predict_category", fake_predict)

        payload = {
            "account_id": account_id,
            "type": "expense",
            "amount": 10000,
            "currency": "IDR",
            "description": "Test auto predict",
            "occurred_at": "2025-02-01T10:00:00Z",
            "status": "confirmed",
        }
        res = await client.post("/transactions", json=payload, headers=headers)
        assert res.status_code == 201
        data = res.json()
        assert data["predicted_category_id"] == "dummy-cat"
        assert data["predicted_confidence"] == pytest.approx(0.9)
        assert data["category_id"] == "dummy-cat"
        assert data["status"] == models.TransactionStatus.predicted
