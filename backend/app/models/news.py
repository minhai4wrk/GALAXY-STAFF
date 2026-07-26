"""Model bảng tin nội bộ: bài viết, ảnh đính kèm, lượt đọc."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class NewsPost(Base):
    """Bài thông báo nội bộ do Manager đăng."""

    __tablename__ = "news_posts"
    __table_args__ = (
        # Feed mới-nhất-trước + phân trang (FR-NEWS-02, mục tiêu dưới 500ms)
        Index(
            "ix_news_created_desc",
            text("created_at DESC"),
            postgresql_where=text("is_deleted = false"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Để NULL chứ KHÔNG default NOW(): nhãn "Đã chỉnh sửa" xét theo updated_at IS NOT NULL.
    # Nếu cả 2 cột cùng default NOW() thì ORM gọi hàm 2 lần lệch vài micro-giây
    # -> mọi bài mới đều bị gắn nhãn sai.
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))

    author: Mapped["User"] = relationship(foreign_keys=[author_id])
    images: Mapped[list["NewsImage"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", order_by="NewsImage.sort_order"
    )
    reads: Mapped[list["NewsRead"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )


class NewsImage(Base):
    """Ảnh đính kèm bài viết — tách bảng để giữ 1NF (BR-NW-04 cho tối đa 3 ảnh)."""

    __tablename__ = "news_images"
    __table_args__ = (
        # UNIQUE + CHECK kết hợp lại chính là giới hạn cứng 3 ảnh/bài ở cấp CSDL
        UniqueConstraint("post_id", "sort_order", name="uq_news_image_order"),
        CheckConstraint("sort_order BETWEEN 0 AND 2", name="ck_news_image_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("news_posts.id", ondelete="CASCADE"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")

    post: Mapped["NewsPost"] = relationship(back_populates="images")


class NewsRead(Base):
    """Ghi nhận ai đã đọc bài nào (Seen Tracking)."""

    __tablename__ = "news_reads"
    __table_args__ = (
        # Nhờ ràng buộc này mà POST /api/news/{id}/read là idempotent (ON CONFLICT DO NOTHING)
        UniqueConstraint("post_id", "user_id", name="uq_news_read"),
        Index("ix_news_read_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("news_posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    post: Mapped["NewsPost"] = relationship(back_populates="reads")
    reader: Mapped["User"] = relationship()
