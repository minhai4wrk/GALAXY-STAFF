# CHƯƠNG 3: PHÂN TÍCH YÊU CẦU HỆ THỐNG

Chương này trình bày kết quả phân tích yêu cầu cho hệ thống Galaxy Staff. Dựa trên khảo sát quy trình quản lý nhân sự thực tế tại rạp chiếu phim (đã mô tả ở Chương 2), tác giả tiến hành xác định các yêu cầu chức năng, yêu cầu phi chức năng và xây dựng danh sách Use Case. Toàn bộ yêu cầu được phân loại theo mức ưu tiên MoSCoW (Must/Should/Could/Won't) để phù hợp với timeline 8 tuần của dự án.

---

## 3.1. Phân tích yêu cầu chức năng

Hệ thống Galaxy Staff được chia thành các module chức năng độc lập (Authentication & User Management, Availability, Roster & Scheduling, Shift Exchange, News Feed & Notification), mỗi module đảm nhận một nhóm chức năng riêng biệt. Tổng cộng có 55 yêu cầu chức năng được xác định, trong đó phần lớn thuộc mức Must Have — tức là bắt buộc phải hoàn thành để hệ thống có thể hoạt động được.

[Hình 3.1: Sơ đồ tổng quan các module của hệ thống Galaxy Staff — VẼ SAU]

### 3.1.1. Module Authentication & User Management

Module này chịu trách nhiệm xác thực người dùng và quản lý tài khoản. Hệ thống sử dụng JWT (JSON Web Token) [1] để quản lý phiên đăng nhập, kết hợp bcrypt [2] để băm mật khẩu và RBAC (Role-based Access Control) [3] để phân quyền theo 2 vai trò: Manager và Staff.

Bảng 3.1: Yêu cầu chức năng module Authentication & User Management

| Mã | Tên yêu cầu | Actor | Mô tả | Ưu tiên |
|----|-------------|-------|-------|---------|
| FR-AUTH-01 | Đăng nhập | Both | Nhập email + mật khẩu → hệ thống trả về access token + refresh token, redirect Dashboard theo role | Must |
| FR-AUTH-02 | Đăng xuất | Both | Xóa token phía client, redirect về Login | Must |
| FR-AUTH-03 | Refresh Token | Both | Tự động làm mới access token khi hết hạn mà không cần đăng nhập lại | Should |
| FR-AUTH-04 | Xem thông tin cá nhân | Both | Xem họ tên, email, role, chi nhánh, trạng thái tài khoản | Must |
| FR-AUTH-05 | Đổi mật khẩu | Both | Nhập mật khẩu cũ + mới, validate tối thiểu 8 ký tự | Should |
| FR-AUTH-06 | Tạo tài khoản NV | Manager | Tạo tài khoản với email, họ tên, role, chi nhánh. Mật khẩu mặc định | Must |
| FR-AUTH-07 | Xem danh sách NV | Manager | Danh sách toàn bộ NV, có tìm kiếm và lọc theo role/trạng thái | Must |
| FR-AUTH-08 | Xem chi tiết NV | Manager | Xem thông tin chi tiết một nhân viên cụ thể | Must |
| FR-AUTH-09 | Cập nhật thông tin NV | Manager/Self | Manager sửa tất cả. Staff chỉ sửa thông tin cá nhân (không sửa role) | Must |
| FR-AUTH-10 | Vô hiệu hóa tài khoản | Manager | Chuyển `is_active = false`. NV không đăng nhập được (soft delete) | Must |
| FR-AUTH-11 | Reset mật khẩu NV | Manager | Đặt lại mật khẩu về giá trị mặc định. NV liên hệ Manager trực tiếp | Should |
| FR-AUTH-12 | RBAC Middleware | Hệ thống | Mọi API kiểm tra JWT + role. 401 nếu thiếu token, 403 nếu sai role | Must |
| FR-AUTH-13 | Route Guard Frontend | Hệ thống | Protect routes phía client. Chưa login → redirect Login. Sai role → 403 | Must |

Bảng 3.2: Ma trận phân quyền module Authentication

| Chức năng | Manager | Staff |
|-----------|:-------:|:-----:|
| Đăng nhập/Đăng xuất | ✅ | ✅ |
| Xem/sửa thông tin cá nhân | ✅ | ✅ |
| Đổi mật khẩu | ✅ | ✅ |
| Tạo tài khoản mới | ✅ | ❌ |
| Xem danh sách/chi tiết NV | ✅ | ❌ |
| Vô hiệu hóa/Reset mật khẩu | ✅ | ❌ |

### 3.1.2. Module Availability — Đăng ký lịch rảnh

Module Availability cho phép nhân viên đăng ký các khung giờ rảnh hàng tuần qua giao diện grid trực quan, tương tự công cụ When2Meet [4]. Đặc thù nghiệp vụ rạp chiếu phim: tuần làm việc tính từ Thứ 6 đến Thứ 5, khung giờ 8h00–2h00 sáng, mỗi ô 30 phút. Deadline đăng ký là 18h00 Thứ 7 hàng tuần.

Bảng 3.3: Yêu cầu chức năng module Availability

| Mã | Tên yêu cầu | Actor | Mô tả | Ưu tiên |
|----|-------------|-------|-------|---------|
| FR-AVAIL-01 | Overlap View | Both | Grid chồng lớp lịch rảnh toàn team. Màu xanh gradient theo mật độ. Hover → danh sách ai rảnh | Must |
| FR-AVAIL-02 | Mở Edit Availability | Both | Bấm "Edit" → mở grid trống tuần tới. Load dữ liệu cũ nếu có. Khóa nếu qua deadline | Must |
| FR-AVAIL-03 | Kéo-thả (Drag-to-select) | Both | Nhấn giữ + kéo qua ô → tô xanh (rảnh). Kéo lại → toggle xóa | Must |
| FR-AVAIL-04 | Template-shift | Both | 4 mẫu ca sẵn (Sáng/Chiều/Tối/Full). Kéo vào ngày → auto fill | Must |
| FR-AVAIL-05 | Tạo shift bằng nút (+) | Both | Nhập giờ bắt đầu/kết thúc bằng form. Phù hợp thao tác trên mobile | Must |
| FR-AVAIL-06 | Save Availability | Both | Batch upsert lên server. Tạo mới/cập nhật/xóa slot | Must |
| FR-AVAIL-07 | Kiểm tra 5 ngày tối thiểu | Both | < 5 ngày → popup cảnh báo + yêu cầu nhập lý do (warning, không block) | Must |
| FR-AVAIL-08 | Deadline tự động khóa | Hệ thống | Sau 18h Thứ 7 → khóa edit, API từ chối, mở tuần mới | Must |
| FR-AVAIL-09 | Xem lịch rảnh cá nhân | Both | Xem lại lịch đã đăng ký. Trước deadline → edit được. Sau deadline → chỉ đọc | Must |
| FR-AVAIL-10 | Manager xem lịch từng NV | Manager | Click tên NV → xem grid cá nhân + lý do nếu < 5 ngày | Should |
| FR-AVAIL-11 | Thống kê đăng ký | Manager | Danh sách: ✅ đã đăng ký, ⚠️ thiếu ngày, ❌ chưa đăng ký | Should |
| FR-AVAIL-12 | Chuyển đổi tuần | Both | Nút Previous/Next để xem tuần khác nhau | Should |
| FR-AVAIL-13 | Countdown deadline | Both | Đếm ngược "Còn X ngày Y giờ". Gần deadline → đổi màu cảnh báo | Could |

### 3.1.3. Module Roster & Scheduling

Đây là module trung tâm của hệ thống, bao gồm chức năng xếp ca (thủ công và tự động) và công bố lịch làm cho nhân viên. Phần Auto-Scheduling sử dụng thuật toán Greedy kết hợp Constraint Satisfaction [5] để tự động phân công ca dựa trên lịch rảnh.

Bảng 3.4: Yêu cầu chức năng module Roster

| Mã | Tên yêu cầu | Actor | Mô tả | Ưu tiên |
|----|-------------|-------|-------|---------|
| FR-ROSTER-01 | Xem lịch theo ngày | Both | Timeline view: trục dọc = NV, trục ngang = thời gian. Hàng trên cùng = Open-shift | Must |
| FR-ROSTER-02 | Xem lịch theo tuần | Both | Daily Card view: cột = 7 ngày, hàng = NV. Click ô → tạo/sửa ca | Must |
| FR-ROSTER-03 | Tạo ca mới | Manager | Kéo-thả trên timeline (ngày) hoặc form (tuần). Gán NV hoặc để Open-shift | Must |
| FR-ROSTER-04 | Sửa ca | Manager | Click ca → form sửa. Drag resize giờ. Drag di chuyển sang NV khác | Must |
| FR-ROSTER-05 | Xóa ca | Manager | Xóa ca. Nếu đã publish → confirm + notification. Ca pending exchange → không cho xóa | Must |
| FR-ROSTER-06 | Auto-Scheduling | Manager | Thuật toán greedy gán Open-shift vào NV rảnh. Cân bằng giờ. Kết quả = draft | Must |
| FR-ROSTER-07 | Cảnh báo xung đột | Hệ thống | Kiểm tra: chồng giờ, vượt 48h/tuần, nghỉ < 8h, NV bận. Hiển thị đỏ | Must |
| FR-ROSTER-08 | Publish Roster | Manager | Chốt draft → published. Notification toàn bộ Staff | Must |
| FR-ROSTER-09 | Apply Open-shift | Staff | Staff nhận ca trống, chờ Manager duyệt | Should |
| FR-ROSTER-10 | Xem lịch cá nhân | Staff | Ca của mình + đồng nghiệp cùng ca + tổng giờ tuần | Must |

### 3.1.4. Module Shift Exchange

Module trao đổi ca cho phép Staff chủ động xử lý ca khi bận đột xuất sau khi lịch đã publish, với 2 hình thức: **Pass** (nhường ca) và **Nhận** (nhận ca người khác pass). Giao diện chính là **bảng trao đổi ca (Exchange Board)** hiển thị tuần làm tương tự Roster: ca bình thường xám/nhạt, ca đang đăng trao đổi hiện màu nổi bật; click vào ca nổi bật để xem lời nhắn và bấm "Nhận ca". Tính năng **Swap ca** (đổi ca 2 chiều) được lên kế hoạch cho **Version 2**.

Bảng 3.5: Yêu cầu chức năng module Shift Exchange

| Mã | Tên yêu cầu | Actor | Mô tả | Ưu tiên |
|----|-------------|-------|-------|---------|
| FR-EXCHANGE-01 | Đăng pass ca (+ lời nhắn) | Staff | Click ca → "Pass ca" + lời nhắn → ca chuyển highlight trên Exchange Board | Should |
| FR-EXCHANGE-02 | Nhận ca | Staff | Bấm "Nhận ca" → cảnh báo nếu trùng ca → Pending lock. Chỉ 1 người nhận (optimistic locking) | Should |
| FR-EXCHANGE-04 | Duyệt exchange | Manager | Approve: ca chuyển sang Staff B. Reject: ca quay về. Notification A + B | Should |
| FR-EXCHANGE-05 | Xem danh sách exchange | Both | Manager xem tất cả. Staff xem của mình. Filter theo trạng thái | Should |
| FR-EXCHANGE-06 | Exchange Board UI | Both | Giao diện tuần: ca bình thường = xám, ca đang trao đổi = highlight; click → lời nhắn + nút Nhận | Should |

### 3.1.5. Module News Feed & Notification

Module này thay thế việc gửi thông báo qua Facebook Messenger — vốn là cách làm phổ biến nhưng gây ra nhiều bất cập như thông tin bị trôi và khó theo dõi ai đã đọc. Manager đăng bài trực tiếp trên hệ thống, Staff xem và hệ thống tự động tracking lượt đọc.

Bảng 3.6: Yêu cầu chức năng module News Feed

| Mã | Tên yêu cầu | Actor | Mô tả | Ưu tiên |
|----|-------------|-------|-------|---------|
| FR-NEWS-01 | Tạo bài thông báo | Manager | Nhập tiêu đề, nội dung, đính kèm ảnh (max 3 ảnh × 5MB). Publish → notification Staff | Must |
| FR-NEWS-02 | Xem danh sách feed | Both | Bài mới nhất trước. Bài chưa đọc có badge "Mới". Phân trang/infinite scroll | Must |
| FR-NEWS-03 | Xem chi tiết bài | Both | Nội dung đầy đủ + ảnh. Auto mark read khi Staff mở | Must |
| FR-NEWS-04 | Sửa bài | Manager | Chỉnh sửa nội dung/ảnh. Hiện label "Đã chỉnh sửa" | Should |
| FR-NEWS-05 | Xóa bài | Manager | Xóa bài khỏi feed (soft delete). Yêu cầu confirm | Should |
| FR-NEWS-06 | Seen Tracking | Manager | Danh sách ai đã đọc (kèm thời gian) / chưa đọc. Tổng: "8/12 đã đọc" | Must |

Bảng 3.7: Yêu cầu chức năng module Notification

| Mã | Tên yêu cầu | Actor | Mô tả | Ưu tiên |
|----|-------------|-------|-------|---------|
| FR-NOTIF-01 | Xem notification | Both | Icon chuông + badge số. Dropdown danh sách. Click → navigate context | Must |
| FR-NOTIF-02 | Mark as read | Both | Click 1 notification hoặc "Đánh dấu tất cả đã đọc" | Must |
| FR-NOTIF-03 | Notify publish roster | Hệ thống | Auto gửi khi Manager publish lịch | Must |
| FR-NOTIF-04 | Notify exchange | Hệ thống | Auto gửi khi nhận ca, approve, reject | Should |
| FR-NOTIF-05 | Notify news mới | Hệ thống | Auto gửi khi Manager đăng bài | Must |
| FR-NOTIF-06 | WebSocket real-time | Hệ thống | Push notification real-time. Fallback: polling 30s | Should |
| FR-NOTIF-07 | Notify open-shift | Hệ thống | Auto gửi khi Staff apply open-shift và khi Manager duyệt | Should |

### 3.1.6. Tổng hợp yêu cầu chức năng

Bảng 3.8: Tổng hợp yêu cầu chức năng theo module và mức ưu tiên

| Module | Must | Should | Could | Tổng |
|--------|:----:|:------:|:-----:|:----:|
| Authentication & User Management | 10 | 3 | 0 | 13 |
| Availability | 9 | 3 | 1 | 13 |
| Roster | 9 | 1 | 0 | 10 |
| Shift Exchange | 0 | 5 | 0 | 5 |
| News Feed | 4 | 2 | 0 | 6 |
| Notification | 4 | 3 | 0 | 7 |
| **Tổng** | **36** | **17** | **1** | **54** |

---

## 3.2. Yêu cầu phi chức năng

Ngoài các yêu cầu chức năng, hệ thống cần đáp ứng một số tiêu chí phi chức năng để đảm bảo chất lượng tổng thể. Tác giả phân loại thành 7 nhóm, tổng cộng 37 yêu cầu.

### 3.2.1. Hiệu năng (Performance)

Bảng 3.9: Yêu cầu hiệu năng

| Mã | Tên | Tiêu chí đo lường | Ưu tiên |
|----|-----|-------------------|---------|
| NFR-PERF-01 | Thời gian phản hồi API | 95% request ≤ 300ms | Must |
| NFR-PERF-02 | Auto-Scheduling | ≤ 10 giây cho 100 NV × 300 ca | Must |
| NFR-PERF-03 | Tải đồng thời peak hour | ≥ 50 request đồng thời không lỗi 5xx | Should |
| NFR-PERF-04 | Tải trang Frontend | First Contentful Paint ≤ 2s trên 4G | Should |
| NFR-PERF-05 | Database query | Không query nào > 1 giây | Should |

### 3.2.2. Bảo mật (Security)

Bảng 3.10: Yêu cầu bảo mật

| Mã | Tên | Tiêu chí đo lường | Ưu tiên |
|----|-----|-------------------|---------|
| NFR-SEC-01 | JWT | Access token 30 phút, Refresh 7 ngày. 401 khi thiếu/hết hạn | Must |
| NFR-SEC-02 | Bcrypt | Cost factor ≥ 12. Không trả về password_hash qua API | Must |
| NFR-SEC-03 | RBAC | 100% endpoint Manager-only trả 403 khi Staff gọi | Must |
| NFR-SEC-04 | Chống SQL Injection | Dùng SQLAlchemy ORM, không raw SQL với user input | Must |
| NFR-SEC-05 | CORS | Dev: localhost. Prod: chỉ domain frontend cụ thể | Must |
| NFR-SEC-06 | Rate Limiting | Login: max 10 lần/phút/IP → 429 | Could |
| NFR-SEC-07 | Chống XSS | Sanitize input News Feed. Frontend escape HTML | Should |

### 3.2.3. Khả năng sử dụng (Usability)

Bảng 3.11: Yêu cầu khả năng sử dụng

| Mã | Tên | Tiêu chí đo lường | Ưu tiên |
|----|-----|-------------------|---------|
| NFR-UI-01 | Responsive Design | Không vỡ layout trên 375px, 414px, 768px, ≥1024px | Must |
| NFR-UI-02 | Desktop-first cho Manager | Drag-drop mượt trên ≥ 1024px | Must |
| NFR-UI-03 | Mobile-friendly cho Staff | Thao tác chính ≤ 3 tap. Touch target ≥ 44px | Must |
| NFR-UI-04 | Color-coding | ≥ 4 trạng thái màu phân biệt rõ (xanh/xám/đỏ/cam) | Should |
| NFR-UI-05 | Thông báo lỗi | 100% lỗi hiển thị message tiếng Việt user-friendly | Should |
| NFR-UI-06 | Loading state | Spinner/skeleton cho API > 500ms. Disable nút khi loading | Should |

### 3.2.4. Độ tin cậy (Reliability)

Bảng 3.12: Yêu cầu độ tin cậy

| Mã | Tên | Tiêu chí đo lường | Ưu tiên |
|----|-----|-------------------|---------|
| NFR-REL-01 | Error handling | 100% endpoint có try-except + HTTPException | Must |
| NFR-REL-02 | Pydantic validation | 100% POST/PUT có schema. Thiếu field → 422 | Must |
| NFR-REL-03 | DB constraint | Unique email, FK, check enum, not null | Must |
| NFR-REL-04 | Optimistic Locking | Shift Exchange: 5 request đồng thời → chỉ 1 thành công | Must |
| NFR-REL-05 | Graceful degradation | WebSocket fail → fallback polling 30s, không hiện lỗi | Should |

### 3.2.5. Khả năng bảo trì (Maintainability)

Bảng 3.13: Yêu cầu bảo trì

| Mã | Tên | Tiêu chí đo lường | Ưu tiên |
|----|-----|-------------------|---------|
| NFR-MAINT-01 | Cấu trúc code | Đúng cấu trúc thư mục quy định. Tách module rõ ràng | Must |
| NFR-MAINT-02 | Type safety | Python type hints. TypeScript strict, không `any` | Must |
| NFR-MAINT-03 | Docstring | 100% function có docstring tiếng Việt 1 dòng | Must |
| NFR-MAINT-04 | Linting | Ruff (backend), ESLint + Prettier (frontend). Không warning | Should |
| NFR-MAINT-05 | Cấu hình tập trung | Mọi config qua `.env` + `config.py`. Không hardcode | Must |
| NFR-MAINT-06 | DB migration | Alembic cho mọi thay đổi schema. `upgrade head` từ DB trống | Must |
| NFR-MAINT-07 | Test coverage | ≥ 20 unit test. 3 integration test pass 100% | Should |

### 3.2.6. Triển khai (Deployment)

Bảng 3.14: Yêu cầu triển khai

| Mã | Tên | Tiêu chí đo lường | Ưu tiên |
|----|-----|-------------------|---------|
| NFR-DEPLOY-01 | Docker Compose | `docker-compose up` → chạy hoàn chỉnh trong ≤ 5 phút | Must |
| NFR-DEPLOY-02 | Dockerfile tối ưu | Multi-stage build. Backend ≤ 500MB, Frontend ≤ 200MB | Should |
| NFR-DEPLOY-03 | Deploy production | Live URL trên Render/Railway. Ổn định khi demo | Should |
| NFR-DEPLOY-04 | Seed data | Script tạo 1 Manager + 12 Staff + lịch 2 tuần | Must |
| NFR-DEPLOY-05 | README | Setup guide đầy đủ. Developer mới chạy được trong ≤ 15 phút | Must |

### 3.2.7. Tương thích (Compatibility)

Bảng 3.15: Yêu cầu tương thích

| Mã | Tên | Tiêu chí đo lường | Ưu tiên |
|----|-----|-------------------|---------|
| NFR-COMPAT-01 | Desktop browser | Chrome ≥ 100, Firefox ≥ 100, Edge ≥ 100 | Must |
| NFR-COMPAT-02 | Mobile browser | Chrome Android + Safari iOS (2 phiên bản gần nhất) | Must |
| NFR-COMPAT-03 | Không cần cài app | Truy cập bằng URL trên trình duyệt, không cần tải app | Must |

### 3.2.8. Tổng hợp yêu cầu phi chức năng

Bảng 3.16: Tổng hợp NFR theo nhóm và mức ưu tiên

| Nhóm | Must | Should | Could | Tổng |
|------|:----:|:------:|:-----:|:----:|
| Performance | 2 | 3 | 0 | 5 |
| Security | 4 | 1 | 1 | 7 |
| Usability | 3 | 3 | 0 | 6 |
| Reliability | 4 | 1 | 0 | 5 |
| Maintainability | 4 | 3 | 0 | 7 |
| Deployment | 3 | 2 | 0 | 5 |
| Compatibility | 3 | 0 | 0 | 3 |
| **Tổng** | **24** | **12** | **1** | **37** |

---

## 3.3. Danh sách Use Case

Dựa trên các yêu cầu chức năng đã phân tích ở mục 3.1, tác giả xác định 14 Use Case chính cho hệ thống. Mỗi Use Case mô tả một luồng tương tác giữa người dùng (Actor) với hệ thống để hoàn thành một mục tiêu cụ thể.

[Hình 3.2: Use Case Diagram tổng quan hệ thống Galaxy Staff — VẼ SAU]

### 3.3.1. Bảng tổng hợp Use Case

Bảng 3.17: Danh sách 14 Use Case của hệ thống Galaxy Staff

| UC-ID | Tên Use Case | Actor | Module | Ưu tiên |
|-------|-------------|-------|--------|---------|
| UC-01 | Đăng nhập / Đăng xuất | Manager, Staff | Authentication | Must |
| UC-02 | Đăng ký lịch rảnh | Staff (Manager cũng có thể) | Availability | Must |
| UC-03 | Xem tổng hợp lịch rảnh | Manager, Staff | Availability | Must |
| UC-04 | Xếp ca thủ công | Manager | Roster | Must |
| UC-05 | Auto-Scheduling | Manager | Roster | Must |
| UC-06 | Publish lịch làm | Manager | Roster | Must |
| UC-07 | Xem lịch làm | Staff (Manager cũng xem) | Roster | Must |
| UC-08 | Pass ca (Nhường ca) | Staff | Shift Exchange | Should |
| UC-09 | Nhận ca | Staff | Shift Exchange | Should |
| UC-10 | Duyệt trao đổi ca | Manager | Shift Exchange | Should |
| UC-11 | Tạo thông báo nội bộ | Manager | News Feed | Must |
| UC-12 | Xem thông báo | Manager, Staff | News + Notification | Must |
| UC-13 | Quản lý nhân viên | Manager | User Management | Must |
Bảng 3.18: Ma trận Actor × Use Case

| Use Case | Manager | Staff |
|----------|:-------:|:-----:|
| UC-01: Đăng nhập/Đăng xuất | ✅ | ✅ |
| UC-02: Đăng ký lịch rảnh | ✅ | ✅ |
| UC-03: Xem tổng hợp lịch rảnh | ✅ | ✅ |
| UC-04: Xếp ca thủ công | ✅ | ❌ |
| UC-05: Auto-Scheduling | ✅ | ❌ |
| UC-06: Publish lịch làm | ✅ | ❌ |
| UC-07: Xem lịch làm | ✅ | ✅ |
| UC-08: Pass ca | ❌ | ✅ |
| UC-09: Nhận ca | ❌ | ✅ |
| UC-10: Duyệt trao đổi ca | ✅ | ❌ |
| UC-11: Tạo thông báo | ✅ | ❌ |
| UC-12: Xem thông báo | ✅ | ✅ |
| UC-13: Quản lý nhân viên | ✅ | ❌ |

Có thể thấy, Manager tham gia 11/13 Use Case (vai trò quản trị), Staff tham gia 6/13 Use Case (vai trò thao tác hàng ngày). Điều này phản ánh đúng thực tế: Manager cần nhiều chức năng quản lý hơn, trong khi Staff chủ yếu đăng ký lịch, xem ca và trao đổi ca. Tính năng Swap ca (đổi ca 2 chiều) được lên kế hoạch cho Version 2.

### 3.3.2. Use Case chi tiết

Trong phần này, tác giả trình bày chi tiết 3 Use Case quan trọng nhất — đại diện cho 3 luồng nghiệp vụ cốt lõi của hệ thống. Các Use Case còn lại được trình bày dạng tóm tắt.

#### UC-01: Đăng nhập / Đăng xuất

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager, Staff |
| **Mô tả** | Người dùng nhập email + mật khẩu để đăng nhập. Hệ thống xác thực bằng JWT, trả về access token (30 phút) + refresh token (7 ngày). Redirect đến Dashboard theo role. Đăng xuất xóa token phía client. |
| **Tiền điều kiện** | Tài khoản đã được tạo bởi Manager, trạng thái active |

**Luồng chính (Đăng nhập):**
1. Người dùng truy cập URL hệ thống → hiển thị trang Login
2. Nhập email và mật khẩu → bấm "Đăng nhập"
3. Hệ thống xác thực: tìm user theo email → so sánh mật khẩu bằng bcrypt → kiểm tra `is_active`
4. Tạo access token + refresh token → trả về client
5. Frontend lưu token, redirect đến Dashboard (Manager → `/dashboard/manager`, Staff → `/dashboard/staff`)

**Luồng ngoại lệ:**
- Email/mật khẩu sai → 401: "Email hoặc mật khẩu không đúng" (message chung, không phân biệt)
- Tài khoản bị khóa → 403: "Tài khoản đã bị khóa, vui lòng liên hệ quản lý"
- Access token hết hạn → Frontend tự gửi refresh token để lấy token mới (người dùng không bị gián đoạn)

**Hậu điều kiện:** Token được lưu, người dùng ở Dashboard đúng role. Mọi API request gửi kèm `Authorization: Bearer <token>`.

**FR liên quan:** FR-AUTH-01, 02, 03, 04, 12, 13

[Hình 3.3: Activity Diagram UC-01 Đăng nhập — VẼ SAU]

---

#### UC-02: Đăng ký lịch rảnh

| Mục | Nội dung |
|-----|---------|
| **Actor** | Staff (Manager cũng có thể) |
| **Mô tả** | Staff mở grid 7 ngày × 36 slot (30 phút), dùng kéo-thả/template-shift/nút (+) để chọn khung giờ rảnh. Lưu trước deadline 18h Thứ 7. Tối thiểu 5 ngày/tuần. |
| **Tiền điều kiện** | Đã đăng nhập. Chưa qua deadline 18h Thứ 7. |

**Luồng chính:**
1. Staff mở tab Availability → xem Overlap View → bấm "Edit Availability"
2. Grid mở ra: 7 cột (Thứ 6 → Thứ 5) × 36 hàng (8h–2h). Load dữ liệu cũ nếu có.
3. Staff chọn khung giờ rảnh bằng 1 trong 3 cách: kéo-thả tô ô, kéo template (Sáng/Chiều/Tối/Full), hoặc bấm (+) nhập giờ
4. Bấm "Save Availability" → hệ thống đếm số ngày ≥ 5 → gửi batch upsert lên server
5. Lưu thành công → redirect về Overlap View

**Luồng ngoại lệ:**
- Qua deadline → nút Edit bị khóa, hiển thị "Đã hết hạn đăng ký"
- < 5 ngày → popup cảnh báo + ô nhập lý do (warning, không block lưu)
- Kéo lại ô đã xanh → toggle xóa (bỏ đăng ký)

**Hậu điều kiện:** Lịch rảnh lưu trong DB. Overlap View cập nhật. Manager có thể xem và dùng để xếp ca.

**FR liên quan:** FR-AVAIL-01 → 09

[Hình 3.4: Activity Diagram UC-02 Đăng ký lịch rảnh — VẼ SAU]

---

#### UC-05: Auto-Scheduling

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager |
| **Mô tả** | Manager bấm "Auto-Schedule", hệ thống chạy thuật toán greedy gán Open-shift vào NV rảnh. Ưu tiên cân bằng giờ, tuân thủ constraint. Kết quả là draft — Manager review rồi mới publish. |
| **Tiền điều kiện** | Đã qua deadline lịch rảnh. Có Open-shift + có NV đã đăng ký rảnh. |

**Luồng chính:**
1. Manager mở Roster → chọn tuần → bấm "Auto-Schedule"
2. Popup xác nhận → Manager đồng ý → loading spinner
3. Backend chạy thuật toán: sort ca theo ưu tiên → filter NV rảnh + đủ điều kiện → gán NV ít giờ nhất
4. Trả về kết quả draft: X ca đã gán, Y ca không đủ người
5. Roster hiển thị draft (viền nét đứt). Manager review → sửa tay nếu cần → Publish (UC-06)

**Thuật toán Greedy — tóm tắt:**
```
FOR EACH open_shift (sorted by priority):
    eligible_staff = filter(rảnh + chưa vượt 48h + đủ nghỉ 8h + < 6 ngày liên tiếp)
    sort eligible_staff by assigned_hours ASC (ít giờ nhất trước)
    IF eligible_staff not empty: gán staff[0]
    ELSE: giữ lại ở Open-shift
```

**Constraint:** Max 48h/tuần, min 8h nghỉ giữa ca, max 6 ngày liên tiếp, không chồng giờ, phải rảnh.

**Luồng ngoại lệ:**
- Không có Open-shift → "Không có ca trống cần phân công"
- Thiếu người → ca giữ lại Open-shift + cảnh báo "Z ca không thể tự động gán"
- Timeout > 30s → lỗi, yêu cầu thử lại

**Hậu điều kiện:** Roster hiển thị draft. Ca gán tay trước đó không bị thay đổi. Manager có thể sửa, reset, hoặc publish.

**FR liên quan:** FR-ROSTER-06, 07, 03, 04, 08

[Hình 3.5: Flowchart thuật toán Auto-Scheduling — VẼ SAU]

---

#### Các Use Case còn lại (tóm tắt)

Bảng 3.19: Tóm tắt Use Case UC-03, UC-04, UC-06 → UC-14

| UC | Luồng chính (tóm tắt) | Ngoại lệ chính | FR liên quan |
|----|----------------------|----------------|-------------|
| **UC-03** Xem Overlap View | Mở Availability → grid gradient theo mật độ → hover xem danh sách NV rảnh | Chưa ai đăng ký → grid trống | FR-AVAIL-01, 10, 11, 12 |
| **UC-04** Xếp ca thủ công | Mở Roster → kéo-thả hoặc form → gán NV vào ca → kiểm tra xung đột → lưu draft | NV bận/vượt 48h → cảnh báo đỏ, cho override | FR-ROSTER-01–05, 07 |
| **UC-06** Publish lịch | Review draft → bấm Publish → ca chuyển published → notification toàn bộ Staff | Còn Open-shift → cảnh báo, vẫn cho publish | FR-ROSTER-08, FR-NOTIF-03 |
| **UC-07** Xem lịch làm | Staff mở Roster → xem ca cá nhân (ngày/tuần) + đồng nghiệp + tổng giờ | Lịch chưa publish → "Chưa có lịch" | FR-ROSTER-01, 02, 09, 10 |
| **UC-08** Pass ca | Mở Exchange → click ca → "Pass ca" + lời nhắn → ca chuyển highlight trên Board | Ca đã qua → không cho pass | FR-EXCHANGE-01, 06 |
| **UC-09** Nhận ca | Xem Exchange Board → click ca highlight → "Nhận ca" → cảnh báo nếu trùng ca → Pending lock → notification Manager | Trùng ca → cảnh báo; 2 người bấm cùng lúc → 1 thành công (optimistic lock) | FR-EXCHANGE-02, FR-NOTIF-04 |
| **UC-10** Duyệt exchange | Manager nhận notification → xem chi tiết → Approve (ca A → B) hoặc Reject | NV nhận bị xung đột giờ → hiện cảnh báo | FR-EXCHANGE-04, 05 |
| **UC-11** Tạo thông báo | Tạo bài (tiêu đề + nội dung + ảnh) → đăng → notification Staff | Thiếu tiêu đề / ảnh quá lớn → validation | FR-NEWS-01, FR-NOTIF-05 |
| **UC-12** Xem thông báo | Xem feed (bài chưa đọc có badge) + icon chuông (notification) → click → mark read | Không có bài mới → feed trống | FR-NEWS-02, 03, 06, FR-NOTIF-01, 02 |
| **UC-13** Quản lý NV | Tạo NV (email, tên, role) → xem danh sách → sửa/vô hiệu hóa/reset mật khẩu | Email trùng → lỗi. Manager tự khóa mình → từ chối | FR-AUTH-06–11 |

### 3.3.3. Mapping Use Case → Yêu cầu chức năng

Bảng 3.20: Truy vết Use Case đến yêu cầu chức năng

| UC-ID | Số FR liên quan | FR chính |
|-------|:--------------:|----------|
| UC-01 | 5 | FR-AUTH-01, 02, 03, 12, 13 |
| UC-02 | 9 | FR-AVAIL-02 → 09 |
| UC-03 | 5 | FR-AVAIL-01, 10, 11, 12, 13 |
| UC-04 | 6 | FR-ROSTER-01 → 05, 07 |
| UC-05 | 5 | FR-ROSTER-03, 04, 06, 07, 08 |
| UC-06 | 2 | FR-ROSTER-08, FR-NOTIF-03 |
| UC-07 | 4 | FR-ROSTER-01, 02, 09, 10 |
| UC-08 | 2 | FR-EXCHANGE-01, 06 |
| UC-09 | 2 | FR-EXCHANGE-02, FR-NOTIF-04 |
| UC-10 | 3 | FR-EXCHANGE-04, 05, FR-NOTIF-04 |
| UC-11 | 2 | FR-NEWS-01, FR-NOTIF-05 |
| UC-12 | 6 | FR-NEWS-02, 03, 06, FR-NOTIF-01, 02, 06 |
| UC-13 | 6 | FR-AUTH-06 → 11 |
| UC-14 | 3 | FR-EXCHANGE-03, 06, FR-NOTIF-04 |

---

## Kết chương

Chương 3 đã trình bày toàn bộ kết quả phân tích yêu cầu cho hệ thống Galaxy Staff, bao gồm:

- **55 yêu cầu chức năng** phân bổ trên 4 module chính (Authentication, Availability, Roster, News Feed) và 2 module bổ trợ (Shift Exchange, Notification). Trong đó 36 yêu cầu ở mức Must Have — bắt buộc hoàn thành trong 8 tuần.

- **37 yêu cầu phi chức năng** chia thành 7 nhóm (hiệu năng, bảo mật, khả năng sử dụng, độ tin cậy, bảo trì, triển khai, tương thích), mỗi yêu cầu có tiêu chí đo lường cụ thể.

- **14 Use Case** mô tả các luồng tương tác chính giữa Manager/Staff với hệ thống. 3 Use Case trọng tâm (Đăng nhập, Đăng ký lịch rảnh, Auto-Scheduling) được phân tích chi tiết với luồng chính, luồng ngoại lệ và ghi chú kỹ thuật.

Các yêu cầu trên sẽ làm cơ sở cho giai đoạn thiết kế cơ sở dữ liệu, thiết kế API và thiết kế giao diện được trình bày trong các phần tiếp theo của báo cáo.

[Hình 3.6: Sơ đồ tổng kết chương 3 — các mối quan hệ giữa UC, FR và NFR — VẼ SAU]

---

*Danh sách hình cần vẽ/chụp cho Chương 3:*

| Hình | Mô tả | Công cụ |
|------|-------|---------|
| Hình 3.1 | Sơ đồ tổng quan 4 module | draw.io |
| Hình 3.2 | Use Case Diagram tổng quan | draw.io / PlantUML |
| Hình 3.3 | Activity Diagram UC-01 Đăng nhập | draw.io |
| Hình 3.4 | Activity Diagram UC-02 Đăng ký lịch rảnh | draw.io |
| Hình 3.5 | Flowchart thuật toán Auto-Scheduling | draw.io |
| Hình 3.6 | Sơ đồ tổng kết chương 3 | draw.io |
