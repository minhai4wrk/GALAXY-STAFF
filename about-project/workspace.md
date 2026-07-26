# 🎬 GALAXY STAFF — Claude Code Workspace Blueprint

> Copy toàn bộ cấu trúc này vào thư mục gốc `galaxy-staff/` của dự án.

---

## 📁 CẤU TRÚC THƯ MỤC `.claude/`

```
galaxy-staff/
├── CLAUDE.md                          # File chính — quy tắc dự án
├── CLAUDE.local.md                    # Ghi chú cá nhân (gitignore)
├── .gitignore
├── .claude/
│   ├── agents/
│   │   ├── backend-dev.md             # Agent chuyên backend FastAPI
│   │   ├── frontend-dev.md            # Agent chuyên frontend React
│   │   ├── report-writer.md           # Agent viết báo cáo tiếng Việt
│   │   ├── code-reviewer.md           # Agent review code
│   │   ├── test-writer.md             # Agent viết test
│   │   └── debugger.md                # Agent debug lỗi
│   ├── hooks/
│   │   ├── PostToolUse.sh             # Auto-format sau khi sửa file
│   │   └── PreCompact.sh             # Lưu trạng thái trước khi compact
│   ├── commands/
│   │   ├── sprint-status.md           # Xem tiến độ sprint hiện tại
│   │   ├── ship.md                    # Build, lint, test trước khi commit
│   │   ├── new-feature.md             # Scaffold tính năng mới
│   │   ├── seed-data.md               # Tạo/reset mock data
│   │   └── screenshot-remind.md       # Nhắc chụp screenshot cho báo cáo
│   ├── rules/
│   │   ├── api.md                     # Quy tắc viết API endpoint
│   │   ├── react.md                   # Quy tắc viết React component
│   │   └── testing.md                 # Quy tắc viết test
│   ├── output-styles/
│   │   └── terse.md                   # Chỉ code, không văn phong
│   └── settings.json
├── backend/
├── frontend/
└── docker-compose.yml
```

---

## 📄 NỘI DUNG TỪNG FILE

---

### `CLAUDE.md` (file gốc — < 200 dòng)

```markdown
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
2. Mỗi file ≤ 300 dòng. Nếu dài hơn → tách module
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

## Database Tables
users, locations, availabilities, shifts, shift_exchanges, news_posts, news_reads, notifications
→ Xem chi tiết ERD trong docs/erd.md
→ swap_offers (Swap ca) được bỏ khỏi Version 1, lên kế hoạch cho Version 2

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
- ⏰ Mỗi tính năng bị kẹt > 4h → đơn giản hóa, hỏi Claude
- 📸 Hoàn thành tính năng → CHỤP SCREENSHOT NGAY cho báo cáo
- 📝 Mỗi sprint xong → viết luôn phần báo cáo tương ứng
- 🧪 Viết test NGAY sau khi code, không để dồn
```

---

### `CLAUDE.local.md` (cá nhân, bị .gitignore)

```markdown
# Ghi chú cá nhân

## Tiến độ hiện tại
- Sprint: 0
- Ngày bắt đầu: [CẬP NHẬT]
- Task đang làm: [CẬP NHẬT]

## Ghi nhớ
- Báo cáo viết bằng Word (.docx)
- Diagram dùng draw.io
- Wireframe dùng Figma
- Notion để quản lý task

## Lỗi đã gặp & cách fix
(Ghi lại để không lặp)
```

---

### `.claude/agents/backend-dev.md`

```markdown
# Agent: Backend Developer

## Vai trò
Chuyên viết code backend FastAPI cho dự án Galaxy Staff.

## Ngữ cảnh
- Python 3.11 + FastAPI + SQLAlchemy 2.0 (async) + Alembic + PostgreSQL 16
- Auth: JWT (python-jose) + bcrypt + RBAC
- Validation: Pydantic v2
- Test: pytest + httpx

## Quy tắc
1. Mỗi endpoint có Pydantic schema rõ ràng (request + response)
2. Dependency injection qua FastAPI Depends()
3. Business logic đặt trong services/, KHÔNG viết trong router
4. Mọi query dùng SQLAlchemy async session
5. Luôn handle lỗi: HTTPException(status_code, detail)
6. Docstring tiếng Việt 1 dòng cho mỗi function
7. Type hints đầy đủ
8. Viết migration Alembic khi thay đổi model

## Template endpoint
```python
@router.post("/", response_model=ShiftResponse, status_code=201)
async def create_shift(
    data: ShiftCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_manager),  # RBAC
):
    """Tạo ca làm mới (chỉ Manager)."""
    shift = await shift_service.create(db, data, current_user.id)
    return shift
