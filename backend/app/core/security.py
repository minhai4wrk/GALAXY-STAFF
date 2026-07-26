"""Băm mật khẩu bằng bcrypt và phát hành / xác thực JWT."""

from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt cost factor lấy từ .env (NFR yêu cầu >= 12)
pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS
)

TokenType = Literal["access", "refresh"]


def hash_password(plain_password: str) -> str:
    """Băm mật khẩu thô bằng bcrypt trước khi lưu vào database."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """So khớp mật khẩu thô với chuỗi băm đã lưu."""
    return pwd_context.verify(plain_password, password_hash)


def _create_token(subject: int, token_type: TokenType, expires_delta: timedelta) -> str:
    """Phát hành một JWT ký bằng HS256 với thời hạn cho trước."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),  # chuẩn JWT yêu cầu `sub` là chuỗi
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int) -> str:
    """Tạo access token ngắn hạn cho một user."""
    return _create_token(
        user_id, "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(user_id: int) -> str:
    """Tạo refresh token dài hạn cho một user."""
    return _create_token(
        user_id, "refresh", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_token(token: str, expected_type: TokenType) -> int | None:
    """Giải mã token và trả về user_id, hoặc None nếu token hỏng / sai loại / hết hạn."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None

    # Chặn việc dùng refresh token để gọi API như access token
    if payload.get("type") != expected_type:
        return None

    subject = payload.get("sub")
    if subject is None:
        return None
    try:
        return int(subject)
    except (TypeError, ValueError):
        return None
