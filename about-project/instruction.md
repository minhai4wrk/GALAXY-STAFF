  
**PROJECT INSTRUCTION**

Hướng dẫn Thực hiện Dự án

**GALAXY STAFF**  
*Hệ thống Quản lý Nhân sự Rạp Chiếu Phim*

| Phiên bản: | 1.0 |
| :---- | :---- |
| **Ngày tạo:** | Tháng 5/2026 |
| **Tài liệu:** | Hướng dẫn triển khai |

# **1\. Yêu cầu Chức năng Chi tiết**

## **1.1. Module Availability – Đăng ký lịch rảnh**

| \# | Yêu cầu | Mô tả chi tiết |
| ----- | ----- | ----- |
| F1.1 | Grid đăng ký kiểu When2Meet | Lưới 7 ngày × các ô 30 phút (8h–02h), hỗ trợ nhấn giữ kéo-thả để tô màu, kéo lần 2 để xóa. |
| F1.2 | Overlap View tổng hợp | Hiển thị chồng lớp lịch rảnh của toàn team. Màu xanh đậm \= nhiều người rảnh. Hover/click hiện danh sách. |
| F1.3 | Template-shift | 4 mẫu có sẵn: Sáng (8–13h), Chiều (13–18h), Tối (18h–closed), Full. Kéo vào ngày để tự động fill. |
| F1.4 | Tạo shift thủ công | Nút (+) cho phép tạo ca bằng cách nhập giờ bắt đầu và kết thúc. |
| F1.5 | Deadline tự động | Khóa đăng ký lúc 18h Thứ 7\. Tự động mở tuần mới. |
| F1.6 | Kiểm tra tối thiểu 5 ngày | Cảnh báo nếu đăng ký dưới 5 ngày, yêu cầu nhập lý do. |

## **1.2. Module Roster – Lịch làm việc**

| \# | Yêu cầu | Mô tả chi tiết |
| ----- | ----- | ----- |
| F2.1 | Xem lịch theo ngày/tuần | Timeline view (ngày) và Daily Card (tuần). Cột \= ngày, hàng \= nhân viên, hàng trên cùng \= Open-shift. |
| F2.2 | Kéo-thả xếp ca (Manager) | Tạo/di chuyển khối ca bằng drag-and-drop. Click để modify giờ. |
| F2.3 | Auto-Scheduling | Thuật toán Rules-based tự động gán ca từ Open-shift vào nhân viên rảnh. Xử lý 50–100 NV, 200–300 ca/tuần trong \< 10s. |
| F2.4 | Publish Roster | Chốt lịch và gửi thông báo đến toàn bộ Staff. |
| F2.5 | Apply Open-shift (Staff) | Staff đăng ký nhận ca trống, chờ Manager phê duyệt. |
| F2.6 | Cảnh báo xung đột | Hiển thị đỏ khi xếp người vào giờ bận hoặc vượt quá số giờ quy định. |

## **1.3. Module Shift Exchange – Trao đổi ca**

| \# | Yêu cầu | Mô tả chi tiết |
| ----- | ----- | ----- |
| F3.1 | Đăng pass ca (+ lời nhắn) | Staff chọn ca của mình, bấm Pass (kèm lời nhắn tùy chọn) → ca chuyển màu highlight trên bảng Shift Exchange. |
| F3.2 | Nhận ca (cảnh báo trùng ca) | Staff khác click ca highlight → xem lời nhắn → bấm Nhận ca → request gửi lên Manager. Nếu ca nhận trùng giờ ca hiện có → cảnh báo trước. |
| F3.3 | Khóa Pending | Sau khi có người nhận, ca chuyển Pending Approval, các Staff khác không thao tác được nữa. |
| F3.4 | Phê duyệt / Từ chối | Manager duyệt: ca chuyển từ A sang B. Từ chối: ca quay về trạng thái ban đầu. Cả hai đều bắn notification. |
| F3.5 | Bảng trao đổi ca (Board) | Giao diện tuần như Roster: ca thường xám/nhạt, ca đang trao đổi highlight; click để xem chi tiết + nút Nhận ca. |
| — | *Swap ca (Version 2)* | *Đổi ca 2 chiều — lên kế hoạch cho phiên bản tiếp theo.* |

## **1.4. Module News Feed – Bảng tin nội bộ**