```

## Khi được gọi
- Viết code hoàn chỉnh, giải thích ngắn trong comment
- Luôn tạo kèm test file tương ứng
- Chạy `ruff check` trước khi xong

---

### `.claude/agents/frontend-dev.md`

```markdown
# Agent: Frontend Developer

## Vai trò
Chuyên viết code frontend React cho dự án Galaxy Staff.

## Ngữ cảnh
- React 18 + TypeScript strict + Vite
- UI: Tailwind CSS + shadcn/ui (KHÔNG tự viết component từ đầu)
- State: Zustand (auth, UI state) + TanStack Query (server data)
- HTTP: Axios instance với JWT interceptor
- Router: React Router v6

## Quy tắc
1. Mọi component là functional component + TypeScript interface cho props
2. KHÔNG dùng `any` — định nghĩa type trong types/
3. API call đặt trong services/, dùng TanStack Query hooks trong component
4. Tách logic ra custom hooks trong hooks/
5. Responsive: Desktop-first, dùng Tailwind breakpoints (md:, lg:)
6. Manager UI: Sidebar layout | Staff UI: Bottom nav (mobile)
7. Loading/Error state bắt buộc cho mọi data fetch
8. Comment tiếng Việt ngắn gọn

## Template component
```tsx
interface ShiftCardProps {
  shift: Shift;
  onEdit?: (id: string) => void;
}

export function ShiftCard({ shift, onEdit }: ShiftCardProps) {
  // Hiển thị thông tin 1 ca làm
  return (
    <Card className="p-4">
      <CardTitle>{shift.date}</CardTitle>
      {/* ... */}
    </Card>
  );
}
```

## Template API service
```tsx
// services/shift.service.ts
import { api } from "@/lib/axios";
import type { Shift, ShiftCreate } from "@/types/shift";

export const shiftService = {
  getAll: (params: { date: string; view: "day" | "week" }) =>
    api.get<Shift[]>("/shifts", { params }),
  create: (data: ShiftCreate) =>
    api.post<Shift>("/shifts", data),
};
```

## Template TanStack Query hook
```tsx
// hooks/useShifts.ts
import { useQuery } from "@tanstack/react-query";
import { shiftService } from "@/services/shift.service";

export function useShifts(date: string, view: "day" | "week") {
  return useQuery({
    queryKey: ["shifts", date, view],
    queryFn: () => shiftService.getAll({ date, view }),
  });
}
```

---

### `.claude/agents/report-writer.md`

```markdown
# Agent: Report Writer

## Vai trò
Viết báo cáo đồ án tiếng Việt, chuẩn học thuật, cho file Word (.docx).

## Ngữ cảnh
- Báo cáo ≥ 50 trang, tiếng Việt, định dạng chuẩn đại học VN
- Cấu trúc: Mở đầu → Chương 2 (Lý thuyết) → Chương 3 (Phân tích & Thiết kế) → Chương 4 (Kết quả) → Kết luận
- Citation: IEEE format
- Hình ảnh: mỗi ảnh có caption "Hình X.Y: Mô tả"
- Bảng: mỗi bảng có caption "Bảng X.Y: Mô tả"

## Quy tắc
1. Văn phong học thuật, không dùng "tôi/mình" — dùng "tác giả" hoặc câu bị động
2. Mỗi khái niệm kỹ thuật phải có citation [X]
3. KHÔNG copy-paste — viết bằng lời của mình, paraphrase
4. Mỗi chương bắt đầu bằng đoạn giới thiệu ngắn
5. Đoạn kết mỗi chương tóm tắt nội dung đã trình bày
6. Dùng thuật ngữ nhất quán xuyên suốt (ví dụ: "ca làm" không lúc "ca", lúc "shift")
7. Screenshot placeholder: [Hình X.Y: Mô tả — CHỤP SAU]

## Khi được gọi
- Viết từng section, không viết cả chương một lúc
- Output: nội dung sẵn sàng paste vào Word
- Ghi rõ chỗ nào cần chèn hình/bảng
```

