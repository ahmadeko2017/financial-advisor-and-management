import os
import time
from decimal import Decimal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app import models
from app.database import Base, engine
from app.routers import accounts, auth, categories, transactions, dashboard
from app.security import get_password_hash


def init_db_with_retry(attempts: int = 5, delay: float = 1.0):
    for i in range(attempts):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            seed_default_categories()
            seed_demo_data()
            return
        except OperationalError:
            if i == attempts - 1:
                raise
            time.sleep(delay)


def seed_default_categories():
    from sqlalchemy.orm import Session
    from app.models import Category, TransactionType

    defaults = [
        ("Gaji", TransactionType.income),
        ("Lainnya", TransactionType.income),
        ("Makan", TransactionType.expense),
        ("Transport", TransactionType.expense),
        ("Tagihan", TransactionType.expense),
        ("Kesehatan", TransactionType.expense),
    ]

    db: Session | None = None
    try:
        db = Session(bind=engine)
        existing = db.query(Category).filter(Category.user_id == None).count()  # noqa: E711
        if existing == 0:
            for name, ctype in defaults:
                db.add(Category(user_id=None, name=name, type=ctype))
            db.commit()
    finally:
        if db:
            db.close()


def seed_demo_data():
    # Allow disabling demo seed via env
    flag = os.getenv("SEED_DEMO_DATA", "true").lower()
    if flag not in {"1", "true", "yes", "on"}:
        return

    from sqlalchemy.orm import Session
    from datetime import datetime, timedelta
    from app.models import User, Account, Transaction, TransactionType, TransactionStatus, Category

    db: Session | None = None
    try:
        db = Session(bind=engine)
        user = db.query(User).filter(User.email == "demo@example.com").first()
        if not user:
            user = User(
                email="demo@example.com",
                name="Demo User",
                password_hash=get_password_hash("secret123"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        account = (
            db.query(Account)
            .filter(Account.user_id == user.id, Account.name == "Demo Cash")
            .first()
        )
        if not account:
            account = Account(user_id=user.id, name="Demo Cash", type="cash", currency="IDR")
            db.add(account)
            db.commit()
            db.refresh(account)

        makan_cat = (
            db.query(Category)
            .filter(Category.name == "Makan", Category.user_id == None)  # noqa: E711
            .first()
        )
        if not makan_cat:
            makan_cat = Category(user_id=None, name="Makan", type=models.TransactionType.expense)
            db.add(makan_cat)
            db.commit()
            db.refresh(makan_cat)

        tx_exists = (
            db.query(Transaction)
            .filter(Transaction.user_id == user.id, Transaction.description == "Makan Siang Demo")
            .first()
        )
        if not tx_exists:
            tx = Transaction(
                user_id=user.id,
                account_id=account.id,
                category_id=makan_cat.id if makan_cat else None,
                type=TransactionType.expense,
                amount=Decimal("45000.00"),
                currency="IDR",
                description="Makan Siang Demo",
                occurred_at=datetime.utcnow() - timedelta(days=1),
                source="manual",
                status=TransactionStatus.confirmed,
            )
            db.add(tx)
            db.commit()
    finally:
        if db:
            db.close()


init_db_with_retry()

app = FastAPI(title="Financial Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Financial Tracker API"}
