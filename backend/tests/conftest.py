"""测试夹具 — 使用内存数据库，与生产 imts_demo.db 完全隔离"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models import Email, Task  # noqa: F401 确保模型注册到 Base.metadata
from app.main import app

# ── 测试专用引擎（内存 SQLite，StaticPool 保证所有会话共享同一连接）──

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="function", autouse=True)
def _setup_db():
    """每个测试前后建表/删表，保证完全隔离"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """数据库会话（可直接用于 seed 数据）"""
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client():
    """FastAPI TestClient（API 请求自动走测试数据库）"""
    def override_get_db():
        s = TestSessionLocal()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
