"""Model ca làm việc và đơn xin nhận ca trống."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import (
    APPLY_STATUS_ENUM,
    ASSIGN_SOURCE_ENUM,
    SHIFT_STATUS_ENUM,
    ApplyStatus,
    AssignSource,
    ShiftStatus,
)

if TYPE_CHECKING:
    from app.models.exchange import ShiftExchange
    from app.models.location import Location
    from app.models.user import User


class Shift(Base):
    """Một ca làm việc.

    Dùng start_at/end_at kiểu TIMESTAMPTZ chứ KHÔNG phải date + start_time + end_time:
    ca 18h→2h với 3 cột rời sẽ có end_time nhỏ hơn start_time, làm sai mọi phép tính giờ.
    """

    __tablename__ = "shifts"
    __table_args__ = (
        CheckConstraint("end_at > start_at", name="ck_shift_time_order"),
        # Open-shift thì không có nguồn gán, và ngược lại
        CheckConstraint(
            "(assigned_user_id IS NULL) = (assignment_source IS NULL)",
            name="ck_shift_assign_pair",
        ),
        # Chỉ ca đã publish mới có mốc publish
        CheckConstraint(
            "status = 'published' OR published_at IS NULL", name="ck_shift_published_at"
        ),
        Index("ix_shift_location_date", "location_id", "work_date"),
        # Tính tổng giờ tuần cho ràng buộc C1-C3
        Index("ix_shift_user_week", "assigned_user_id", "week_start"),
        # Lấy Open-shift cho auto-schedule
        Index(
            "ix_shift_open",
            "week_start",
            postgresql_where=text("assigned_user_id IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False
    )
    # Ngày vận hành do nghiệp vụ quyết định — ca kết thúc 02:00 vẫn thuộc ngày hôm trước
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # NULL = Open-shift (KHÔNG dùng status để biểu diễn điều này)
    assigned_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )
    assignment_source: Mapped[AssignSource | None] = mapped_column(
        Enum(
            AssignSource,
            name=ASSIGN_SOURCE_ENUM,
            values_callable=lambda e: [i.value for i in e],
        )
    )
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[ShiftStatus] = mapped_column(
        Enum(
            ShiftStatus,
            name=SHIFT_STATUS_ENUM,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        server_default=ShiftStatus.DRAFT.value,
    )
    # Phi chuẩn hóa có chủ ý: tránh JOIN 2 bảng khi tải Roster tuần (NFR-PERF-01)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    unassigned_reason: Mapped[str | None] = mapped_column(String(255))
    # Khác NULL nghĩa là Manager đã cố ý ghi đè cảnh báo xung đột (FR-ROSTER-07)
    override_reason: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    location: Mapped["Location"] = relationship(back_populates="shifts")
    assigned_user: Mapped["User | None"] = relationship(foreign_keys=[assigned_user_id])
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    applications: Mapped[list["ShiftApplication"]] = relationship(
        back_populates="shift", cascade="all, delete-orphan"
    )
    exchanges: Mapped[list["ShiftExchange"]] = relationship(
        back_populates="shift", cascade="all, delete-orphan"
    )


class ShiftApplication(Base):
    """Đơn Staff xin nhận một ca trống (FR-ROSTER-09).

    Không dùng chung shift_exchanges được vì bảng đó bắt buộc có from_user_id và
    BR-EX-02 giới hạn 1 người pending — trái với việc nhiều Staff cùng xin một ca trống.
    """

    __tablename__ = "shift_applications"
    __table_args__ = (
        # Đã xét duyệt thì phải có người xét
        CheckConstraint(
            "status = 'pending' OR status = 'cancelled' OR reviewed_by IS NOT NULL",
            name="ck_application_reviewer",
        ),
        Index("ix_application_shift_status", "shift_id", "status"),
        # Một Staff chỉ có 1 đơn đang chờ cho mỗi ca, nhưng vẫn apply lại được sau khi bị từ chối
        Index(
            "uq_application_pending",
            "shift_id",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    shift_id: Mapped[int] = mapped_column(
        ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[ApplyStatus] = mapped_column(
        Enum(
            ApplyStatus,
            name=APPLY_STATUS_ENUM,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        server_default=ApplyStatus.PENDING.value,
    )
    has_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # Snapshot mô tả vi phạm TẠI THỜI ĐIỂM xin — tới lúc duyệt dữ liệu giờ làm có thể đã đổi
    conflict_note: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    shift: Mapped["Shift"] = relationship(back_populates="applications")
    applicant: Mapped["User"] = relationship(foreign_keys=[user_id])
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewed_by])
