# USE CASE CHI TIẾT

## UC-02: Đăng ký lịch rảnh

| Hạng mục | Thông tin |
|----------|-----------|
| **Use Case ID** | UC-02 |
| **Tên** | Đăng ký lịch rảnh hàng tuần |
| **Actor** | Staff (Manager cũng có thể đăng ký) |
| **Module** | Availability |
| **Mức ưu tiên** | Must Have |
| **Phiên bản** | 1.0 |
| **Ngày tạo** | 08/05/2026 |

---

## 1. Mô tả ngắn

Nhân viên đăng ký các khung giờ rảnh trong tuần tới thông qua giao diện grid (tương tự When2Meet). Grid gồm 7 ngày (Thứ 6 → Thứ 5) × các ô 30 phút (8h00 – 2h00 sáng). Staff có thể dùng kéo-thả, template-shift hoặc nhập tay để chọn khung giờ. Dữ liệu được lưu lên hệ thống trước deadline 18h00 Thứ 7. Sau deadline, Manager sẽ dựa vào lịch rảnh này để xếp ca.

---

## 2. Tiền điều kiện (Preconditions)

| # | Điều kiện |
|---|-----------|
| 1 | Người dùng đã đăng nhập thành công (UC-01) |
| 2 | Chưa qua deadline 18h00 Thứ 7 của tuần đăng ký |
| 3 | Tuần đăng ký đã được hệ thống mở (tự động mở sau deadline tuần trước) |

---

## 3. Luồng chính — Đăng ký mới bằng kéo-thả (Main Flow)

| Bước | Actor | Hành động |
|------|-------|-----------|
| 1 | Staff | Mở tab **Availability** trên sidebar/navbar |
| 2 | Hệ thống | Hiển thị trang Overlap View — grid tổng hợp lịch rảnh toàn team |
| 3 | Hệ thống | Hiển thị countdown: "Hạn đăng ký: còn X ngày Y giờ" |
| 4 | Staff | Bấm nút **"Edit Availability"** |
| 5 | Hệ thống | Kiểm tra deadline: chưa qua 18h Thứ 7 → cho phép |
| 6 | Hệ thống | Mở grid trống 7 cột (Thứ 6 → Thứ 5) × 36 hàng (8h00 – 2h00, mỗi ô 30 phút). Nếu Staff đã đăng ký trước đó → load dữ liệu cũ lên grid |
| 7 | Staff | Nhấn giữ chuột tại ô bắt đầu (ví dụ: Thứ 6, 9h00) |
| 8 | Staff | Kéo chuột xuống/ngang qua các ô liên tiếp (ví dụ: đến 13h00) |
| 9 | Hệ thống | Các ô được kéo qua chuyển sang **màu xanh** (đánh dấu rảnh) |
| 10 | Staff | Thả chuột — các ô giữ nguyên trạng thái xanh |
| 11 | Staff | Lặp lại bước 7–10 cho các ngày/khung giờ khác |
| 12 | Staff | Bấm nút **"Save Availability"** |
| 13 | Hệ thống | Đếm số ngày có ít nhất 1 slot rảnh |
| 14 | Hệ thống | Kết quả ≥ 5 ngày → gửi request `POST /api/availabilities` (batch upsert) |
| 15 | Hệ thống | Lưu thành công → hiển thị toast "Đã lưu lịch rảnh thành công" |
| 16 | Hệ thống | Redirect về trang Overlap View — dữ liệu vừa lưu đã phản ánh trên grid tổng hợp |

---

## 4. Luồng phụ (Alternative Flows)

### 4a. Đăng ký bằng Template-shift

| Bước | Actor | Hành động |
|------|-------|-----------|
| 7a.1 | Staff | Thay vì kéo-thả từng ô, Staff nhìn vào thanh Template-shift bên cạnh grid |
| 7a.2 | Staff | Kéo template **"Ca sáng (8h–13h)"** thả vào cột Thứ 6 |
| 7a.3 | Hệ thống | Tự động tô xanh 10 ô (8h00–13h00) của Thứ 6 |
| 7a.4 | Staff | Kéo template **"Ca tối (18h–closed)"** thả vào cột Thứ 7 |
| 7a.5 | Hệ thống | Tự động tô xanh các ô 18h00–2h00 của Thứ 7 |
| 7a.6 | Staff | Kéo template **"Cả ngày (Full)"** vào Chủ Nhật |
| 7a.7 | Hệ thống | Tô toàn bộ ô trong ngày Chủ Nhật |
| 7a.8 | | Tiếp tục từ bước 12 (Save) |

**4 template có sẵn:**

| Template | Khung giờ | Số ô |
|----------|-----------|------|
| Ca sáng | 8h00 – 13h00 | 10 ô |
| Ca chiều | 13h00 – 18h00 | 10 ô |
| Ca tối | 18h00 – 2h00 (closed) | 16 ô |
| Cả ngày (Full) | 8h00 – 2h00 | 36 ô |

