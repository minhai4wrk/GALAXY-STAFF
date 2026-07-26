# PHÂN TÍCH YÊU CẦU CHỨC NĂNG CHI TIẾT

## Module: News Feed & Notification

| Hạng mục | Thông tin |
|----------|-----------|
| Hệ thống | Galaxy Staff – Hệ thống Quản lý Nhân sự Rạp Chiếu Phim |
| Module | News Feed (Bảng tin nội bộ) + Notification (Thông báo) |
| Phiên bản | 1.0 |
| Ngày tạo | 08/05/2026 |

---

## 1. Tổng quan Module

### 1.1. News Feed – Bảng tin nội bộ

Thay thế việc gửi thông báo qua Facebook/Messenger — Manager đăng bài thông báo nội bộ (lịch chiếu phim, CTKM, lịch họp,...) trực tiếp trên hệ thống. Staff xem feed và hệ thống theo dõi ai đã đọc, ai chưa (Seen tracking).

### 1.2. Notification – Thông báo hệ thống

Thông báo tự động (in-app) được gửi khi có sự kiện quan trọng: lịch làm được publish, có yêu cầu trao đổi ca, bài viết mới,... Hỗ trợ WebSocket cho real-time hoặc polling làm fallback.

---

## PHẦN A: NEWS FEED

---

### FR-NEWS-01: Tạo bài thông báo mới

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NEWS-01 |
| **Tên yêu cầu** | Manager tạo bài thông báo nội bộ |
| **Mô tả chi tiết** | Manager bấm "Tạo thông báo mới", nhập: tiêu đề, nội dung (text), đính kèm hình ảnh (optional, tối đa 1–3 ảnh). Bấm "Đăng bài" để publish. Bài viết xuất hiện trên đầu News Feed và hệ thống tự động gửi notification đến toàn bộ Staff. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập với role Manager |
| **Kết quả mong đợi** | - Đăng thành công: bài xuất hiện đầu feed, notification gửi cho tất cả Staff. <br> - Thiếu tiêu đề: validation error. <br> - Ảnh quá lớn (> 5MB): lỗi "Kích thước ảnh vượt quá giới hạn". |
| **Mức ưu tiên** | **Must** |

**API:** `POST /api/news/images` (upload từng ảnh, trả về `image_url`) → `POST /api/news` (tạo bài, truyền danh sách URL vào `image_urls`)

> Upload tách thành bước riêng vì BR-NW-04 cho tối đa 3 ảnh và mỗi ảnh tối đa 5MB:
> nhồi cả 3 ảnh vào một request multipart cùng tiêu đề/nội dung thì chỉ cần một ảnh lỗi
> là mất trắng toàn bộ bài đang soạn. Tách ra thì Manager upload xong ảnh nào chắc ảnh đó.
> Endpoint upload vốn bị thiếu ở bản 1.0 của tài liệu (bảng `news_images` đã có trong ERD
> nhưng không có đường nào đưa ảnh lên) — xem [docs/api/README.md](../api/README.md) mục 4.

---

### FR-NEWS-02: Xem danh sách bài thông báo (News Feed)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NEWS-02 |
| **Tên yêu cầu** | Xem danh sách bài thông báo |
| **Mô tả chi tiết** | Trang News Feed hiển thị danh sách bài viết theo thứ tự mới nhất trước (reverse chronological). Mỗi bài hiển thị: tiêu đề, nội dung tóm tắt (preview), ảnh thumbnail (nếu có), tên người đăng, thời gian đăng, trạng thái đã đọc/chưa đọc. Hỗ trợ infinite scroll hoặc phân trang. Bài chưa đọc có badge/highlight để dễ nhận biết. |
| **Actor** | Both |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Kết quả mong đợi** | - Bài mới nhất hiện đầu. <br> - Bài chưa đọc: có badge "Mới" hoặc highlight nền. <br> - Phân trang/infinite scroll hoạt động mượt. |
| **Mức ưu tiên** | **Must** |

**API:** `GET /api/news?page=&limit=`

---

### FR-NEWS-03: Xem chi tiết bài thông báo

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NEWS-03 |
| **Tên yêu cầu** | Xem nội dung đầy đủ bài thông báo |
| **Mô tả chi tiết** | Click vào bài trên feed để xem toàn bộ nội dung, hình ảnh đính kèm, tên tác giả, thời gian đăng. Khi Staff mở bài, hệ thống tự động ghi nhận "đã đọc" (mark as read). Manager xem bài thì thấy thêm nút sửa/xóa và danh sách ai đã đọc. |
| **Actor** | Both |
| **Điều kiện tiên quyết** | Đã đăng nhập. Bài viết tồn tại. |
| **Kết quả mong đợi** | - Hiển thị đầy đủ nội dung + ảnh. <br> - Tự động mark as read khi Staff mở bài. <br> - Manager: thấy thêm danh sách seen + nút sửa/xóa. |
| **Mức ưu tiên** | **Must** |

