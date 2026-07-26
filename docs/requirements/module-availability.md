# PHÂN TÍCH YÊU CẦU CHỨC NĂNG CHI TIẾT

## Module: Availability – Đăng ký Lịch rảnh

| Hạng mục | Thông tin |
|----------|-----------|
| Hệ thống | Galaxy Staff – Hệ thống Quản lý Nhân sự Rạp Chiếu Phim |
| Module | Availability (Đăng ký lịch rảnh) |
| Phiên bản | 1.0 |
| Ngày tạo | 08/05/2026 |

---

## 1. Tổng quan Module

Module Availability cho phép nhân viên đăng ký lịch rảnh hàng tuần thông qua giao diện grid trực quan (tương tự When2Meet). Manager sử dụng Overlap View để tổng hợp và xem lịch rảnh của toàn bộ nhân viên, từ đó làm cơ sở xếp ca ở module Roster.

**Đặc thù nghiệp vụ:**
- Tuần làm việc của rạp tính từ **Thứ 6 đến Thứ 5 tuần sau**.
- Khung giờ hoạt động: **8h00 sáng đến "closed" (~2h00 sáng hôm sau)**, mỗi ô 30 phút.
- Deadline đăng ký: **18h00 Thứ 7** hàng tuần (trước tuần đăng ký).
- Yêu cầu đăng ký tối thiểu **5 ngày/tuần**.

---

## 2. Danh sách Yêu cầu Chức năng

---

### FR-AVAIL-01: Hiển thị Overlap View tổng hợp lịch rảnh

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-01 |
| **Tên yêu cầu** | Hiển thị tổng hợp lịch rảnh toàn team (Overlap View) |
| **Mô tả chi tiết** | Trang chính của module Availability hiển thị lưới grid 7 ngày × các slot 30 phút, thể hiện chồng lớp lịch rảnh của toàn bộ nhân viên. Ô nào có nhiều người rảnh thì màu xanh càng đậm, ít người rảnh thì nhạt dần, không ai rảnh thì trống. Khi hover hoặc click vào một ô, hiện popup/tooltip danh sách ai rảnh, ai bận tại khung giờ đó. Manager dùng view này để nắm tình hình trước khi xếp ca. Staff cũng xem được để biết mình đã đăng ký đúng chưa. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Đã đăng nhập. Có ít nhất 1 nhân viên đã đăng ký lịch rảnh cho tuần được chọn. |
| **Kết quả mong đợi** | - Grid hiển thị đúng dữ liệu chồng lớp. <br> - Màu sắc gradient: trắng (0 người) → xanh nhạt → xanh đậm (nhiều người). <br> - Hover/click hiện danh sách nhân viên rảnh tại ô đó. <br> - Có thể chuyển đổi giữa các tuần (tuần hiện tại, tuần tới). |
| **Mức ưu tiên** | **Must** |

**API tương ứng:** `GET /api/availabilities/overview?week_start=YYYY-MM-DD`

---

### FR-AVAIL-02: Mở giao diện đăng ký lịch rảnh (Edit Availability)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-02 |
| **Tên yêu cầu** | Mở bảng đăng ký lịch rảnh cá nhân |
| **Mô tả chi tiết** | Từ trang Overlap View, Staff bấm nút "Edit Availability" để mở bảng grid trống của tuần tới. Grid hiển thị 7 cột (Thứ 6 → Thứ 5) × các hàng ô 30 phút (từ 8h00 đến 2h00 sáng hôm sau = 36 ô/ngày). Nếu Staff đã đăng ký trước đó, grid sẽ load lại dữ liệu cũ để chỉnh sửa. Nếu đã qua deadline thì nút "Edit Availability" bị khóa. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Đã đăng nhập. Chưa qua deadline 18h00 Thứ 7. |
| **Kết quả mong đợi** | - Trước deadline: mở grid chỉnh sửa thành công, load dữ liệu cũ nếu có. <br> - Sau deadline: nút bị disable, hiển thị "Đã hết hạn đăng ký cho tuần này". |
| **Mức ưu tiên** | **Must** |

