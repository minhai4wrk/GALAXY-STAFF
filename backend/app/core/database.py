"""Khởi tạo SQLAlchemy engine, session factory và Base cho toàn bộ model."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # tự kiểm tra connection chết trước khi dùng lại
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Base class chung cho mọi SQLAlchemy model."""


def get_db() -> Generator[Session, None, None]:
    """Dependency FastAPI: mở session cho mỗi request và luôn đóng khi xong."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