**API:** `GET /api/news/{id}` + `POST /api/news/{id}/read`

---

### FR-NEWS-04: Sửa bài thông báo

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NEWS-04 |
| **Tên yêu cầu** | Manager chỉnh sửa bài thông báo đã đăng |
| **Mô tả chi tiết** | Manager mở bài → bấm "Sửa" → chỉnh sửa tiêu đề, nội dung, thêm/xóa hình ảnh → bấm "Cập nhật". Bài sau khi sửa có thể hiện label "Đã chỉnh sửa" để Staff biết. Không reset trạng thái "đã đọc" của Staff. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập Manager. Bài do Manager này tạo hoặc có quyền sửa. |
| **Kết quả mong đợi** | - Sửa thành công: nội dung cập nhật, hiện "Đã chỉnh sửa". <br> - Trạng thái seen của Staff không bị reset. |
| **Mức ưu tiên** | **Should** |

**API:** `PUT /api/news/{id}`

---

### FR-NEWS-05: Xóa bài thông báo

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NEWS-05 |
| **Tên yêu cầu** | Manager xóa bài thông báo |
| **Mô tả chi tiết** | Manager bấm "Xóa" trên bài → popup xác nhận "Bạn có chắc muốn xóa bài này?" → xác nhận xóa. Bài bị xóa khỏi feed, dữ liệu seen liên quan cũng bị xóa. Có thể dùng soft-delete (đánh dấu deleted) thay vì xóa vĩnh viễn. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập Manager |
| **Kết quả mong đợi** | - Xóa thành công: bài biến mất khỏi feed. <br> - Yêu cầu confirm trước khi xóa. |
| **Mức ưu tiên** | **Should** |

**API:** `DELETE /api/news/{id}`

---

### FR-NEWS-06: Theo dõi lượt đọc (Seen Tracking)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NEWS-06 |
| **Tên yêu cầu** | Manager xem ai đã đọc / chưa đọc bài |
| **Mô tả chi tiết** | Trên trang chi tiết bài viết, Manager thấy danh sách: nhân viên đã đọc (kèm thời gian đọc) và nhân viên chưa đọc. Hiển thị tổng: "8/12 nhân viên đã đọc". Giúp Manager biết thông tin quan trọng đã được truyền đạt chưa — thay thế việc hỏi từng người trên Messenger. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập Manager. Bài viết tồn tại. |
| **Kết quả mong đợi** | - Danh sách 2 tab: "Đã đọc" (kèm thời gian) + "Chưa đọc". <br> - Tổng: "8/12 đã đọc". |
| **Mức ưu tiên** | **Must** |

**API:** `GET /api/news/{id}/reads`

---

## PHẦN B: NOTIFICATION (Thông báo hệ thống)

---

### FR-NOTIF-01: Xem danh sách thông báo

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NOTIF-01 |
| **Tên yêu cầu** | Xem danh sách thông báo cá nhân |
| **Mô tả chi tiết** | Người dùng bấm icon chuông trên header → dropdown/panel hiện danh sách notification. Mỗi notification gồm: message, thời gian, trạng thái đọc/chưa đọc, icon theo loại (ca mới, exchange, news,...). Chưa đọc có highlight. Click vào notification → chuyển đến trang liên quan (ví dụ: click notification exchange → mở trang Shift Exchange). Badge số trên icon chuông hiển thị số notification chưa đọc. |
| **Actor** | Both |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Kết quả mong đợi** | - Danh sách notification theo thứ tự mới nhất. <br> - Badge số chưa đọc trên icon chuông. <br> - Click → navigate đến context tương ứng. |
| **Mức ưu tiên** | **Must** |

**API:** `GET /api/notifications`

---

### FR-NOTIF-02: Đánh dấu đã đọc thông báo

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NOTIF-02 |
| **Tên yêu cầu** | Đánh dấu thông báo đã đọc |
| **Mô tả chi tiết** | Người dùng click vào notification → tự động mark as read. Hoặc bấm nút "Đánh dấu tất cả đã đọc" để mark all. Badge số trên icon chuông cập nhật tương ứng. |
| **Actor** | Both |
| **Điều kiện tiên quyết** | Có notification chưa đọc |
| **Kết quả mong đợi** | - Click 1 notification: notification đó chuyển đã đọc, badge giảm 1. <br> - "Đánh dấu tất cả": tất cả chuyển đã đọc, badge = 0. |
| **Mức ưu tiên** | **Must** |

**API:** `PUT /api/notifications/{id}/read` + `PUT /api/notifications/read-all`