---

### FR-AVAIL-03: Đăng ký lịch rảnh bằng kéo-thả (Drag-to-select)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-03 |
| **Tên yêu cầu** | Kéo-thả để đăng ký khung giờ rảnh |
| **Mô tả chi tiết** | Trên bảng grid, Staff nhấn giữ chuột và kéo qua các ô 30 phút để "tô màu" — đánh dấu là rảnh. Các ô được tô sẽ chuyển sang màu xanh. Nếu kéo lại qua các ô đã tô, ô đó sẽ bị xóa (toggle). Thao tác này cho phép Staff đăng ký nhanh nhiều khung giờ liên tiếp. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Đang ở màn hình Edit Availability, chưa qua deadline |
| **Kết quả mong đợi** | - Kéo qua ô trống → ô chuyển xanh (đã đăng ký rảnh). <br> - Kéo qua ô đã xanh → ô trở về trống (hủy đăng ký). <br> - Thao tác mượt mà, không lag trên desktop. |
| **Mức ưu tiên** | **Must** |

---

### FR-AVAIL-04: Sử dụng Template-shift

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-04 |
| **Tên yêu cầu** | Áp dụng mẫu ca có sẵn (Template-shift) |
| **Mô tả chi tiết** | Hệ thống cung cấp 4 mẫu ca sẵn: **Ca sáng (8h–13h)**, **Ca chiều (13h–18h)**, **Ca tối (18h–closed)**, **Cả ngày (Full)**. Staff kéo mẫu ca vào ngày mong muốn trên grid, hệ thống tự động fill các ô 30 phút tương ứng. Nếu khung giờ đã có dữ liệu, template sẽ ghi đè lên. Template giúp tiết kiệm thời gian so với kéo-thả từng ô. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Đang ở màn hình Edit Availability |
| **Kết quả mong đợi** | - Kéo template "Ca sáng" vào Thứ 6 → các ô từ 8h00–13h00 của Thứ 6 tự động tô xanh. <br> - Kéo template "Full" → tô toàn bộ ô trong ngày đó. <br> - Có thể áp dụng nhiều template cho nhiều ngày khác nhau. |
| **Mức ưu tiên** | **Must** |

---

### FR-AVAIL-05: Tạo shift thủ công bằng nút (+)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-05 |
| **Tên yêu cầu** | Tạo khung giờ rảnh bằng cách nhập tay |
| **Mô tả chi tiết** | Ngoài kéo-thả, Staff có thể bấm nút (+) trên mỗi cột ngày để mở form nhập tay: chọn giờ bắt đầu và giờ kết thúc. Hệ thống sẽ tự động fill các ô 30 phút tương ứng vào grid. Phù hợp cho trường hợp muốn đăng ký chính xác hoặc thao tác trên thiết bị di động (kéo-thả khó dùng trên mobile). |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Đang ở màn hình Edit Availability |
| **Kết quả mong đợi** | - Bấm (+) → mở form với 2 field: Start Time, End Time (dropdown hoặc time picker). <br> - Giờ kết thúc phải sau giờ bắt đầu. <br> - Submit → fill tự động các ô tương ứng trên grid. |
| **Mức ưu tiên** | **Must** |

---

### FR-AVAIL-06: Lưu lịch rảnh (Save Availability)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-06 |
| **Tên yêu cầu** | Lưu lịch rảnh đã đăng ký lên hệ thống |
| **Mô tả chi tiết** | Staff bấm "Save Availability" để lưu toàn bộ lịch rảnh đã chọn trên grid. API nhận danh sách các slot (batch upsert): tạo mới nếu chưa có, cập nhật nếu đã tồn tại, xóa slot nào Staff đã bỏ chọn. Sau khi lưu thành công, quay về trang Overlap View. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Đang ở màn hình Edit Availability, có ít nhất 1 ô được chọn, chưa qua deadline |
| **Kết quả mong đợi** | - Lưu thành công: hiển thị thông báo "Đã lưu lịch rảnh", redirect về Overlap View. <br> - Grid trống hoàn toàn: cảnh báo "Bạn chưa chọn khung giờ rảnh nào". <br> - Lỗi mạng/server: hiển thị lỗi, giữ nguyên dữ liệu trên grid để không mất công chọn lại. |
| **Mức ưu tiên** | **Must** |

