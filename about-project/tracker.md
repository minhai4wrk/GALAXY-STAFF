# KẾ HOẠCH TRIỂN KHAI CHI TIẾT

## DỰ ÁN GALAXY STAFF – Hệ thống Quản lý Nhân sự Rạp Chiếu Phim

| Hạng mục | Thông tin |
|----------|-----------|
| Loại dự án | Đồ án cá nhân cấp đại học |
| Thời gian | 4 tháng / 17 tuần (01/06 – 27/09/2026) |
| Số người thực hiện | 1 |
| Đầu ra | Hệ thống demo + Báo cáo ≥ 50 trang |

---

## PHẦN A: PHƯƠNG PHÁP TRIỂN KHAI

### 1. Phương pháp phát triển: Agile cá nhân (Personal Scrum)

Do dự án chỉ có 1 người, áp dụng mô hình **Agile cá nhân** kết hợp **Incremental Development**:

- **Sprint**: 7 sprint trong 17 tuần. 3 sprint trọng điểm (Thiết kế, Availability, Roster) kéo dài **3 tuần**; 4 sprint còn lại **2 tuần**.
- **Daily log**: Ghi nhật ký công việc mỗi ngày (thay cho daily standup).
- **Sprint Review**: Cuối mỗi sprint tự đánh giá, demo nội bộ, chụp ảnh màn hình cho báo cáo.
- **Kanban board**: Dùng GitHub Projects hoặc Notion để quản lý task theo trạng thái: Backlog → In Progress → Review → Done.
- **Version Control**: Git Flow đơn giản hóa — nhánh `main` (production), `develop` (phát triển), `feature/*` cho từng tính năng.

### 2. Chiến lược ưu tiên (MoSCoW) — Điều chỉnh cho 1 người

Vì chỉ có 1 người, cần phân loại rõ tính năng theo mức ưu tiên:

| Mức | Tính năng | Ghi chú |
|-----|-----------|---------|
| **Must Have** | Auth (JWT+RBAC), **Availability đầy đủ** (grid kéo-thả + Overlap view + Template-shift + deadline + min-5 ngày), Roster (xem ngày/tuần + xếp ca thủ công kéo-thả), Auto-Scheduling (rules-based), News Feed, Notification in-app (WebSocket) | Bắt buộc hoàn thành |
| **Should Have** | Shift Exchange (pass ca, nhận ca, duyệt, concurrency), Responsive **mobile-web** cho Staff, Cảnh báo xung đột real-time, Stress test | Cố gắng hoàn thành |
| **Could Have** | Sequence diagram chi tiết, hiệu ứng UX nâng cao, polish loading/empty states | Làm nếu còn thời gian |
| **Won't Have (→ Version 2)** | **Native mobile app (Flutter)**, **Push notification FCM**, **Swap ca 2 chiều (UC-14)**, Multi-location UI, Payroll API | Bỏ qua, chỉ ghi nhận trong báo cáo |

### 3. Chiến lược phát triển kỹ thuật

- **Vertical slice theo module**: làm trọn từng module (backend → test Swagger → frontend) trong mỗi sprint thay vì dồn toàn bộ backend rồi mới frontend. Sprint 1 cố tình làm tính năng "nhẹ" (Auth + News Feed) trước để thông pipeline & deploy sớm, rồi mới vào phần khó (Availability, Roster).
- **Database-first**: Thiết kế schema PostgreSQL kỹ lưỡng ngay từ đầu, dùng Alembic migration.
- **Component-driven Frontend**: Dùng shadcn/ui có sẵn, không tự code component từ đầu.
- **Docker từ ngày đầu**: Setup docker-compose ngay Sprint 0 để đảm bảo môi trường nhất quán.

---

## PHẦN B: CÁC BƯỚC TRIỂN KHAI CHI TIẾT

> Lịch theo tuần (deadline = cuối tuần). CN mỗi tuần là buffer. Báo cáo viết song song theo sprint.

---

### SPRINT 0 — PHÂN TÍCH, THIẾT KẾ & SETUP (Tuần 1–3)

**Mục tiêu**: Hoàn thành toàn bộ tài liệu thiết kế (full scope), setup môi trường, scaffold, prototype shell. Viết Chương 2 song song.

#### Tuần 1: Phân tích & thiết kế lõi

