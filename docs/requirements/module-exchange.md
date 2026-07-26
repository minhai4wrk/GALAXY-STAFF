# PHÂN TÍCH YÊU CẦU CHỨC NĂNG CHI TIẾT

## Module: Shift Exchange (Trao đổi ca)

| Hạng mục | Thông tin |
|----------|-----------|
| Hệ thống | Galaxy Staff – Hệ thống Quản lý Nhân sự Rạp Chiếu Phim |
| Module | Shift Exchange (Trao đổi ca) |
| Phiên bản | 1.0 |
| Ngày tạo | 08/05/2026 |
| Phụ thuộc | Module Roster (ca làm phải đã publish) — xem [module-roster.md](module-roster.md) |

---

## 1. Tổng quan Module

> **Version 1** — Module này chỉ triển khai **Pass ca** và **Nhận ca**. Tính năng **Swap ca** (đổi ca 2 chiều) được lên kế hoạch cho **Version 2**.

Module Shift Exchange cho phép Staff chủ động trao đổi ca khi có việc bận đột xuất, với **2 hình thức**: **Pass ca** (nhường hẳn ca cho người khác) và **Nhận ca** (nhận ca mà người khác đăng pass).

Giao diện chính của module là **bảng trao đổi ca (Shift Exchange Board)** hiển thị tuần làm việc tương tự Roster: các ca bình thường hiện màu xám/nhạt, chỉ những ca đang được đăng trao đổi mới hiện màu nổi bật (highlight). Khi bấm vào một ca nổi bật, hệ thống hiện thông tin ca (ngày/giờ), **lời nhắn** của người đăng, trạng thái, và nút hành động **"Nhận ca"**.

Quy trình: Staff A đăng pass (kèm lời nhắn) → Staff B bấm "Nhận ca" → Manager phê duyệt/từ chối.

Khi Nhận ca mà ca đó **trùng giờ với ca hiện có** của người nhận, hệ thống hiển thị cảnh báo trước khi tiếp tục. Hệ thống dùng Pending lock để tránh xung đột khi nhiều người cùng thao tác trên một yêu cầu.

### 1.1. Trạng thái của một yêu cầu trao đổi

| Trạng thái | Ý nghĩa |
|-----------|---------|
| `available_for_exchange` | Ca đang mở (highlight trên Board), chờ người nhận |
| `pending_approval` | Đã có người nhận, chờ Manager duyệt |
| `approved` | Manager đã duyệt, Roster đã cập nhật |
| `rejected` | Manager từ chối, ca quay về trạng thái ban đầu |
| `cancelled` | Người đăng hủy bài khi chưa có ai chốt |

---

## 2. Yêu cầu chức năng

---

### FR-EXCHANGE-01: Đăng yêu cầu trao đổi ca (Pass + lời nhắn)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-EXCHANGE-01 |
| **Tên yêu cầu** | Staff đăng yêu cầu trao đổi ca (nhường ca) kèm lời nhắn |
| **Mô tả chi tiết** | Staff mở tab Shift Exchange, click vào ca làm của mình → bấm "Pass ca", nhập **lời nhắn** (tùy chọn, ví dụ "Mình bận việc gia đình, ai nhận giúp với"). Ca chuyển sang trạng thái **available_for_exchange** và hiển thị **nổi bật (highlight)** trên Exchange Board; các ca khác vẫn hiện xám/nhạt. Khi Staff khác bấm vào ca nổi bật này sẽ thấy lời nhắn và nút "Nhận ca". Staff có thể hủy pass khi chưa có người chốt nhận. |
| **Actor** | Staff |
| **Điều kiện tiên quyết** | Ca đã publish, thuộc về Staff đang đăng nhập, chưa diễn ra |
| **Kết quả mong đợi** | - Pass thành công: ca chuyển màu highlight trên Exchange Board (kèm lời nhắn). <br> - Ca đã qua: không cho pass (lỗi "Ca này đã diễn ra"). <br> - Hủy pass (chưa ai nhận): ca quay về bình thường. |
| **Mức ưu tiên** | **Should** |

**API:** `POST /api/exchanges` — body: `{ shift_id, message }`

---

