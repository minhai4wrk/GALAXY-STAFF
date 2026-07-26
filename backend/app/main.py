"""Điểm khởi động ứng dụng FastAPI của Galaxy Staff."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API quản lý nhân sự rạp chiếu phim — Auth, Lịch rảnh, Roster, Trao đổi ca, Bảng tin.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Kiểm tra ứng dụng và kết nối database còn sống (dùng cho Docker healthcheck)."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "up"
    except Exception:  # noqa: BLE001 — healthcheck không được ném lỗi ra ngoài
        db_status = "down"
    return {"status": "ok", "database": db_status, "version": settings.APP_VERSION}


# TODO(Sprint 1): đăng ký router auth, users, availabilities, shifts, exchanges, news, notifications
