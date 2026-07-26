# PHÂN TÍCH YÊU CẦU CHỨC NĂNG CHI TIẾT

## Module: Roster & Scheduling (Lịch làm việc)

| Hạng mục | Thông tin |
|----------|-----------|
| Hệ thống | Galaxy Staff – Hệ thống Quản lý Nhân sự Rạp Chiếu Phim |
| Module | Roster & Scheduling (Lịch làm việc) |
| Phiên bản | 1.0 |
| Ngày tạo | 08/05/2026 |
| Module liên quan | Shift Exchange (Trao đổi ca) — tách riêng, xem [module-exchange.md](module-exchange.md) |

---

## 1. Tổng quan Module

Module Roster là nơi Manager tạo, sắp xếp và công bố lịch làm việc cho nhân viên. Hỗ trợ hai cách xếp ca: thủ công (kéo-thả hoặc form) và tự động (Auto-Scheduling). Staff xem lịch làm cá nhân và có thể đăng ký nhận ca trống (Open-shift).

Việc **trao đổi ca** (pass / nhận) sau khi lịch đã publish được tách thành một module độc lập — xem [module-exchange.md](module-exchange.md).

---

## 2. Yêu cầu chức năng

---

### FR-ROSTER-01: Xem lịch làm theo ngày (Timeline View)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-ROSTER-01 |
| **Tên yêu cầu** | Hiển thị lịch làm theo ngày (Timeline View) |
| **Mô tả chi tiết** | Hiển thị lịch làm của 1 ngày cụ thể dạng timeline ngang. Trục dọc là danh sách nhân viên, trục ngang là thời gian (8h–2h). Mỗi ca làm là 1 thanh màu nằm trên hàng của nhân viên tương ứng. Hàng trên cùng là **Open-shift** — chứa các ca chưa được phân công. Manager thấy toàn bộ nhân viên, Staff chỉ thấy lịch cá nhân + Open-shift. |
| **Actor** | Both |
| **Điều kiện tiên quyết** | Đã đăng nhập. Lịch làm đã được tạo cho ngày đó. |
| **Kết quả mong đợi** | - Hiển thị đúng các ca theo timeline. <br> - Thanh màu phân biệt trạng thái (assigned/open/pending). <br> - Click vào thanh ca → xem chi tiết. |
| **Mức ưu tiên** | **Must** |

**API:** `GET /api/shifts?date=YYYY-MM-DD&view=day`

---

### FR-ROSTER-02: Xem lịch làm theo tuần (Daily Card View)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-ROSTER-02 |
| **Tên yêu cầu** | Hiển thị lịch làm theo tuần (Daily Card View) |
| **Mô tả chi tiết** | Hiển thị lịch làm cả tuần dạng bảng. Cột = 7 ngày (Thứ 6 → Thứ 5), hàng = nhân viên. Mỗi ô chứa card ca làm với giờ bắt đầu–kết thúc. Hàng trên cùng là Open-shift. Manager click vào ô để tạo/sửa ca. Staff xem lịch cá nhân. |
| **Actor** | Both |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Kết quả mong đợi** | - Bảng tuần hiển thị đúng, có scroll ngang trên mobile. <br> - Click vào ngày (Manager) → mở form tạo/sửa ca. <br> - Color-coding: xanh = assigned, xám = open, đỏ = xung đột. |
| **Mức ưu tiên** | **Must** |

**API:** `GET /api/shifts?date=YYYY-MM-DD&view=week`

---

### FR-ROSTER-03: Tạo ca làm mới (Manager)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-ROSTER-03 |
| **Tên yêu cầu** | Tạo ca làm mới |
| **Mô tả chi tiết** | Manager tạo ca làm bằng 2 cách: (1) Chế độ ngày — kéo-thả trên timeline để tạo khối ca, (2) Chế độ tuần — click vào ô ngày để mở form nhập. Form gồm: ngày, giờ bắt đầu, giờ kết thúc, nhân viên (optional — nếu bỏ trống thì thành Open-shift). Hệ thống validate xung đột trước khi lưu. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập với role Manager |
| **Kết quả mong đợi** | - Tạo thành công: ca hiển thị trên roster. <br> - Xung đột giờ (nhân viên đã có ca khác): cảnh báo đỏ, cho phép Manager quyết định. <br> - Thiếu trường bắt buộc: validation error. |
| **Mức ưu tiên** | **Must** |

