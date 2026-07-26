# YÊU CẦU PHI CHỨC NĂNG

## Hệ thống Galaxy Staff – Quản lý Nhân sự Rạp Chiếu Phim

| Hạng mục | Thông tin |
|----------|-----------|
| Hệ thống | Galaxy Staff |
| Phiên bản | 1.0 |
| Ngày tạo | 08/05/2026 |

---

## 1. Tổng quan

Tài liệu này mô tả các yêu cầu phi chức năng (Non-Functional Requirements – NFR) của hệ thống Galaxy Staff, bao gồm các tiêu chí về hiệu năng, bảo mật, khả năng sử dụng, độ tin cậy, khả năng bảo trì, triển khai và tương thích. Mỗi yêu cầu đều có tiêu chí đo lường cụ thể để phục vụ kiểm thử và nghiệm thu.

---

## 2. Performance – Hiệu năng (NFR-PERF)

| Mã | Tên | Mô tả | Tiêu chí đo lường | Mức ưu tiên |
|----|-----|-------|-------------------|-------------|
| NFR-PERF-01 | Thời gian phản hồi API | 95% các API thông thường (CRUD, đọc dữ liệu) phải phản hồi nhanh. Tận dụng async của FastAPI để xử lý I/O không chặn. | Response time ≤ 300ms cho 95% request (đo bằng Swagger/Postman hoặc Locust) | **Must** |
| NFR-PERF-02 | Hiệu suất Auto-Scheduling | Engine auto-schedule phải xử lý xong bài toán xếp ca và trả về kết quả draft trong thời gian chấp nhận được, không để Manager chờ quá lâu. | Hoàn thành ≤ 10 giây cho 100 nhân viên × 300 ca/tuần | **Must** |
| NFR-PERF-03 | Tải đồng thời peak hour | Hệ thống phải chịu được tải cao vào khung giờ sát deadline (18h Thứ 7) khi nhiều Staff đồng loạt lưu lịch rảnh. | Xử lý ≥ 50 request đồng thời mà không lỗi 5xx (đo bằng Locust/JMeter) | **Should** |
| NFR-PERF-04 | Tải trang Frontend | Các trang chính (Dashboard, Roster, Availability) phải load nhanh để trải nghiệm không bị gián đoạn. | First Contentful Paint ≤ 2 giây trên mạng 4G (đo bằng Lighthouse) | **Should** |
| NFR-PERF-05 | Tối ưu database query | Các truy vấn phức tạp (overlap view, auto-schedule) phải được tối ưu bằng index và query plan hợp lý. | Không có query nào chạy quá 1 giây trên dataset 100 users × 4 tuần dữ liệu | **Should** |

---

## 3. Security – Bảo mật (NFR-SEC)

| Mã | Tên | Mô tả | Tiêu chí đo lường | Mức ưu tiên |
|----|-----|-------|-------------------|-------------|
| NFR-SEC-01 | Xác thực JWT | Sử dụng JSON Web Token (HS256) để xác thực. Access token hết hạn ngắn, refresh token hết hạn dài. Secret key lấy từ biến môi trường, không hardcode. | Access token TTL = 30 phút, Refresh token TTL = 7 ngày. Mọi API (trừ login) từ chối request không có token hợp lệ (401). | **Must** |
| NFR-SEC-02 | Băm mật khẩu bcrypt | Mật khẩu người dùng phải được băm bằng bcrypt trước khi lưu vào database. Không bao giờ lưu hoặc trả về plain-text password qua API. | Cost factor ≥ 12. Không có endpoint nào trả về trường `password_hash`. | **Must** |
| NFR-SEC-03 | Phân quyền RBAC | Mỗi API endpoint phải kiểm tra role người dùng. Staff không thể truy cập endpoint dành cho Manager và ngược lại (khi áp dụng). | 100% endpoint Manager-only trả về 403 khi Staff gọi. Kiểm tra bằng test case. | **Must** |
| NFR-SEC-04 | Chống SQL Injection | Sử dụng SQLAlchemy ORM cho mọi truy vấn, không viết raw SQL trực tiếp với input người dùng. | Không có raw SQL nào nhận trực tiếp user input mà không qua parameterized query. | **Must** |
| NFR-SEC-05 | Cấu hình CORS | Backend phải cấu hình CORS chỉ cho phép origin từ frontend domain, không dùng wildcard `*` trong production. | Dev: cho phép `localhost:5173`. Prod: chỉ cho phép domain frontend cụ thể. | **Must** |
| NFR-SEC-06 | Rate Limiting | Giới hạn số request/phút cho endpoint login để chống brute-force. Các endpoint khác có thể áp rate limit tùy mức độ. | Login: tối đa 10 lần/phút/IP. Sau khi vượt → trả về 429 Too Many Requests. | **Could** |
| NFR-SEC-07 | Bảo vệ XSS | Sanitize input người dùng (đặc biệt nội dung News Feed) trước khi lưu và hiển thị. Frontend escape HTML khi render. | Không có trường nào cho phép inject script khi hiển thị trên UI. | **Should** |

