"""Các kiểu ENUM dùng chung — khớp 1-1 với mục 4 của docs/erd.md."""

import enum


class UserRole(str, enum.Enum):
    """Vai trò người dùng trong hệ thống."""

    MANAGER = "manager"
    STAFF = "staff"


class ShiftStatus(str, enum.Enum):
    """Trạng thái công bố của ca — CHỈ có 2 giá trị.

    "Open-shift" KHÔNG nằm ở đây (đó là assigned_user_id IS NULL) và
    trạng thái khóa khi trao đổi cũng không (đó là cột is_locked).
    """

    DRAFT = "draft"
    PUBLISHED = "published"


class AssignSource(str, enum.Enum):
    """Nguồn gán ca — cho phép Reset Auto-Schedule chỉ gỡ đúng ca do máy xếp."""

    MANUAL = "manual"
    AUTO = "auto"
    APPLICATION = "application"
    EXCHANGE = "exchange"


class ApplyStatus(str, enum.Enum):
    """Trạng thái đơn xin nhận ca trống."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ExchangeStatus(str, enum.Enum):
    """Vòng đời một yêu cầu trao đổi ca."""

    AVAILABLE_FOR_EXCHANGE = "available_for_exchange"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class NotificationType(str, enum.Enum):
    """10 loại sự kiện sinh thông báo (BR-NW-06)."""

    ROSTER_PUBLISHED = "roster_published"
    SHIFT_UPDATED = "shift_updated"
    SHIFT_DELETED = "shift_deleted"
    SHIFT_APPLIED = "shift_applied"
    SHIFT_APPLY_APPROVED = "shift_apply_approved"
    SHIFT_APPLY_REJECTED = "shift_apply_rejected"
    EXCHANGE_REQUEST = "exchange_request"
    EXCHANGE_APPROVED = "exchange_approved"
    EXCHANGE_REJECTED = "exchange_rejected"
    NEWS_POSTED = "news_posted"


# Tên type native trong PostgreSQL — dùng lại ở model và migration để không lệch nhau
USER_ROLE_ENUM = "user_role"
SHIFT_STATUS_ENUM = "shift_status"
ASSIGN_SOURCE_ENUM = "assign_source"
APPLY_STATUS_ENUM = "apply_status"
EXCHANGE_STATUS_ENUM = "exchange_status"
NOTIFICATION_TYPE_ENUM = "notification_type"