**API:** `POST /api/shifts`

---

### FR-ROSTER-04: Sửa ca làm (Manager)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-ROSTER-04 |
| **Tên yêu cầu** | Chỉnh sửa thông tin ca làm |
| **Mô tả chi tiết** | Manager click vào thanh/card ca để mở form chỉnh sửa: thay đổi giờ, đổi nhân viên, hoặc chuyển thành Open-shift. Ở chế độ ngày, Manager có thể kéo hai đầu thanh ca để thay đổi giờ, hoặc kéo cả thanh để di chuyển sang nhân viên khác. Chỉ sửa được ca chưa publish hoặc ca ở trạng thái draft. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Ca chưa publish hoặc Manager có quyền override |
| **Kết quả mong đợi** | - Sửa thành công: roster cập nhật ngay. <br> - Drag resize → giờ thay đổi tương ứng. <br> - Drag di chuyển → ca chuyển sang nhân viên khác. |
| **Mức ưu tiên** | **Must** |

**API:** `PUT /api/shifts/{id}`

---

### FR-ROSTER-05: Xóa ca làm (Manager)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-ROSTER-05 |
| **Tên yêu cầu** | Xóa ca làm |
| **Mô tả chi tiết** | Manager xóa ca làm khỏi roster. Nếu ca đã publish, hệ thống yêu cầu xác nhận và gửi notification cho nhân viên bị ảnh hưởng. Ca đang trong quá trình exchange (pending) không thể xóa. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Ca không ở trạng thái pending exchange |
| **Kết quả mong đợi** | - Xóa thành công: ca biến mất khỏi roster. <br> - Ca đã publish: popup xác nhận + gửi notification. <br> - Ca đang pending exchange: từ chối xóa, hiện lỗi. |
| **Mức ưu tiên** | **Must** |

**API:** `DELETE /api/shifts/{id}`

---

### FR-ROSTER-06: Auto-Scheduling (Xếp ca tự động)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-ROSTER-06 |
| **Tên yêu cầu** | Tự động xếp ca bằng thuật toán |
| **Mô tả chi tiết** | Manager bấm "Auto-Schedule". Hệ thống lấy danh sách Open-shift (ca trống) và lịch rảnh của toàn bộ Staff, chạy thuật toán greedy để gán ca. **Thuật toán:** (1) Sort ca theo ưu tiên (ca tối > sáng, cuối tuần > ngày thường), (2) Với mỗi ca, tìm Staff rảnh + chưa vượt max giờ + đủ nghỉ giữa ca, (3) Sort Staff theo ít giờ nhất (cân bằng công bằng), (4) Gán Staff đầu tiên đủ điều kiện. Kết quả hiển thị dạng draft — Manager review trước khi publish. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Có Open-shift cần gán. Có lịch rảnh của nhân viên (sau deadline availability). |
| **Kết quả mong đợi** | - ≥ 90% ca được gán đúng người rảnh. <br> - Không vi phạm constraint (max giờ, min nghỉ, xung đột). <br> - Hoàn thành < 10 giây cho 100 NV × 300 ca. <br> - Ca không đủ người: giữ lại ở Open-shift, hiển thị cảnh báo. <br> - Kết quả là draft — chưa publish, Manager có thể sửa. |
| **Mức ưu tiên** | **Must** |

**API:** `POST /api/shifts/auto-schedule`

---

