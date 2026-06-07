"""Alembic 迁移环境 — 自动检测 app.models 变更"""
import sys
from pathlib import Path

# 确保 backend/ 在 sys.path，使 app.* 可导入
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Alembic Config ──
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── 目标元数据：所有 ORM 模型的集合 ──
from app.database import Base  # noqa: E402
from app.models import Email, Task  # noqa: E402, F401 确保模型注册到 Base.metadata

target_metadata = Base.metadata

# ── 数据库 URL（从项目统一入口读取，不在 alembic.ini 中硬编码）──
from app.database import DATABASE_URL  # noqa: E402

config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
