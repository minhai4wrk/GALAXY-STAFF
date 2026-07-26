"""Model yêu cầu trao đổi ca (pass / nhận)."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EXCHANGE_STATUS_ENUM, ExchangeStatus

if TYPE_CHECKING:
    from app.models.shift import Shift
    from app.models.user import User


class ShiftExchange(Base):
    """Yêu cầu trao đổi ca: Staff A pass -> Staff B nhận -> Manager duyệt.

    Tên cột là `reviewed_by` chứ không phải `approved_by` vì cùng một cột được dùng
    cho cả duyệt lẫn từ chối.
    """

    __tablename__ = "shift_exchanges"
    __table_args__ = (
        # BR-EX-03: không ai tự nhận ca mình đăng — chốt ở cấp CSDL, không chỉ ở service
        CheckConstraint(
            "to_user_id IS NULL OR to_user_id <> from_user_id", name="ck_exchange_not_self"
        ),
        # Chưa ai nhận thì không được có người nhận
        CheckConstraint(
            "status <> 'available_for_exchange' OR to_user_id IS NULL",
            name="ck_exchange_open_no_taker",
        ),
        # Đã xét duyệt thì phải đủ cả người nhận lẫn người xét
        CheckConstraint(
            "status NOT IN ('approved', 'rejected') "
            "OR (to_user_id IS NOT NULL AND reviewed_by IS NOT NULL)",
            name="ck_exchange_reviewed_complete",
        ),
        Index("ix_exchange_status", "status"),
        Index("ix_exchange_from_status", "from_user_id", "status"),
        Index("ix_exchange_to_status", "to_user_id", "status"),
        # BR-EX-02: mỗi ca chỉ có tối đa 1 yêu cầu đang hoạt động.
        # Đây là lớp bảo vệ cuối (NFR-REL-03): 5 request đồng thời -> chỉ 1 thành công.
        Index(
            "uq_exchange_active",
            "shift_id",
            unique=True,
            postgresql_where=text(
                "status IN ('available_for_exchange', 'pending_approval')"
            ),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    shift_id: Mapped[int] = mapped_column(
        ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False
    )
    from_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    # NULL khi chưa ai bấm nhận
    to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ExchangeStatus] = mapped_column(
        Enum(
            ExchangeStatus,
            name=EXCHANGE_STATUS_ENUM,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
        server_default=ExchangeStatus.AVAILABLE_FOR_EXCHANGE.value,
    )
    has_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    conflict_note: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # 3 mốc riêng thay vì 1 updated_at bị ghi đè — FR-EXCHANGE-05 cần hiển thị lịch sử
    taken_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    shift: Mapped["Shift"] = relationship(back_populates="exchanges")
    from_user: Mapped["User"] = relationship(foreign_keys=[from_user_id])
    to_user: Mapped["User | None"] = relationship(foreign_keys=[to_user_id])
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewed_by])
