"""Kiểm chứng các bảo đảm ở CẤP CƠ SỞ DỮ LIỆU của ERD v2.0.

Những ràng buộc này là lớp bảo vệ cuối cùng (NFR-REL-03): kể cả khi tầng service có
lỗi logic, database vẫn phải từ chối dữ liệu sai. Vì vậy chúng cần test riêng, không
gộp vào test của API.
"""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Availability,
    AvailabilitySubmission,
    Location,
    Shift,
    ShiftExchange,
    User,
)
from app.models.enums import AssignSource, ExchangeStatus, ShiftStatus

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
WEEK_START = date(2026, 8, 7)  # một ngày Thứ 6


def make_submission(db: Session, user: User) -> AvailabilitySubmission:
    """Tạo nhanh một bản đăng ký lịch rảnh rỗng."""
    submission = AvailabilitySubmission(user_id=user.id, week_start=WEEK_START, total_days=1)
    db.add(submission)
    db.flush()
    return submission


def make_shift(
    db: Session,
    location: Location,
    manager: User,
    start: datetime,
    end: datetime,
    assignee: User | None = None,
) -> Shift:
    """Tạo nhanh một ca làm việc."""
    shift = Shift(
        location_id=location.id,
        work_date=start.astimezone(VN_TZ).date(),
        week_start=WEEK_START,
        start_at=start,
        end_at=end,
        assigned_user_id=assignee.id if assignee else None,
        assignment_source=AssignSource.MANUAL if assignee else None,
        status=ShiftStatus.DRAFT,
        created_by=manager.id,
    )
    db.add(shift)
    db.flush()
    return shift


# ----------------------------------------------------------------------
# op_minute() — hàm quy đổi giờ, gốc rễ của việc xử lý ca qua nửa đêm
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("clock", "expected"),
    [
        ("08:00", 0),  # mốc mở cửa
        ("13:00", 300),
        ("18:00", 600),
        ("23:30", 930),
        ("00:00", 960),  # đã qua nửa đêm, phải TĂNG chứ không quay về 0
        ("02:00", 1080),  # mốc đóng cửa
    ],
)
def test_op_minute_maps_operating_window_correctly(db: Session, clock: str, expected: int):
    """op_minute quy đổi giờ đồng hồ sang số phút tính từ 08:00, tăng đơn điệu qua nửa đêm."""
    result = db.execute(text("SELECT op_minute(:t)"), {"t": clock}).scalar_one()
    assert result == expected


# ----------------------------------------------------------------------
# availabilities — ca qua nửa đêm và chống chồng giờ
# ----------------------------------------------------------------------


def test_midnight_availability_is_accepted(db: Session, staff: User):
    """Khung giờ 18:00 -> 02:00 hôm sau phải được chấp nhận (ca tối của rạp)."""
    submission = make_submission(db, staff)
    db.add(
        Availability(
            submission_id=submission.id,
            day_of_week=0,
            start_time=time(18, 0),
            end_time=time(2, 0),
        )
    )
    db.flush()

    saved = db.query(Availability).filter_by(submission_id=submission.id).one()
    assert saved.start_time == time(18, 0)
    assert saved.end_time == time(2, 0)


