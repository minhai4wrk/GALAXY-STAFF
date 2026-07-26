"""Fixture dùng chung cho toàn bộ test.

Theo quy tắc testing.md: KHÔNG mock database — chạy trên database test thật trong Docker.
"""

from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from alembic.config import Config
from app.core.config import settings
from app.core.security import hash_password
from app.models import Location, User
from app.models.enums import UserRole

BACKEND_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    """Dựng lại schema database test từ migration, dùng chung cho cả phiên test."""
    url = settings.TEST_DATABASE_URL or settings.DATABASE_URL
    if url == settings.DATABASE_URL:
        pytest.exit("TEST_DATABASE_URL đang trùng DATABASE_URL — từ chối chạy test trên DB dev")

    alembic_cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    # Chạy qua migration chứ không dùng create_all: op_minute(), EXCLUDE và các
    # partial index chỉ tồn tại trong migration, mà chúng chính là thứ cần kiểm chứng
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(url)
    yield engine
    engine.dispose()


@pytest.fixture
def db(test_engine: Engine) -> Generator[Session, None, None]:
    """Mỗi test chạy trong một transaction rồi rollback — test không ảnh hưởng lẫn nhau."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    try:
        yield session
    finally:
        session.close()
        # Test kiểm chứng constraint sẽ làm transaction tự abort khi database raise lỗi,
        # lúc đó transaction đã rời khỏi connection nên rollback lần nữa sẽ cảnh báo
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture
def location(db: Session) -> Location:
    """Một cụm rạp mẫu."""
    item = Location(name="Galaxy Test", address="Số 1 Đường Test")
    db.add(item)
    db.flush()
    return item


@pytest.fixture
def manager(db: Session, location: Location) -> User:
    """Tài khoản Manager mẫu."""
    user = User(
        email="manager@test.vn",
        password_hash=hash_password("GalaxyStaff@123"),
        full_name="Quản Lý Test",
        role=UserRole.MANAGER,
        location_id=location.id,
        must_change_password=False,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def staff(db: Session, location: Location) -> User:
    """Tài khoản Staff mẫu."""
    user = User(
        email="staff@test.vn",
        password_hash=hash_password("GalaxyStaff@123"),
        full_name="Nhân Viên Test",
        role=UserRole.STAFF,
        location_id=location.id,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def staff2(db: Session, location: Location) -> User:
    """Tài khoản Staff thứ hai — dùng cho kịch bản trao đổi ca."""
    user = User(
        email="staff2@test.vn",
        password_hash=hash_password("GalaxyStaff@123"),
        full_name="Nhân Viên Test 2",
        role=UserRole.STAFF,
        location_id=location.id,
    )
    db.add(user)
    db.flush()
    return user