| ID | Công việc | Đầu ra |
|----|-----------|--------|
| S0-01 | Phân tích yêu cầu, viết đặc tả 14 Use Case cho 4 module | Tài liệu Use Case (Ch3) |
| S0-02 | Vẽ Use Case Diagram (tổng quan + từng module) | File UML |
| S0-03 | Vẽ Activity Diagram (5 luồng chính) | File UML |
| S0-04 | Vẽ Sequence Diagram cho luồng phức tạp (pass ca concurrency, auto-schedule) | File UML *(có thể cắt nếu trễ)* |
| S0-05 | Thiết kế ERD chi tiết: quan hệ, constraint, index, status enum | ERD + SQL schema |

**Chi tiết Use Case cần phân tích:**

1. UC-01: Đăng nhập/Đăng xuất (Staff, Manager)
2. UC-02: Đăng ký lịch rảnh (Staff)
3. UC-03: Xem tổng hợp lịch rảnh (Manager)
4. UC-04: Xếp ca thủ công (Manager)
5. UC-05: Auto-scheduling (Manager)
6. UC-06: Publish lịch làm (Manager)
7. UC-07: Xem lịch làm + Apply open-shift (Staff)
8. UC-08: Pass ca (Staff)
9. UC-09: Nhận ca (Staff)
10. UC-10: Duyệt trao đổi ca (Manager)
11. UC-11: Tạo thông báo (Manager)
12. UC-12: Xem thông báo (Staff)
13. UC-13: Quản lý nhân viên (Manager)
14. UC-14: Swap ca — đổi ca 2 chiều *(Version 2)*

**Chi tiết ERD — Các bảng cần thiết:**

```
users (id, email, password_hash, full_name, role, location_id, is_active, created_at)
locations (id, name, address)
availabilities (id, user_id FK, week_start, day_of_week, start_time, end_time, status)
shifts (id, location_id FK, date, start_time, end_time, assigned_user_id FK, status, created_by FK)
shift_exchanges (id, shift_id FK, from_user_id FK, to_user_id FK, message, status [open/pending/approved/rejected], approved_by FK, created_at)
news_posts (id, author_id FK, title, content, image_url, created_at)
news_reads (id, post_id FK, user_id FK, read_at)
notifications (id, user_id FK, type, reference_id, message, is_read, created_at)
```

#### Tuần 2: Đặc tả API, wireframe & khởi tạo repo

| ID | Công việc | Đầu ra |
|----|-----------|--------|
| S0-06 | Thiết kế API Specification (OpenAPI 3.0) cho ~32 endpoint | File openapi.yaml |
| S0-07 | Viết tài liệu SRS (chức năng + phi chức năng) | SRS document |
| S0-08 | Vẽ wireframe 8 màn hình chính (Figma/Excalidraw) | Wireframe file |
| S0-09 | Thiết kế chi tiết tương tác drag-drop (Availability + Roster): state, ô 30p, logic template-shift | Tài liệu thiết kế UX |
| S0-10 | Tạo GitHub repo, Git Flow, README, .gitignore, Conventional Commits | Repo GitHub |

**Chi tiết API Endpoints cần thiết kế:**

```
# Auth
POST   /api/auth/login
POST   /api/auth/register (Manager only)
GET    /api/auth/me

# Users
GET    /api/users
GET    /api/users/{id}
PUT    /api/users/{id}
PATCH  /api/users/{id}/status

# Availability
GET    /api/availabilities?week_start=YYYY-MM-DD
POST   /api/availabilities (batch upsert)
GET    /api/availabilities/overview?week_start=YYYY-MM-DD  (Manager: overlap view)

# Shifts / Roster
GET    /api/shifts?date=YYYY-MM-DD&view=day|week
POST   /api/shifts
PUT    /api/shifts/{id}
DELETE /api/shifts/{id}
POST   /api/shifts/auto-schedule  (Manager)
POST   /api/shifts/publish        (Manager)
POST   /api/shifts/{id}/apply     (Staff: apply open-shift)

# Shift Exchange
GET    /api/exchanges
POST   /api/exchanges                                  (Staff: pass ca + lời nhắn)
POST   /api/exchanges/{id}/take                        (Staff: nhận ca)
PUT    /api/exchanges/{id}/approve                     (Manager)
PUT    /api/exchanges/{id}/reject                      (Manager)

# News Feed
GET    /api/news
POST   /api/news
GET    /api/news/{id}
GET    /api/news/{id}/reads        (Manager)
POST   /api/news/{id}/read         (Staff: mark as read)

# Notifications
GET    /api/notifications
PUT    /api/notifications/{id}/read
PUT    /api/notifications/read-all
```