---

### `.claude/agents/code-reviewer.md`

```markdown
# Agent: Code Reviewer

## Vai trò
Review code, tìm bug, gợi ý cải thiện.

## Checklist review
1. Type safety: có thiếu type hints / dùng any không?
2. Error handling: có try-except / error boundary không?
3. Security: SQL injection? XSS? Token leak? Hardcoded secret?
4. Performance: N+1 query? Unnecessary re-render? Missing index?
5. Code style: theo quy tắc CLAUDE.md không?
6. Test: có test cho logic mới không?

## Output format
- 🔴 Critical: bug hoặc security issue
- 🟡 Warning: nên sửa
- 🟢 Suggestion: nice-to-have
- Kèm code fix gợi ý
```

---

### `.claude/agents/test-writer.md`

```markdown
# Agent: Test Writer

## Vai trò
Viết test cho backend (pytest) và frontend (Vitest).

## Backend test template
```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seed_user):
    """Đăng nhập thành công với credentials đúng."""
    response = await client.post("/api/auth/login", json={
        "email": "staff@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, seed_user):
    """Đăng nhập thất bại với password sai."""
    response = await client.post("/api/auth/login", json={
        "email": "staff@test.com",
        "password": "wrong"
    })
    assert response.status_code == 401
```

## Quy tắc
1. Mỗi endpoint tối thiểu 3 test: success, validation error, auth error
2. Dùng fixtures cho seed data
3. Test name mô tả hành vi, docstring tiếng Việt
4. Happy path trước, edge case sau
5. Mục tiêu: ≥ 20 test cases backend, ≥ 10 frontend
```

---

### `.claude/agents/debugger.md`

```markdown
# Agent: Debugger

## Vai trò
Giúp debug khi bị kẹt (chỉ gọi khi cần).

## Quy trình debug
1. Đọc error message/traceback đầy đủ
2. Xác định file + dòng lỗi
3. Kiểm tra: lỗi logic, lỗi type, lỗi async, lỗi import?
4. Đề xuất fix CỤ THỂ (code snippet)
5. Giải thích NGẮN tại sao lỗi xảy ra (1-2 câu)
6. Gợi ý cách tránh lỗi tương tự trong tương lai

## Lỗi thường gặp dự án này
- SQLAlchemy async session: quên `await`, quên `async with`
- Alembic migration conflict: chạy `alembic heads` để check
- CORS error: kiểm tra middleware trong main.py
- JWT expired: kiểm tra token expiry trong config
- React re-render loop: dependency array trong useEffect
- Tailwind class không hoạt động: kiểm tra tailwind.config.ts content paths
```

---

### `.claude/hooks/PostToolUse.sh`

```bash
#!/bin/bash
# Tự động format code sau khi Claude sửa file

FILE="$1"
EXT="${FILE##*.}"

case "$EXT" in
  py)
    ruff format "$FILE" 2>/dev/null
    ruff check --fix "$FILE" 2>/dev/null
    ;;
  ts|tsx|js|jsx)
    npx prettier --write "$FILE" 2>/dev/null
    ;;
esac
```

---

### `.claude/hooks/PreCompact.sh`

```bash
#!/bin/bash
# Lưu trạng thái trước khi compact context

echo "=== PRE-COMPACT STATE $(date) ===" >> .claude/compact-log.md
echo "Current branch: $(git branch --show-current)" >> .claude/compact-log.md
echo "Last 3 commits:" >> .claude/compact-log.md
git log --oneline -3 >> .claude/compact-log.md
echo "Modified files:" >> .claude/compact-log.md
git status --short >> .claude/compact-log.md
echo "---" >> .claude/compact-log.md
```

---

### `.claude/commands/sprint-status.md`

```markdown
# /sprint-status

Kiểm tra tiến độ sprint hiện tại:

1. Đọc CLAUDE.local.md để biết sprint hiện tại
2. So sánh với timeline trong CLAUDE.md
3. Liệt kê:
   - ✅ Task đã hoàn thành
   - 🔄 Task đang làm
   - ⏳ Task chưa bắt đầu
   - ⚠️ Task có nguy cơ trễ deadline
4. Nhắc: Đã chụp screenshot chưa? Đã viết báo cáo phần tương ứng chưa?
```

---

### `.claude/commands/ship.md`

```markdown
# /ship

Chạy trước khi commit:

1. Backend: `cd backend && ruff check . && pytest tests/ -v --tb=short`
2. Frontend: `cd frontend && npx tsc --noEmit && npx eslint src/ && npx vitest run`
3. Nếu pass hết → hiển thị git diff --stat
4. Đề xuất commit message theo Conventional Commits
5. HỎI xác nhận trước khi commit
```

---

### `.claude/commands/new-feature.md`

```markdown
# /new-feature $feature_name $module

Scaffold tính năng mới:

1. Backend:
   - Tạo `backend/app/models/$feature_name.py`
   - Tạo `backend/app/schemas/$feature_name.py`
   - Tạo `backend/app/api/$feature_name.py`
   - Tạo `backend/app/tests/test_$feature_name.py`
   - Đăng ký router trong main.py

2. Frontend:
   - Tạo `frontend/src/types/$feature_name.ts`
   - Tạo `frontend/src/services/$feature_name.service.ts`
   - Tạo `frontend/src/hooks/use${FeatureName}.ts`
   - Tạo `frontend/src/pages/${FeatureName}Page.tsx`

3. Tạo Alembic migration nếu có model mới
```

---

### `.claude/commands/seed-data.md`

```markdown
# /seed-data

Tạo hoặc reset mock data:

1. Chạy `alembic upgrade head`
2. Chạy script `backend/scripts/seed.py`:
   - 1 Manager account (manager@galaxy.com / admin123)
   - 12 Staff accounts (staff01~12@galaxy.com / staff123)
   - 1 Location: "Galaxy Cinema Nguyễn Du"
   - Availability data: 2 tuần, random 60-80% slots available
   - 20 shifts mẫu (mix assigned + open)
   - 5 news posts mẫu
   - 3 shift exchange mẫu (pending, approved, rejected)
3. Hiển thị tóm tắt data đã seed
```

---

### `.claude/commands/screenshot-remind.md`

```markdown
# /screenshot-remind

Nhắc chụp screenshot cho báo cáo:

1. Kiểm tra sprint hiện tại
2. Liệt kê các tính năng đã hoàn thành trong sprint
3. Với mỗi tính năng, nhắc:
   - [ ] Screenshot UI chính
   - [ ] Screenshot Swagger API
   - [ ] Screenshot kết quả test (nếu có)
4. Gợi ý caption cho mỗi screenshot: "Hình X.Y: [mô tả]"
5. Nhắc lưu vào `docs/screenshots/sprint-X/`
```

---

### `.claude/rules/api.md`

```markdown
# Quy tắc API

- URL: lowercase, dấu gạch ngang, số nhiều: `/api/shifts`, `/api/news`
- Response format thống nhất:
  - Success: `{ data: T }` hoặc `{ data: T[], total: number }`
  - Error: `{ detail: string }`
- Pagination: `?page=1&size=20`
- Filter: query params: `?date=2026-06-15&view=week`
- Auth: Bearer token trong header Authorization
- Status codes: 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found
- Mọi endpoint Manager-only phải dùng `Depends(get_current_manager)`
```

---

### `.claude/rules/react.md`

```markdown
# Quy tắc React

- File naming: PascalCase cho component (ShiftCard.tsx), camelCase cho hooks (useShifts.ts)
- Mỗi page có Loading skeleton + Error fallback
- Form validation: React Hook Form + Zod
- Toast notification: sonner (đã có trong shadcn/ui)
- Date handling: date-fns (KHÔNG dùng moment.js)
- Icon: lucide-react
- Không inline style — chỉ dùng Tailwind classes
- Tối đa 1 component per file (trừ sub-components nhỏ)
```

---

### `.claude/rules/testing.md`

```markdown
# Quy tắc Testing

- Backend: pytest + httpx AsyncClient
- Frontend: Vitest + React Testing Library
- Mỗi API endpoint: tối thiểu 3 test (success, validation, auth)
- Test file đặt cạnh source: `tests/test_<module>.py`
- Fixtures trong `conftest.py`: db session, client, seed users
- KHÔNG mock database — dùng test database thật (Docker)
- Naming: `test_<action>_<expected_result>`
```

---

### `.claude/output-styles/terse.md`

```markdown
# Output style: Terse

- Chỉ code, không giải thích dài dòng
- Comment ngắn trong code thay vì giải thích ngoài
- Nếu cần giải thích: tối đa 2-3 dòng bullet
- Không lặp lại yêu cầu của user
- Không "Certainly!" / "Sure!" / "Great question!"
```

---

### `.claude/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Bash(ruff *)",
      "Bash(pytest *)",
      "Bash(npx prettier *)",
      "Bash(npx eslint *)",
      "Bash(npx tsc *)",
      "Bash(npx vitest *)",
      "Bash(docker compose *)",
      "Bash(alembic *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git branch *)"
    ],
    "deny": [
      "Bash(git push *)",
      "Bash(git commit *)",
      "Bash(rm -rf *)"
    ]
  }
}
```

---

### `.gitignore` (thêm dòng)

```
CLAUDE.local.md
.claude/compact-log.md
```

---

## 🔧 SETUP NHANH

Chạy lần lượt trong terminal:

```bash
# 1. Tạo cấu trúc thư mục
mkdir -p .claude/{agents,hooks,commands,rules,output-styles}
mkdir -p docs/screenshots/{sprint-0,sprint-1,sprint-2,sprint-3}

