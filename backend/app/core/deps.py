"""Các dependency dùng chung cho router: lấy session, user hiện tại, kiểm tra vai trò."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.enums import UserRole
from app.models.user import User

# auto_error=False để tự trả thông báo lỗi tiếng Việt thay vì câu mặc định của FastAPI
bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    """Lấy user từ Bearer token, ném 401 nếu token thiếu, hỏng, hết hạn hoặc user đã bị khóa."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không có quyền truy cập, vui lòng đăng nhập lại",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    user_id = decode_token(credentials.credentials, expected_type="access")
    if user_id is None:
        raise unauthorized

    user = db.get(User, user_id)
    if user is None:
        raise unauthorized

    # Tài khoản bị vô hiệu hóa sau khi đã phát token thì token cũng mất hiệu lực ngay
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa, vui lòng liên hệ quản lý",
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_manager(current_user: CurrentUser) -> User:
    """Chỉ cho qua nếu người dùng có vai trò Manager (FR-AUTH-12)."""
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )
    return current_user


CurrentManager = Annotated[User, Depends(get_current_manager)]


def ensure_self_or_manager(current_user: User, target_user_id: int) -> None:
    """Chặn Staff đụng vào dữ liệu của người khác (BR-07)."""
    if current_user.role == UserRole.MANAGER:
        return
    if current_user.id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chỉ có thể xem hoặc sửa thông tin của chính mình",
        )