| \# | Yêu cầu | Mô tả chi tiết |
| ----- | ----- | ----- |
| F4.1 | Tạo thông báo | Manager tạo bài với tiêu đề, nội dung, hình ảnh đính kèm. |
| F4.2 | Hiển thị & Notify | Bài mới lên đầu feed, đồng thời gửi in-app notification qua WebSocket. |
| F4.3 | Theo dõi Seen | Hệ thống ghi nhận ai đã đọc, Manager xem được danh sách. |

## **1.5. Yêu cầu phi chức năng**

* **Bảo mật:** JWT \+ bcrypt \+ RBAC. API chống SQL Injection (SQLAlchemy ORM) và XSS.

* **Hiệu năng:** 95% API phản hồi \< 300ms. Auto-Scheduling \< 10s cho 100 NV.

* **Đồng thời:** Chịu tải peak hour (sát deadline Thứ 7). Optimistic locking cho Shift Exchange.

* **Khả năng mở rộng:** DB chuẩn hóa, RESTful API, Docker containerization.

# **2\. Kiến trúc Công nghệ**

| Tầng | Công nghệ | Lý do lựa chọn |
| ----- | ----- | ----- |
| Frontend – Web | React.js \+ TypeScript \+ Tailwind CSS | Hệ sinh thái lớn, Tailwind giúp responsive nhanh, drag-and-drop tốt. |
| UI Components | shadcn/ui hoặc Ant Design | Bộ component sẵn responsive, tiết kiệm thời gian trong timeline gấp rút của đồ án. |
| Backend | Python \+ FastAPI | Async-first, tự động sinh Swagger, hiệu năng cao, dễ học. |
| Database | PostgreSQL | Ổn định, hỗ trợ constraint mạnh, tương thích SQLAlchemy ORM. |
| Real-time Notify | WebSocket (FastAPI native) | Thông báo in-app tực thì, không cần FCM do chỉ có web. |
| Container | Docker \+ Docker Compose | Đóng gói toàn bộ stack, triển khai nhất quán mọi môi trường. |
| Version Control | Git \+ GitHub | Quản lý source, branching strategy (Git Flow). |

 

## **2.1. Đề xuất thư viện bổ sung**

* **dnd-kit:** Drag-and-drop hiệu năng cao cho lưới Availability và Roster trên web.

* **Alembic:** Database migration cho PostgreSQL qua SQLAlchemy.

* **Pydantic:** Đã tích hợp với FastAPI, dùng validate request/response schema.

* **pytest \+ httpx:** Unit test và integration test cho API.

* **Zustand hoặc Redux Toolkit:** Quản lý state phía React.

* **date-fns / Day.js:** Xử lý các phép tính ngày giờ (tuần, deadline, khung giờ) phía frontend.

# **3\. Các Giai đoạn Triển khai**

## **3.1. Giai đoạn 1 – Phân tích & Thiết kế (Tuần 1–2)**

* Phân tích yêu cầu chi tiết, viết tài liệu SRS.

* Thiết kế ERD, Database Schema và API Specification (OpenAPI/Swagger).

* Vẽ wireframe/mockup (Figma) cho các màn hình chính, ưu tiên góc nhìn mobile.

* Thiết lập môi trường: Git repo, Docker Compose, CI pipeline cơ bản.

* Xác định constraint rules cho thuật toán Auto-Scheduling.

## **3.2. Giai đoạn 2 – Phát triển cốt lõi – Sprint 1 (Tuần 3–4)**

Mục tiêu: hệ thống chạy được end-to-end với 2 module đầu tiên.

* Backend: Auth (JWT \+ RBAC), CRUD User, DB migration (Alembic).

* Module Availability: API đầy đủ \+ Grid UI kéo-thả trên web, Responsive cho mobile browser.

* Module News Feed: API đầy đủ \+ UI Manager \+ WebSocket notification cơ bản.

* Scaffold React project (Vite \+ TypeScript \+ Tailwind \+ shadcn/ui).

## **3.3. Giai đoạn 3 – Phát triển chính – Sprint 2 (Tuần 5–6)**

Mục tiêu: hoàn thiện 2 module phức tạp nhất.

* Module Roster: API \+ Drag-drop UI (chế độ ngày/tuần) \+ Auto-Scheduling engine v1.

* Module Shift Exchange: API \+ UI (Board) \+ Pass/Nhận ca \+ cảnh báo trùng ca \+ Pending lock \+ Approve/Reject flow.

* Tích hợp toàn bộ WebSocket notification (pass ca, publish roster, news).

* Kiểm tra responsive trên nhiều kích thước màn hình.