#### Tuần 3: Setup môi trường, scaffold & prototype

| ID | Công việc | Đầu ra |
|----|-----------|--------|
| S0-11 | Setup Docker Compose (FastAPI + PostgreSQL + Frontend), chạy 1 lệnh | docker-compose.yml chạy được |
| S0-12 | Scaffold Backend FastAPI (structure, config, security, deps, Dockerfile) | Backend scaffold |
| S0-13 | Scaffold Frontend Vite + React + TS + Tailwind + shadcn/ui + Zustand | Frontend scaffold |
| S0-14 | DB models SQLAlchemy (8 bảng) + Alembic initial migration + seed cơ bản | Migration files |
| S0-15 | Prototype Login + Dashboard shell (sidebar Manager / nav responsive Staff) | UI prototype |
| S0-16 | Viết draft **Chương 2** (cơ sở lý thuyết + công nghệ, 10–15 trang) | Draft Chương 2 |

**Cấu trúc thư mục dự án:**

```
galaxy-staff/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── availabilities.py
│   │   │   ├── shifts.py
│   │   │   ├── exchanges.py
│   │   │   ├── news.py
│   │   │   └── notifications.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── deps.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── availability.py
│   │   │   ├── shift.py
│   │   │   ├── exchange.py
│   │   │   ├── news.py
│   │   │   └── notification.py
│   │   ├── schemas/
│   │   │   └── (pydantic schemas)
│   │   ├── services/
│   │   │   ├── auto_scheduler.py
│   │   │   └── notification_service.py
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/  (API calls)
│   │   ├── stores/    (Zustand)
│   │   └── types/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

> **Mốc M1 (cuối Tuần 3):** Thiết kế chốt, môi trường chạy được, prototype shell.

---

### SPRINT 1 — AUTH + NEWS FEED + NOTIFICATION (Tuần 4–5)

**Mục tiêu**: Thông toàn bộ pipeline full-stack qua các tính năng "nhẹ" (Auth + News Feed + Notification) và **deploy slice sớm** trước khi vào phần khó.

#### Tuần 4: Backend Auth + News Feed + Notification

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S1-01 | Backend Auth: login, JWT generate/verify, bcrypt, RBAC middleware | python-jose + passlib |
| S1-02 | User Management API (CRUD, list staff, toggle active, register Manager-only) | Manager-only endpoints |
| S1-03 | Frontend Auth: Login connect API, token storage, ProtectedRoute, role routing | Protected routes |
| S1-04 | News Feed API (CRUD, upload ảnh, mark-as-read, reads list) | 5 endpoints |
| S1-05 | Notification API + WebSocket server (connect, push, mark read) | Polling fallback nếu khó |

#### Tuần 5: Frontend News Feed + Notification + Deploy slice

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S1-06 | News Feed UI (list, tạo bài + ảnh, đọc, mark read, seen indicator) | CRUD UI |
| S1-07 | Notification UI (bell + badge, dropdown, real-time WebSocket) | Real-time |
| S1-08 | Trigger notification khi đăng news mới | — |
| S1-09 | Unit test Auth + News + Notification (pytest + httpx, ≥10 TC) | Test coverage |
| S1-10 | Sprint 1 Review + **deploy thử slice** lên Render (smoke test live) | Live URL sớm |
| S1-11 | Viết draft **Chương 3.1–3.2** (phương pháp, phân tích yêu cầu) | Draft Chương 3 |

> **Mốc M2 (cuối Tuần 5):** Auth + News Feed + Notification chạy end-to-end, đã deploy live.

---

### SPRINT 2 — AVAILABILITY MODULE (Tuần 6–8)

**Mục tiêu**: Module Availability **đầy đủ theo `description.md`** — grid kéo-thả + Overlap view + Template-shift + deadline + min-5 ngày. Đây là phần UX khó nhất, không hạ cấp.

#### Tuần 6: Backend Availability + nền tảng Grid

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S2-01 | Availability API: batch upsert, model slot 30p (8h–02h), tuần T6→T5 | Backend |
| S2-02 | Availability API: Overview/Overlap endpoint (aggregate đếm người rảnh/slot) | Aggregate query |
| S2-03 | Availability API: deadline (khóa 18h T7, mở tuần mới) + min-5-ngày + flow xin phép | Deadline logic |
| S2-04 | Availability Grid component: lưới ngày × slot 30p, render khung | Nền tảng UI |

#### Tuần 7: UX cốt lõi (kéo-thả + overlap)

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S2-05 | Availability **drag-to-paint**: giữ + kéo tô/xóa, mouse + touch | ⚠️ Khó — core UX |
| S2-06 | **Template-shift**: kéo Sáng/Chiều/Tối/Full → auto-fill; nút (+) tạo shift thủ công | — |
| S2-07 | **Overlap view**: heatmap xanh theo mật độ + hover/click ô → ai rảnh/bận | ⚠️ Khó — core UX |

#### Tuần 8: Tích hợp & test

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S2-08 | Integration: save/load, deadline warning, đếm ngày + popup xin phép <5 ngày | — |
| S2-09 | Test Availability (CRUD, deadline, overlap aggregate, ≥6 TC) | — |
| S2-10 | Sprint 2 Review + screenshot + redeploy | — |
| S2-11 | Viết **Chương 3.3** (thiết kế DB) + phần Availability của 3.5 | Draft Chương 3 |

> **Mốc M3 (cuối Tuần 8):** Module Availability hoàn chỉnh.

---

### SPRINT 3 — ROSTER + AUTO-SCHEDULING (Tuần 9–11)

**Mục tiêu**: Roster (xem ngày/tuần, kéo-thả xếp ca) + Auto-Scheduling + publish + apply open-shift. **Kết thúc sprint = CORE MVP feature-complete.**

#### Tuần 9: Backend Roster + thuật toán

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S3-01 | Shifts/Roster API: CRUD, assign, filter ngày/tuần, open-shift list | Backend Roster |
| S3-02 | **Auto-Scheduling engine v1**: rules-based greedy + constraints | auto_scheduler.py |

**Chi tiết thuật toán Auto-Scheduling (Rules-based):**

```
Input:
  - open_shifts: Danh sách ca trống cần gán (tuần tới)
  - availabilities: Lịch rảnh của tất cả staff
  - constraints: {max_hours_per_week, min_rest_between_shifts, max_consecutive_days}

