"""add transaction aggregation indexes"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_add_tx_indexes"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_transactions_user_occurred_at", "transactions", ["user_id", "occurred_at"])
    op.create_index(
        "ix_transactions_user_category_occurred_at",
        "transactions",
        ["user_id", "category_id", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_user_category_occurred_at", table_name="transactions")
    op.drop_index("ix_transactions_user_occurred_at", table_name="transactions")
