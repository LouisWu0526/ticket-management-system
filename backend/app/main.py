"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .init_db import init_db
from .routers import auth, tickets, uploads


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：建表 + 初始化默认管理员
    init_db()
    yield


app = FastAPI(title=settings.APP_NAME, version="1.0.0", lifespan=lifespan)

# 开发环境跨域（生产由 Nginx 同源代理，可按需收紧）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 上传文件静态访问，如 http://host:8000/uploads/xxx.png
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 业务路由
app.include_router(auth.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")


@app.get("/api/health", tags=["系统"])
def health():
    return {"status": "ok", "app": settings.APP_NAME}
