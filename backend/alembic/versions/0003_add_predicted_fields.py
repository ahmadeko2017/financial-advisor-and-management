"""add predicted category fields to transactions"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_add_predicted_fields"
down_revision = "0002_add_tx_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("transactions", sa.Column("predicted_category_id", sa.String(), nullable=True))
    op.add_column("transactions", sa.Column("predicted_confidence", sa.Numeric(5, 4), nullable=True))
    op.create_index(
        "ix_transactions_predicted_category_id",
        "transactions",
        ["predicted_category_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_predicted_category_id", table_name="transactions")
    op.drop_column("transactions", "predicted_confidence")
    op.drop_column("transactions", "predicted_category_id")
