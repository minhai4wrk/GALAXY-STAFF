"""Tạo dữ liệu mẫu để demo và test (NFR-DEPLOY-04).

Chạy:
    docker compose exec backend python -m app.seed          # chỉ chạy khi DB trống
    docker compose exec backend python -m app.seed --reset  # xóa sạch rồi tạo lại
"""

import sys
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import (
    Availability,
    AvailabilitySubmission,
    Location,
    NewsPost,
    NewsRead,
    Notification,
    Shift,
    User,
)
from app.models.enums import AssignSource, NotificationType, ShiftStatus, UserRole

CINEMA_TZ = ZoneInfo(settings.CINEMA_TIMEZONE)

STAFF_NAMES = [
    "Nguyễn Văn An",
    "Trần Thanh Bình",
    "Lê Thị Cẩm",
    "Phạm Minh Dũng",
    "Hoàng Thị Em",
    "Vũ Đức Phong",
    "Đặng Thu Giang",
    "Bùi Quốc Huy",
    "Ngô Thị Kim",
    "Dương Văn Long",
    "Lý Thị Mai",
    "Phan Hoàng Nam",
]

# 4 mẫu ca của rạp: (giờ bắt đầu, giờ kết thúc, tên)
SHIFT_TEMPLATES = [
    (time(8, 0), time(13, 0), "Ca sáng"),
    (time(13, 0), time(18, 0), "Ca chiều"),
    (time(18, 0), time(2, 0), "Ca tối"),  # kết thúc 02:00 hôm sau
]


def current_week_start(today: date) -> date:
    """Trả về ngày Thứ 6 gần nhất trước hoặc bằng hôm nay (tuần rạp chạy T6 -> T5)."""
    # weekday(): Thứ 2 = 0 ... Thứ 6 = 4
    return today - timedelta(days=(today.weekday() - 4) % 7)


def to_utc(day: date, clock: time, plus_day: bool = False) -> datetime:
    """Ghép ngày + giờ địa phương của rạp rồi quy về UTC để lưu TIMESTAMPTZ."""
    target_day = day + timedelta(days=1) if plus_day else day
    return datetime.combine(target_day, clock, tzinfo=CINEMA_TZ)


def wipe(db: Session) -> None:
    """Xóa sạch toàn bộ dữ liệu nghiệp vụ, giữ nguyên cấu trúc bảng."""
    db.execute(
        text(
            "TRUNCATE notifications, news_reads, news_images, news_posts, "
            "shift_exchanges, shift_applications, shifts, availabilities, "
            "availability_submissions, users, locations RESTART IDENTITY CASCADE"
        )
    )
    db.commit()


def seed_users(db: Session, location: Location) -> tuple[User, list[User]]:
    """Tạo 1 Manager và 12 Staff, tất cả dùng mật khẩu mặc định."""
    password = hash_password(settings.DEFAULT_USER_PASSWORD)

    manager = User(
        email="manager@galaxy.vn",
        password_hash=password,
        full_name="Nguyễn Quản Lý",
        role=UserRole.MANAGER,
        location_id=location.id,
        must_change_password=False,
    )
    db.add(manager)

    staffs: list[User] = []
    for index, name in enumerate(STAFF_NAMES, start=1):
        staffs.append(
            User(
                email=f"staff{index:02d}@galaxy.vn",
                password_hash=password,
                full_name=name,
                role=UserRole.STAFF,
                location_id=location.id,
                # Chỉ staff01 giữ cờ này để demo màn hình ép đổi mật khẩu lần đầu
                must_change_password=(index == 1),
                is_active=(index != 12),  # staff12 bị khóa để demo tài khoản vô hiệu hóa
            )
        )
    db.add_all(staffs)
    db.flush()
    return manager, staffs


def seed_availabilities(db: Session, staffs: list[User], weeks: list[date]) -> None:
    """Tạo lịch rảnh 2 tuần cho từng nhân viên, mỗi ngày tối đa 1 khung giờ.

    Giữ mỗi ngày một khung để không đụng ràng buộc EXCLUDE chống chồng giờ.
    """
    for week_start in weeks:
        for index, staff in enumerate(staffs):
            # Nhân viên 11 và 12 cố tình đăng ký thiếu ngày để demo cảnh báo FR-AVAIL-07
            day_count = 4 if index >= 10 else (5 + index % 2)
            days = [(index + offset) % 7 for offset in range(day_count)]

            submission = AvailabilitySubmission(
                user_id=staff.id,
                week_start=week_start,
                total_days=day_count,
                reason=(
                    "Tuần này em có lịch thi cuối kỳ" if day_count < 5 else None
                ),
            )
            db.add(submission)
            db.flush()

            for order, day_of_week in enumerate(days):
                start, end, _ = SHIFT_TEMPLATES[(index + order) % len(SHIFT_TEMPLATES)]
                db.add(
                    Availability(
                        submission_id=submission.id,
                        day_of_week=day_of_week,
                        start_time=start,
                        end_time=end,
                    )
                )