---

### FR-NOTIF-03: Tự động gửi notification khi Publish Roster

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NOTIF-03 |
| **Tên yêu cầu** | Notification tự động khi lịch làm được công bố |
| **Mô tả chi tiết** | Khi Manager publish roster (FR-ROSTER-08), hệ thống tự động tạo notification cho toàn bộ Staff: "Lịch làm việc tuần [ngày] đã được công bố". Click notification → chuyển đến trang Roster. |
| **Actor** | Hệ thống (trigger tự động) |
| **Điều kiện tiên quyết** | Manager vừa publish roster |
| **Kết quả mong đợi** | - Mỗi Staff nhận 1 notification. <br> - Message rõ ràng, có tuần cụ thể. <br> - Click → navigate đến Roster. |
| **Mức ưu tiên** | **Must** |

---

### FR-NOTIF-04: Notification khi có yêu cầu trao đổi ca

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NOTIF-04 |
| **Tên yêu cầu** | Notification cho các sự kiện Shift Exchange |
| **Mô tả chi tiết** | Hệ thống gửi notification tại mỗi bước exchange: (1) Staff B nhận ca → notification cho Manager + Staff A, (2) Manager approve → notification cho Staff A + B, (3) Manager reject → notification cho Staff A + B. Message mô tả rõ: ai, ca nào, kết quả. |
| **Actor** | Hệ thống (trigger tự động) |
| **Điều kiện tiên quyết** | Có sự kiện exchange xảy ra |
| **Kết quả mong đợi** | - Đúng người nhận đúng thông báo. <br> - Message cụ thể: "Nguyễn Văn A đã nhận ca ngày 15/06 (18h–23h). Chờ duyệt." <br> - Click → navigate đến Exchange. |
| **Mức ưu tiên** | **Should** |

---

### FR-NOTIF-05: Notification khi có bài News mới

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NOTIF-05 |
| **Tên yêu cầu** | Notification khi Manager đăng bài thông báo mới |
| **Mô tả chi tiết** | Khi Manager đăng bài News (FR-NEWS-01), hệ thống gửi notification cho toàn bộ Staff: "Quản lý vừa đăng thông báo mới: [Tiêu đề bài]". Click → chuyển đến bài viết. |
| **Actor** | Hệ thống (trigger tự động) |
| **Điều kiện tiên quyết** | Manager vừa đăng bài news |
| **Kết quả mong đợi** | - Mỗi Staff nhận 1 notification kèm tiêu đề bài. <br> - Click → navigate đến chi tiết bài. |
| **Mức ưu tiên** | **Must** |

---

### FR-NOTIF-06: Real-time notification qua WebSocket

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NOTIF-06 |
| **Tên yêu cầu** | Nhận thông báo real-time qua WebSocket |
| **Mô tả chi tiết** | Frontend duy trì kết nối WebSocket đến server. Khi có notification mới, server push trực tiếp đến client mà không cần refresh trang. Badge chuông tự động cập nhật. Có thể hiện toast/popup nhỏ góc màn hình. **Fallback:** Nếu WebSocket không khả dụng, dùng polling (fetch mỗi 30 giây). |
| **Actor** | Hệ thống |
| **Điều kiện tiên quyết** | User đang online (có kết nối WebSocket) |
| **Kết quả mong đợi** | - Notification hiện real-time (< 2 giây). <br> - Toast popup góc phải. <br> - Badge chuông tự cập nhật. <br> - Nếu WebSocket fail → fallback polling 30s. |
| **Mức ưu tiên** | **Should** |

---

### FR-NOTIF-07: Notification khi Open-shift apply được duyệt

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-NOTIF-07 |
| **Tên yêu cầu** | Notification khi Manager duyệt yêu cầu apply open-shift |
| **Mô tả chi tiết** | Khi Staff apply open-shift (FR-ROSTER-09), Manager nhận notification. Khi Manager approve/reject, Staff nhận notification kết quả. |
| **Actor** | Hệ thống (trigger tự động) |
| **Điều kiện tiên quyết** | Có sự kiện apply open-shift |
| **Kết quả mong đợi** | - Staff apply → Manager nhận notification. <br> - Manager approve → Staff nhận "Bạn đã được gán ca ngày X". <br> - Manager reject → Staff nhận "Yêu cầu nhận ca ngày X bị từ chối". |
| **Mức ưu tiên** | **Should** |

---

## 3. Ma trận Phân quyền