### FR-ROSTER-07: Cảnh báo xung đột khi xếp ca

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-ROSTER-07 |
| **Tên yêu cầu** | Phát hiện và cảnh báo xung đột lịch |
| **Mô tả chi tiết** | Khi Manager xếp ca (thủ công hoặc auto), hệ thống kiểm tra: (1) Nhân viên có rảnh khung giờ đó không, (2) Nhân viên đã có ca khác chồng giờ chưa, (3) Tổng giờ tuần có vượt 48h không, (4) Khoảng nghỉ giữa 2 ca có đủ (ví dụ ≥ 8h) không. Nếu vi phạm, hiển thị cảnh báo màu đỏ. Manager có thể override (ghi đè) nhưng hệ thống ghi log. |
| **Actor** | Hệ thống (tự động kiểm tra) |
| **Điều kiện tiên quyết** | Manager đang thực hiện thao tác xếp ca |
| **Kết quả mong đợi** | - Xung đột giờ: thanh ca chuyển đỏ + tooltip mô tả xung đột. <br> - Vượt max giờ: cảnh báo "NV X đã làm 46/48h tuần này". <br> - Không rảnh: cảnh báo "NV X đã báo bận khung giờ này". |
| **Mức ưu tiên** | **Must** |

---

### FR-ROSTER-08: Publish Roster (Công bố lịch làm)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-ROSTER-08 |
| **Tên yêu cầu** | Công bố lịch làm cho nhân viên |
| **Mô tả chi tiết** | Sau khi review xong draft, Manager bấm "Publish Roster" để chốt lịch. Hệ thống chuyển trạng thái các ca từ draft sang published. Gửi notification đến toàn bộ Staff: "Lịch làm việc tuần tới đã được công bố". Staff có thể xem lịch ngay trên app. Sau khi publish, Manager vẫn sửa được nhưng cần confirm và hệ thống gửi notification cập nhật. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Có ít nhất 1 ca đang ở trạng thái draft |
| **Kết quả mong đợi** | - Publish thành công: tất cả ca chuyển sang published. <br> - Notification gửi đến toàn bộ Staff. <br> - Còn Open-shift chưa gán: cảnh báo nhưng vẫn cho publish. |
| **Mức ưu tiên** | **Must** |

**API:** `POST /api/shifts/publish`

---

### FR-ROSTER-09: Staff đăng ký nhận Open-shift

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-ROSTER-09 |
| **Tên yêu cầu** | Staff apply nhận ca trống (Open-shift) |
| **Mô tả chi tiết** | Staff xem lịch trên Roster, thấy hàng Open-shift còn ca trống. Staff click vào ca → bấm "Apply for shift". Request gửi lên Manager để phê duyệt. Hệ thống kiểm tra Staff có rảnh khung giờ đó không, có vượt max giờ không. Nếu vi phạm → cảnh báo nhưng vẫn cho apply (Manager sẽ quyết). |
| **Actor** | Staff |
| **Điều kiện tiên quyết** | Lịch đã publish. Có Open-shift tồn tại. |
| **Kết quả mong đợi** | - Apply thành công: request pending, gửi notification cho Manager. <br> - Manager approve: ca chuyển từ Open-shift xuống hàng của Staff. <br> - Manager reject: ca giữ nguyên ở Open-shift, gửi notification cho Staff. |
| **Mức ưu tiên** | **Should** |

**API:** `POST /api/shifts/{id}/apply`

---

### FR-ROSTER-10: Staff xem lịch làm cá nhân

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-ROSTER-10 |
| **Tên yêu cầu** | Staff xem lịch làm cá nhân |
| **Mô tả chi tiết** | Staff xem lịch làm của riêng mình theo ngày hoặc tuần. Chế độ ngày: hiển thị chi tiết ca (giờ, vị trí). Chế độ tuần: card tóm tắt mỗi ngày. Ngoài ca của mình, Staff cũng thấy ai làm cùng ca (đồng nghiệp cùng khung giờ). Hiển thị tổng số giờ đã xếp trong tuần. |
| **Actor** | Staff |
| **Điều kiện tiên quyết** | Đã đăng nhập. Lịch đã publish. |
| **Kết quả mong đợi** | - Hiển thị đúng ca của Staff đang đăng nhập. <br> - Hiện danh sách đồng nghiệp cùng ca. <br> - Hiện tổng giờ tuần: "Tuần này: 32h". |
| **Mức ưu tiên** | **Must** |

