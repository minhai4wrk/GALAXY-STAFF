"""Model cụm rạp chiếu phim."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.shift import Shift
    from app.models.user import User


class Location(Base):
    """Cụm rạp — V1 chỉ vận hành 1 rạp, giữ bảng để dễ mở rộng đa cụm."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    users: Mapped[list["User"]] = relationship(back_populates="location")
    shifts: Mapped[list["Shift"]] = relationship(back_populates="location")