# 2. Copy nội dung từng file ở trên vào đúng vị trí

# 3. Cấp quyền cho hooks
chmod +x .claude/hooks/*.sh

# 4. Thêm vào .gitignore
echo "CLAUDE.local.md" >> .gitignore
echo ".claude/compact-log.md" >> .gitignore
```

---

## 🎯 CÁCH SỬ DỤNG

| Bạn muốn... | Gõ trong Claude Code |
|---|---|
| Viết API mới | `@backend-dev Tạo CRUD endpoint cho shifts` |
| Viết UI mới | `@frontend-dev Tạo trang Availability Grid` |
| Viết báo cáo | `@report-writer Viết phần 2.4 Công nghệ sử dụng` |
| Review code | `@code-reviewer Review file api/shifts.py` |
| Viết test | `@test-writer Viết test cho auth endpoints` |
| Debug lỗi | `@debugger [paste error]` |
| Check tiến độ | `/sprint-status` |
| Trước khi commit | `/ship` |
| Tạo tính năng mới | `/new-feature shifts roster` |
| Reset mock data | `/seed-data` |
| Nhắc chụp ảnh | `/screenshot-remind` |

---

## 📋 GỢI Ý SKILLS TÁI SỬ DỤNG

Nếu muốn mở rộng, có thể thêm `.claude/skills/`:

| Skill | Mô tả | Khi nào dùng |
|---|---|---|
| `crud-generator/` | Auto-generate model + schema + router + test | Mỗi khi tạo module mới |
| `docker-helper/` | Các lệnh Docker thường dùng | Debug container |
| `alembic-helper/` | Tạo/chạy/rollback migration | Thay đổi DB schema |
| `report-chapter/` | Template cho từng chương báo cáo | Viết báo cáo |

---

## ⚡ MẸO QUAN TRỌNG

1. **Bắt đầu mỗi session** → gõ `/sprint-status` để Claude biết bạn đang ở đâu
2. **Kết thúc mỗi session** → cập nhật `CLAUDE.local.md` với tiến độ mới
3. **Mỗi khi xong feature** → gõ `/screenshot-remind`
4. **Trước khi commit** → gõ `/ship`
5. **Bị kẹt > 30 phút** → gọi `@debugger` hoặc đơn giản hóa tính năng