def seed_shifts(
    db: Session, manager: User, staffs: list[User], location: Location, weeks: list[date]
) -> int:
    """Tạo ca 2 tuần: tuần hiện tại đã publish, tuần sau còn draft và có ca trống."""
    active_staffs = [s for s in staffs if s.is_active]
    created = 0

    for week_index, week_start in enumerate(weeks):
        is_published = week_index == 0

        for day_offset in range(7):
            work_date = week_start + timedelta(days=day_offset)

            for template_index, (start, end, _) in enumerate(SHIFT_TEMPLATES):
                slot = day_offset * len(SHIFT_TEMPLATES) + template_index

                # Tuần sau chừa lại vài ca trống để demo Auto-Schedule và Apply Open-shift
                leave_open = (not is_published) and slot % 5 == 0
                assignee = None if leave_open else active_staffs[slot % len(active_staffs)]

                shift = Shift(
                    location_id=location.id,
                    work_date=work_date,
                    week_start=week_start,
                    start_at=to_utc(work_date, start),
                    # Ca tối kết thúc 02:00 NGÀY HÔM SAU
                    end_at=to_utc(work_date, end, plus_day=end < start),
                    assigned_user_id=assignee.id if assignee else None,
                    assignment_source=AssignSource.MANUAL if assignee else None,
                    assigned_at=datetime.now(CINEMA_TZ) if assignee else None,
                    status=ShiftStatus.PUBLISHED if is_published else ShiftStatus.DRAFT,
                    published_at=datetime.now(CINEMA_TZ) if is_published else None,
                    unassigned_reason=(
                        "Chưa có nhân viên nào rảnh khung giờ này" if leave_open else None
                    ),
                    created_by=manager.id,
                )
                db.add(shift)
                created += 1

    return created


def seed_news(db: Session, manager: User, staffs: list[User]) -> None:
    """Tạo 3 bài thông báo, trong đó 1 bài đã có người đọc để demo Seen Tracking."""
    posts = [
        NewsPost(
            author_id=manager.id,
            title="Lịch chiếu phim tuần mới và chương trình khuyến mãi",
            content=(
                "Từ Thứ 6 tuần này rạp áp dụng giá vé ưu đãi cho toàn bộ suất chiếu "
                "trước 12h00. Các bạn nhân viên quầy vé lưu ý cập nhật bảng giá mới "
                "và thông báo cho khách khi bán vé."
            ),
        ),
        NewsPost(
            author_id=manager.id,
            title="Nhắc đăng ký lịch rảnh trước 18h00 Thứ 7",
            content=(
                "Đề nghị toàn bộ nhân viên hoàn tất đăng ký lịch rảnh cho tuần kế tiếp "
                "trước 18h00 Thứ 7. Sau thời điểm này hệ thống sẽ khóa và không nhận "
                "đăng ký nữa. Bạn nào đăng ký dưới 5 ngày nhớ ghi rõ lý do."
            ),
        ),
        NewsPost(
            author_id=manager.id,
            title="Họp toàn rạp đầu tháng",
            content=(
                "Cuộc họp toàn rạp sẽ diễn ra lúc 09h00 Thứ 2 đầu tháng tại phòng nghỉ "
                "nhân viên. Nội dung: tổng kết doanh thu tháng trước và phổ biến quy "
                "trình vệ sinh phòng chiếu mới."
            ),
        ),
    ]
    db.add_all(posts)
    db.flush()

    # 8/12 nhân viên đã đọc bài đầu — vừa đủ để ảnh chụp Seen Tracking có số liệu đẹp
    for staff in staffs[:8]:
        db.add(NewsRead(post_id=posts[0].id, user_id=staff.id))

    # Thông báo tương ứng cho toàn bộ nhân viên đang hoạt động
    for staff in staffs:
        if staff.is_active:
            db.add(
                Notification(
                    user_id=staff.id,
                    type=NotificationType.NEWS_POSTED,
                    reference_id=posts[0].id,
                    message=f"Quản lý vừa đăng thông báo mới: {posts[0].title}",
                )
            )


def main() -> None:
    """Điểm vào của script seed."""
    reset = "--reset" in sys.argv

    with SessionLocal() as db:
        if reset:
            wipe(db)
            print("Đã xóa sạch dữ liệu cũ.")
        elif db.scalar(select(User).limit(1)) is not None:
            print("Database đã có dữ liệu. Dùng --reset nếu muốn tạo lại từ đầu.")
            return

        location = Location(name="Galaxy Nguyễn Du", address="116 Nguyễn Du, Quận 1, TP.HCM")
        db.add(location)
        db.flush()

        manager, staffs = seed_users(db, location)

        this_week = current_week_start(date.today())
        weeks = [this_week, this_week + timedelta(days=7)]

        seed_availabilities(db, staffs, weeks)
        shift_count = seed_shifts(db, manager, staffs, location, weeks)
        seed_news(db, manager, staffs)

        db.commit()

    print("Seed xong.")
    print("  Rạp        : Galaxy Nguyễn Du")
    print(f"  Tài khoản  : 1 Manager + {len(STAFF_NAMES)} Staff (staff12 đang bị khóa)")
    print(f"  Tuần dữ liệu: {weeks[0]} (đã publish) và {weeks[1]} (draft)")
    print(f"  Ca làm     : {shift_count}")
    print("  Bài thông báo: 3")
    print()
    print(f"  Đăng nhập  : manager@galaxy.vn / {settings.DEFAULT_USER_PASSWORD}")
    print(f"               staff01@galaxy.vn / {settings.DEFAULT_USER_PASSWORD}")


if __name__ == "__main__":
    main()
