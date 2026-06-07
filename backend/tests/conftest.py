"""测试夹具 — 使用项目数据库，测试前后清理数据"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# 先导入模型确保注册到 Base.metadata
from app.models import Email, Task  # noqa: E402, F401
from app.database import Base, engine, SessionLocal  # noqa: E402

# 确保表存在
Base.metadata.create_all(bind=engine)

from app.main import app  # noqa: E402

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _clean_db():
    """每个测试前后清理数据，保证隔离"""
    # 测试前清理
    s = SessionLocal()
    s.query(Task).delete()
    s.query(Email).delete()
    s.commit()
    s.close()
    yield
    # 测试后清理
    s = SessionLocal()
    s.query(Task).delete()
    s.query(Email).delete()
    s.commit()
    s.close()


@pytest.fixture
def client():
    """FastAPI TestClient"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db():
    """数据库会话（测试前后自动清理，可直接使用）"""
    session = SessionLocal()
    yield session
    session.close()

