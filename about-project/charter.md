  
**PROJECT CHARTER**

Bản Tuyên bố Dự án

**GALAXY STAFF**  
*Hệ thống Quản lý Nhân sự Rạp Chiếu Phim*

| Phiên bản: | 1.0 |
| :---- | :---- |
| **Ngày tạo:** | Tháng 5/2026 |
| **Trạng thái:** | Draft |

# **1\. Tổng quan Dự án**

| Hạng mục | Nội dung |
| ----- | ----- |
| Tên dự án | Galaxy Staff – Hệ thống Quản lý Nhân sự Rạp Chiếu Phim |
| Loại dự án | Đồ án môn học cấp đại học (Capstone / Course Project) |
| Nền tảng | Web App duy nhất – Responsive Design (tương thích điện thoại trình duyệt) |
| Ngày bắt đầu (dự kiến) | Tuần 1 – Tháng 6/2026 |
| Ngày kết thúc (dự kiến) | Tuần 4 – Tháng 7/2026 (8 tuần) |

# **2\. Bối cảnh và Vấn đề cần giải quyết**

Trong môi trường vận hành của các rạp chiếu phim, việc quản lý nhân sự hiện tại tồn tại nhiều bất cập nghiêm trọng:

* **Xếp ca thủ công:** Quản lý sử dụng Google Sheets để lên lịch, dẫn đến sai sót và tốn nhiều thời gian.

* **Giao tiếp phân tán:** Lịch làm được gửi qua Facebook, trao đổi ca qua Messenger – thông tin dễ bị trôi và thiếu đồng bộ.

* **Xác nhận công rời rạc:** Cuối tháng, dữ liệu công nằm rải rác trên nhiều nền tảng, gây khó khăn cho việc tổng hợp và đối chiếu.

* **Không có hệ thống tập trung:** Thiếu một nền tảng duy nhất để quản lý toàn bộ quy trình nhân sự từ đăng ký lịch, xếp ca đến trao đổi ca.

# **3\. Mục tiêu Dự án**

## **3.1. Mục tiêu chính**

* **Số hóa toàn bộ quy trình:** Chuyển đổi việc đăng ký lịch rảnh, xếp ca, trao đổi ca và thông báo nội bộ từ các công cụ rời rạc sang một nền tảng duy nhất.

* **Tối ưu thời gian quản lý:** Cung cấp tính năng Auto-Scheduling giúp tự động xếp ca dựa trên lịch rảnh của nhân viên, giảm tải cho quản lý.

* **Nâng cao trải nghiệm nhân viên:** Cung cấp ứng dụng di động tiện lợi để nhân viên chủ động đăng ký, xem ca và trao đổi ca chỉ với 1–2 thao tác chạm.

## **3.2. Mục tiêu học thuật**

* Áp dụng kiến trúc phần mềm đa tầng (Multi-tier Architecture) với Frontend, Backend, Database.

* Thực hành thiết kế RESTful API, xác thực JWT và phân quyền RBAC.

* Triển khai ứng dụng bằng Docker và thực hành CI/CD cơ bản.

* Phát triển thuật toán Auto-Scheduling (Rules-based constraint engine).

# **4\. Các bên liên quan (Stakeholders)**

| Vai trò | Mô tả | Kỳ vọng |
| ----- | ----- | ----- |
| Giảng viên hướng dẫn | Đánh giá đồ án | Sản phẩm đạt yêu cầu kỹ thuật, báo cáo đầy đủ |
| Nhóm phát triển | Sinh viên thực hiện | Hoàn thành đúng hạn, học hỏi công nghệ |
| Quản lý rạp (Manager) | Người dùng chính – Web (desktop) | Xếp ca nhanh, giảm tải thủ công |
| Nhân viên rạp (Staff) | Người dùng – Web (mobile browser) | Thao tác đơn giản, xem ca qua trình duyệt điện thoại |

# **5\. Phạm vi Dự án**

## **5.1. Bao gồm (In-scope)**

* Module Availability: Đăng ký lịch rảnh kiểu kéo-thả (grid 30 phút), template-shift, deadline tự động khóa.

* Module Roster: Hiển thị lịch làm chế độ ngày/tuần, kéo-thả xếp ca, Auto-Scheduling, Publish.

