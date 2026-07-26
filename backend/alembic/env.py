"""Cấu hình môi trường Alembic — lấy URL database từ app config, không hardcode."""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401  — import để Base.metadata biết đủ 11 bảng khi autogenerate
from alembic import context
from app.core.config import settings
from app.core.database import Base

config = context.config
# Ưu tiên URL do bên gọi truyền vào (pytest trỏ sang database test), nếu không thì lấy từ .env
if not config.get_main_option("sqlalchemy.url", None):
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Sinh câu lệnh SQL ra file thay vì chạy trực tiếp trên database."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Chạy migration trực tiếp trên database qua một Connection."""
    section = config.get_section(config.config_ini_section) or {}
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