Algorithm (Greedy + Constraint Satisfaction):
  1. Sort open_shifts theo priority (ca tối > ca sáng, cuối tuần > ngày thường)
  2. For each open_shift:
     a. Tìm danh sách staff rảnh tại thời điểm đó (filter by availability)
     b. Filter thêm: staff chưa vượt max_hours, đủ rest time
     c. Sort eligible staff theo: ít giờ nhất tuần này (cân bằng công bằng)
     d. Gán staff đầu tiên trong danh sách eligible
     e. Cập nhật assigned_hours[staff]
  3. Return: assigned_shifts + unassigned_shifts (nếu không đủ người)

Complexity: O(S × N) với S = số ca, N = số staff → < 1s cho 300 ca × 100 NV
```

#### Tuần 10: Roster API publish/apply + Week view

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S3-03 | Roster API: publish + apply open-shift (Staff) + approve apply (Manager) | — |
| S3-04 | Test + benchmark auto-scheduler (50–100 NV × 200–300 ca, <10s, edge case) | Chuẩn bị TC1 |
| S3-05 | Roster UI — Week view (Daily Card): cột ngày, hàng NV, hàng open-shift, thanh màu | ⚠️ Khó |

#### Tuần 11: Day view + drag-drop xếp ca + tích hợp

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S3-06 | Roster UI — Day view (timeline) | — |
| S3-07 | Roster UI — Manager **kéo-thả xếp ca**: tạo/sửa khối ca (day), click ngày tạo ca (week), modify | ⚠️ Khó — core UX |
| S3-08 | Roster UI — nút Auto-Schedule + Publish + Staff apply open-shift, kết nối API | — |
| S3-09 | Cảnh báo xung đột xếp ca (chồng giờ bận / vượt max_hours / thiếu rest) — màu đỏ | Chuẩn bị TC3 |
| S3-10 | Trigger notification khi publish roster / approve apply | — |
| S3-11 | Sprint 3 Review + screenshot + redeploy | — |
| S3-12 | Viết **Chương 3.4** (API) + **3.6** (thuật toán auto-schedule) | Draft Chương 3 |

> **Mốc M4 (cuối Tuần 11): CORE MVP feature-complete** — còn hơn 1 tháng cho test/deploy/báo cáo.

---

### SPRINT 4 — SHIFT-EXCHANGE + TÍCH HỢP NOTIFICATION (Tuần 12–13)

**Mục tiêu**: Trao đổi ca (pass/nhận + duyệt + concurrency) và rà soát tích hợp notification toàn hệ thống. *(Swap ca 2 chiều → Version 2.)*

#### Tuần 12: Backend Exchange + UI board

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S4-01 | Shift-Exchange API: pass ca (+lời nhắn), nhận ca, pending lock, approve/reject | Backend Exchange |
| S4-02 | Exchange API: concurrency (optimistic/DB constraint, **chỉ 1 người nhận**) + state machine | Chuẩn bị TC2 |
| S4-03 | Shift-Exchange UI: board giống Roster, ca pass highlight, xem lời nhắn + nút nhận | Frontend Exchange |

#### Tuần 13: Duyệt + tích hợp + test + báo cáo

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S4-04 | Exchange UI: cảnh báo trùng giờ trước khi nhận, trạng thái pending/approved/rejected | — |
| S4-05 | Manager Approve/Reject UI + notification 2 chiều (A & B) | — |
| S4-06 | Rà soát notification toàn hệ thống (publish, pass, approve/reject, news, apply) | — |
| S4-07 | Unit test Shifts + Exchange + concurrent (≥8 TC) | — |
| S4-08 | Sprint 4 Review + screenshot + redeploy | — |
| S4-09 | Ghép & hoàn thiện **Chương 3** (3.1–3.6) | Hoàn thiện Chương 3 |

> **Mốc M5 (cuối Tuần 13):** Đủ 4 module, tích hợp xong, đã deploy.

---

### SPRINT 5 — KIỂM THỬ, POLISH & DEPLOY (Tuần 14–15)

**Mục tiêu**: Hệ thống ổn định, responsive, deploy online, mock data demo-ready.

#### Tuần 14: Test + responsive

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S5-01 | Unit test toàn bộ API + coverage report (≥20 TC tổng) | pytest + httpx |
| S5-02 | Integration **TC1** Auto-Scheduling | Nghiệm thu 1 |
| S5-03 | Integration **TC2** Pass ca | Nghiệm thu 2 |
| S5-04 | Integration **TC3** Cảnh báo quá giờ | Nghiệm thu 3 |
| S5-05 | Responsive testing + fix CSS (375 / 414 / 768 / 1024px) | Staff dùng mobile-web |

**Chi tiết 3 Test Case Nghiệm Thu:**

| # | Test Case | Mô tả | Tiêu chí Pass |
|---|-----------|-------|----------------|
| TC1 | Auto-Scheduling | Tạo 200 ca trống, 50 staff có lịch rảnh → Chạy auto-schedule | ≥ 90% ca được gán đúng, không vi phạm constraint, hoàn thành < 10s |
| TC2 | Pass ca / Nhận ca | Staff A pass ca → Staff B nhận → Manager approve → Ca chuyển sang B | Trạng thái đúng tại mỗi bước, cảnh báo trùng ca, notification gửi đúng, concurrent request bị block |
| TC3 | Cảnh báo quá giờ | Xếp staff vượt 48h/tuần hoặc ca chồng giờ bận | Hệ thống hiện warning, không tự động gán khi auto-schedule |

#### Tuần 15: Stress test + deploy + mock data + polish

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S5-06 | Stress test (Locust/JMeter): peak 50–100 user save availability | *Có thể cắt nếu trễ* |
| S5-07 | Deploy hoàn chỉnh (BE+FE+Postgres) + cấu hình env + test live | Render/Railway |
| S5-08 | Mock data hoàn chỉnh: 1 Manager + 12 Staff + lịch 2 tuần + ca mẫu + news | Demo-ready |
| S5-09 | Fix bug tổng hợp + polish UI (color-coding, empty/loading states) | Buffer chính |
| S5-10 | Viết **Chương 4** (kết quả + screenshot 4 module + kết quả test) | Draft Chương 4 |

> **Mốc M6 (cuối Tuần 15):** Demo-ready, đã deploy & test xong.

---

### SPRINT 6 — BÁO CÁO, SLIDE & NGHIỆM THU (Tuần 16–17)

**Mục tiêu**: Hoàn thiện báo cáo ≥ 50 trang, Turnitin, slide, dry-run demo, nộp.

#### Tuần 16: Hoàn thiện báo cáo + Turnitin

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S6-01 | Hoàn thiện Ch4 + viết Kết luận + hướng phát triển V2 (mobile, swap ca, payroll, multi-location) | — |
| S6-02 | Tài liệu tham khảo (IEEE/APA, ≥10–15) + danh mục hình/bảng/viết tắt | — |
| S6-03 | Phụ lục (HDSD Manager/Staff, mã nguồn auto-scheduler, ERD full, Swagger export, cài đặt) | — |
| S6-04 | Mở đầu + Lời cảm ơn + Mục lục + review toàn bộ ≥50 trang (chính tả, format, citation) | — |
| S6-05 | Kiểm tra Turnitin + chỉnh sửa nếu > 20% | Kết quả Turnitin |

#### Tuần 17: Slide + demo + nộp

| ID | Công việc | Chi tiết |
|----|-----------|----------|
| S6-06 | Tạo slide trình bày (15–20 slides: pain → giải pháp → kiến trúc → demo → kết quả) | File PPTX |
| S6-07 | Dry-run demo (tập kịch bản 3 TC live, fix bug cuối) | Sẵn sàng |
| S6-08 | **Buffer cuối kỳ** + dự phòng rủi ro (đừng tiêu trước!) | — |
| S6-09 | **NỘP BÀI** (source, PDF, slide, link demo, Turnitin) | 🎯 DEADLINE CUỐI 27/09 |

> **Mốc M7 (Tuần 17):** Nộp bài.

---

## PHẦN C: CẤU TRÚC BÁO CÁO CHI TIẾT

Tổng: ≥ 50 trang nội dung chính (từ Mở đầu đến Kết luận).

---

### Trang bìa
- Tên trường, khoa, ngành
- Tên đề tài: "GALAXY STAFF – Hệ thống Quản lý Nhân sự Rạp Chiếu Phim"
- Họ tên sinh viên, MSSV
- Giảng viên hướng dẫn
- Tháng/Năm

### Lời cảm ơn (1 trang)

### Mục lục

### Danh mục hình ảnh

### Danh mục bảng biểu

### Danh mục từ viết tắt
- JWT, RBAC, REST, API, CRUD, ORM, SRS, ERD, CI/CD, WebSocket...

---

### MỞ ĐẦU (3–4 trang)
1. **Lý do chọn đề tài**: Thực trạng quản lý nhân sự thủ công tại rạp chiếu phim, bất cập của Google Sheets + Messenger.
2. **Mục tiêu đề tài**: Xây dựng hệ thống web tập trung, số hóa quy trình, tự động xếp ca.
3. **Đối tượng và phạm vi nghiên cứu**: Quy trình xếp ca tại rạp chiếu phim; phạm vi 4 module; 1 location.
4. **Phương pháp nghiên cứu**: Agile, incremental development, khảo sát thực tế, tham khảo hệ thống tương tự.
5. **Bố cục báo cáo**: Tóm tắt nội dung từng chương.

---

### CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ (10–15 trang)

#### 2.1. Tổng quan về quản lý nhân sự trong ngành dịch vụ (2–3 trang)
- Đặc thù nhân sự ngành rạp chiếu phim: ca kíp linh hoạt, part-time, peak hour.
- Các vấn đề thường gặp: xếp ca thủ công, giao tiếp phân tán, thiếu công cụ tập trung.
- Khảo sát quy trình hiện tại (mô tả Google Sheets + Messenger workflow).

#### 2.2. Các giải pháp/hệ thống tương tự (2–3 trang)
- **When2Meet**: Ưu điểm (giao diện grid trực quan), hạn chế (chỉ thu thập lịch rảnh, không xếp ca).
- **Deputy / 7shifts / Homebase**: Phần mềm chuyên nghiệp quản lý ca, ưu/nhược điểm, chi phí.
- **Google Sheets**: Ưu điểm (miễn phí, quen thuộc), hạn chế (thủ công, dễ sai, không real-time).
- So sánh và rút ra yêu cầu cho Galaxy Staff.

#### 2.3. Kiến trúc phần mềm đa tầng (2 trang)
- Multi-tier Architecture: Presentation – Business Logic – Data.
- RESTful API: Nguyên tắc thiết kế, HTTP methods, status codes.
- Microservice vs Monolith: Lý do chọn Monolith cho đồ án cá nhân.

#### 2.4. Công nghệ sử dụng (3–4 trang)
- **React.js + TypeScript**: Component-based, type safety, hệ sinh thái.
- **Tailwind CSS + shadcn/ui**: Utility-first CSS, responsive design.
- **FastAPI (Python)**: Async-first, auto Swagger, Pydantic validation.
- **PostgreSQL + SQLAlchemy + Alembic**: ORM, migration, constraint.
- **JWT + bcrypt + RBAC**: Cơ chế xác thực và phân quyền.
- **WebSocket**: Real-time notification trong web app.
- **Docker + Docker Compose**: Containerization, deployment.

#### 2.5. Thuật toán Auto-Scheduling (2 trang)
- Bài toán Constraint Satisfaction Problem (CSP).
- Cách tiếp cận Rules-based greedy: mô tả thuật toán, pseudocode.
- So sánh với các phương pháp khác (ILP, Genetic Algorithm) và lý do chọn greedy.

---

### CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG (15–20 trang)

#### 3.1. Phương pháp và công cụ (2 trang)
- Quy trình Agile cá nhân, Sprint planning.
- Công cụ: VS Code, Figma, draw.io, GitHub, Docker, Postman/Swagger.
- Quản lý task: GitHub Projects / Notion.

#### 3.2. Phân tích yêu cầu (4–5 trang)
- **Yêu cầu chức năng**: Bảng liệt kê 4 module (F1.1–F4.3) + mô tả.
- **Yêu cầu phi chức năng**: Bảo mật, hiệu năng, khả năng mở rộng.
- **Use Case Diagram**: Tổng quan + chi tiết cho từng module.
- **Activity Diagram**: 3–4 luồng chính (đăng ký lịch rảnh, auto-schedule, pass ca, tạo thông báo).

#### 3.3. Thiết kế cơ sở dữ liệu (3–4 trang)
- ERD tổng thể (Entity-Relationship Diagram).
- Chi tiết từng bảng: tên cột, kiểu dữ liệu, constraint, index.
- Giải thích quan hệ giữa các bảng.
- Lý do thiết kế: chuẩn hóa, foreign key, status enum.

#### 3.4. Thiết kế API (3–4 trang)
- Cấu trúc RESTful API: naming convention, response format.
- Bảng liệt kê endpoint: method, URL, request body, response, quyền truy cập.
- Cơ chế xác thực: JWT flow (login → token → header → middleware).
- Cơ chế phân quyền: RBAC (Manager vs Staff).

#### 3.5. Thiết kế giao diện (3–4 trang)
- Wireframe/Mockup cho các màn hình chính:
  - Login
  - Dashboard (Manager / Staff)
  - Availability Grid
  - Roster View (ngày/tuần)
  - Shift Exchange Board
  - News Feed
  - Notification Panel
- Responsive design strategy: Desktop-first cho Manager, Mobile-friendly cho Staff.

#### 3.6. Thiết kế thuật toán Auto-Scheduling (2 trang)
- Input/Output specification.
- Flowchart thuật toán.
- Constraint rules chi tiết.
- Phân tích độ phức tạp.

---

### CHƯƠNG 4: KẾT QUẢ VÀ THẢO LUẬN (10–15 trang)

#### 4.1. Kết quả triển khai (5–6 trang)
- **Module Authentication**: Screenshot login, phân quyền, Swagger.
- **Module Availability**: Screenshot grid, deadline, tổng hợp Manager.
- **Module Roster**: Screenshot lịch ngày/tuần, auto-schedule result, publish.
- **Module Shift Exchange**: Screenshot pass ca, nhận ca, approve/reject.
- **Module News Feed**: Screenshot tạo bài, danh sách, seen tracking.
- **Notification**: Screenshot in-app notification.

#### 4.2. Kết quả kiểm thử (3–4 trang)
- **Unit test**: Bảng kết quả test case API (pass/fail, coverage).
- **Integration test**: 3 test case nghiệm thu với kết quả.
- **Responsive test**: Screenshot trên các kích thước (375px, 414px, 768px, desktop).
- **Performance test**: Kết quả stress test, thời gian phản hồi API, auto-schedule benchmark.

#### 4.3. Thảo luận và đánh giá (2–3 trang)
- So sánh kết quả với tiêu chí thành công đề ra.
- Đánh giá ưu điểm: những gì đạt được tốt.
- Đánh giá hạn chế: những gì chưa hoàn thiện, lý do.
- Bài học kinh nghiệm từ quá trình phát triển.

---

### KẾT LUẬN (1–2 trang)
- Tóm tắt kết quả đạt được.
- Đóng góp của đề tài.
- Hạn chế và hướng phát triển: Native mobile app (Flutter), Swap ca 2 chiều, Push notification FCM, Payroll module, Multi-location, AI-based scheduling (machine learning).

---

### TÀI LIỆU THAM KHẢO
- Tối thiểu 10–15 tài liệu.
- Gợi ý: FastAPI docs, React docs, PostgreSQL docs, JWT RFC 7519, sách Software Engineering (Sommerville), bài báo về employee scheduling, tài liệu When2Meet/Deputy.

---

### PHỤ LỤC
- **Phụ lục A**: Hướng dẫn cài đặt và sử dụng hệ thống (docker-compose up).
- **Phụ lục B**: Hướng dẫn sử dụng cho Manager.
- **Phụ lục C**: Hướng dẫn sử dụng cho Staff.
- **Phụ lục D**: Mã nguồn thuật toán Auto-Scheduling.
- **Phụ lục E**: Swagger API Documentation (screenshot hoặc export).
- **Phụ lục F**: Kết quả kiểm tra Turnitin.

---

## PHẦN D: CHECKLIST TỔNG THỂ

### Checklist theo tuần

- [ ] **Tuần 1–3 (Sprint 0)**: 14 Use Case, ERD, API Spec, SRS, Wireframe + thiết kế drag-drop; Git/Docker/scaffold BE+FE; DB migration; prototype; Chương 2 draft
- [ ] **Tuần 4–5 (Sprint 1)**: Auth API+UI, News Feed API+UI, Notification WebSocket, unit test, deploy slice sớm, Chương 3.1–3.2 draft
- [ ] **Tuần 6–8 (Sprint 2)**: Availability API + grid kéo-thả + Overlap view + Template-shift + deadline/min-5, test, Chương 3.3 draft
- [ ] **Tuần 9–11 (Sprint 3)**: Shifts API, Auto-Scheduling engine, Roster day/week + kéo-thả xếp ca, publish, apply open-shift, cảnh báo xung đột, Chương 3.4+3.6
- [ ] **Tuần 12–13 (Sprint 4)**: Shift Exchange API + UI, concurrency, approve/reject, rà soát notification, Chương 3 hoàn thiện
- [ ] **Tuần 14–15 (Sprint 5)**: Unit test ≥20, 3 Integration TC, responsive fix, stress test, deploy hoàn chỉnh, mock data, polish, Chương 4 draft
- [ ] **Tuần 16–17 (Sprint 6)**: Kết luận + TLTK + Phụ lục, Turnitin, Slide (15–20), dry-run demo, **nộp bài**

### Checklist sản phẩm đầu ra

- [ ] Source code trên GitHub (có README đầy đủ)
- [ ] docker-compose.yml chạy được 1 lệnh
- [ ] Live demo URL (Render/Railway)
- [ ] Mock data: 1 Manager + 12 Staff
- [ ] Báo cáo PDF ≥ 50 trang
- [ ] Slide trình bày 15–20 slides
- [ ] Swagger API Documentation (tại /docs)
- [ ] Kết quả Turnitin
- [ ] Video demo (nếu yêu cầu)

---

## PHẦN E: MẸO VÀ LƯU Ý CHO DỰ ÁN CÁ NHÂN

### Quản lý thời gian
- **Nguyên tắc 80/20**: 80% giá trị đến từ 20% tính năng. Ưu tiên chức năng cốt lõi chạy ổn định hơn là nhiều tính năng chạy lỗi.
- **Timeboxing**: Mỗi tính năng có deadline cứng. Nếu bị kẹt > 4h, đơn giản hóa hoặc chuyển sang tính năng khác.
- **Viết báo cáo song song**: Không để dồn tuần cuối. Mỗi sprint xong, viết luôn phần tương ứng trong báo cáo.

### Kỹ thuật
- **Seed data sớm**: Tạo script seed 12 staff + lịch rảnh + ca mẫu từ tuần 3, giúp test và demo dễ dàng.
- **Screenshot mọi thứ**: Mỗi khi hoàn thành tính năng, chụp ngay cho báo cáo. Đừng đợi tuần cuối.
- **Swagger = doc miễn phí**: FastAPI tự tạo Swagger UI, tận dụng triệt để cho tài liệu API.
- **Fallback plan**: Nếu drag-and-drop quá phức tạp → dùng form + dropdown. Nếu WebSocket khó → dùng polling. Ghi nhận trong báo cáo phần "Hạn chế".

### Báo cáo
- **Hình ảnh = trang**: Mỗi screenshot + caption chiếm ~1/3 trang. Diagram chiếm ~1/2 trang. Tận dụng để đạt ≥ 50 trang.
- **Trích dẫn đủ**: Mỗi công nghệ, mỗi khái niệm lý thuyết cần có citation. Dùng định dạng IEEE hoặc APA.
- **Turnitin**: Viết bằng lời của mình, không copy-paste từ docs. Paraphrase khi tham khảo.