---

## 4. Usability – Khả năng sử dụng (NFR-UI)

| Mã | Tên | Mô tả | Tiêu chí đo lường | Mức ưu tiên |
|----|-----|-------|-------------------|-------------|
| NFR-UI-01 | Responsive Design | Giao diện phải hiển thị đúng và sử dụng được trên nhiều kích thước màn hình: desktop, tablet, mobile. | Không bị vỡ layout trên 4 breakpoint: 375px (iPhone SE), 414px (iPhone Plus), 768px (iPad), ≥1024px (Desktop). Kiểm tra bằng Chrome DevTools. | **Must** |
| NFR-UI-02 | Desktop-first cho Manager | Giao diện Manager (Roster drag-drop, Availability overview, User management) được tối ưu cho màn hình lớn với nhiều không gian thao tác. | Các trang Manager sử dụng được tốt trên màn hình ≥ 1024px. Drag-drop hoạt động mượt trên desktop. | **Must** |
| NFR-UI-03 | Mobile-friendly cho Staff | Giao diện Staff (xem ca, đăng ký rảnh, nhận ca, news) phải dùng được dễ dàng trên trình duyệt điện thoại. Nút bấm lớn, font rõ ràng, hạn chế thao tác phức tạp. | Mọi thao tác chính của Staff (xem ca, pass ca, đọc news) hoàn thành trong ≤ 3 tap. Touch target ≥ 44px. | **Must** |
| NFR-UI-04 | Color-coding trực quan | Sử dụng hệ thống màu sắc nhất quán: xanh = đã xác nhận, xám = trống/open, đỏ = xung đột/lỗi, cam = pending, xanh đậm gradient = overlap density. | Có ít nhất 4 trạng thái màu phân biệt rõ ràng trên Roster và Availability. | **Should** |
| NFR-UI-05 | Thông báo lỗi rõ ràng | Mọi lỗi phải hiển thị message tiếng Việt dễ hiểu cho người dùng, không hiện lỗi kỹ thuật (stack trace, error code). | 100% lỗi validation/API hiển thị message user-friendly bằng tiếng Việt. | **Should** |
| NFR-UI-06 | Loading state | Các thao tác tốn thời gian (auto-schedule, save, load data) phải hiện loading indicator để người dùng biết hệ thống đang xử lý. | Mọi API call > 500ms phải có spinner/skeleton. Nút submit disable khi đang loading để tránh double-click. | **Should** |

---

## 5. Reliability – Độ tin cậy (NFR-REL)

| Mã | Tên | Mô tả | Tiêu chí đo lường | Mức ưu tiên |
|----|-----|-------|-------------------|-------------|
| NFR-REL-01 | Error handling API | Mọi API endpoint phải có try-except, trả về HTTPException với status code và message rõ ràng. Không để server crash với lỗi 500 không rõ nguyên nhân. | 100% endpoint có error handling. Lỗi 500 phải log chi tiết server-side nhưng trả client message chung "Lỗi hệ thống". | **Must** |
| NFR-REL-02 | Data validation (Pydantic) | Mọi request body phải qua Pydantic schema validation. Kiểm tra type, format, required fields, value range trước khi xử lý business logic. | 100% POST/PUT endpoint có Pydantic schema. Request thiếu field → 422 với chi tiết field nào lỗi. | **Must** |
| NFR-REL-03 | Database constraint | Sử dụng constraint ở cấp database (unique, foreign key, check, not null) làm lớp bảo vệ cuối cùng, không chỉ dựa vào application logic. | Email unique constraint. Foreign key trên tất cả bảng liên kết. Enum check cho status fields. | **Must** |
| NFR-REL-04 | Xử lý concurrent (Optimistic Locking) | Shift Exchange phải xử lý đúng khi nhiều Staff nhận cùng 1 ca: chỉ 1 người thành công, còn lại nhận thông báo "Ca đã được người khác nhận". | Test 5 request đồng thời nhận cùng ca → chỉ 1 thành công, 4 thất bại (không lỗi 500). | **Must** |
| NFR-REL-05 | Graceful degradation | Khi WebSocket không khả dụng, hệ thống tự fallback sang polling mà không ảnh hưởng chức năng chính. | Notification vẫn hoạt động (polling 30s) khi WebSocket bị ngắt. Không hiện lỗi cho user. | **Should** |

---

## 6. Maintainability – Khả năng bảo trì (NFR-MAINT)

