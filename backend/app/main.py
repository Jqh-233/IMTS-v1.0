"""
IMTS FastAPI 应用入口
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

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

app = FastAPI(
    title="IMTS API",
    description="Intelligent Mail Task Synergy System",
    version="0.1.0",
)

# 自动建表（首次运行无 .db 文件时创建，已有表则跳过）
from app.database import engine, Base
from app.models import Email, Task  # noqa: F401  确保模型注册到 Base.metadata
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