**API tương ứng:** `POST /api/availabilities` (batch upsert)

---

### FR-AVAIL-07: Kiểm tra tối thiểu 5 ngày đăng ký

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-07 |
| **Tên yêu cầu** | Cảnh báo khi đăng ký ít hơn 5 ngày/tuần |
| **Mô tả chi tiết** | Khi Staff bấm Save, hệ thống đếm số ngày có ít nhất 1 slot rảnh. Nếu ít hơn 5 ngày, hiển thị popup cảnh báo yêu cầu nhập lý do (ví dụ: "Thi cuối kỳ", "Ốm",...). Staff có thể bỏ qua cảnh báo và vẫn lưu được (chỉ warning, không block). Lý do sẽ được lưu để Manager xem xét. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Staff bấm Save với dữ liệu < 5 ngày |
| **Kết quả mong đợi** | - < 5 ngày: popup cảnh báo + ô nhập lý do. Staff có thể nhập lý do rồi bấm "Gửi" hoặc bấm "Bỏ qua". Cả hai đều cho phép lưu. <br> - ≥ 5 ngày: lưu bình thường, không cảnh báo. |
| **Mức ưu tiên** | **Must** |

---

### FR-AVAIL-08: Deadline tự động khóa đăng ký

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-08 |
| **Tên yêu cầu** | Tự động khóa đăng ký khi hết deadline |
| **Mô tả chi tiết** | Hệ thống tự động khóa chức năng đăng ký lịch rảnh vào lúc **18h00 Thứ 7** hàng tuần. Sau thời điểm này: nút "Edit Availability" bị disable, API từ chối request tạo/sửa availability cho tuần đó. Đồng thời, hệ thống tự động mở đăng ký cho tuần kế tiếp. Hiển thị countdown timer hoặc thông báo deadline trên giao diện. |
| **Actor** | Hệ thống (tự động) |
| **Điều kiện tiên quyết** | Thời gian hiện tại vượt qua 18h00 Thứ 7 |
| **Kết quả mong đợi** | - Trước deadline: giao diện mở bình thường, hiển thị "Còn X ngày Y giờ". <br> - Sau deadline: nút Edit bị khóa, hiển thị "Đã hết hạn đăng ký". <br> - API trả về 400 "Đã qua deadline đăng ký cho tuần này" nếu client cố gửi request. |
| **Mức ưu tiên** | **Must** |

---

### FR-AVAIL-09: Xem lịch rảnh cá nhân đã đăng ký

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-09 |
| **Tên yêu cầu** | Xem lại lịch rảnh đã đăng ký của bản thân |
| **Mô tả chi tiết** | Staff có thể xem lại lịch rảnh mà mình đã đăng ký cho tuần hiện tại hoặc tuần tới. Dữ liệu hiển thị trên grid với các ô đã chọn được tô màu. Nếu chưa qua deadline, Staff có thể bấm Edit để chỉnh sửa. Nếu đã qua deadline, chỉ xem, không chỉnh sửa được. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Kết quả mong đợi** | - Hiển thị đúng các slot đã đăng ký trên grid. <br> - Trước deadline: nút "Edit" hiện. <br> - Sau deadline: nút "Edit" bị ẩn hoặc disable. |
| **Mức ưu tiên** | **Must** |

**API tương ứng:** `GET /api/availabilities?week_start=YYYY-MM-DD`

---

