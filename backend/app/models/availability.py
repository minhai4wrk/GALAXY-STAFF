"""Model đăng ký lịch rảnh theo tuần và các khung giờ con."""

from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class AvailabilitySubmission(Base):
    """Bản đăng ký lịch rảnh của một nhân viên cho một tuần.

    Tồn tại riêng vì `reason` và `total_days` phụ thuộc vào cặp (nhân viên, tuần),
    không phụ thuộc từng khung giờ — nhét vào `availabilities` sẽ vi phạm 2NF.
    """

    __tablename__ = "availability_submissions"
    __table_args__ = (
        # BR-AV-05: mỗi nhân viên chỉ có 1 bản đăng ký cho mỗi tuần
        UniqueConstraint("user_id", "week_start", name="uq_submission_user_week"),
        CheckConstraint("total_days BETWEEN 0 AND 7", name="ck_submission_total_days"),
        # Overlap View + thống kê toàn rạp theo tuần
        Index("ix_submission_week", "week_start"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    # Ngày Thứ 6 đầu tuần vận hành của rạp (BR-AV-01)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    total_days: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    # Lý do khi đăng ký dưới 5 ngày (FR-AVAIL-07)
    reason: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="submissions")
    slots: Mapped[list["Availability"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )


class Availability(Base):
    """Một khung giờ rảnh cụ thể trong ngày.

    CẢNH BÁO: `end_time` có thể NHỎ HƠN `start_time` khi khung giờ vắt qua nửa đêm
    (ca tối 18:00 → 02:00). Mọi so sánh phải đi qua hàm SQL op_minute().
    """

    __tablename__ = "availabilities"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_avail_dow"),
        # 3 ràng buộc khung giờ dùng op_minute(): 8h00 = 0 phút, 2h00 hôm sau = 1080 phút
        CheckConstraint("op_minute(start_time) BETWEEN 0 AND 1049", name="ck_avail_start"),
        CheckConstraint("op_minute(end_time) BETWEEN 30 AND 1080", name="ck_avail_end"),
        CheckConstraint(
            "op_minute(end_time) > op_minute(start_time)", name="ck_avail_order"
        ),
        Index("ix_avail_submission", "submission_id"),
        # Dựng lưới Overlap View
        Index("ix_avail_dow_start", "day_of_week", "start_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("availability_submissions.id", ondelete="CASCADE"), nullable=False
    )
    # 0 = Thứ 6, 1 = Thứ 7, ..., 6 = Thứ 5
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    submission: Mapped["AvailabilitySubmission"] = relationship(back_populates="slots")
