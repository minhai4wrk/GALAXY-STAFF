"""Model thông báo hệ thống."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import NOTIFICATION_TYPE_ENUM, NotificationType

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base):
    """Thông báo in-app gửi tới một người dùng cụ thể."""

    __tablename__ = "notifications"
    __table_args__ = (
        # Badge số chưa đọc
        Index("ix_notification_user_unread", "user_id", "is_read"),
        Index("ix_notification_user_created", "user_id", text("created_at DESC")),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(
            NotificationType,
            name=NOTIFICATION_TYPE_ENUM,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
    )
    # Đa hình: trỏ tới nhiều loại thực thể tùy `type` nên CỐ Ý không đặt khóa ngoại
    reference_id: Mapped[int | None] = mapped_column(Integer)
    # Chỉ dùng cho roster_published — publish là thao tác hàng loạt nên không trỏ được
    # tới một bản ghi duy nhất, mà FR-NOTIF-03 cần mở đúng tuần trên Roster
    reference_date: Mapped[date | None] = mapped_column(Date)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="notifications")