### FR-AVAIL-10: Manager xem lịch rảnh từng nhân viên

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-10 |
| **Tên yêu cầu** | Manager xem chi tiết lịch rảnh của một nhân viên cụ thể |
| **Mô tả chi tiết** | Trên Overlap View, khi Manager click vào tên nhân viên trong danh sách popup (hover ô), hệ thống hiển thị grid lịch rảnh cá nhân của nhân viên đó. Manager có thể xem ai đăng ký bao nhiêu ngày, khung giờ nào, và lý do nếu đăng ký < 5 ngày. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập với role Manager |
| **Kết quả mong đợi** | - Hiển thị grid lịch rảnh cá nhân của nhân viên được chọn. <br> - Hiển thị tổng số ngày đã đăng ký. <br> - Nếu < 5 ngày: hiển thị lý do (nếu có) kèm cảnh báo. |
| **Mức ưu tiên** | **Should** |

**API tương ứng:** `GET /api/availabilities?week_start=YYYY-MM-DD&user_id={id}`

---

### FR-AVAIL-11: Thống kê trạng thái đăng ký

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-11 |
| **Tên yêu cầu** | Hiển thị thống kê ai đã đăng ký, ai chưa |
| **Mô tả chi tiết** | Manager xem được danh sách tổng quan: nhân viên nào đã đăng ký lịch rảnh, ai chưa đăng ký, ai đăng ký < 5 ngày. Hiển thị dạng bảng hoặc badge trên Overlap View. Giúp Manager nhắc nhở nhân viên chưa đăng ký trước deadline. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập với role Manager |
| **Kết quả mong đợi** | - Danh sách nhân viên kèm trạng thái: ✅ Đã đăng ký (X ngày), ⚠️ Đăng ký thiếu (< 5 ngày), ❌ Chưa đăng ký. <br> - Tổng số: "8/12 nhân viên đã đăng ký". |
| **Mức ưu tiên** | **Should** |

---

### FR-AVAIL-12: Chuyển đổi giữa các tuần

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-12 |
| **Tên yêu cầu** | Điều hướng xem lịch rảnh theo tuần |
| **Mô tả chi tiết** | Trên Overlap View, có nút Previous/Next hoặc date picker để chuyển giữa các tuần. Hiển thị rõ tuần đang xem (ví dụ: "Tuần 13/06 – 19/06/2026"). Tuần mặc định khi vào trang là tuần đang mở đăng ký. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Kết quả mong đợi** | - Bấm Next/Previous → grid cập nhật dữ liệu tuần tương ứng. <br> - Hiển thị rõ ràng "Thứ 6 ngày X → Thứ 5 ngày Y". <br> - Tuần có deadline đang mở được đánh dấu nổi bật. |
| **Mức ưu tiên** | **Should** |

---

### FR-AVAIL-13: Hiển thị countdown deadline

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AVAIL-13 |
| **Tên yêu cầu** | Đếm ngược thời gian deadline đăng ký |
| **Mô tả chi tiết** | Trên trang Availability (cả Overlap View lẫn Edit), hiển thị countdown timer: "Hạn đăng ký: còn 2 ngày 5 giờ 30 phút". Khi gần deadline (ví dụ < 6 giờ), timer chuyển sang màu đỏ/cam để nhắc nhở. Sau deadline, hiển thị "Đã hết hạn đăng ký". |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Tuần đang xem có deadline chưa qua |
| **Kết quả mong đợi** | - Timer đếm ngược chính xác theo thời gian thực. <br> - < 6 giờ: đổi màu cảnh báo. <br> - Hết hạn: hiện "Đã hết hạn". |
| **Mức ưu tiên** | **Could** |

---

## 3. Ma trận Phân quyền

Bảng 1: Ma trận phân quyền module Availability

