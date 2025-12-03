"""add transaction aggregation indexes"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_add_tx_indexes"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_transactions_user_occurred_at",
        "transactions",
        ["user_id", "occurred_at"],
        unique=False,
        if_not_exists=True,
    )
    op.create_index(
        "ix_transactions_user_category_occurred_at",
        "transactions",
        ["user_id", "category_id", "occurred_at"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS "ix_transactions_user_category_occurred_at";')
    op.execute('DROP INDEX IF EXISTS "ix_transactions_user_occurred_at";')
