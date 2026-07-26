"""Cấu hình ứng dụng — đọc toàn bộ từ biến môi trường, không hardcode."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Gom toàn bộ biến môi trường của backend vào một object có type hint."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ---------- App ----------
    APP_NAME: str = "Galaxy Staff API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # ---------- Database ----------
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    # ---------- JWT ----------
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    DEFAULT_USER_PASSWORD: str = "GalaxyStaff@123"

    # ---------- Nghiệp vụ rạp ----------
    CINEMA_TIMEZONE: str = "Asia/Ho_Chi_Minh"
    CINEMA_OPEN_HOUR: int = 8
    AVAILABILITY_DEADLINE_WEEKDAY: int = 5  # 5 = Thứ 7 (Monday=0 theo chuẩn Python)
    AVAILABILITY_DEADLINE_HOUR: int = 18
    MAX_HOURS_PER_WEEK: int = 48
    MIN_REST_HOURS_BETWEEN_SHIFTS: int = 8
    MAX_CONSECUTIVE_WORK_DAYS: int = 6
    MIN_AVAILABILITY_DAYS: int = 5  # dưới ngưỡng này thì bắt nhập lý do (FR-AVAIL-07)

    # ---------- Upload ảnh ----------
    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_SIZE_MB: int = 5
    MAX_IMAGES_PER_POST: int = 3

    # ---------- CORS ----------
    # Giữ kiểu str: pydantic-settings tự JSON-parse mọi field kiểu list TRƯỚC khi validator
    # chạy, nên khai báo list[str] sẽ chết ngay lúc khởi động với chuỗi "a,b" trong .env.
    BACKEND_CORS_ORIGINS: str = ""

    @property
    def cors_origins(self) -> list[str]:
        """Tách chuỗi CORS ngăn cách bởi dấu phẩy thành danh sách origin."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Trả về Settings dạng singleton để không đọc lại .env mỗi request."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