### 4b. Đăng ký bằng nút (+) — nhập tay

| Bước | Actor | Hành động |
|------|-------|-----------|
| 7b.1 | Staff | Bấm nút **(+)** trên cột ngày muốn đăng ký |
| 7b.2 | Hệ thống | Mở popup/form: "Giờ bắt đầu" (dropdown) + "Giờ kết thúc" (dropdown) |
| 7b.3 | Staff | Chọn giờ bắt đầu: 14h00, giờ kết thúc: 22h00 |
| 7b.4 | Staff | Bấm "Thêm" |
| 7b.5 | Hệ thống | Validate: `start_time < end_time`, trong khoảng 8h–2h → hợp lệ |
| 7b.6 | Hệ thống | Tô xanh các ô 14h00–22h00 trên grid |
| 7b.7 | | Tiếp tục từ bước 12 (Save) |

### 4c. Chỉnh sửa lịch đã đăng ký (trước deadline)

| Bước | Actor | Hành động |
|------|-------|-----------|
| 6c.1 | Hệ thống | Load dữ liệu đã lưu trước đó lên grid (ô xanh = đã đăng ký) |
| 6c.2 | Staff | Kéo chuột qua ô đã xanh → ô chuyển về **trống** (toggle xóa) |
| 6c.3 | Staff | Kéo-thả thêm ô mới hoặc dùng template |
| 6c.4 | Staff | Bấm Save → hệ thống ghi đè (upsert) dữ liệu mới |

### 4d. Xóa toàn bộ lịch đã chọn

| Bước | Actor | Hành động |
|------|-------|-----------|
| d.1 | Staff | Bấm nút **"Xóa tất cả"** trên toolbar grid |
| d.2 | Hệ thống | Popup: "Bạn có chắc muốn xóa toàn bộ lịch rảnh?" |
| d.3 | Staff | Xác nhận → grid trở về trống hoàn toàn |
| d.4 | | Staff có thể chọn lại từ đầu hoặc Save grid trống |

---

## 5. Luồng ngoại lệ (Exception Flows)

### 5a. Đã qua deadline

| Bước | Actor | Hành động |
|------|-------|-----------|
| 5a.1 | Hệ thống | Thời gian hiện tại > 18h00 Thứ 7 |
| 5a.2 | Hệ thống | Nút "Edit Availability" bị **disable** (xám) |
| 5a.3 | Hệ thống | Hiển thị: "Đã hết hạn đăng ký cho tuần này" |
| 5a.4 | | Nếu client cố gửi API → trả về 400: `"Đã qua deadline đăng ký"` |

### 5b. Đăng ký ít hơn 5 ngày

| Bước | Actor | Hành động |
|------|-------|-----------|
| 13b.1 | Hệ thống | Đếm số ngày có slot rảnh → kết quả < 5 |
| 13b.2 | Hệ thống | Hiển thị popup cảnh báo: "Bạn chỉ đăng ký X/5 ngày tối thiểu" |
| 13b.3 | Hệ thống | Hiện ô nhập: "Lý do đăng ký thiếu buổi (tùy chọn)" |
| 13b.4 | Staff | Nhập lý do (ví dụ: "Thi cuối kỳ") hoặc bấm "Bỏ qua" |
| 13b.5 | Hệ thống | Cả hai lựa chọn đều cho phép lưu (warning, không block) |
| 13b.6 | Hệ thống | Lưu lý do (nếu có) để Manager xem xét |

### 5c. Grid trống hoàn toàn khi Save

| Bước | Actor | Hành động |
|------|-------|-----------|
| 12c.1 | Staff | Bấm Save nhưng không có ô nào được chọn |
| 12c.2 | Hệ thống | Hiển thị cảnh báo: "Bạn chưa chọn khung giờ rảnh nào" |
| 12c.3 | | Không gửi request, giữ nguyên trang edit |

### 5d. Giờ bắt đầu ≥ giờ kết thúc (nhập tay)

| Bước | Actor | Hành động |
|------|-------|-----------|
| 7b.5d.1 | Hệ thống | Validate thất bại: `start_time >= end_time` |
| 7b.5d.2 | Hệ thống | Hiển thị lỗi: "Giờ kết thúc phải sau giờ bắt đầu" |
| 7b.5d.3 | | Không thêm vào grid, giữ nguyên form |

### 5e. Lỗi mạng khi Save

| Bước | Actor | Hành động |
|------|-------|-----------|
| 14e.1 | Frontend | Request timeout hoặc network error |
| 14e.2 | Frontend | Hiển thị: "Lưu thất bại. Vui lòng thử lại." |
| 14e.3 | | Giữ nguyên dữ liệu trên grid để Staff không mất công chọn lại |

---

## 6. Hậu điều kiện (Postconditions)

### Sau đăng ký thành công:
| # | Điều kiện |
|---|-----------|
| 1 | Dữ liệu lịch rảnh được lưu trong bảng `availabilities` |
| 2 | Overlap View cập nhật phản ánh dữ liệu mới |
| 3 | Manager có thể xem lịch rảnh của Staff này qua FR-AVAIL-10 |
| 4 | Staff có thể quay lại Edit để chỉnh sửa (nếu chưa qua deadline) |

