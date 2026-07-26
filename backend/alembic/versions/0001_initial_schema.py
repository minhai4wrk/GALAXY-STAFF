"""Khởi tạo schema Galaxy Staff — 11 bảng theo ERD v2.0

Migration này viết tay (không autogenerate) vì chứa 4 thứ Alembic không tự sinh được:
hàm SQL op_minute(), 2 ràng buộc EXCLUDE chống chồng giờ, 2 unique index có điều kiện,
và index biểu thức created_at DESC.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Extension + hàm xử lý ca qua nửa đêm
    # ------------------------------------------------------------------
    # btree_gist cần cho EXCLUDE constraint kết hợp cột thường với range
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    # Rạp mở 08:00 -> 02:00 hôm sau nên kiểu TIME không so sánh trực tiếp được
    # (02:00 < 18:00). Hàm này đổi giờ đồng hồ sang số phút tính từ 08:00:
    # 08:00 = 0, 18:00 = 600, 00:00 = 960, 02:00 hôm sau = 1080.
    #
    # ⚠️ Cộng thẳng 1440 phút cho nhánh sau nửa đêm, KHÔNG dùng
    # `t + INTERVAL '24 hours'`: kiểu TIME của PostgreSQL cuộn vòng modulo 24 giờ nên
    # TIME '02:00' + INTERVAL '24 hours' vẫn ra 02:00 — phép cộng vô tác dụng và
    # op_minute('02:00') sẽ trả về -360 thay vì 1080.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION op_minute(t TIME) RETURNS INTEGER
          LANGUAGE sql IMMUTABLE STRICT AS $$
          SELECT (EXTRACT(EPOCH FROM (t - TIME '08:00')) / 60)::INTEGER
               + CASE WHEN t >= TIME '08:00' THEN 0 ELSE 1440 END;
        $$;
        """
    )

    # ------------------------------------------------------------------
    # 2. Kiểu ENUM (tạo tường minh để create_table không tự tạo lại)
    # ------------------------------------------------------------------
    op.execute("CREATE TYPE user_role AS ENUM ('manager', 'staff')")
    op.execute("CREATE TYPE shift_status AS ENUM ('draft', 'published')")
    op.execute(
        "CREATE TYPE assign_source AS ENUM ('manual', 'auto', 'application', 'exchange')"
    )
    op.execute(
        "CREATE TYPE apply_status AS ENUM ('pending', 'approved', 'rejected', 'cancelled')"
    )
    op.execute(
        """
        CREATE TYPE exchange_status AS ENUM (
            'available_for_exchange', 'pending_approval', 'approved', 'rejected', 'cancelled'
        )
        """
    )
    op.execute(
        """
        CREATE TYPE notification_type AS ENUM (
            'roster_published', 'shift_updated', 'shift_deleted', 'shift_applied',
            'shift_apply_approved', 'shift_apply_rejected', 'exchange_request',
            'exchange_approved', 'exchange_rejected', 'news_posted'
        )
        """
    )

    user_role = postgresql.ENUM(name="user_role", create_type=False)
    shift_status = postgresql.ENUM(name="shift_status", create_type=False)
    assign_source = postgresql.ENUM(name="assign_source", create_type=False)
    apply_status = postgresql.ENUM(name="apply_status", create_type=False)
    exchange_status = postgresql.ENUM(name="exchange_status", create_type=False)
    notification_type = postgresql.ENUM(name="notification_type", create_type=False)

    # ------------------------------------------------------------------
    # 3. locations
    # ------------------------------------------------------------------
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("address", sa.String(255)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # 4. users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column(
            "location_id",
            sa.Integer(),
            sa.ForeignKey("locations.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "must_change_password",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index(
        "ix_users_location_role_active", "users", ["location_id", "role", "is_active"]
    )

    # ------------------------------------------------------------------
    # 5. availability_submissions
    # ------------------------------------------------------------------
    op.create_table(
        "availability_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("total_days", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        # BR-AV-05 enforce ở cấp cấu trúc, không phụ thuộc application logic
        sa.UniqueConstraint("user_id", "week_start", name="uq_submission_user_week"),
        sa.CheckConstraint("total_days BETWEEN 0 AND 7", name="ck_submission_total_days"),
    )
    op.create_index("ix_submission_week", "availability_submissions", ["week_start"])

    # ------------------------------------------------------------------
    # 6. availabilities
    # ------------------------------------------------------------------
    op.create_table(
        "availabilities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "submission_id",
            sa.Integer(),
            sa.ForeignKey("availability_submissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("day_of_week", sa.SmallInteger(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_avail_dow"),
        # Chặn slot nằm ngoài khung vận hành 08:00 - 02:00
        sa.CheckConstraint("op_minute(start_time) BETWEEN 0 AND 1049", name="ck_avail_start"),
        sa.CheckConstraint("op_minute(end_time) BETWEEN 30 AND 1080", name="ck_avail_end"),
        # KHÔNG dùng end_time > start_time: ca tối 18:00 -> 02:00 sẽ bị từ chối oan
        sa.CheckConstraint(
            "op_minute(end_time) > op_minute(start_time)", name="ck_avail_order"
        ),
    )
    op.create_index("ix_avail_submission", "availabilities", ["submission_id"])
    op.create_index("ix_avail_dow_start", "availabilities", ["day_of_week", "start_time"])

    # Một nhân viên không thể đăng ký 2 khung giờ chồng nhau trong cùng một ngày.
    # UNIQUE thường không chặn được vì 08:00-13:00 và 09:00-10:00 có start_time khác nhau.
    op.execute(
        """
        ALTER TABLE availabilities ADD CONSTRAINT ex_avail_overlap
          EXCLUDE USING gist (
            submission_id WITH =,
            day_of_week   WITH =,
            int4range(op_minute(start_time), op_minute(end_time)) WITH &&
          )
        """
    )

    # ------------------------------------------------------------------
    # 7. shifts
    # ------------------------------------------------------------------
    op.create_table(
        "shifts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "location_id",
            sa.Integer(),
            sa.ForeignKey("locations.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        # NULL = Open-shift
        sa.Column(
            "assigned_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
        ),
        sa.Column("assignment_source", assign_source),
        sa.Column("assigned_at", sa.DateTime(timezone=True)),
        sa.Column(
            "status", shift_status, server_default=sa.text("'draft'"), nullable=False
        ),
        sa.Column("is_locked", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("unassigned_reason", sa.String(255)),
        sa.Column("override_reason", sa.Text()),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        # Với TIMESTAMPTZ thì ràng buộc này luôn hợp lệ, kể cả ca 18:00 -> 02:00 hôm sau
        sa.CheckConstraint("end_at > start_at", name="ck_shift_time_order"),
        sa.CheckConstraint(
            "(assigned_user_id IS NULL) = (assignment_source IS NULL)",
            name="ck_shift_assign_pair",
        ),
        sa.CheckConstraint(
            "status = 'published' OR published_at IS NULL", name="ck_shift_published_at"
        ),
    )
    op.create_index("ix_shift_location_date", "shifts", ["location_id", "work_date"])
    op.create_index("ix_shift_user_week", "shifts", ["assigned_user_id", "week_start"])
    op.create_index(
        "ix_shift_open",
        "shifts",
        ["week_start"],
        postgresql_where=sa.text("assigned_user_id IS NULL"),
    )

    # Ràng buộc C4 của thuật toán greedy, do CSDL bảo đảm thay vì tin vào application logic
    op.execute(
        """
        ALTER TABLE shifts ADD CONSTRAINT ex_shift_overlap
          EXCLUDE USING gist (
            assigned_user_id WITH =,
            tstzrange(start_at, end_at) WITH &&
          ) WHERE (assigned_user_id IS NOT NULL AND NOT is_deleted)
        """
    )

    # ------------------------------------------------------------------
    # 8. shift_applications
    # ------------------------------------------------------------------
    op.create_table(
        "shift_applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "shift_id",
            sa.Integer(),
            sa.ForeignKey("shifts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "status", apply_status, server_default=sa.text("'pending'"), nullable=False
        ),
        sa.Column(
            "has_conflict", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("conflict_note", sa.Text()),
        sa.Column(
            "reviewed_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "status = 'pending' OR status = 'cancelled' OR reviewed_by IS NOT NULL",
            name="ck_application_reviewer",
        ),
    )
    op.create_index("ix_application_shift_status", "shift_applications", ["shift_id", "status"])
    # Một Staff chỉ có 1 đơn chờ cho mỗi ca, nhưng apply lại được sau khi bị từ chối
    op.create_index(
        "uq_application_pending",
        "shift_applications",
        ["shift_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )

    # ------------------------------------------------------------------
    # 9. shift_exchanges
    # ------------------------------------------------------------------
    op.create_table(
        "shift_exchanges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "shift_id",
            sa.Integer(),
            sa.ForeignKey("shifts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "from_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "to_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT")
        ),
        sa.Column("message", sa.Text()),
        sa.Column(
            "status",
            exchange_status,
            server_default=sa.text("'available_for_exchange'"),
            nullable=False,
        ),
        sa.Column(
            "has_conflict", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("conflict_note", sa.Text()),
        sa.Column(
            "reviewed_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("taken_at", sa.DateTime(timezone=True)),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("cancelled_at", sa.DateTime(timezone=True)),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # BR-EX-03 enforce ở cấp CSDL đúng yêu cầu NFR-REL-03
        sa.CheckConstraint(
            "to_user_id IS NULL OR to_user_id <> from_user_id", name="ck_exchange_not_self"
        ),
        sa.CheckConstraint(
            "status <> 'available_for_exchange' OR to_user_id IS NULL",
            name="ck_exchange_open_no_taker",
        ),
        sa.CheckConstraint(
            "status NOT IN ('approved', 'rejected') "
            "OR (to_user_id IS NOT NULL AND reviewed_by IS NOT NULL)",
            name="ck_exchange_reviewed_complete",
        ),
    )
    op.create_index("ix_exchange_status", "shift_exchanges", ["status"])
    op.create_index("ix_exchange_from_status", "shift_exchanges", ["from_user_id", "status"])
    op.create_index("ix_exchange_to_status", "shift_exchanges", ["to_user_id", "status"])
    # BR-EX-02: lớp bảo vệ cuối cho tình huống 5 người cùng bấm nhận một ca
    op.create_index(
        "uq_exchange_active",
        "shift_exchanges",
        ["shift_id"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('available_for_exchange', 'pending_approval')"
        ),
    )

    # ------------------------------------------------------------------
    # 10. news_posts / news_images / news_reads
    # ------------------------------------------------------------------
    op.create_table(
        "news_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "author_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # CỐ Ý để NULL: nhãn "Đã chỉnh sửa" xét theo updated_at IS NOT NULL
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column(
            "deleted_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT")
        ),
    )
    op.execute(
        "CREATE INDEX ix_news_created_desc ON news_posts (created_at DESC) "
        "WHERE is_deleted = false"
    )

    op.create_table(
        "news_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "post_id",
            sa.Integer(),
            sa.ForeignKey("news_posts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("sort_order", sa.SmallInteger(), server_default="0", nullable=False),
        # UNIQUE + CHECK = giới hạn cứng 3 ảnh mỗi bài ở cấp CSDL
        sa.UniqueConstraint("post_id", "sort_order", name="uq_news_image_order"),
        sa.CheckConstraint("sort_order BETWEEN 0 AND 2", name="ck_news_image_order"),
    )

    op.create_table(
        "news_reads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "post_id",
            sa.Integer(),
            sa.ForeignKey("news_posts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "read_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Nhờ ràng buộc này mà mark-as-read là idempotent
        sa.UniqueConstraint("post_id", "user_id", name="uq_news_read"),
    )
    op.create_index("ix_news_read_user", "news_reads", ["user_id"])

    # ------------------------------------------------------------------
    # 11. notifications
    # ------------------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", notification_type, nullable=False),
        # Đa hình theo `type` nên CỐ Ý không đặt khóa ngoại
        sa.Column("reference_id", sa.Integer()),
        # Chỉ dùng cho roster_published (publish là thao tác hàng loạt)
        sa.Column("reference_date", sa.Date()),
        sa.Column("message", sa.String(255), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_notification_user_unread", "notifications", ["user_id", "is_read"])
    op.execute(
        "CREATE INDEX ix_notification_user_created ON notifications (user_id, created_at DESC)"
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("news_reads")
    op.drop_table("news_images")
    op.drop_table("news_posts")
    op.drop_table("shift_exchanges")
    op.drop_table("shift_applications")
    op.drop_table("shifts")
    op.drop_table("availabilities")
    op.drop_table("availability_submissions")
    op.drop_table("users")
    op.drop_table("locations")

    for enum_name in (
        "notification_type",
        "exchange_status",
        "apply_status",
        "assign_source",
        "shift_status",
        "user_role",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

    op.execute("DROP FUNCTION IF EXISTS op_minute(TIME)")
