import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"
    transfer = "transfer"


class TransactionStatus(str, enum.Enum):
    predicted = "predicted"
    confirmed = "confirmed"


def _uuid() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    accounts = relationship("Account", back_populates="user")
    categories = relationship("Category", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # cash/bank/e-wallet
    currency = Column(String, default="IDR")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # null = global
    name = Column(String, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False, index=True)
    category_id = Column(String, ForeignKey("categories.id"), nullable=True, index=True)
    predicted_category_id = Column(String, ForeignKey("categories.id"), nullable=True, index=True)
    predicted_confidence = Column(Numeric(5, 4), nullable=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String, default="IDR")
    description = Column(Text, nullable=True)
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    source = Column(String, default="manual")
    status = Column(Enum(TransactionStatus), default=TransactionStatus.confirmed, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
