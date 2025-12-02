from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models import TransactionStatus, TransactionType


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserOut(UserBase):
    id: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AccountBase(BaseModel):
    name: str
    type: str
    currency: str = "IDR"


class AccountCreate(AccountBase):
    pass


class AccountOut(AccountBase):
    id: str
    model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str
    type: TransactionType


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: str
    user_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class TransactionBase(BaseModel):
    account_id: str
    category_id: Optional[str] = None
    type: TransactionType
    amount: float
    currency: str = "IDR"
    description: Optional[str] = None
    occurred_at: datetime
    status: TransactionStatus = TransactionStatus.confirmed
    source: str = "manual"


class TransactionCreate(TransactionBase):
    pass


class TransactionOut(TransactionBase):
    id: str
    model_config = ConfigDict(from_attributes=True)


class CategoryTotal(BaseModel):
    category_id: Optional[str] = None
    name: Optional[str] = None
    total: float


class DashboardSummary(BaseModel):
    period: str
    start_date: datetime
    end_date: datetime
    income: float
    expense: float
    balance: float
    top_categories: list[CategoryTotal]


class Pagination(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class TransactionsPage(BaseModel):
    items: list[TransactionOut]
    pagination: Pagination