### Sau deadline:
| # | Điều kiện |
|---|-----------|
| 1 | Lịch rảnh bị khóa, chỉ đọc |
| 2 | Manager bắt đầu xếp ca dựa trên dữ liệu này (UC-04, UC-05) |

---

## 7. Yêu cầu chức năng liên quan

| FR | Tên | Vai trò trong UC-02 |
|----|-----|---------------------|
| FR-AVAIL-01 | Overlap View | Trang chính trước khi vào Edit |
| FR-AVAIL-02 | Mở Edit Availability | Bước 4–6 luồng chính |
| FR-AVAIL-03 | Kéo-thả (Drag-to-select) | Bước 7–10 luồng chính |
| FR-AVAIL-04 | Template-shift | Luồng phụ 4a |
| FR-AVAIL-05 | Tạo shift bằng nút (+) | Luồng phụ 4b |
| FR-AVAIL-06 | Save Availability | Bước 12–16 luồng chính |
| FR-AVAIL-07 | Kiểm tra 5 ngày tối thiểu | Bước 13–14, ngoại lệ 5b |
| FR-AVAIL-08 | Deadline tự động khóa | Tiền điều kiện + ngoại lệ 5a |
| FR-AVAIL-09 | Xem lịch cá nhân | Load dữ liệu cũ (bước 6) |

---

## 8. Ghi chú kỹ thuật

### Cấu trúc Grid

```
Cột: 7 ngày (Thứ 6 → Thứ 5)
Hàng: 36 slot × 30 phút = 18 giờ/ngày
  - 8h00, 8h30, 9h00, ... 1h00, 1h30 (= 2h00 closed)
Tổng: 7 × 36 = 252 ô

Tuần rạp: Thứ 6 (ngày X) → Thứ 5 (ngày X+6)
```

### Database Schema liên quan

```sql
availabilities (
  id            SERIAL PRIMARY KEY,
  user_id       INT REFERENCES users(id),
  week_start    DATE NOT NULL,          -- Ngày Thứ 6 đầu tuần
  day_of_week   SMALLINT NOT NULL,      -- 0=Thứ 6, 1=Thứ 7, ..., 6=Thứ 5
  start_time    TIME NOT NULL,
  end_time      TIME NOT NULL,
  status        VARCHAR DEFAULT 'active',
  created_at    TIMESTAMP DEFAULT NOW(),

  UNIQUE(user_id, week_start, day_of_week, start_time)
)
```

### API Request/Response

**Save Availability (batch upsert):**
```json
POST /api/availabilities
Authorization: Bearer <token>
Content-Type: application/json

{
  "week_start": "2026-06-12",
  "slots": [
    { "day_of_week": 0, "start_time": "08:00", "end_time": "13:00" },
    { "day_of_week": 0, "start_time": "18:00", "end_time": "23:00" },
    { "day_of_week": 1, "start_time": "08:00", "end_time": "02:00" },
    { "day_of_week": 2, "start_time": "13:00", "end_time": "22:00" }
  ],
  "reason": "Thi cuối kỳ nên chỉ đăng ký 4 ngày"
}
```

**Response (200 OK):**
```json
{
  "message": "Đã lưu lịch rảnh thành công",
  "total_days": 4,
  "total_slots": 4,
  "warning": "Đăng ký ít hơn 5 ngày tối thiểu"
}
```

### Deadline Logic (Backend)

```python
from datetime import datetime, time

def is_before_deadline(week_start: date) -> bool:
    """Kiểm tra còn trước deadline 18h Thứ 7 không."""
    # Thứ 7 = ngày thứ 2 trong tuần rạp (week_start + 1 ngày)
    deadline_date = week_start + timedelta(days=1)  # Thứ 7
    deadline = datetime.combine(deadline_date, time(18, 0))
    return datetime.now() < deadline
```

---

## 9. Giao diện tham khảo

### Grid đăng ký lịch rảnh
- Grid 7 cột × 36 hàng, ô vuông nhỏ, hover highlight
- Thanh Template-shift bên trái hoặc trên grid
- Nút (+) góc trên mỗi cột ngày
- Nút "Save Availability" và "Xóa tất cả" ở dưới grid
- Countdown deadline góc trên phải

[Hình 3.X: Giao diện grid đăng ký lịch rảnh — CHỤP SAU]

### Overlap View
- Grid tương tự nhưng màu gradient (trắng → xanh đậm)
- Tooltip khi hover: danh sách tên nhân viên rảnh
- Nút "Edit Availability" nổi bật

[Hình 3.X: Giao diện Overlap View tổng hợp lịch rảnh — CHỤP SAU]

---

*Tài liệu này phục vụ cho phần phân tích Use Case chi tiết (Chương 3.2) trong báo cáo đồ án.*
