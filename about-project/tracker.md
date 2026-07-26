# KẾ HOẠCH TRIỂN KHAI CHI TIẾT

## DỰ ÁN GALAXY STAFF – Hệ thống Quản lý Nhân sự Rạp Chiếu Phim

| Hạng mục | Thông tin |
|----------|-----------|
| Loại dự án | Đồ án cá nhân cấp đại học |
| Số người thực hiện | 1 |
| **Hạn nộp** | **05/10/2026 (Thứ 2)** |
| **Thời gian thi công còn lại** | **10 tuần — 27/07/2026 → 04/10/2026** |
| Giai đoạn đã xong | Phân tích & Thiết kế (kết thúc 26/07/2026) |
| Đầu ra | Hệ thống demo chạy online + Báo cáo ≥ 50 trang |
| Phiên bản kế hoạch | **2.0 — tái lập mốc ngày 26/07/2026** (xem [Phần F](#phần-f-nhật-ký-thay-đổi-kế-hoạch)) |

> ⚠️ **Bản 2.0 thay thế hoàn toàn bản 1.0.** Bản cũ đặt mốc 01/06 → 27/09 và chứa ERD 8 bảng + danh sách ~32 endpoint đã bị bác bỏ trong đợt audit thiết kế. Mọi số liệu trong tài liệu này đã đối chiếu với `docs/erd.md` v2.0 và `docs/api/openapi.yaml`.

---

## PHẦN A: PHƯƠNG PHÁP TRIỂN KHAI

### 1. Phương pháp phát triển: Agile cá nhân (Personal Scrum)

- **Sprint**: 7 sprint trong 10 tuần thi công. Sprint dài 1–2 tuần tùy khối lượng.
- **Daily log**: ghi nhật ký công việc mỗi ngày vào `CLAUDE.local.md` (thay cho daily standup).
- **Sprint Review**: cuối mỗi sprint tự đánh giá, demo nội bộ, **chụp màn hình ngay** cho báo cáo.
- **Definition of Done**: mỗi sprint có tiêu chí nghiệm thu riêng (xem từng sprint ở Phần B). Không tự cho phép "gần xong" — hoặc đạt hết tiêu chí, hoặc ghi vào nợ kỹ thuật của sprint sau.
- **Kanban board**: Notion hoặc GitHub Projects, trạng thái Backlog → In Progress → Review → Done.
- **Version Control**: Git Flow rút gọn — `main` (ổn định), `develop` (tích hợp), `feature/*` · `fix/*` · `docs/*`. Chi tiết ở [docs/git-workflow.md](../docs/git-workflow.md).

### 2. Chiến lược ưu tiên (MoSCoW) — bản đã chốt sau khi tái lập mốc

| Mức | Tính năng | Ghi chú |
|-----|-----------|---------|
| **Must Have** | Auth (JWT + RBAC), **Availability đầy đủ** (grid kéo-thả + Overlap view + Template-shift + deadline + min-5 ngày), Roster (xem ngày/tuần + xếp ca **bằng form/modal**), Auto-Scheduling (greedy), News Feed, Notification in-app (WebSocket) | Bắt buộc hoàn thành |
| **Should Have** | Shift Exchange (pass / nhận / duyệt + concurrency), Responsive mobile-web cho Staff, Cảnh báo xung đột khi xếp ca, Stress test | Đã cam kết giữ trong bản 2.0 |
| **Could Have** | Hiệu ứng UX nâng cao, polish loading/empty state, countdown deadline real-time (FR-AVAIL-13) | Làm nếu còn thời gian |
| **Won't Have (→ V2)** | **Kéo-thả xếp ca ở Roster** *(cắt ngày 26/07)*, Native mobile app (Flutter), Push notification FCM, **Swap ca 2 chiều (UC-14)**, Multi-location UI, Payroll API, bảng `audit_logs`, bảng `refresh_tokens` | Ghi vào mục "Hạn chế" và "Hướng phát triển" của báo cáo |

> **Vì sao cắt kéo-thả ở Roster mà giữ ở Availability**: drag-to-paint trên lưới Availability chính là điểm nhấn kiểu When2Meet — thứ phân biệt hệ thống này với một cái form thường, nên không hạ cấp. Còn ở Roster, thao tác kéo khối ca và kéo đổi người chỉ là *tiện nghi*: click ô ngày → mở form vẫn cho ra đúng kết quả nghiệp vụ. Đổi lại tiết kiệm khoảng 1 tuần cho phần khó thật sự là thuật toán auto-schedule.

### 3. Chiến lược phát triển kỹ thuật

- **Vertical slice theo module**: làm trọn từng module (backend → test qua Swagger → frontend) thay vì dồn hết backend rồi mới frontend. Sprint 2 cố tình làm nhóm tính năng "nhẹ" (Auth + News + Notification) trước để **thông pipeline và deploy sớm**, rồi mới vào phần khó.
- **Spec-first**: `docs/api/openapi.yaml` là hợp đồng. Mỗi `components.schemas.X` ứng với một class trong `backend/app/schemas/`. Giữ nguyên tên trường để `/docs` do FastAPI sinh ra trùng khớp file spec — lệch tên là dấu hiệu code đi chệch thiết kế.
- **Database-first**: schema đã chốt ở ERD v2.0, dùng Alembic migration ngay từ Sprint 1.
- **Component-driven Frontend**: dùng shadcn/ui có sẵn, không tự code component từ đầu.
- **Docker từ đầu**: môi trường nhất quán giữa dev và Render.

---

## PHẦN B: LỘ TRÌNH 10 TUẦN

> Tuần chạy từ **Thứ 2 đến Chủ nhật**. Chủ nhật là buffer, đừng tiêu trước.
> Báo cáo viết **song song từng sprint** — đây là điều kiện sống còn của bản kế hoạch nén này.

### Bảng mốc tổng thể

| Sprint | Nội dung | Tuần | Ngày | Mốc |
|--------|----------|------|------|-----|
| **S1** | Nền tảng (trả nợ thiết kế → chạy được) | T1 | 27/07 – 02/08 | M1 |
| **S2** | Auth + News Feed + Notification | T2–T3 | 03/08 – 16/08 | M2 |
| **S3** | Availability | T4–T5 | 17/08 – 30/08 | M3 |
| **S4** | Roster + Auto-Scheduling | T6–T7 | 31/08 – 13/09 | **M4 — CORE MVP** |
| **S5** | Shift Exchange | T8 | 14/09 – 20/09 | M5 |
| **S6** | Kiểm thử, Responsive & Deploy | T9 | 21/09 – 27/09 | M6 |
| **S7** | Hoàn thiện báo cáo, Slide & Nộp | T10 | 28/09 – 04/10 | M7 |
| — | **🎯 NỘP BÀI** | — | **05/10/2026** | — |

---

## ✅ GIAI ĐOẠN 0 — PHÂN TÍCH & THIẾT KẾ (đã hoàn thành 26/07/2026)

Giữ lại trong tài liệu để đối chiếu khi viết Chương 3 và khi bảo vệ.

| ID | Công việc | Trạng thái | Sản phẩm thực tế |
|----|-----------|-----------|------------------|
| S0-01 | Phân tích yêu cầu, đặc tả Use Case | ✅ | **55 FR** trên 5 module + **14 UC** (3 chi tiết, 11 tóm tắt) — `docs/requirements/` |
| S0-02 | Use Case Diagram | ✅ | 6 file: tổng quan + 5 module — `docs/diagrams/usecase-*.md` |
| S0-03 | Activity Diagram | ✅ | **4 sơ đồ** (availability, auto-schedule, shift-exchange, news-post) — đúng số lượng Chương 3.2 yêu cầu |
| S0-04 | Sequence Diagram | ✅ | 5 file / **12 sơ đồ**, lifeline theo tầng kiến trúc — `docs/diagrams/sequence-*.md` |
| S0-05 | Thiết kế ERD | ✅ | **ERD v2.0 — 11 bảng**, 3NF, đã soát chéo 2 lượt với toàn bộ FR/BR — `docs/erd.md` |
| S0-06 | API Specification | ✅ | **OpenAPI 3.0.3 — 45 endpoint / 36 path**, qua `openapi-spec-validator` không lỗi — `docs/api/openapi.yaml` |
| S0-07 | Tài liệu SRS | ✅ | 55 FR + **39 NFR** + 14 UC, gộp tại `docs/requirements/chapter3-requirements.md` |
| S0-10a | GitHub repo + Git Flow | ✅ | [github.com/minhai4wrk/GALAXY-STAFF](https://github.com/minhai4wrk/GALAXY-STAFF) — `main` + `develop`, Conventional Commits, `.gitignore` |
| S0-11 | Docker Compose | ✅ | postgres 16 + backend FastAPI, đã chạy thật, `/health` trả `{"status":"ok","database":"up"}` |

**Kết quả nổi bật của giai đoạn thiết kế** (dùng cho Chương 4.3 — Thảo luận):

| Đợt audit | Cách làm | Phát hiện |
|-----------|----------|-----------|
| Audit ERD | Đi từng FR/BR, hỏi *"dữ liệu này lưu ở cột nào?"* | **8 lỗi nặng + 12 lỗi vừa**, trong đó 3 lỗi khiến chức năng không thể chạy (ca qua nửa đêm bị CHECK constraint từ chối, thiếu bảng lưu đơn xin ca, không phân biệt được ca auto vs gán tay). ERD 8 → 11 bảng |
| Audit API | Đi từng FR, hỏi *"client gọi endpoint nào?"* | **8 endpoint** đã mô tả hành vi nhưng chưa từng đặc tả — nặng nhất là duyệt/từ chối đơn xin ca trống: bảng và ENUM đã có, endpoint thì không, nên đơn của Staff sẽ nằm chết ở `pending` |

> Cả hai đợt cho thấy cùng một bài học: **đọc xuôi tài liệu rồi đoán xem thiếu gì thì không bao giờ tìm ra**. Phải đi ngược từ yêu cầu về thiết kế.

### ❗ Nợ còn lại của giai đoạn thiết kế → dồn vào Sprint 1

| ID | Việc còn nợ | Vì sao chưa xong |
|----|-------------|------------------|
| S0-08 | Wireframe các màn hình chính | Chưa vẽ. Chương 3.5 cần 3–4 trang, không có wireframe thì không viết được |
| S0-09 | Đặc tả tương tác drag-to-paint (Availability) | Chưa viết. Bỏ qua bước này thì lúc code S3-05 sẽ mò |
| S0-10b | README.md | Chưa có. Còn là yêu cầu bắt buộc **NFR-DEPLOY-05** |
| S0-12b | `core/security.py` + `core/deps.py` | Scaffold backend mới có `config.py` + `database.py` |
| S0-13 | Scaffold Frontend | Thư mục `frontend/` chưa tồn tại |
| S0-14 | SQLAlchemy models + Alembic + seed | `models/` còn rỗng, chưa có `alembic/` |
| S0-17 | Export PNG/SVG toàn bộ diagram | `docs/diagrams/out/` chưa tồn tại — cần cho báo cáo |

---

## SPRINT 1 — NỀN TẢNG (Tuần 1: 27/07 – 02/08)

**Mục tiêu**: trả hết nợ thiết kế và đưa dự án từ trạng thái "có tài liệu" sang "chạy được". Kết thúc sprint phải gõ được `docker compose up` là có DB đủ 11 bảng, dữ liệu mẫu, và một trang React trắng hiện ra.

| ID | Công việc | Chi tiết | Ước lượng |
|----|-----------|----------|-----------|
| S1-01 | SQLAlchemy models — 11 bảng | Đúng ERD v2.0: ENUM native, `shifts.start_at/end_at` TIMESTAMPTZ, `assignment_source`, `is_locked` | 1,5 ngày |
| S1-02 | Alembic initial migration | Gồm cả hàm SQL `op_minute()`, extension `btree_gist`, 2 ràng buộc `EXCLUDE` chống chồng giờ, 2 unique index có điều kiện | 1 ngày |
| S1-03 | `core/security.py` + `core/deps.py` | Băm bcrypt (cost 12), tạo/verify JWT, `get_current_user`, `get_current_manager` | 0,5 ngày |
| S1-04 | Seed data | 1 Manager + 12 Staff + 1 location + lịch rảnh 2 tuần + ca mẫu + 3 bài news | 0,5 ngày |
| S1-05 | Scaffold Frontend | Vite + React 18 + TS strict + Tailwind + shadcn/ui + Zustand + TanStack Query + axios instance | 1 ngày |
| S1-06 | README.md | Mô tả dự án, kiến trúc, cài đặt, `.env`, chạy Docker, cấu trúc thư mục (NFR-DEPLOY-05) | 0,5 ngày |
| S1-07 | Export diagram PNG/SVG | Toàn bộ UCD + Activity + Sequence + ERD → `docs/diagrams/out/` | 0,5 ngày |
| S1-08 | Wireframe 8 màn hình (lo-fi) | Login · Dashboard M/S · Availability Grid · Overlap View · Roster tuần/ngày · Exchange Board · News Feed · Notification panel | 1 ngày |
| S1-09 | Đặc tả tương tác drag-to-paint | State machine của grid: mousedown/move/up, chế độ tô vs xóa, gộp ô liền nhau thành khoảng, logic template-shift, hành vi trên touch | 0,5 ngày |

**Definition of Done — M1 (02/08)**
- [ ] `alembic upgrade head` tạo đủ **11 bảng** + `op_minute()` + `btree_gist` + EXCLUDE constraint
- [ ] Chèn thử 2 khung giờ chồng nhau trong cùng ngày → **database từ chối** (chứng minh EXCLUDE hoạt động)
- [ ] Chèn thử ca `18:00 → 02:00` hôm sau → **được chấp nhận** (chứng minh đã hết bug ca qua nửa đêm)
- [ ] Seed chạy xong: đăng nhập được bằng tài khoản Manager mẫu qua Swagger
- [ ] `npm run dev` lên được trang React có Tailwind
- [ ] README đọc xong là người lạ chạy được dự án trong 15 phút

---

## SPRINT 2 — AUTH + NEWS FEED + NOTIFICATION (Tuần 2–3: 03/08 – 16/08)

**Mục tiêu**: thông toàn bộ pipeline full-stack bằng nhóm tính năng nhẹ, và **deploy live sớm** để rủi ro deploy không dồn về cuối kỳ.

### Tuần 2 (03/08 – 09/08): Backend

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S2-01 | Auth API — 5 endpoint | login, refresh, me, change-password, register. Lỗi đăng nhập **không phân biệt** email sai / mật khẩu sai (BR-06) |
| S2-02 | Users API — 5 endpoint | list (search/filter/phân trang), detail, update, toggle status, reset password. Chặn Manager tự vô hiệu hóa mình (BR-04) |
| S2-03 | News API — 8 endpoint | CRUD + upload ảnh (≤ 5MB, tối đa 3 ảnh) + mark-as-read **idempotent** + danh sách seen |
| S2-04 | Notification API — 3 endpoint + WebSocket | list, mark read, read-all; `WS /ws/notifications` fan-out khi có bài news mới |
| S2-05 | Test backend (≥ 12 TC) | Mỗi endpoint tối thiểu 3 ca: success / validation / auth |

### Tuần 3 (10/08 – 16/08): Frontend + Deploy

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S2-06 | Auth UI | Login, ProtectedRoute, điều hướng theo role, ép đổi mật khẩu khi `must_change_password = true` |
| S2-07 | Quản lý nhân viên UI (Manager) | Bảng danh sách + tìm kiếm + tạo/sửa + toggle active + reset mật khẩu |
| S2-08 | News Feed UI | Feed, tạo bài + ảnh, chi tiết, badge "Mới", panel seen tracking cho Manager |
| S2-09 | Notification UI | Chuông + badge số, dropdown, kết nối WebSocket, **fallback polling 30s** nếu WS lỗi |
| S2-10 | Deploy slice lên Render | Backend + Postgres + Frontend, cấu hình biến môi trường, smoke test trên URL live |
| S2-11 | Viết **Chương 2** (10–15 trang) | Cơ sở lý thuyết + công nghệ. Viết song song, không dồn |
| S2-12 | Sprint Review + **screenshot** | Chụp Login, phân quyền, News Feed, seen tracking, notification, Swagger |

**Definition of Done — M2 (16/08)**
- [ ] Đăng nhập → xem feed → nhận thông báo real-time, **chạy trên URL live** chứ không chỉ localhost
- [ ] Staff gọi endpoint Manager-only → nhận đúng **403**
- [ ] ≥ 12 test case xanh
- [ ] Đã có ảnh chụp màn hình cho Chương 4.1 phần Auth + News + Notification
- [ ] Chương 2 xong bản draft

---

## SPRINT 3 — AVAILABILITY (Tuần 4–5: 17/08 – 30/08)

**Mục tiêu**: module UX khó nhất, **không hạ cấp**. Đây là phần tạo ấn tượng khi demo.

### Tuần 4 (17/08 – 23/08): Backend + nền tảng lưới

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S3-01 | Availability API — batch upsert | Thay trọn bản đăng ký của tuần, server tự tính `total_days` |
| S3-02 | Overlap endpoint | Aggregate SQL đếm số người rảnh mỗi ô; **chỉ trả ô có người** để payload không phình |
| S3-03 | Deadline + min-5-ngày + stats | Khóa 18h00 Thứ 7 tính ở tầng service (không lưu cột), warning kèm `reason`, endpoint thống kê ai đã/chưa đăng ký |
| S3-04 | Test Availability (≥ 8 TC) | Đặc biệt: ca qua nửa đêm, chồng giờ, gọi API sau deadline phải nhận 403 |
| S3-05 | Component lưới 7 ngày × 36 ô | Render khung, header ngày T6→T5, cột giờ 8h00–02h00 |

### Tuần 5 (24/08 – 30/08): UX cốt lõi

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S3-06 | **Drag-to-paint** | Giữ + kéo để tô/xóa, hỗ trợ cả chuột lẫn cảm ứng — theo đặc tả S1-09 ⚠️ Khó |
| S3-07 | **Template-shift** | Sáng / Chiều / Tối / Full → tự fill; nút (+) nhập tay cho mobile |
| S3-08 | **Overlap View** | Heatmap gradient theo mật độ + hover/click ô hiện ai rảnh, ai bận ⚠️ Khó |
| S3-09 | Tích hợp | Save/load, countdown deadline, popup nhập lý do khi dưới 5 ngày, chuyển tuần |
| S3-10 | Viết **Chương 3.3** (thiết kế DB) + phần Availability của **3.5** | — |
| S3-11 | Sprint Review + **screenshot** | Grid, drag-to-paint, template, overlap heatmap, popup lý do, màn hình sau deadline |

**Definition of Done — M3 (30/08)**
- [ ] Staff đăng ký được lịch bằng kéo-thả **và** bằng nút (+), lưu rồi tải lại vẫn đúng
- [ ] Đăng ký ca tối `18:00 → 02:00` không lỗi ở cả API lẫn UI
- [ ] Overlap View hiện đúng mật độ, hover ra danh sách người
- [ ] Gọi API sau 18h00 Thứ 7 → 403 ngay cả khi bỏ qua giao diện
- [ ] Chương 3.3 xong draft

---

## SPRINT 4 — ROSTER + AUTO-SCHEDULING (Tuần 6–7: 31/08 – 13/09)

**Mục tiêu**: trái tim của hệ thống. Kết thúc sprint = **CORE MVP feature-complete**.

### Tuần 6 (31/08 – 06/09): Backend + thuật toán

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S4-01 | Shifts API — CRUD + filter | Tạo/sửa/xóa mềm, lọc theo ngày/tuần, lọc Open-shift. Chặn sửa/xóa ca `is_locked` |
| S4-02 | **Auto-Scheduling engine** | Greedy + ràng buộc C1–C5, kèm endpoint reset chỉ gỡ ca `assignment_source = auto` |
| S4-03 | Publish + đơn xin ca | Publish theo tuần + fan-out notification; apply / list / approve / reject / cancel đơn xin ca trống |
| S4-04 | Kiểm tra xung đột | 5 mã lỗi: `not_available`, `overlapping_shift`, `exceeds_weekly_hours`, `insufficient_rest`, `too_many_consecutive_days` + cơ chế `override_reason` |
| S4-05 | Benchmark + test (≥ 10 TC) | 50–100 NV × 200–300 ca, mục tiêu dưới 10 giây → chuẩn bị sẵn số liệu cho TC1 |

**Thuật toán Auto-Scheduling (greedy + constraint satisfaction)**

```
Input:
  open_shifts    : ca trống của tuần (assigned_user_id IS NULL)
  availabilities : lịch rảnh toàn bộ nhân viên trong tuần đó
  constraints    : max_hours_per_week=48, min_rest_hours=8, max_consecutive_days=6

Thuật toán:
  1. Sắp open_shifts theo độ ưu tiên (ca tối trước ca sáng, cuối tuần trước ngày thường)
  2. Với mỗi ca:
     a. Lọc nhân viên RẢNH đúng khung giờ  ......................... C5
     b. Loại người vi phạm: quá 48h/tuần (C1), nghỉ dưới 8h (C2),
        quá 6 ngày liên tiếp (C3), chồng ca đã có (C4)
     c. Sắp ứng viên còn lại theo tổng giờ ÍT NHẤT trước (cân bằng công bằng)
     d. Gán người đầu danh sách, cập nhật assigned_hours
     e. Không còn ai đủ điều kiện → giữ ca ở Open-shift + ghi unassigned_reason
  3. Trả về: assigned_shifts, unassigned_shifts, workload từng người

Độ phức tạp: O(S × N log N) — S ca, N nhân viên
Kết quả là DRAFT, Manager review rồi mới publish
```

> ⚠️ **Chỗ dễ sinh bug nhất toàn dự án**: `availabilities` lưu `day_of_week` + `TIME`, còn `shifts` lưu `TIMESTAMPTZ`. Khi kiểm tra C5 phải quy đổi `start_at` sang **giờ địa phương của rạp** rồi mới tính `op_minute` — server production chạy UTC. Công thức quy đổi ở [docs/erd.md](../docs/erd.md) mục 8.

### Tuần 7 (07/09 – 13/09): Frontend Roster

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S4-06 | Roster — Week view | Cột 7 ngày, hàng nhân viên, **hàng Open-shift trên cùng**, card ca có màu theo trạng thái |
| S4-07 | Roster — Day view | Timeline ngang 8h–02h, mỗi ca là một thanh |
| S4-08 | Xếp ca bằng **form/modal** | Click ô ngày → form tạo/sửa ca *(đã cắt kéo-thả — xem MoSCoW)* |
| S4-09 | Nút Auto-Schedule + Reset + Publish | Hiện kết quả: tỉ lệ phủ, ca chưa gán, bảng cân bằng giờ |
| S4-10 | Cảnh báo xung đột trên UI | Card đỏ + tooltip mô tả, hộp thoại xác nhận ghi đè → chuẩn bị TC3 |
| S4-11 | Staff: xem lịch cá nhân + apply Open-shift | Kèm tổng giờ tuần và danh sách đồng nghiệp cùng ca |
| S4-12 | Viết **Chương 3.4** (API) + **3.6** (thuật toán) | — |
| S4-13 | Sprint Review + **screenshot** | Week view, Day view, form xếp ca, kết quả auto-schedule, cảnh báo đỏ, publish |

**Definition of Done — M4 (13/09) — CORE MVP**
- [ ] Manager tạo ca → chạy Auto-Schedule → sửa tay vài ca → Publish → Staff thấy lịch
- [ ] Auto-Schedule đạt **≥ 90%** tỉ lệ gán và chạy **dưới 10 giây** ở quy mô benchmark
- [ ] Xếp người vượt 48h → hiện cảnh báo đỏ, có đường ghi đè kèm lý do
- [ ] Staff apply ca trống → Manager duyệt → ca chuyển sang Staff + thông báo tới nơi
- [ ] Chương 3.4 và 3.6 xong draft

---

## SPRINT 5 — SHIFT EXCHANGE (Tuần 8: 14/09 – 20/09)

**Mục tiêu**: trao đổi ca (pass / nhận / duyệt) với xử lý tranh chấp đồng thời. Nén còn 1 tuần vì thiết kế đã xong trọn vẹn và đây là lần thứ ba lặp lại mẫu CRUD + approve/reject.

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S5-01 | Exchange API — 6 endpoint | list, pass ca (+ lời nhắn), hủy pass, nhận ca, approve, reject |
| S5-02 | Chống tranh chấp | Optimistic locking `UPDATE ... WHERE status='available_for_exchange'` + unique index có điều kiện ở DB → chuẩn bị TC2 |
| S5-03 | Cảnh báo trùng giờ hai bước | Lần gọi đầu trả 409 kèm mô tả; gọi lại với `confirm_conflict=true` mới cho nhận, đánh dấu để Manager thấy khi duyệt |
| S5-04 | Exchange Board UI | Bố cục như Roster: ca thường xám nhạt, ca đang pass highlight cam, ca chờ duyệt highlight tím |
| S5-05 | UI nhận ca + duyệt | Popup chi tiết + lời nhắn + nút "Nhận ca"; màn hình duyệt của Manager có hiện cảnh báo |
| S5-06 | Test Exchange (≥ 8 TC) | Bắt buộc có ca **5 request đồng thời → đúng 1 thành công** |
| S5-07 | Rà soát notification toàn hệ thống | Đủ 10 loại `notification_type`, click điều hướng đúng ngữ cảnh |
| S5-08 | Sprint Review + **screenshot** | Board, popup lời nhắn, cảnh báo trùng giờ, màn duyệt, thông báo hai chiều |

**Definition of Done — M5 (20/09)**
- [ ] Chuỗi A pass → B nhận → Manager duyệt → ca sang B, cả hai đều nhận thông báo
- [ ] Test đồng thời 5 request: đúng 1 thành công, 4 nhận 409
- [ ] Không ai tự nhận được ca mình đăng (chặn ở cả service lẫn CHECK constraint)
- [ ] Đủ **5 module**, notification phủ hết sự kiện

---

## SPRINT 6 — KIỂM THỬ, RESPONSIVE & DEPLOY (Tuần 9: 21/09 – 27/09)

**Mục tiêu**: hệ thống ổn định, chạy tốt trên điện thoại, deploy hoàn chỉnh, dữ liệu sẵn sàng demo.

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S6-01 | Unit test toàn bộ + coverage | Tổng ≥ 40 TC (cộng dồn các sprint), xuất báo cáo coverage |
| S6-02 | **TC1** — Auto-Scheduling | 200 ca trống × 50 nhân viên → ≥ 90% gán đúng, không vi phạm ràng buộc, dưới 10s |
| S6-03 | **TC2** — Pass ca / Nhận ca | Đúng trạng thái từng bước, cảnh báo trùng giờ, thông báo đúng người, request đồng thời bị chặn |
| S6-04 | **TC3** — Cảnh báo quá giờ | Xếp vượt 48h hoặc chồng ca → hiện cảnh báo; auto-schedule **không** tự gán ca vi phạm |
| S6-05 | Responsive + fix CSS | 375 / 414 / 768 / 1024px. Staff dùng mobile-web là chính |
| S6-06 | Stress test | Locust hoặc JMeter: 50–100 người cùng lưu lịch rảnh sát deadline |
| S6-07 | Deploy hoàn chỉnh + mock data | Toàn bộ stack trên Render, seed 1 Manager + 12 Staff + lịch 2 tuần + ca + news |
| S6-08 | Fix bug tổng + polish | Color-coding, empty state, loading skeleton, thông báo lỗi tiếng Việt |
| S6-09 | Viết **Chương 4** | Kết quả triển khai (ảnh 5 module) + kết quả kiểm thử |

**Definition of Done — M6 (27/09)**
- [ ] Cả 3 test case nghiệm thu **đạt**, có số liệu và ảnh chụp
- [ ] Không còn lỗi chặn luồng demo
- [ ] URL live chạy được từ điện thoại
- [ ] Chương 4 xong draft

---

## SPRINT 7 — BÁO CÁO, SLIDE & NỘP (Tuần 10: 28/09 – 04/10)

**Mục tiêu**: hoàn thiện báo cáo ≥ 50 trang, Turnitin, slide, tổng duyệt demo.

| ID | Công việc | Chi tiết | Hạn |
|----|-----------|----------|-----|
| S7-01 | Hoàn thiện Chương 4 + Kết luận | Đánh giá ưu/nhược, bài học, hướng phát triển V2 | 29/09 |
| S7-02 | Tài liệu tham khảo + danh mục | ≥ 10–15 nguồn theo IEEE/APA; danh mục hình / bảng / viết tắt | 30/09 |
| S7-03 | Phụ lục A–F | HDSD Manager & Staff, mã nguồn auto-scheduler, ERD đầy đủ, export Swagger, hướng dẫn cài đặt | 01/10 |
| S7-04 | Mở đầu + Lời cảm ơn + Mục lục + soát toàn bộ | Chính tả, định dạng, đánh số hình/bảng, trích dẫn | 02/10 |
| S7-05 | **Turnitin** | Chỉnh sửa nếu vượt 20% — **chừa đủ thời gian, đây là mục dễ vỡ kế hoạch nhất** | 02/10 |
| S7-06 | Slide 15–20 trang | Vấn đề → giải pháp → kiến trúc → demo → kết quả | 03/10 |
| S7-07 | Dry-run demo | Diễn thử kịch bản 3 test case trên bản live, fix lỗi cuối | 03/10 |
| S7-08 | Buffer dự phòng | **Đừng tiêu trước** | 04/10 |
| S7-09 | 🎯 **NỘP BÀI** | Source, PDF, slide, link demo, kết quả Turnitin | **05/10** |

**Definition of Done — M7 (04/10)**
- [ ] Báo cáo ≥ 50 trang nội dung chính, định dạng thống nhất
- [ ] Turnitin dưới ngưỡng cho phép
- [ ] Slide + kịch bản demo đã diễn thử ít nhất một lượt trọn vẹn

---

## PHẦN C: THAM CHIẾU THIẾT KẾ (đã chốt)

> Phần này thay thế các khối ERD/API lỗi thời của bản 1.0. **Nguồn sự thật** vẫn là
> [docs/erd.md](../docs/erd.md) và [docs/api/openapi.yaml](../docs/api/openapi.yaml) — nếu lệch, tin hai file đó.

### C.1. ERD v2.0 — 11 bảng

```
locations                (id, name, address, created_at)
users                    (id, email UK, password_hash, full_name, role,
                          location_id FK, is_active, must_change_password, created_at, updated_at)
availability_submissions (id, user_id FK, week_start, total_days, reason,
                          submitted_at, updated_at)               UNIQUE(user_id, week_start)
availabilities           (id, submission_id FK, day_of_week, start_time, end_time, created_at)
shifts                   (id, location_id FK, work_date, week_start, start_at, end_at,
                          assigned_user_id FK NULL, assignment_source, assigned_at,
                          status, is_locked, unassigned_reason, override_reason,
                          is_deleted, created_by FK, published_at, created_at, updated_at)
shift_applications       (id, shift_id FK, user_id FK, status, has_conflict, conflict_note,
                          reviewed_by FK, created_at, reviewed_at)
shift_exchanges          (id, shift_id FK, from_user_id FK, to_user_id FK NULL, message,
                          status, has_conflict, conflict_note, reviewed_by FK,
                          created_at, taken_at, reviewed_at, cancelled_at, updated_at)
news_posts               (id, author_id FK, title, content, is_deleted,
                          created_at, updated_at, deleted_at, deleted_by FK)
news_images              (id, post_id FK, image_url, sort_order)   UNIQUE(post_id, sort_order)
news_reads               (id, post_id FK, user_id FK, read_at)     UNIQUE(post_id, user_id)
notifications            (id, user_id FK, type, reference_id, reference_date,
                          message, is_read, created_at)
```

**Bốn quy ước dễ code sai nhất** — dán lên màn hình khi làm Sprint 1 và 4:

| # | Quy ước | Hậu quả nếu làm sai |
|---|---------|---------------------|
| 1 | `shifts` dùng `start_at`/`end_at` TIMESTAMPTZ, **không** dùng date + start_time + end_time | Ca 18h→2h có `end_time < start_time` làm sai mọi phép tính giờ và bị CHECK constraint từ chối |
| 2 | **Open-shift** = `assigned_user_id IS NULL`, **không** phải `status = 'open'` | `shift_status` chỉ có `draft`/`published`; không biểu diễn được "ca trống nhưng lịch đã publish" mà FR-ROSTER-09 cần |
| 3 | Khóa khi trao đổi dùng cột `is_locked`, không nhét vào `status` | Hai khái niệm "đã phân công chưa" và "đã công bố chưa" có thể cùng đúng một lúc → phải là hai cột |
| 4 | So sánh giờ ở `availabilities` phải qua `op_minute()` | `02:00 < 18:00` theo kiểu TIME, so sánh trực tiếp luôn cho kết quả sai |

### C.2. API — 45 endpoint / 36 path

```
System (1)
  GET    /health

Auth (5)                              Users (5)
  POST   /api/auth/login                GET    /api/users
  POST   /api/auth/refresh              GET    /api/users/{id}
  GET    /api/auth/me                   PUT    /api/users/{id}
  PUT    /api/auth/change-password      PATCH  /api/users/{id}/status
  POST   /api/auth/register             POST   /api/users/{id}/reset-password

Availabilities (4)                    Shifts (9)
  GET    /api/availabilities            GET    /api/shifts
  POST   /api/availabilities            GET    /api/shifts/{id}
  GET    /api/availabilities/overview   POST   /api/shifts
  GET    /api/availabilities/stats      PUT    /api/shifts/{id}
                                        DELETE /api/shifts/{id}
Shift Applications (4)                  POST   /api/shifts/auto-schedule
  GET    /api/shift-applications         POST   /api/shifts/auto-schedule/reset
  PUT    /api/shift-applications/{id}/approve   POST /api/shifts/publish
  PUT    /api/shift-applications/{id}/reject    POST /api/shifts/{id}/apply
  DELETE /api/shift-applications/{id}

Exchanges (6)                         News (8)
  GET    /api/exchanges                 GET    /api/news
  POST   /api/exchanges                 POST   /api/news
  DELETE /api/exchanges/{id}            POST   /api/news/images
  POST   /api/exchanges/{id}/take       GET    /api/news/{id}
  PUT    /api/exchanges/{id}/approve    PUT    /api/news/{id}
  PUT    /api/exchanges/{id}/reject     DELETE /api/news/{id}
                                        POST   /api/news/{id}/read
Notifications (3)                       GET    /api/news/{id}/reads
  GET    /api/notifications
  PUT    /api/notifications/{id}/read   WebSocket (không mô tả được bằng OpenAPI 3.0)
  PUT    /api/notifications/read-all      WS   /ws/notifications?token=
```

> **Bẫy khai báo route trong FastAPI**: đăng ký đường dẫn tĩnh **trước** đường dẫn có tham số.
> Ba chỗ dính: `/api/shifts/auto-schedule` (trước `/{id}`), `/api/notifications/read-all`
> (trước `/{id}/read`), `/api/news/images` (trước `/{id}`).

### C.3. Cấu trúc thư mục

```
GALAXY_STAFF/
├── backend/
│   ├── app/
│   │   ├── api/          auth · users · availabilities · shifts
│   │   │                 shift_applications · exchanges · news · notifications
│   │   ├── core/         config.py · database.py · security.py · deps.py
│   │   ├── models/       (11 bảng theo ERD v2.0)
│   │   ├── schemas/      (Pydantic, ánh xạ 1-1 với components.schemas của OpenAPI)
│   │   ├── services/     auto_scheduler.py · notification_service.py
│   │   ├── tests/        conftest.py + test_<module>.py
│   │   └── main.py
│   ├── alembic/          versions/
│   ├── uploads/          (ảnh News — không commit)
│   ├── Dockerfile · requirements.txt · pyproject.toml
├── frontend/
│   ├── src/              components/ pages/ hooks/ services/ stores/ types/ lib/
│   ├── Dockerfile · package.json
├── docker/postgres/init/ 01-init.sql
├── docs/
│   ├── requirements/     55 FR · 39 NFR · 14 UC · chapter3-requirements.md
│   ├── diagrams/         6 UCD · 4 Activity · 12 Sequence · out/ (PNG export)
│   ├── api/              openapi.yaml · README.md
│   ├── erd.md · git-workflow.md
├── about-project/        charter · description · instruction · tracker · workspace
├── docker-compose.yml · .env.example · README.md · CLAUDE.md
```

---

## PHẦN D: CẤU TRÚC BÁO CÁO

Tổng ≥ 50 trang nội dung chính (Mở đầu → Kết luận). Cột cuối ghi **sprint nào viết phần nào** — bám theo đó thì không bị dồn.

| Phần | Nội dung | Số trang | Viết ở |
|------|----------|----------|--------|
| Trang bìa, Lời cảm ơn, Mục lục, Danh mục hình/bảng/viết tắt | — | ~6 | S7 |
| **MỞ ĐẦU** | Lý do chọn đề tài · Mục tiêu · Đối tượng & phạm vi · Phương pháp · Bố cục | 3–4 | S7 |
| **CHƯƠNG 1** | Tổng quan đề tài, bài toán thực tế tại rạp | 3–5 | S2 |
| **CHƯƠNG 2** | Cơ sở lý thuyết & công nghệ | 10–15 | **S2** |
| **CHƯƠNG 3** | Phân tích & thiết kế hệ thống | 15–20 | S2→S4 |
| **CHƯƠNG 4** | Kết quả & thảo luận | 10–15 | **S6** |
| **KẾT LUẬN** | Kết quả · đóng góp · hạn chế · hướng phát triển | 1–2 | S7 |
| Tài liệu tham khảo · Phụ lục A–F | — | — | S7 |

### Chương 2 — Cơ sở lý thuyết và công nghệ (10–15 trang)
- **2.1** Quản lý nhân sự ngành dịch vụ: đặc thù rạp chiếu phim (ca kíp linh hoạt, part-time, giờ cao điểm), vấn đề của quy trình Google Sheets + Messenger
- **2.2** Hệ thống tương tự: When2Meet (grid trực quan nhưng không xếp ca), Deputy / 7shifts / Homebase (chuyên nghiệp nhưng tốn phí), Google Sheets — so sánh rồi rút ra yêu cầu
- **2.3** Kiến trúc đa tầng: Presentation – Business – Data; nguyên tắc REST; vì sao chọn Monolith
- **2.4** Công nghệ: React + TS, Tailwind + shadcn/ui, FastAPI, PostgreSQL + SQLAlchemy + Alembic, JWT + bcrypt + RBAC, WebSocket, Docker
- **2.5** Bài toán xếp ca như một Constraint Satisfaction Problem: cách tiếp cận greedy, so sánh với ILP và Genetic Algorithm, lý do chọn greedy

### Chương 3 — Phân tích và thiết kế (15–20 trang)
- **3.1** Phương pháp & công cụ *(S2)* — Personal Scrum, Git Flow, Notion, draw.io, Figma
- **3.2** Phân tích yêu cầu *(S2)* — **55 FR** trên 5 module, **39 NFR** trên 7 nhóm, **14 UC**, 6 Use Case Diagram, 4 Activity Diagram
- **3.3** Thiết kế cơ sở dữ liệu *(S3)* — ERD **11 bảng**, chi tiết cột/ràng buộc/index, phân tích 3NF, **17 quyết định thiết kế kèm lý do** (mục 9 của erd.md — phần đáng giá nhất khi bảo vệ)
- **3.4** Thiết kế API *(S4)* — quy ước REST, **45 endpoint**, luồng JWT, ma trận RBAC, 12 Sequence Diagram
- **3.5** Thiết kế giao diện *(S3–S4)* — wireframe 8 màn hình, chiến lược responsive (desktop-first cho Manager, mobile-friendly cho Staff)
- **3.6** Thuật toán Auto-Scheduling *(S4)* — input/output, lưu đồ, ràng buộc C1–C5, độ phức tạp

### Chương 4 — Kết quả và thảo luận (10–15 trang)
- **4.1** Kết quả triển khai — ảnh chụp 5 module + Swagger
- **4.2** Kết quả kiểm thử — bảng unit test + 3 test case nghiệm thu + responsive + hiệu năng
- **4.3** Thảo luận — đối chiếu với tiêu chí đề ra; **hai đợt audit thiết kế** (20 lỗi ERD + 8 lỗ hổng API) là chất liệu tốt cho phần bài học kinh nghiệm; hạn chế đã biết: không có audit log, JWT không thu hồi được, tỉ lệ đọc không snapshot, chỉ 1 rạp, không kéo-thả ở Roster

---

## PHẦN E: QUẢN TRỊ RỦI RO

### E.1. Sổ rủi ro

| # | Rủi ro | Khả năng | Ảnh hưởng | Phòng ngừa | Dấu hiệu kích hoạt |
|---|--------|----------|-----------|------------|--------------------|
| R1 | Drag-to-paint (S3-06) ngốn quá nhiều thời gian | Cao | Trễ M3 | Đã có đặc tả tương tác từ S1-09 trước khi code | Hết 23/08 mà lưới chưa tô được ô nào |
| R2 | Auto-schedule sai vì quy đổi TIMESTAMPTZ ↔ TIME | Cao | Sai kết quả TC1 | Viết test cho `op_minute()` **trước** khi viết thuật toán | Ca tối bị bỏ sót khi gán |
| R3 | Deploy Render lỗi vì khác môi trường | Trung bình | Trễ M6 | Đã deploy slice từ S2 (16/08), không dồn về cuối | Smoke test trên live thất bại |
| R4 | Turnitin vượt 20% | Trung bình | Trễ nộp | Viết bằng lời mình, paraphrase mọi tài liệu tham khảo | Kết quả lần quét đầu > 20% |
| R5 | WebSocket không ổn định trên free tier | Trung bình | Mất tính năng real-time | Đã thiết kế sẵn fallback polling 30s (BR-NW-08) | Kết nối rớt liên tục khi test live |
| R6 | Báo cáo dồn vào tuần cuối | Cao | Không đủ 50 trang | Mỗi sprint có task viết chương tương ứng, tính vào Definition of Done | Kết thúc sprint mà chương tương ứng chưa có draft |
| R7 | Quá tải sát deadline 18h Thứ 7 | Thấp | Staff không lưu được lịch | Stress test ở S6-06 | Thời gian phản hồi API vượt 1 giây khi test tải |

### E.2. Thứ tự cắt nếu chạm điểm kiểm tra mà chưa xong

Cắt **theo đúng thứ tự này**, cắt xong ghi ngay vào mục "Hạn chế" của báo cáo:

| Ưu tiên cắt | Hạng mục | Tiết kiệm | Điểm kiểm tra |
|-------------|----------|-----------|---------------|
| 1 | Stress test (S6-06) | ~2 ngày | 25/09 |
| 2 | WebSocket → polling 30s | ~3 ngày | 09/08 (trước khi làm S2-09) |
| 3 | Countdown deadline real-time (Could Have) | ~1 ngày | 28/08 |
| 4 | Day view của Roster, chỉ giữ Week view | ~2 ngày | 10/09 |
| 5 | **Shift Exchange → Version 2** | ~1 tuần | **13/09 — nếu M4 chưa đạt thì cắt ngay, không do dự** |

> Điểm kiểm tra quan trọng nhất là **13/09 (M4)**. Đến ngày đó mà CORE MVP chưa feature-complete thì bỏ hẳn Shift Exchange và dùng Tuần 8 cho kiểm thử. Thiết kế của module này đã hoàn chỉnh (FR + Sequence + ERD + 6 endpoint đặc tả) nên **vẫn viết được trọn vẹn vào phần thiết kế của báo cáo dù không code** — mất tính năng nhưng không mất trang báo cáo.

### E.3. Nguyên tắc làm việc

**Thời gian**
- **80/20**: chức năng cốt lõi chạy ổn định hơn là nhiều chức năng chạy lỗi.
- **Timeboxing**: kẹt quá 4 giờ → đơn giản hóa hoặc chuyển việc khác, đừng cố đấm.
- **Báo cáo viết song song**: mỗi sprint xong là chương tương ứng phải có draft. Đây là điều kiện của Definition of Done, không phải lời khuyên.

**Kỹ thuật**
- **Seed data sớm** (S1-04): có dữ liệu từ Tuần 1 thì test và demo dễ hơn hẳn.
- **Chụp màn hình ngay** khi xong tính năng. Đừng đợi cuối kỳ — lúc đó giao diện đã đổi, dữ liệu đã khác.
- **Swagger là tài liệu miễn phí**: FastAPI tự sinh, tận dụng cho Phụ lục E.
- **Viết test ngay sau khi code**, không để dồn. Mỗi endpoint tối thiểu 3 ca: success, validation, auth.
- **Nhật ký lỗi**: mọi bug mất hơn 1 giờ để tìm ra đều ghi vào mục "Lỗi đã gặp & cách fix" của `CLAUDE.local.md` — đây là chất liệu trực tiếp cho Chương 4.3.

**Báo cáo**
- **Hình ảnh = trang**: mỗi ảnh kèm chú thích chiếm khoảng 1/3 trang, mỗi sơ đồ khoảng 1/2 trang.
- **Trích dẫn đủ**: mỗi công nghệ, mỗi khái niệm lý thuyết đều cần nguồn, theo IEEE hoặc APA.
- **Turnitin**: viết bằng lời của mình. Không copy-paste từ tài liệu gốc.

---

## PHẦN F: NHẬT KÝ THAY ĐỔI KẾ HOẠCH

### Bản 2.0 — 26/07/2026: tái lập mốc

| Thay đổi | Bản 1.0 | Bản 2.0 | Lý do |
|----------|---------|---------|-------|
| Hạn nộp | 27/09/2026 | **05/10/2026** | Mốc mới nhất từ phía nhà trường |
| Xung đột timeline | `charter.md` và `CLAUDE.md` ghi 8 tuần (kết thúc cuối T7), `tracker.md` ghi 17 tuần | Đồng bộ toàn bộ về **05/10/2026** | Ba tài liệu ghi ba mốc khác nhau, không thể lập kế hoạch trên nền mâu thuẫn |
| Cấu trúc sprint | 7 sprint / 17 tuần, tính từ 01/06 | 7 sprint / **10 tuần thi công**, tính từ 27/07 | Giai đoạn thiết kế đã tiêu hết phần thời gian trước 26/07 |
| Khối ERD trong tài liệu | 8 bảng, `availabilities.status`, `shifts.date+start_time+end_time`, `news_posts.image_url` | **11 bảng** đúng ERD v2.0 | Bản cũ chính là thiết kế **đã bị bác bỏ** trong đợt audit. Copy vào báo cáo sẽ mâu thuẫn với Chương 3.3 |
| Khối API trong tài liệu | ~32 endpoint | **45 endpoint** | Thiếu toàn bộ nhóm đơn xin ca, reset auto-schedule, upload ảnh, healthcheck |
| Kéo-thả xếp ca ở Roster | Must Have | **Won't Have → V2** | Cắt để dồn thời gian cho auto-schedule. Click ô → form vẫn cho ra đúng kết quả nghiệp vụ |
| Sprint Availability | 3 tuần | 2 tuần | Backend rút ngắn được vì API đã đặc tả xong hoàn toàn từ trước |
| Sprint Roster | 3 tuần | 2 tuần | Nhờ cắt kéo-thả |
| Sprint Exchange | 2 tuần | 1 tuần | Thiết kế đã trọn vẹn, và là lần thứ ba lặp mẫu CRUD + approve/reject |
| Definition of Done | Không có | Có, cho từng sprint | Tránh tự đánh lừa bằng trạng thái "gần xong" |
| Sổ rủi ro | 1 dòng | 7 rủi ro + cut-list kèm ngày kiểm tra | Kế hoạch nén thì phải biết trước sẽ cắt gì và cắt lúc nào |

### Đánh giá độ khả thi

Khối lượng còn lại theo bản 1.0 là khoảng 14 tuần công việc, nay phải gói trong 10 tuần. Ba nguồn bù đắp:

1. **Thiết kế đã xong 100%** — ERD, 45 endpoint, 12 sequence diagram đều đã chốt. Bản 1.0 giả định vừa code vừa thiết kế; giờ chỉ còn hiện thực hóa.
2. **Cắt kéo-thả ở Roster** — tiết kiệm khoảng 1 tuần ở đúng chỗ khó.
3. **Chương 3 gần như đã viết sẵn** — `docs/requirements/`, `docs/erd.md`, `docs/api/README.md` là bản thảo trực tiếp cho các mục 3.2–3.4. Việc còn lại là biên tập, không phải viết mới.

**Vẫn còn căng ở hai chỗ**: Sprint 5 nén Shift Exchange xuống 1 tuần, và Sprint 7 chỉ có 1 tuần cho khâu hoàn thiện báo cáo. Cả hai đã có phương án đối phó — cut-list mục E.2 và quy tắc viết báo cáo song song từng sprint.

---

*Tài liệu này là kế hoạch triển khai chính thức của dự án. Khi có xung đột với `charter.md` hoặc `CLAUDE.md`, lấy tài liệu này làm chuẩn và cập nhật lại hai file kia.*
