"""
IMTS FastAPI 应用入口
"""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.logging_config import get_logger, setup_logging

logger = get_logger(__name__)
setup_logging()
logger.info("IMTS 后端启动，日志系统已初始化")

PROJECT_ROOT = BACKEND_DIR.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动：自动执行数据库迁移（通过 Alembic）"""
    from alembic.config import Config as AlembicConfig
    from alembic import command
    alembic_cfg = AlembicConfig(BACKEND_DIR / "alembic.ini")
    # 防止 alembic 读取自己的 argv（与 uvicorn 冲突）
    alembic_cfg.cmd_opts = type("_", (), {"x": None})()
    command.upgrade(alembic_cfg, "head")
    yield


app = FastAPI(
    title="IMTS API",
    description="Intelligent Mail Task Synergy System",
    version="0.1.0",
    lifespan=lifespan,
)

cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
allow_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API 路由 ──

from app.api.tasks import router as tasks_router
from app.api.emails import router as emails_router
from app.api.config import router as config_router

app.include_router(tasks_router)
app.include_router(emails_router)
app.include_router(config_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.delete("/api/data", status_code=204)
def clear_all():
    """清空所有邮件和任务"""
    from app.database import SessionLocal
    from app.models import Email, Task
    db = SessionLocal()
    try:
        db.query(Task).delete()
        db.query(Email).delete()
        db.commit()
    finally:
        db.close()


# ── 前端静态文件 ──

FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """SPA 兜底：所有路径返回 index.html，Vue Router 接管路由"""
        if full_path.startswith("api/") or full_path == "health":
            return FileResponse(FRONTEND_DIST / "index.html", status_code=404)
        return FileResponse(FRONTEND_DIST / "index.html")
