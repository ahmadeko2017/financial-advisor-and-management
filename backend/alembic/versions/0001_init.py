"""init schema"""

from alembic import op
import sqlalchemy as sa
from app.models import TransactionStatus, TransactionType

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=False, default="user"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "accounts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("currency", sa.String(), default="IDR"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.Enum(TransactionType), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("account_id", sa.String(), sa.ForeignKey("accounts.id"), nullable=False, index=True),
        sa.Column("category_id", sa.String(), sa.ForeignKey("categories.id"), nullable=True, index=True),
        sa.Column("type", sa.Enum(TransactionType), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(), default="IDR"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("source", sa.String(), default="manual"),
        sa.Column("status", sa.Enum(TransactionStatus), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_transactions_user_occurred_at", "transactions", ["user_id", "occurred_at"])
    op.create_index(
        "ix_transactions_user_category_occurred_at",
        "transactions",
        ["user_id", "category_id", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_user_category_occurred_at", table_name="transactions")
    op.drop_index("ix_transactions_user_occurred_at", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("categories")
    op.drop_table("accounts")
    op.drop_table("users")