### FR-EXCHANGE-02: Nhận ca (Take shift) — cảnh báo trùng ca

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-EXCHANGE-02 |
| **Tên yêu cầu** | Staff nhận ca được đăng pass |
| **Mô tả chi tiết** | Staff B xem Exchange Board, thấy ca nổi bật của Staff A. Click vào ca → xem chi tiết (thông tin ca + lời nhắn) → bấm **"Nhận ca"**. Hệ thống kiểm tra: nếu ca được nhận **trùng giờ với một ca hiện có** của Staff B → hiển thị **cảnh báo** ("Ca này trùng giờ với ca [ngày/giờ] của bạn") và yêu cầu xác nhận trước khi tiếp tục. Sau khi xác nhận, ca chuyển trạng thái **pending_approval** và **khóa** — các Staff khác không thể thao tác trên ca này nữa (Pending lock). Request gửi lên Manager để phê duyệt. |
| **Actor** | Staff |
| **Điều kiện tiên quyết** | Ca đang ở trạng thái available_for_exchange. Staff B không phải Staff A. |
| **Kết quả mong đợi** | - Nhận thành công: ca chuyển pending, khóa cho Staff khác. <br> - Trùng ca: cảnh báo xác nhận; Staff B vẫn có thể tiếp tục (Manager sẽ thấy cảnh báo khi duyệt). <br> - Notification gửi cho Manager + Staff A. <br> - Nhiều người bấm nhận đồng thời: chỉ 1 người thành công (optimistic locking). |

| **Mức ưu tiên** | **Should** |

**API:** `POST /api/exchanges/{id}/take`

---

> **FR-EXCHANGE-03 — Swap ca (đổi ca 2 chiều)**: đã cắt khỏi Version 1, lên kế hoạch cho **Version 2**.
> Mã số được giữ nguyên (không đánh số lại) để không phá vỡ tham chiếu ở các tài liệu khác.
> Bảng `swap_offers` tương ứng cũng không có trong ERD V1.

---

### FR-EXCHANGE-04: Manager phê duyệt trao đổi ca

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-EXCHANGE-04 |
| **Tên yêu cầu** | Manager duyệt hoặc từ chối yêu cầu trao đổi ca |
| **Mô tả chi tiết** | Manager nhận notification về yêu cầu pass ca (đã ở trạng thái pending_approval — Staff B đã nhận). Mở xem chi tiết: ca của Staff A, Staff B nhận, giờ giấc, cùng cảnh báo trùng giờ/quá giờ nếu có. **Approve:** ca chuyển từ Staff A sang Staff B trên Roster, gán nhãn "Trao đổi ca". **Reject:** ca quay về trạng thái ban đầu cho A. Cả hai đều gửi notification cho A và B. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Có yêu cầu exchange đang pending_approval (Staff B đã nhận ca) |
| **Kết quả mong đợi** | - Approve: ca chuyển sang Staff B, Roster cập nhật, notification A + B. <br> - Reject: ca quay về trạng thái cũ, notification A + B. |
| **Mức ưu tiên** | **Should** |

**API:** `PUT /api/exchanges/{id}/approve` và `PUT /api/exchanges/{id}/reject`

---

### FR-EXCHANGE-05: Xem danh sách yêu cầu trao đổi ca

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-EXCHANGE-05 |
| **Tên yêu cầu** | Xem lịch sử và danh sách trao đổi ca |
| **Mô tả chi tiết** | Manager xem toàn bộ yêu cầu exchange: pending, approved, rejected. Staff xem các yêu cầu liên quan đến mình. Có filter theo trạng thái, tuần. Hiển thị: ca nào, ai pass, ai nhận, trạng thái, thời gian tạo. |
| **Actor** | Both |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Kết quả mong đợi** | - Manager: xem tất cả exchanges. <br> - Staff: xem exchanges liên quan đến mình. <br> - Filter theo status: pending/approved/rejected. |
| **Mức ưu tiên** | **Should** |

**API:** `GET /api/exchanges`

---

