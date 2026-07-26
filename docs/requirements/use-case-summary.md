# TỔNG HỢP USE CASE

## Hệ thống Galaxy Staff – Quản lý Nhân sự Rạp Chiếu Phim

| Hạng mục | Thông tin |
|----------|-----------|
| Hệ thống | Galaxy Staff |
| Tổng số Use Case | 13 |
| Ngày tạo | 08/05/2026 |

---

## 1. Bảng tóm tắt Use Case

| UC-ID | Tên Use Case | Actor | Module | Mức ưu tiên |
|-------|-------------|-------|--------|-------------|
| UC-01 | Đăng nhập / Đăng xuất | Manager, Staff | Authentication | Must |
| UC-02 | Đăng ký lịch rảnh | Staff (Manager cũng có thể) | Availability | Must |
| UC-03 | Xem tổng hợp lịch rảnh (Overlap View) | Manager, Staff | Availability | Must |
| UC-04 | Xếp ca thủ công | Manager | Roster | Must |
| UC-05 | Auto-Scheduling (Xếp ca tự động) | Manager | Roster | Must |
| UC-06 | Publish lịch làm | Manager | Roster | Must |
| UC-07 | Xem lịch làm | Staff (Manager cũng xem) | Roster | Must |
| UC-08 | Pass ca (Nhường ca) | Staff | Shift Exchange | Should |
| UC-09 | Nhận ca | Staff | Shift Exchange | Should |
| UC-10 | Duyệt trao đổi ca | Manager | Shift Exchange | Should |
| UC-11 | Tạo thông báo nội bộ | Manager | News Feed | Must |
| UC-12 | Xem thông báo | Manager, Staff | News Feed + Notification | Must |
| UC-13 | Quản lý nhân viên | Manager | User Management | Must |

---

## 2. Mô tả chi tiết từng Use Case

---

### UC-01: Đăng nhập / Đăng xuất

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager, Staff |
| **Mô tả** | Người dùng nhập email và mật khẩu để đăng nhập. Hệ thống xác thực bằng JWT, trả về access token + refresh token. Đăng xuất xóa token phía client. |
| **Luồng chính** | 1. Nhập email + mật khẩu → 2. Hệ thống xác thực → 3. Trả token, redirect Dashboard |
| **Luồng ngoại lệ** | Sai mật khẩu → lỗi chung. Tài khoản bị khóa → từ chối đăng nhập. |
| **FR liên quan** | FR-AUTH-01, FR-AUTH-02, FR-AUTH-03, FR-AUTH-12, FR-AUTH-13 |

---

### UC-02: Đăng ký lịch rảnh

| Mục | Nội dung |
|-----|---------|
| **Actor** | Staff (Manager cũng có thể đăng ký) |
| **Mô tả** | Staff mở grid 7 ngày × slot 30 phút (8h–2h), dùng kéo-thả, template-shift, hoặc nút (+) để đăng ký khung giờ rảnh. Lưu lên hệ thống trước deadline 18h Thứ 7. Tối thiểu 5 ngày/tuần. |
| **Luồng chính** | 1. Mở Edit Availability → 2. Chọn khung giờ (drag/template/form) → 3. Save → 4. Kiểm tra ≥ 5 ngày → 5. Lưu thành công |
| **Luồng ngoại lệ** | Quá deadline → khóa edit. < 5 ngày → cảnh báo + yêu cầu lý do. |
| **FR liên quan** | FR-AVAIL-02 → FR-AVAIL-08 |

---

### UC-03: Xem tổng hợp lịch rảnh (Overlap View)

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager, Staff |
| **Mô tả** | Hiển thị grid chồng lớp lịch rảnh toàn team. Ô xanh đậm = nhiều người rảnh. Hover/click → danh sách ai rảnh. Manager dùng để nắm tình hình trước khi xếp ca. |
| **Luồng chính** | 1. Mở trang Availability → 2. Xem Overlap View → 3. Hover ô → xem danh sách |
| **Luồng ngoại lệ** | Chưa ai đăng ký → grid trống. |
| **FR liên quan** | FR-AVAIL-01, FR-AVAIL-10, FR-AVAIL-11, FR-AVAIL-12 |

---

### UC-04: Xếp ca thủ công

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager |
| **Mô tả** | Manager tạo ca và gán nhân viên trên Roster. Chế độ ngày: kéo-thả trên timeline. Chế độ tuần: click vào ô → form nhập. Hệ thống cảnh báo xung đột (giờ chồng, vượt max giờ, nhân viên bận). |
| **Luồng chính** | 1. Mở Roster → 2. Tạo ca (drag hoặc form) → 3. Gán nhân viên → 4. Kiểm tra xung đột → 5. Lưu |
| **Luồng ngoại lệ** | Xung đột giờ → cảnh báo đỏ, Manager có thể override. |
| **FR liên quan** | FR-ROSTER-03, FR-ROSTER-04, FR-ROSTER-05, FR-ROSTER-07 |

