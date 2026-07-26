# Galaxy Staff — Hệ thống Quản lý Nhân sự Rạp Chiếu Phim

## Dự án
- Đồ án cá nhân đại học, 8 tuần (T6–T7/2026), mục tiêu điểm cao nhất
- 1 người làm, dùng Personal Scrum (4 sprint × 2 tuần)
- Demo + Báo cáo ≥ 50 trang (.docx)

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

## Sprint Timeline
- Sprint 0 (Tuần 1-2): Thiết kế + Setup
- Sprint 1 (Tuần 3-4): Auth + Availability + News Feed
- Sprint 2 (Tuần 5-6): Roster + Auto-Schedule + Shift Exchange
- Sprint 3 (Tuần 7-8): Test + Polish + Báo cáo + Deploy

## Nhắc nhở quan trọng
- Mỗi tính năng bị kẹt > 4h → đơn giản hóa, hỏi Claude
- Hoàn thành tính năng → CHỤP SCREENSHOT NGAY cho báo cáo
- Mỗi sprint xong → viết luôn phần báo cáo tương ứng
- Viết test NGAY sau khi code, không để dồn