| Mã | Tên | Mô tả | Tiêu chí đo lường | Mức ưu tiên |
|----|-----|-------|-------------------|-------------|
| NFR-MAINT-01 | Cấu trúc code | Backend và Frontend tuân thủ cấu trúc thư mục đã định (api/, models/, schemas/, services/ cho backend; components/, pages/, hooks/, services/ cho frontend). | Không có file nào nằm ngoài cấu trúc quy định. Mỗi module tách riêng file. | **Must** |
| NFR-MAINT-02 | Type safety | Python sử dụng type hints bắt buộc. TypeScript strict mode, không dùng `any`. | 100% function có type hints (Python). tsconfig strict = true, noImplicitAny = true. | **Must** |
| NFR-MAINT-03 | Docstring & Comment | Mỗi function có docstring 1 dòng tiếng Việt. Code phức tạp có comment giải thích. Tên biến/function bằng tiếng Anh. | 100% function có docstring. Comment tiếng Việt cho logic phức tạp. | **Must** |
| NFR-MAINT-04 | Linting & Formatting | Backend: Ruff (lint + format). Frontend: ESLint + Prettier. Đảm bảo code style nhất quán. | Chạy lint không có warning/error. Format tự động khi save. | **Should** |
| NFR-MAINT-05 | Cấu hình tập trung | Mọi config (database URL, JWT secret, CORS origin) lấy từ `.env` qua `config.py` (Pydantic Settings). Không hardcode. | Không có literal connection string, secret key trong source code. Tất cả qua env vars. | **Must** |
| NFR-MAINT-06 | Database migration | Sử dụng Alembic để quản lý schema migration. Mọi thay đổi DB phải qua migration file, không sửa trực tiếp. | Có migration file cho mỗi lần thay đổi schema. `alembic upgrade head` chạy thành công từ DB trống. | **Must** |
| NFR-MAINT-07 | Test coverage | Viết unit test (pytest) cho API endpoints và business logic quan trọng. Integration test cho 3 test case nghiệm thu. | ≥ 20 unit test cases. 3 integration test cases pass 100%. | **Should** |

---

## 7. Deployment – Triển khai (NFR-DEPLOY)

| Mã | Tên | Mô tả | Tiêu chí đo lường | Mức ưu tiên |
|----|-----|-------|-------------------|-------------|
| NFR-DEPLOY-01 | Docker Compose | Toàn bộ stack (FastAPI + PostgreSQL + Frontend) được đóng gói bằng Docker. Chạy bằng 1 lệnh `docker-compose up`. | `docker-compose up` từ máy mới (có Docker) → hệ thống chạy hoàn chỉnh trong ≤ 5 phút. | **Must** |
| NFR-DEPLOY-02 | Dockerfile tối ưu | Mỗi service có Dockerfile riêng, sử dụng multi-stage build để giảm image size. Cài đặt dependencies trước, copy code sau (tận dụng cache). | Backend image ≤ 500MB. Frontend image ≤ 200MB. Build time ≤ 3 phút. | **Should** |
| NFR-DEPLOY-03 | Deploy production | Hệ thống có thể deploy lên cloud platform (Render hoặc Railway free tier) để demo online. | Có live URL truy cập được từ internet. Uptime ổn định trong buổi demo. | **Should** |
| NFR-DEPLOY-04 | Seed data | Có script tạo dữ liệu mẫu (1 Manager + 12 Staff + lịch rảnh + ca làm 2 tuần) để demo và test. | Chạy seed script → dữ liệu sẵn sàng demo ngay, không cần nhập tay. | **Must** |
| NFR-DEPLOY-05 | README & Setup guide | README.md đầy đủ: mô tả dự án, hướng dẫn cài đặt, cấu hình `.env`, chạy dev, chạy Docker, cấu trúc thư mục. | Developer mới đọc README → setup và chạy được trong ≤ 15 phút. | **Must** |

---

## 8. Compatibility – Tương thích (NFR-COMPAT)

| Mã | Tên | Mô tả | Tiêu chí đo lường | Mức ưu tiên |
|----|-----|-------|-------------------|-------------|
| NFR-COMPAT-01 | Trình duyệt Desktop | Hỗ trợ các trình duyệt phổ biến phiên bản hiện tại trên desktop. | Hoạt động đúng trên Chrome ≥ 100, Firefox ≥ 100, Edge ≥ 100. Safari ≥ 15 (nếu có thể). | **Must** |
| NFR-COMPAT-02 | Trình duyệt Mobile | Hỗ trợ Chrome và Safari trên iOS/Android — hai trình duyệt phổ biến nhất trên điện thoại. | Hoạt động đúng trên Chrome Android và Safari iOS (2 phiên bản gần nhất). | **Must** |
| NFR-COMPAT-03 | Không yêu cầu cài đặt | Staff sử dụng qua trình duyệt điện thoại, không cần cài app native. Đường dẫn truy cập đơn giản. | Truy cập bằng URL trên trình duyệt → sử dụng được ngay, không cần tải app. | **Must** |

---

## 9. Tổng hợp theo mức ưu tiên

| Mức ưu tiên | Số lượng | Ghi chú |
|-------------|----------|---------|
| **Must** | 24 | Bắt buộc — ảnh hưởng trực tiếp đến chất lượng sản phẩm và điểm đồ án |
| **Should** | 12 | Cố gắng hoàn thành — nâng cao chất lượng đáng kể |
| **Could** | 1 | Làm nếu còn thời gian |
| **Tổng** | **37** | |

---

*Tài liệu này phục vụ cho phần Phân tích yêu cầu phi chức năng (Chương 3.2) trong báo cáo đồ án.*