---

### UC-05: Auto-Scheduling

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager |
| **Mô tả** | Manager bấm "Auto-Schedule". Hệ thống dùng thuật toán greedy: sort ca theo ưu tiên → tìm Staff rảnh chưa vượt max giờ → gán Staff ít giờ nhất. Kết quả là draft, Manager review trước khi publish. |
| **Luồng chính** | 1. Bấm Auto-Schedule → 2. Hệ thống chạy thuật toán → 3. Hiển thị draft → 4. Manager review + sửa nếu cần |
| **Luồng ngoại lệ** | Không đủ nhân viên rảnh → ca giữ lại ở Open-shift + cảnh báo. |
| **FR liên quan** | FR-ROSTER-06, FR-ROSTER-07 |

---

### UC-06: Publish lịch làm

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager |
| **Mô tả** | Sau khi review draft, Manager bấm "Publish Roster". Lịch chuyển từ draft → published. Hệ thống gửi notification đến toàn bộ Staff. |
| **Luồng chính** | 1. Review draft → 2. Bấm Publish → 3. Lịch chốt → 4. Notification gửi cho tất cả Staff |
| **Luồng ngoại lệ** | Còn Open-shift chưa gán → cảnh báo nhưng vẫn cho publish. |
| **FR liên quan** | FR-ROSTER-08, FR-NOTIF-03 |

---

### UC-07: Xem lịch làm

| Mục | Nội dung |
|-----|---------|
| **Actor** | Staff (Manager cũng xem được) |
| **Mô tả** | Staff xem lịch làm cá nhân theo ngày hoặc tuần. Thấy ca của mình, đồng nghiệp cùng ca, tổng giờ tuần. Tại hàng Open-shift, Staff có thể apply nhận ca trống. |
| **Luồng chính** | 1. Mở Roster → 2. Chọn ngày/tuần → 3. Xem ca cá nhân + đồng nghiệp |
| **Luồng ngoại lệ** | Lịch chưa publish → hiện thông báo "Chưa có lịch". |
| **FR liên quan** | FR-ROSTER-01, FR-ROSTER-02, FR-ROSTER-09, FR-ROSTER-10 |

---

### UC-08: Pass ca (Nhường ca)

| Mục | Nội dung |
|-----|---------|
| **Actor** | Staff |
| **Mô tả** | Staff có việc bận → mở Shift Exchange → click ca của mình → "Pass ca" kèm lời nhắn. Ca chuyển highlight trên Exchange Board, Staff khác bấm vào thấy lời nhắn + nút "Nhận ca". Staff có thể hủy pass trước khi có người nhận. |
| **Luồng chính** | 1. Mở Shift Exchange → 2. Click ca + nhập lời nhắn → 3. Pass ca → 4. Ca chuyển highlight trên Board |
| **Luồng ngoại lệ** | Ca đã diễn ra → không cho pass. |
| **FR liên quan** | FR-EXCHANGE-01, FR-EXCHANGE-06 |

---

### UC-09: Nhận ca

| Mục | Nội dung |
|-----|---------|
| **Actor** | Staff |
| **Mô tả** | Staff B thấy ca highlight trên Exchange Board → click → bấm "Nhận ca". Nếu ca trùng giờ với ca hiện có của B → cảnh báo. Sau xác nhận, hệ thống khóa ca (Pending lock) → gửi request lên Manager phê duyệt. |
| **Luồng chính** | 1. Xem Exchange Board → 2. Click ca highlight → bấm Nhận ca → 3. Cảnh báo nếu trùng ca → 4. Ca chuyển Pending → 5. Notification gửi Manager |
| **Luồng ngoại lệ** | Trùng ca → cảnh báo xác nhận. Nhiều người bấm cùng lúc → chỉ 1 người thành công (optimistic locking). |
| **FR liên quan** | FR-EXCHANGE-02, FR-NOTIF-04 |

---

### UC-10: Duyệt trao đổi ca

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager |
| **Mô tả** | Manager nhận notification yêu cầu pass ca → xem chi tiết (ai đăng, ai nhận, ca nào, có cảnh báo trùng giờ không) → Approve hoặc Reject. Approve: ca chuyển từ Staff A sang Staff B. Reject: ca quay về. Notification gửi cho cả hai. |
| **Luồng chính** | 1. Nhận notification → 2. Xem chi tiết → 3. Approve/Reject → 4. Roster cập nhật → 5. Notification gửi A + B |
| **Luồng ngoại lệ** | Staff B bị xung đột giờ → Manager thấy cảnh báo khi review. |
| **FR liên quan** | FR-EXCHANGE-04, FR-EXCHANGE-05, FR-NOTIF-04 |