### FR-EXCHANGE-06: Giao diện Shift Exchange Board

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-EXCHANGE-06 |
| **Tên yêu cầu** | Giao diện bảng trao đổi ca |
| **Mô tả chi tiết** | Trang Shift Exchange hiển thị tuần làm việc tương tự Roster, nhưng tất cả ca bình thường hiện màu xám/nhạt, chỉ ca đang được đăng trao đổi mới hiện màu nổi bật (highlight). Staff dễ dàng nhận ra ca nào đang cần người nhận. Click vào ca highlight → mở chi tiết: thông tin ca, **lời nhắn** của người đăng, nút "Nhận ca". |
| **Actor** | Both |
| **Điều kiện tiên quyết** | Đã đăng nhập. Có lịch đã publish. |
| **Kết quả mong đợi** | - Ca bình thường: xám/nhạt. <br> - Ca đang đăng trao đổi: highlight (màu cam/vàng). <br> - Ca pending approval: highlight khác (màu tím/xanh dương) + label "Đang chờ duyệt". <br> - Click ca highlight → chi tiết + lời nhắn + nút Nhận ca. |
| **Mức ưu tiên** | **Should** |

---

## 3. Ma trận Phân quyền

Bảng 1: Ma trận phân quyền module Shift Exchange

| Chức năng | Manager | Staff |
|-----------|---------|-------|
| Đăng pass ca (FR-EXCHANGE-01) | ❌ | ✅ |
| Nhận ca (FR-EXCHANGE-02) | ❌ | ✅ |
| Duyệt exchange (FR-EXCHANGE-04) | ✅ | ❌ |
| Xem danh sách exchange (FR-EXCHANGE-05) | ✅ (tất cả) | ✅ (của mình) |
| Xem Exchange Board (FR-EXCHANGE-06) | ✅ | ✅ |

---

## 4. Tổng hợp API Endpoints

Bảng 2: API endpoints module Shift Exchange

| Method | Endpoint | Mô tả | Quyền | FR |
|--------|----------|-------|-------|-----|
| `GET` | `/api/exchanges` | Danh sách exchange | Authenticated | FR-EXCHANGE-05 |
| `POST` | `/api/exchanges` | Đăng pass ca (kèm lời nhắn) | Staff | FR-EXCHANGE-01 |
| `DELETE` | `/api/exchanges/{id}` | Hủy pass ca (khi chưa ai nhận) | Staff (chủ bài) | FR-EXCHANGE-01 |
| `POST` | `/api/exchanges/{id}/take` | Nhận ca | Staff | FR-EXCHANGE-02 |
| `PUT` | `/api/exchanges/{id}/approve` | Duyệt exchange | Manager | FR-EXCHANGE-04 |
| `PUT` | `/api/exchanges/{id}/reject` | Từ chối exchange | Manager | FR-EXCHANGE-04 |

---

## 5. Quy tắc Nghiệp vụ (Business Rules)

| Mã | Quy tắc |
|----|---------|
| BR-EX-01 | Staff chỉ đăng trao đổi được ca chưa diễn ra và thuộc về mình. |
| BR-EX-02 | Mỗi ca đang đăng trao đổi chỉ có tối đa 1 người pending nhận (optimistic locking). |
| BR-EX-03 | Staff không thể tự nhận ca mình đã đăng. |
| BR-EX-04 | Sau khi exchange approved, Roster tự động cập nhật: ca chuyển từ Staff A sang Staff B. |
| BR-EX-05 | Khi Nhận ca mà ca đó trùng giờ với ca hiện có của người nhận → hệ thống cảnh báo, cho phép tiếp tục nhưng đánh dấu để Manager xem khi duyệt. |
| BR-EX-06 | Ca đang ở trạng thái pending exchange không thể bị Manager xóa/sửa trên Roster (ràng buộc với [module-roster.md](module-roster.md) FR-ROSTER-05). |

---

## 6. Yêu cầu Phi chức năng

| Hạng mục | Yêu cầu |
|----------|---------|
| **Hiệu năng** | API exchanges response < 300ms. Tải Exchange Board (tuần) < 500ms. |
| **Concurrent** | Optimistic locking cho exchange: dùng DB constraint + status check để tránh 2 Staff cùng nhận một ca. Test 5 request đồng thời → chỉ 1 thành công. |
| **UX Mobile** | Exchange Board hiển thị tốt trên mobile (scroll ngang tuần), nút "Nhận ca" lớn (touch target ≥ 44px) cho Staff thao tác trên điện thoại. |
| **Data Integrity** | Foreign key constraint giữa exchanges–shifts, exchanges–users. Cascade/chặn khi xóa ca đang liên quan đến exchange. |

---

*Tài liệu này phục vụ cho phần Phân tích yêu cầu (Chương 3.2) trong báo cáo đồ án.*
