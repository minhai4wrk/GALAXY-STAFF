# Galaxy Staff — Hệ thống Quản lý Nhân sự Rạp Chiếu Phim

## Dự án
- Đồ án cá nhân đại học, **hạn nộp 05/10/2026**, mục tiêu điểm cao nhất
- Thiết kế xong 26/07/2026 · Thi công 27/07 → 04/10/2026 (10 tuần, 7 sprint)
- 1 người làm, dùng Personal Scrum
- Demo + Báo cáo ≥ 50 trang (.docx)
- Kế hoạch chi tiết: `about-project/tracker.md` (bản 2.0 — tài liệu chuẩn khi có xung đột mốc)

## Tech Stack
- **Backend**: Python 3.11 + FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL 16
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **State**: Zustand (global) + TanStack Query (server state/cache)
- **Auth**: JWT (python-jose) + bcrypt + RBAC (Manager/Staff)
- **Infra**: Docker Compose (dev), deploy lên Render (prod)
- **Test**: pytest + httpx (backend), Vitest (frontend)
- **Linting**: ESLint + Prettier (frontend), Ruff (backend)

## Quy tắc code TUYỆT ĐỐI
1. Code bằng tiếng Anh, comment giải thích ngắn bằng tiếng Việt
2. Nếu file quá dài → tách module
3. Mỗi function có docstring 1 dòng tiếng Việt
4. Type hints bắt buộc (Python + TypeScript strict)
5. Không dùng `any` trong TypeScript
6. Pydantic schema cho mọi request/response (backend)
7. Mọi API endpoint phải có try-except + HTTPException rõ ràng
8. Không hardcode: dùng .env + config.py
9. Import tuyệt đối, không relative import lung tung

## Git Rules
- Conventional Commits: feat|fix|docs|style|refactor|test|chore
- Format: `feat(module): mô tả ngắn tiếng Anh`
- Ví dụ: `feat(auth): add JWT login endpoint`
- HỎI TRƯỚC KHI COMMIT — không tự động commit
- Branch: main (prod), develop (dev), feature/* (tính năng)

## Cấu trúc Backend
```
backend/app/
├── api/           # Router endpoints (auth, users, availabilities, shifts, exchanges, news, notifications)
├── core/          # config.py, security.py, deps.py
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic request/response schemas
├── services/      # Business logic (auto_scheduler, notification_service)
├── tests/         # pytest test files
└── main.py        # FastAPI app entry
```

## Cấu trúc Frontend
```
frontend/src/
├── components/    # Reusable UI components
├── pages/         # Route pages
├── hooks/         # Custom React hooks
├── services/      # API call functions (axios instances)
├── stores/        # Zustand stores
├── types/         # TypeScript interfaces/types
├── lib/           # Utility functions
└── App.tsx
```

## Module Priority (MoSCoW)
- **Must**: Auth(JWT+RBAC), Availability Grid, Roster(xem+xếp ca), News Feed, Auto-Schedule(greedy)
- **Should**: Shift Exchange, WebSocket notification, Responsive
- **Could**: Drag-drop, Overlap View, Template-shift
- **Won't**: Multi-location, Payroll, Push FCM

## Database Tables (11 bảng — ERD v2.0)
locations, users, availability_submissions, availabilities, shifts, shift_applications, shift_exchanges, news_posts, news_images, news_reads, notifications
→ Xem chi tiết ERD trong docs/erd.md (mục 9 ghi lại lý do từng quyết định thiết kế)

Quy ước QUAN TRỌNG khi code (dễ sai nhất):
- `shifts` dùng `start_at`/`end_at` kiểu TIMESTAMPTZ, KHÔNG dùng date+start_time+end_time (rạp mở tới 2h sáng)
- `availabilities` dùng TIME + hàm SQL `op_minute()` để so sánh giờ qua nửa đêm
- "Open-shift" = `assigned_user_id IS NULL`, KHÔNG phải `status = 'open'`
- `shift_status` chỉ có `draft|published`; khóa khi trao đổi dùng cột `is_locked`
- Mọi cột thời điểm là TIMESTAMPTZ (server prod chạy UTC, rạp ở UTC+7)
- `swap_offers` (Swap ca) dời sang Version 2 — không có trong V1

## Khi tạo API endpoint mới
1. Tạo model trong models/
2. Tạo schema trong schemas/
3. Tạo router trong api/
4. Đăng ký router trong main.py
5. Viết test trong tests/
6. Chạy: pytest tests/ -v

## Khi tạo React page mới
1. Tạo page trong pages/
2. Tạo API service trong services/
3. Thêm route trong App.tsx
4. Dùng shadcn/ui components, KHÔNG tự viết từ đầu
5. Responsive: Desktop-first cho Manager, Mobile-friendly cho Staff

## Sprint Timeline (bản 2.0 — hạn nộp 05/10/2026)
| Sprint | Nội dung | Ngày |
|--------|----------|------|
| S0 ✅ | Phân tích + Thiết kế (55 FR, ERD 11 bảng, OpenAPI 45 endpoint) | → 26/07 |
| S1 | Nền tảng: models + Alembic + seed + scaffold FE + README | 27/07 – 02/08 |
| S2 | Auth + News Feed + Notification + deploy slice | 03/08 – 16/08 |
| S3 | Availability (grid kéo-thả + Overlap view) | 17/08 – 30/08 |
| S4 | Roster + Auto-Schedule → **CORE MVP** | 31/08 – 13/09 |
| S5 | Shift Exchange | 14/09 – 20/09 |
| S6 | Kiểm thử + Responsive + Deploy | 21/09 – 27/09 |
| S7 | Báo cáo + Slide + Nộp | 28/09 – 04/10 |

⚠️ Đã cắt khỏi V1: **kéo-thả xếp ca ở Roster** (dùng form/modal). Vẫn giữ kéo-thả ở Availability.

## Nhắc nhở quan trọng
- Mỗi tính năng bị kẹt > 4h → đơn giản hóa, hỏi Claude
- Hoàn thành tính năng → CHỤP SCREENSHOT NGAY cho báo cáo
- Mỗi sprint xong → viết luôn phần báo cáo tương ứng
- Viết test NGAY sau khi code, không để dồn
