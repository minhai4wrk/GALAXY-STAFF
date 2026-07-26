"""Gom toàn bộ model để Alembic autogenerate nhìn thấy đủ 11 bảng."""

from app.models.availability import Availability, AvailabilitySubmission
from app.models.enums import (
    ApplyStatus,
    AssignSource,
    ExchangeStatus,
    NotificationType,
    ShiftStatus,
    UserRole,
)
from app.models.exchange import ShiftExchange
from app.models.location import Location
from app.models.news import NewsImage, NewsPost, NewsRead
from app.models.notification import Notification
from app.models.shift import Shift, ShiftApplication
from app.models.user import User

__all__ = [
    # 11 bảng
    "Location",
    "User",
    "AvailabilitySubmission",
    "Availability",
    "Shift",
    "ShiftApplication",
    "ShiftExchange",
    "NewsPost",
    "NewsImage",
    "NewsRead",
    "Notification",
    # 6 ENUM
    "UserRole",
    "ShiftStatus",
    "AssignSource",
    "ApplyStatus",
    "ExchangeStatus",
    "NotificationType",
]
