import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from app.database import Base
from app.config import get_settings
from app import models  # noqa: F401

config = context.config

# Ensure URL is set from env or settings default
settings = get_settings()
raw_url = os.getenv("DATABASE_URL", settings.database_url)
db_url = raw_url if raw_url and not raw_url.startswith("${") else settings.database_url
if not db_url or db_url.startswith("${"):
    db_url = "sqlite:///./dev.db"
config.set_main_option("sqlalchemy.url", db_url)

fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(db_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