## **3.4. Giai đoạn 4 – Kiểm thử, Responsive & Nghiệm thu (Tuần 7–8)**

* Viết unit test và integration test cho các API quan trọng (pytest \+ httpx).

* Kiểm thử 3 test case nghiệm thu: Auto-scheduling chính xác, Pass ca, Cảnh báo quá giờ.

* Kiểm thử Responsive trên các thiết bị phổ biến (Chrome DevTools: 375px, 414px, 768px).

* Stress test peak hour (Locust) với kịch bản nhiều Staff lưu đồng thời.

* Triển khai lên Render / Railway (free tier) để demo online.

* Chuẩn bị mock data (1 Manager \+ 10–15 Staff), hoàn thiện báo cáo PDF và slide.

# **4\. Sản phẩm Đầu ra**

| \# | Sản phẩm | Mô tả | Ghi chú |
| ----- | ----- | ----- | ----- |
| 1 | Source Code | Backend (FastAPI) \+ Web App (React, Responsive) | Trên GitHub, có README |
| 2 | Docker Setup | docker-compose.yml chạy toàn bộ stack | 1 lệnh docker-compose up |
| 3 | Báo cáo PDF | SRS, ERD, API Spec, Auto-Scheduling Algorithm | Xuất Swagger từ FastAPI |
| 4 | Slide trình bày | Pain points, giải pháp, kiến trúc, kết quả | 15–20 slides |
| 5 | Live Demo | Chạy 3 test case nghiệm thu với mock data | 1 Manager \+ 10–15 Staff |
| 6 | API Documentation | Swagger UI tự động từ FastAPI | Truy cập tại /docs |

# **5\. Thiết kế Cơ sở dữ liệu (Gợi ý)**

Dưới đây là các bảng chính cần thiết kế trong PostgreSQL:

| Bảng (Table) | Mô tả & Các trường chính |
| ----- | ----- |
| users | id, email, password\_hash, full\_name, role (manager/staff), location\_id, is\_active, created\_at |
| locations | id, name, address – hỗ trợ mở rộng đa cụm rạp |
| availabilities | id, user\_id (FK), week\_start, day\_of\_week, start\_time, end\_time, status |
| shifts | id, location\_id, date, start\_time, end\_time, assigned\_user\_id (FK nullable), status (open/assigned/pending), created\_by |
| shift\_exchanges | id, shift\_id (FK), from\_user\_id, to\_user\_id, message, status (open/pending/approved/rejected), approved\_by, created\_at |
| news\_posts | id, author\_id (FK), title, content, image\_url, created\_at |
| news\_reads | id, post\_id (FK), user\_id (FK), read\_at – theo dõi Seen |
| notifications | id, user\_id, type, reference\_id, message, is\_read, created\_at |

# **6\. Tiêu chí Đánh giá (Đồ án Sinh viên)**

| \# | Tiêu chí | Trọng số (gợi ý) | Yêu cầu đạt |
| ----- | ----- | ----- | ----- |
| 1 | Chức năng hoàn chỉnh | 30% | 4 module chạy được, không lỗi nghiêm trọng |
| 2 | Chất lượng code & Kiến trúc | 20% | Clean code, RESTful, đúng pattern |
| 3 | UI/UX | 15% | Trực quan, responsive, drag-drop mượt |
| 4 | Tài liệu & Báo cáo | 15% | SRS, ERD, API doc, Algorithm đầy đủ |
| 5 | Demo & Nghiệm thu | 10% | 3 test case pass, live demo mượt mà |
| 6 | Teamwork & Quy trình | 10% | Git log đều, task board rõ ràng, đúng hạn |

# **7\. Hướng dẫn Phân công Nhóm (Gợi ý)**

Với nhóm 3–4 thành viên, có thể phân công như sau:

| Vai trò | Trách nhiệm chính | Kỹ năng cần |
| ----- | ----- | ----- |
| Backend Dev | Auth, User, Availability API, Shift Exchange API, DB Schema | Python, FastAPI, PostgreSQL, SQLAlchemy |
| Backend Dev 2 / Algo | Roster API, Auto-Scheduling engine, WebSocket | Python, thuật toán, Alembic |
| Frontend Dev 1 | Availability Grid, Roster drag-drop, Shift Exchange UI | React, TypeScript, dnd-kit, Tailwind |
| Frontend Dev 2 / Lead | Auth, News Feed, Responsive QA, Docker, Tài liệu | React, DevOps, Git, viết báo cáo |