---

### UC-11: Tạo thông báo nội bộ

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager |
| **Mô tả** | Manager mở News Feed → bấm "Tạo thông báo mới" → nhập tiêu đề, nội dung, đính kèm hình ảnh → bấm "Đăng bài". Bài xuất hiện đầu feed, notification gửi cho tất cả Staff. |
| **Luồng chính** | 1. Bấm tạo mới → 2. Nhập nội dung + ảnh → 3. Đăng bài → 4. Notification cho Staff |
| **Luồng ngoại lệ** | Ảnh quá lớn → lỗi. Thiếu tiêu đề → validation error. |
| **FR liên quan** | FR-NEWS-01, FR-NEWS-04, FR-NEWS-05, FR-NOTIF-05 |

---

### UC-12: Xem thông báo

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager, Staff |
| **Mô tả** | Người dùng xem News Feed (bài viết) và Notification (chuông). Bài chưa đọc có highlight. Click bài → xem chi tiết + auto mark read. Manager xem thêm danh sách seen. Click notification → navigate đến context liên quan. |
| **Luồng chính** | 1. Mở News Feed → 2. Xem danh sách → 3. Click bài → 4. Đọc + auto mark read |
| **Luồng ngoại lệ** | Không có bài mới → feed trống. |
| **FR liên quan** | FR-NEWS-02, FR-NEWS-03, FR-NEWS-06, FR-NOTIF-01, FR-NOTIF-02 |

---

### UC-13: Quản lý nhân viên

| Mục | Nội dung |
|-----|---------|
| **Actor** | Manager |
| **Mô tả** | Manager tạo tài khoản nhân viên mới, xem danh sách, sửa thông tin, vô hiệu hóa/kích hoạt tài khoản, reset mật khẩu. Staff không thể tự đăng ký — phải do Manager tạo. |
| **Luồng chính** | 1. Mở User Management → 2. Tạo/xem/sửa/vô hiệu hóa nhân viên |
| **Luồng ngoại lệ** | Email trùng → lỗi. Manager tự vô hiệu hóa mình → từ chối. |
| **FR liên quan** | FR-AUTH-06 → FR-AUTH-11 |

---

> **UC-14 Swap ca — Version 2**: Tính năng đổi ca 2 chiều (Staff B đề nghị đổi ca của mình lấy ca Staff A đăng) được lên kế hoạch triển khai trong phiên bản tiếp theo. Version 1 chỉ hỗ trợ Pass ca (UC-08) và Nhận ca (UC-09).

---

## 3. Ma trận Actor × Use Case

| Use Case | Manager | Staff |
|----------|---------|-------|
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
| **Tổng** | **11** | **6** |

---

## 4. Mapping Use Case → Module → FR

| UC-ID | Module | FR liên quan |
|-------|--------|-------------|
| UC-01 | Auth | FR-AUTH-01, 02, 03, 12, 13 |
| UC-02 | Availability | FR-AVAIL-02, 03, 04, 05, 06, 07, 08 |
| UC-03 | Availability | FR-AVAIL-01, 09, 10, 11, 12 |
| UC-04 | Roster | FR-ROSTER-03, 04, 05, 07 |
| UC-05 | Roster | FR-ROSTER-06, 07 |
| UC-06 | Roster | FR-ROSTER-08 + FR-NOTIF-03 |
| UC-07 | Roster | FR-ROSTER-01, 02, 09, 10 |
| UC-08 | Exchange | FR-EXCHANGE-01, 06 |
| UC-09 | Exchange | FR-EXCHANGE-02 + FR-NOTIF-04 |
| UC-10 | Exchange | FR-EXCHANGE-04, 05 + FR-NOTIF-04 |
| UC-11 | News | FR-NEWS-01, 04, 05 + FR-NOTIF-05 |
| UC-12 | News + Notification | FR-NEWS-02, 03, 06 + FR-NOTIF-01, 02 |
| UC-13 | User Management | FR-AUTH-06, 07, 08, 09, 10, 11 |

---

*Tài liệu này phục vụ cho phần Use Case Diagram và phân tích Use Case (Chương 3.2) trong báo cáo đồ án.*
*Use Case Diagram tổng quan sẽ được vẽ bằng draw.io/PlantUML dựa trên bảng này.*