* Module Shift Exchange: Đăng pass ca (kèm lời nhắn), nhận ca (cảnh báo trùng ca), phê duyệt quản lý, xử lý xung đột. *(Swap ca — Version 2)*

* Module News Feed: Đăng, xem thông báo nội bộ, đính kèm hình ảnh, theo dõi lượt đọc.

* Giao diện Responsive Web: tối ưu cho màn hình máy tính (Manager) và sử dụng được qua trình duyệt điện thoại (Staff).

* Hệ thống xác thực JWT, phân quyền RBAC (Manager/Staff).

* Thông báo trong ứng dụng (In-app notification) qua WebSocket hoặc polling.

* Đóng gói Docker và triển khai lên server (Render hoặc Railway – free tier).

## **5.2. Không bao gồm (Out-of-scope)**

* Ứng dụng di động nàtive (iOS/Android) – chỉ hỗ trợ qua trình duyệt điện thoại (mobile browser).

* Push Notification qua FCM – thay bằng in-app notification.

* Module tính lương (Payroll) – chỉ để lại API mở rộng.

* Tích hợp máy chấm công vật lý.

* Quản lý đa cụm rạp (multi-location) – thiết kế DB hỗ trợ nhưng chưa triển khai UI.

* Phân quyền nâng cao (Super Admin, HR).

# **6\. Timeline tổng quan**

Dự án được triển khai trong 8 tuần (2 tháng), chia thành 4 giai đoạn chính:

| \# | Giai đoạn | Thời gian | Sản phẩm đầu ra |
| ----- | ----- | ----- | ----- |
| 1 | Phân tích & Thiết kế | Tuần 1–2 | SRS, ERD, Wireframe, API Spec |
| 2 | Phát triển cốt lõi (Sprint 1\) | Tuần 3–4 | Auth, Availability, News Feed |
| 3 | Phát triển chính (Sprint 2\) | Tuần 5–6 | Roster \+ Auto-Scheduling, Shift Exchange |
| 4 | Kiểm thử, Responsive & Nghiệm thu | Tuần 7–8 | Test Report, Docker, Demo, Báo cáo, Slide |

# **7\. Phân tích Rủi ro**

| \# | Rủi ro | Mức độ | Tác động | Biện pháp giảm thiểu |
| ----- | ----- | ----- | ----- | ----- |
| 1 | Auto-Scheduling phức tạp hơn dự kiến | Cao | Trễ tiến độ Sprint 2–3 | Bắt đầu từ Rules-based đơn giản, nâng cấp dần |
| 2 | Drag-and-Drop trên web phức tạp | Trung bình | Chất lượng UX Manager giảm | Sử dụng thư viện đã có (react-beautiful-dnd) |
| 3 | Xung đột concurrent khi pass ca | Cao | Dữ liệu sai, 2 người nhận cùng ca | Khóa Optimistic với Pending state \+ DB constraint |
| 4 | Responsive trên màn hình nhỏ phức tạp | Trung bình | UX Staff trên điện thoại kém | Thiết kế mobile-first từ đầu, test trên Chrome DevTools |
| 5 | Quá tải hệ thống gần deadline 18h Thứ 7 | Trung bình | Staff không lưu được lịch | Cache \+ queue \+ stress test trước khi release |

# **8\. Tiêu chí thành công**

* Hoàn thành 4 module chính (Availability, Roster, Shift Exchange, News Feed) chạy ổn định.

* Giao diện Responsive hiển thị đúng trên cả desktop (Manager) và mobile browser (Staff).

* Auto-Scheduling xếp ca chính xác cho 50–100 nhân viên trong dưới 10 giây.

* 3 test case nghiệm thu (Auto-scheduling, Pass ca, Cảnh báo quá giờ) đạt 100%.

* API phản hồi dưới 300ms cho 95% request thông thường.

* Báo cáo PDF, Slide, Source code đầy đủ, có tài liệu Swagger API.

# **9\. Phê duyệt**

Bảng ký phê duyệt Project Charter:

| Vai trò | Họ tên | Chữ ký | Ngày |
| ----- | ----- | ----- | ----- |
| Giảng viên HD |  |  |  |
| Trưởng nhóm |  |  |  |