---

## 3. Ma trận Phân quyền

Bảng 1: Ma trận phân quyền module Roster

| Chức năng | Manager | Staff |
|-----------|---------|-------|
| Xem lịch ngày/tuần (FR-ROSTER-01, 02) | ✅ (tất cả NV) | ✅ (cá nhân + đồng nghiệp cùng ca) |
| Tạo ca (FR-ROSTER-03) | ✅ | ❌ |
| Sửa ca (FR-ROSTER-04) | ✅ | ❌ |
| Xóa ca (FR-ROSTER-05) | ✅ | ❌ |
| Auto-Schedule (FR-ROSTER-06) | ✅ | ❌ |
| Publish Roster (FR-ROSTER-08) | ✅ | ❌ |
| Apply Open-shift (FR-ROSTER-09) | ❌ | ✅ |
| Xem lịch cá nhân (FR-ROSTER-10) | ✅ | ✅ |

---

## 4. Tổng hợp API Endpoints

Bảng 2: API endpoints module Roster

| Method | Endpoint | Mô tả | Quyền | FR |
|--------|----------|-------|-------|-----|
| `GET` | `/api/shifts?date=&view=day\|week` | Xem lịch | Authenticated | FR-ROSTER-01, 02 |
| `POST` | `/api/shifts` | Tạo ca | Manager | FR-ROSTER-03 |
| `PUT` | `/api/shifts/{id}` | Sửa ca | Manager | FR-ROSTER-04 |
| `DELETE` | `/api/shifts/{id}` | Xóa ca | Manager | FR-ROSTER-05 |
| `POST` | `/api/shifts/auto-schedule` | Auto-schedule | Manager | FR-ROSTER-06 |
| `POST` | `/api/shifts/publish` | Publish lịch | Manager | FR-ROSTER-08 |
| `POST` | `/api/shifts/{id}/apply` | Apply open-shift | Staff | FR-ROSTER-09 |

> **Ghi chú:** API trao đổi ca (`/api/exchanges/*`) thuộc module Shift Exchange — xem [module-exchange.md](module-exchange.md).

---

## 5. Quy tắc Nghiệp vụ (Business Rules)

| Mã | Quy tắc |
|----|---------|
| BR-RS-01 | Mỗi nhân viên tối đa 48h/tuần. Auto-schedule tự động tuân thủ, xếp thủ công thì cảnh báo. |
| BR-RS-02 | Khoảng nghỉ tối thiểu giữa 2 ca: 8 giờ. |
| BR-RS-03 | Tối đa 6 ngày liên tiếp làm việc. |
| BR-RS-04 | Auto-schedule ưu tiên cân bằng giờ giữa các nhân viên (ít giờ nhất được xếp trước). |
| BR-RS-05 | Chỉ Manager mới publish được roster. Sau publish, Staff mới xem được. |
| BR-RS-06 | Ca đang ở trạng thái pending exchange không thể bị xóa/sửa (ràng buộc với module Shift Exchange — xem [module-exchange.md](module-exchange.md), BR-EX-06). |

> **Ghi chú:** Các quy tắc nghiệp vụ về trao đổi ca (pass/nhận) đã chuyển sang [module-exchange.md](module-exchange.md) với prefix `BR-EX-*`.

---

## 6. Yêu cầu Phi chức năng

| Hạng mục | Yêu cầu |
|----------|---------|
| **Hiệu năng** | Auto-schedule < 10s cho 100 NV × 300 ca. API shifts response < 300ms. |
| **UX Desktop** | Drag-drop mượt trên Roster (dnd-kit). Color-coding rõ ràng. |
| **UX Mobile** | Card view tối giản, nút bấm lớn cho Staff. Hạn chế drag-drop trên mobile. |
| **Data Integrity** | Foreign key constraint giữa shifts–users. Cascade logic khi xóa ca (lưu ý chặn xóa ca đang pending exchange). |

---

*Tài liệu này phục vụ cho phần Phân tích yêu cầu (Chương 3.2) trong báo cáo đồ án.*
