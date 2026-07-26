"""Model tài khoản người dùng."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import USER_ROLE_ENUM, UserRole

if TYPE_CHECKING:
    from app.models.availability import AvailabilitySubmission
    from app.models.location import Location
    from app.models.notification import Notification


class User(Base):
    """Tài khoản Manager hoặc Staff — Staff không tự đăng ký, Manager tạo."""

    __tablename__ = "users"
    __table_args__ = (
        # Lọc danh sách nhân viên (FR-AUTH-07)
        Index("ix_users_location_role_active", "location_id", "role", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name=USER_ROLE_ENUM, values_callable=lambda e: [i.value for i in e]),
        nullable=False,
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    # TRUE = đang dùng mật khẩu mặc định, frontend phải ép đổi trước khi vào Dashboard
    must_change_password: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # NULL = chưa từng bị sửa
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    location: Mapped["Location"] = relationship(back_populates="users")
    submissions: Mapped[list["AvailabilitySubmission"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