| Chức năng | Manager | Staff |
|-----------|---------|-------|
| Tạo bài news (FR-NEWS-01) | ✅ | ❌ |
| Xem feed (FR-NEWS-02) | ✅ | ✅ |
| Xem chi tiết bài (FR-NEWS-03) | ✅ | ✅ |
| Sửa bài (FR-NEWS-04) | ✅ | ❌ |
| Xóa bài (FR-NEWS-05) | ✅ | ❌ |
| Xem seen tracking (FR-NEWS-06) | ✅ | ❌ |
| Xem notification (FR-NOTIF-01) | ✅ | ✅ |
| Mark as read (FR-NOTIF-02) | ✅ | ✅ |

---

## 4. Tổng hợp API Endpoints

| Method | Endpoint | Mô tả | Quyền | FR |
|--------|----------|-------|-------|-----|
| `GET` | `/api/news` | Danh sách bài viết | Authenticated | FR-NEWS-02 |
| `POST` | `/api/news` | Tạo bài mới | Manager | FR-NEWS-01 |
| `POST` | `/api/news/images` | Upload ảnh đính kèm (≤ 5MB, JPEG/PNG/WebP) | Manager | FR-NEWS-01, BR-NW-04 |
| `GET` | `/api/news/{id}` | Chi tiết bài | Authenticated | FR-NEWS-03 |
| `PUT` | `/api/news/{id}` | Sửa bài | Manager | FR-NEWS-04 |
| `DELETE` | `/api/news/{id}` | Xóa bài | Manager | FR-NEWS-05 |
| `POST` | `/api/news/{id}/read` | Mark as read | Authenticated | FR-NEWS-03 |
| `GET` | `/api/news/{id}/reads` | Danh sách seen | Manager | FR-NEWS-06 |
| `GET` | `/api/notifications` | Danh sách notification | Authenticated | FR-NOTIF-01 |
| `PUT` | `/api/notifications/{id}/read` | Mark 1 notification read | Authenticated | FR-NOTIF-02 |
| `PUT` | `/api/notifications/read-all` | Mark all read | Authenticated | FR-NOTIF-02 |

> **Đặc tả đầy đủ** (request/response body, mã lỗi, ví dụ): [docs/api/openapi.yaml](../api/openapi.yaml).
>
> WebSocket `WS /ws/notifications?token=` (FR-NOTIF-06) không nằm trong bảng trên vì
> OpenAPI 3.0 không mô tả được giao thức WebSocket — đã ghi trong phần mô tả của spec.
>
> Khi khai báo router FastAPI, đặt `/api/news/images` **trước** `/api/news/{id}` và
> `/api/notifications/read-all` **trước** `/api/notifications/{id}/read`, nếu không đường dẫn
> tĩnh sẽ bị route tham số nuốt mất và báo lỗi ép kiểu int.

---

## 5. Quy tắc Nghiệp vụ

| Mã | Quy tắc |
|----|---------|
| BR-NW-01 | Chỉ Manager mới tạo/sửa/xóa bài News. |
| BR-NW-02 | Bài News hiển thị theo thứ tự mới nhất trước. |
| BR-NW-03 | "Đã đọc" được ghi nhận khi Staff mở chi tiết bài, không phải khi scroll qua trên feed. |
| BR-NW-04 | Hình ảnh đính kèm tối đa 5MB/ảnh, tối đa 3 ảnh/bài. |
| BR-NW-05 | Notification tự động không cần Manager tạo thủ công — trigger bởi sự kiện hệ thống. |
| BR-NW-06 | Notification có `type` phân loại (10 giá trị — xem ENUM `notification_type` trong [erd.md](../erd.md) mục 4): `roster_published`, `shift_updated`, `shift_deleted`, `shift_applied`, `shift_apply_approved`, `shift_apply_rejected`, `exchange_request`, `exchange_approved`, `exchange_rejected`, `news_posted`. |
| BR-NW-07 | Notification có `reference_id` để navigate đến đúng context (bài news, ca làm, exchange). |
| BR-NW-08 | WebSocket là Should Have. Nếu không kịp triển khai → dùng polling 30s làm fallback, ghi nhận trong báo cáo phần "Hạn chế". |

---

## 6. Yêu cầu Phi chức năng

| Hạng mục | Yêu cầu |
|----------|---------|
| **Hiệu năng** | Feed load < 500ms. Notification list < 200ms. |
| **Upload ảnh** | Hỗ trợ JPEG, PNG, WebP. Resize server-side nếu quá lớn. Lưu vào local storage hoặc cloud (S3). |
| **WebSocket** | FastAPI native WebSocket. Mỗi user 1 connection. Auto-reconnect phía client. |
| **Fallback** | Polling interval 30s khi WebSocket không khả dụng. |
| **Mobile UX** | Feed dạng card dọc, ảnh responsive, font lớn dễ đọc. Notification dropdown thay vì trang riêng. |

---

*Tài liệu này phục vụ cho phần Phân tích yêu cầu (Chương 3.2) trong báo cáo đồ án.*