def test_overlapping_availability_same_day_is_rejected(db: Session, staff: User):
    """Hai khung giờ chồng nhau trong cùng một ngày phải bị EXCLUDE constraint chặn.

    UNIQUE thường không bắt được trường hợp này vì 08:00-13:00 và 09:00-10:00
    có start_time khác nhau — đó là lý do phải dùng EXCLUDE USING gist.
    """
    submission = make_submission(db, staff)
    db.add(
        Availability(
            submission_id=submission.id,
            day_of_week=0,
            start_time=time(8, 0),
            end_time=time(13, 0),
        )
    )
    db.flush()

    db.add(
        Availability(
            submission_id=submission.id,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
    )
    with pytest.raises(IntegrityError, match="ex_avail_overlap"):
        db.flush()


def test_availability_outside_operating_hours_is_rejected(db: Session, staff: User):
    """Khung giờ 03:00 -> 05:00 nằm ngoài giờ vận hành 08:00-02:00 nên bị từ chối."""
    submission = make_submission(db, staff)
    db.add(
        Availability(
            submission_id=submission.id,
            day_of_week=0,
            start_time=time(3, 0),
            end_time=time(5, 0),
        )
    )
    with pytest.raises(IntegrityError, match="ck_avail_"):
        db.flush()


def test_duplicate_submission_same_week_is_rejected(db: Session, staff: User):
    """BR-AV-05: mỗi nhân viên chỉ có đúng 1 bản đăng ký cho mỗi tuần."""
    make_submission(db, staff)
    db.add(AvailabilitySubmission(user_id=staff.id, week_start=WEEK_START, total_days=3))
    with pytest.raises(IntegrityError, match="uq_submission_user_week"):
        db.flush()


# ----------------------------------------------------------------------
# shifts — chống chồng ca và tính nhất quán của Open-shift
# ----------------------------------------------------------------------


def test_midnight_shift_duration_is_eight_hours(
    db: Session, location: Location, manager: User, staff: User
):
    """Ca 18:00 -> 02:00 phải cho ra đúng 8 giờ, không phải số âm."""
    start = datetime(2026, 8, 7, 18, 0, tzinfo=VN_TZ)
    end = datetime(2026, 8, 8, 2, 0, tzinfo=VN_TZ)
    shift = make_shift(db, location, manager, start, end, staff)

    assert (shift.end_at - shift.start_at) == timedelta(hours=8)


def test_overlapping_shifts_for_same_user_are_rejected(
    db: Session, location: Location, manager: User, staff: User
):
    """Ràng buộc C4 của thuật toán greedy: một người không thể bị gán 2 ca chồng giờ."""
    make_shift(
        db,
        location,
        manager,
        datetime(2026, 8, 7, 8, 0, tzinfo=VN_TZ),
        datetime(2026, 8, 7, 13, 0, tzinfo=VN_TZ),
        staff,
    )
    db.add(
        Shift(
            location_id=location.id,
            work_date=date(2026, 8, 7),
            week_start=WEEK_START,
            start_at=datetime(2026, 8, 7, 11, 0, tzinfo=VN_TZ),
            end_at=datetime(2026, 8, 7, 15, 0, tzinfo=VN_TZ),
            assigned_user_id=staff.id,
            assignment_source=AssignSource.MANUAL,
            status=ShiftStatus.DRAFT,
            created_by=manager.id,
        )
    )
    with pytest.raises(IntegrityError, match="ex_shift_overlap"):
        db.flush()


def test_two_users_can_share_the_same_time_slot(
    db: Session, location: Location, manager: User, staff: User, staff2: User
):
    """Ràng buộc chống chồng ca chỉ áp dụng trong phạm vi một người."""
    start = datetime(2026, 8, 7, 8, 0, tzinfo=VN_TZ)
    end = datetime(2026, 8, 7, 13, 0, tzinfo=VN_TZ)
    make_shift(db, location, manager, start, end, staff)
    make_shift(db, location, manager, start, end, staff2)

    assert db.query(Shift).count() == 2


def test_open_shift_must_not_have_assignment_source(
    db: Session, location: Location, manager: User
):
    """Open-shift (chưa có người) thì không được có nguồn gán, và ngược lại."""
    db.add(
        Shift(
            location_id=location.id,
            work_date=date(2026, 8, 7),
            week_start=WEEK_START,
            start_at=datetime(2026, 8, 7, 8, 0, tzinfo=VN_TZ),
            end_at=datetime(2026, 8, 7, 13, 0, tzinfo=VN_TZ),
            assigned_user_id=None,
            assignment_source=AssignSource.AUTO,  # sai: chưa có người mà đã có nguồn gán
            status=ShiftStatus.DRAFT,
            created_by=manager.id,
        )
    )
    with pytest.raises(IntegrityError, match="ck_shift_assign_pair"):
        db.flush()


def test_draft_shift_cannot_have_published_at(
    db: Session, location: Location, manager: User
):
    """Chỉ ca đã publish mới được có mốc published_at."""
    db.add(
        Shift(
            location_id=location.id,
            work_date=date(2026, 8, 7),
            week_start=WEEK_START,
            start_at=datetime(2026, 8, 7, 8, 0, tzinfo=VN_TZ),
            end_at=datetime(2026, 8, 7, 13, 0, tzinfo=VN_TZ),
            status=ShiftStatus.DRAFT,
            published_at=datetime.now(VN_TZ),
            created_by=manager.id,
        )
    )
    with pytest.raises(IntegrityError, match="ck_shift_published_at"):
        db.flush()


# ----------------------------------------------------------------------
# shift_exchanges — BR-EX-02 và BR-EX-03 ở cấp cơ sở dữ liệu
# ----------------------------------------------------------------------


def test_user_cannot_take_own_exchange(
    db: Session, location: Location, manager: User, staff: User
):
    """BR-EX-03: không ai tự nhận được ca do chính mình đăng pass."""
    shift = make_shift(
        db,
        location,
        manager,
        datetime(2026, 8, 7, 18, 0, tzinfo=VN_TZ),
        datetime(2026, 8, 8, 2, 0, tzinfo=VN_TZ),
        staff,
    )
    db.add(
        ShiftExchange(
            shift_id=shift.id,
            from_user_id=staff.id,
            to_user_id=staff.id,  # sai: tự nhận ca của mình
            status=ExchangeStatus.PENDING_APPROVAL,
        )
    )
    with pytest.raises(IntegrityError, match="ck_exchange_not_self"):
        db.flush()


def test_only_one_active_exchange_per_shift(
    db: Session, location: Location, manager: User, staff: User, staff2: User
):
    """BR-EX-02: mỗi ca chỉ có tối đa 1 yêu cầu trao đổi đang hoạt động.

    Đây chính là lớp chặn để 5 request đồng thời chỉ có đúng 1 cái thành công (NFR-REL-04).
    """
    shift = make_shift(
        db,
        location,
        manager,
        datetime(2026, 8, 7, 18, 0, tzinfo=VN_TZ),
        datetime(2026, 8, 8, 2, 0, tzinfo=VN_TZ),
        staff,
    )
    db.add(
        ShiftExchange(
            shift_id=shift.id,
            from_user_id=staff.id,
            status=ExchangeStatus.AVAILABLE_FOR_EXCHANGE,
        )
    )
    db.flush()

    db.add(
        ShiftExchange(
            shift_id=shift.id,
            from_user_id=staff.id,
            status=ExchangeStatus.AVAILABLE_FOR_EXCHANGE,
        )
    )
    with pytest.raises(IntegrityError, match="uq_exchange_active"):
        db.flush()