| Chức năng | Manager | Staff |
|-----------|---------|-------|
| Xem Overlap View (FR-AVAIL-01) | ✅ | ✅ |
| Mở Edit Availability (FR-AVAIL-02) | ✅ | ✅ |
| Kéo-thả đăng ký (FR-AVAIL-03) | ✅ | ✅ |
| Dùng Template-shift (FR-AVAIL-04) | ✅ | ✅ |
| Tạo shift bằng nút + (FR-AVAIL-05) | ✅ | ✅ |
| Save Availability (FR-AVAIL-06) | ✅ | ✅ |
| Kiểm tra 5 ngày (FR-AVAIL-07) | ✅ | ✅ |
| Xem lịch cá nhân (FR-AVAIL-09) | ✅ | ✅ (chỉ bản thân) |
| Xem lịch từng NV (FR-AVAIL-10) | ✅ | ❌ |
| Xem thống kê đăng ký (FR-AVAIL-11) | ✅ | ❌ |

---

## 4. Tổng hợp API Endpoints

Bảng 2: Danh sách API endpoints module Availability

| Method | Endpoint | Mô tả | Quyền | FR |
|--------|----------|-------|-------|-----|
| `GET` | `/api/availabilities?week_start=` | Xem lịch rảnh cá nhân (hoặc theo user_id) | Authenticated | FR-AVAIL-09, 10 |
| `POST` | `/api/availabilities` | Lưu/cập nhật lịch rảnh (batch upsert) | Authenticated | FR-AVAIL-06 |
| `GET` | `/api/availabilities/overview?week_start=` | Overlap view tổng hợp | Authenticated | FR-AVAIL-01 |
| `GET` | `/api/availabilities/stats?week_start=` | Thống kê ai đã/chưa đăng ký | Manager only | FR-AVAIL-11 |

---

## 5. Quy tắc Nghiệp vụ (Business Rules)

| Mã | Quy tắc | Ghi chú |
|----|---------|---------|
| BR-AV-01 | Tuần làm việc tính từ Thứ 6 đến Thứ 5 tuần sau | Khác tuần calendar thông thường |
| BR-AV-02 | Khung giờ hoạt động: 8h00 – 2h00 sáng hôm sau (closed) | 36 slot × 30 phút/ngày |
| BR-AV-03 | Deadline đăng ký: 18h00 Thứ 7 hàng tuần | Sau deadline → khóa edit, mở tuần mới |
| BR-AV-04 | Tối thiểu 5 ngày/tuần | Warning, không hard block |
| BR-AV-05 | Mỗi Staff chỉ có 1 bản đăng ký/tuần | Upsert: đăng ký mới ghi đè bản cũ |
| BR-AV-06 | Manager cũng có thể đăng ký lịch rảnh | Manager cũng có thể tham gia làm ca |
| BR-AV-07 | Sau deadline, lịch rảnh chỉ đọc, không sửa được | Cả API lẫn UI đều phải enforce |

---

## 6. Yêu cầu Phi chức năng liên quan

| Hạng mục | Yêu cầu |
|----------|---------|
| **Hiệu năng** | Overlap View phải render dưới 1 giây cho 50 nhân viên. API overview phải aggregate dữ liệu hiệu quả (SQL GROUP BY). |
| **UX – Desktop** | Kéo-thả mượt mà, không lag. Grid ô 30 phút dễ nhìn, dễ bấm. |
| **UX – Mobile** | Trên mobile browser, ưu tiên nút (+) tạo shift thay vì kéo-thả (khó thao tác trên màn hình nhỏ). Grid có thể scroll ngang. |
| **Concurrent** | Nhiều Staff lưu đồng thời gần deadline (peak hour) → API phải xử lý tốt, không bị race condition. |
| **Validation** | `start_time < end_time`. `day_of_week` thuộc [0–6]. `week_start` phải là ngày Thứ 6. Slot nằm trong khung 8h–2h. |

---

*Tài liệu này phục vụ cho phần Phân tích yêu cầu (Chương 3.2) trong báo cáo đồ án.*
