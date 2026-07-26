# USE CASE CHI TIẾT

## UC-05: Auto-Scheduling (Xếp ca tự động)

| Hạng mục | Thông tin |
|----------|-----------|
| **Use Case ID** | UC-05 |
| **Tên** | Auto-Scheduling — Xếp ca tự động |
| **Actor** | Manager |
| **Module** | Roster & Scheduling |
| **Mức ưu tiên** | Must Have |
| **Phiên bản** | 1.0 |
| **Ngày tạo** | 08/05/2026 |

---

## 1. Mô tả ngắn

Manager kích hoạt chức năng Auto-Schedule để hệ thống tự động phân công nhân viên vào các ca trống (Open-shift) dựa trên lịch rảnh đã đăng ký. Thuật toán greedy ưu tiên cân bằng giờ giữa các nhân viên, đảm bảo không vi phạm ràng buộc (max giờ/tuần, khoảng nghỉ giữa ca, ngày liên tiếp). Kết quả là bản nháp (draft) — Manager review, chỉnh sửa tay nếu cần, rồi mới publish.

---

## 2. Tiền điều kiện (Preconditions)

| # | Điều kiện |
|---|-----------|
| 1 | Manager đã đăng nhập (UC-01) |
| 2 | Đã qua deadline đăng ký lịch rảnh 18h Thứ 7 (lịch rảnh đã khóa) |
| 3 | Có ít nhất 1 Open-shift (ca trống) cần phân công cho tuần được chọn |
| 4 | Có ít nhất 1 Staff đã đăng ký lịch rảnh cho tuần đó |

---

## 3. Luồng chính (Main Flow)

| Bước | Actor | Hành động |
|------|-------|-----------|
| 1 | Manager | Mở tab **Roster** trên sidebar |
| 2 | Hệ thống | Hiển thị Roster view (ngày hoặc tuần) với dữ liệu hiện tại |
| 3 | Manager | Chọn tuần cần xếp ca (date picker hoặc nút Next/Previous) |
| 4 | Hệ thống | Load danh sách ca: hàng Open-shift (ca trống) + hàng nhân viên (ca đã gán nếu có) |
| 5 | Manager | Bấm nút **"Auto-Schedule"** trên toolbar |
| 6 | Hệ thống | Hiển thị popup xác nhận: "Hệ thống sẽ tự động phân công X ca trống cho Y nhân viên. Tiếp tục?" |
| 7 | Manager | Bấm **"Xác nhận"** |
| 8 | Hệ thống | Hiển thị loading spinner: "Đang xếp ca tự động..." |
| 9 | Hệ thống | Gửi request `POST /api/shifts/auto-schedule` với `{ week_start }` |
| 10 | Backend | Lấy danh sách Open-shift cho tuần đó |
| 11 | Backend | Lấy lịch rảnh (availabilities) của tất cả Staff active |
| 12 | Backend | Lấy ca đã gán (shifts assigned) để tính giờ đã làm |
| 13 | Backend | Chạy thuật toán Greedy (xem mục 8) |
| 14 | Backend | Trả về kết quả: `{ assigned_shifts, unassigned_shifts, warnings }` |
| 15 | Hệ thống | Ẩn spinner, hiển thị kết quả trên Roster dạng **draft** (màu khác biệt, ví dụ viền nét đứt) |
| 16 | Hệ thống | Hiển thị thông báo tổng kết: "Đã gán X/Y ca. Z ca không đủ người." |
| 17 | Manager | Review bản draft trên Roster |
| 18 | Manager | Nếu ưng ý → chuyển sang UC-06 (Publish). Nếu cần sửa → xem luồng phụ 4a |

---

## 4. Luồng phụ (Alternative Flows)

### 4a. Manager chỉnh tay sau auto-schedule

| Bước | Actor | Hành động |
|------|-------|-----------|
| 17a.1 | Manager | Nhìn draft, thấy ca cần điều chỉnh (ví dụ: muốn đổi nhân viên) |
| 17a.2 | Manager | **Chế độ ngày:** Kéo thanh ca từ hàng Staff A sang hàng Staff B |
| 17a.3 | Hệ thống | Kiểm tra xung đột: Staff B có rảnh không? Vượt max giờ không? |
| 17a.4 | Hệ thống | Không xung đột → cập nhật draft. Có xung đột → cảnh báo đỏ (FR-ROSTER-07) |
| 17a.5 | Manager | **Chế độ tuần:** Click vào card ca → mở form sửa → đổi nhân viên/giờ |
| 17a.6 | Manager | Hoặc xóa ca auto đã gán → ca quay về Open-shift |
| 17a.7 | | Lặp lại cho đến khi hài lòng → Publish (UC-06) |

### 4b. Chạy lại auto-schedule (reset)

| Bước | Actor | Hành động |
|------|-------|-----------|
| 17b.1 | Manager | Không hài lòng với kết quả → bấm **"Reset Auto-Schedule"** |
| 17b.2 | Hệ thống | Popup: "Hủy kết quả auto-schedule? Các ca đã gán tay trước đó sẽ giữ nguyên." |
| 17b.3 | Manager | Xác nhận |
| 17b.4 | Hệ thống | Xóa các ca auto-assigned (draft), giữ ca gán tay. Ca quay về Open-shift. |
| 17b.5 | Manager | Có thể bấm Auto-Schedule lại hoặc xếp tay toàn bộ |

### 4c. Auto-schedule một phần (có ca đã gán tay)

| Bước | Actor | Hành động |
|------|-------|-----------|
| c.1 | Manager | Trước khi bấm Auto-Schedule, đã tự tay gán một số ca (UC-04) |
| c.2 | Hệ thống | Auto-schedule chỉ xử lý các ca còn ở Open-shift |
| c.3 | Hệ thống | Tính giờ đã gán tay vào tổng giờ/tuần của nhân viên khi tính constraint |
| c.4 | | Kết quả: ca gán tay giữ nguyên + ca auto bổ sung |

---

## 5. Luồng ngoại lệ (Exception Flows)

### 5a. Không có Open-shift nào

| Bước | Actor | Hành động |
|------|-------|-----------|
| 5a.1 | Manager | Bấm Auto-Schedule nhưng hàng Open-shift trống |
| 5a.2 | Hệ thống | Hiển thị: "Không có ca trống cần phân công. Hãy tạo ca trước." |
| 5a.3 | | Không chạy thuật toán |

### 5b. Không có nhân viên đăng ký lịch rảnh

| Bước | Actor | Hành động |
|------|-------|-----------|
| 5b.1 | Backend | Lấy availabilities cho tuần → rỗng |
| 5b.2 | Hệ thống | Trả về lỗi: "Chưa có nhân viên nào đăng ký lịch rảnh cho tuần này." |
| 5b.3 | | Không chạy thuật toán |

### 5c. Một số ca không đủ người

| Bước | Actor | Hành động |
|------|-------|-----------|
| 13c.1 | Backend | Thuật toán không tìm được Staff đủ điều kiện cho một số ca |
| 13c.2 | Hệ thống | Các ca này giữ lại ở Open-shift, đánh dấu "Không đủ nhân viên" |
| 13c.3 | Hệ thống | Hiển thị warning: "Z ca không thể tự động gán do không đủ nhân viên rảnh" |
| 13c.4 | Manager | Có thể gán tay hoặc để trống (publish với Open-shift) |

### 5d. Timeout — thuật toán chạy quá lâu

| Bước | Actor | Hành động |
|------|-------|-----------|
| 9d.1 | Hệ thống | Request vượt quá 30 giây (timeout) |
| 9d.2 | Frontend | Hiển thị: "Xếp ca tự động mất nhiều thời gian hơn dự kiến. Vui lòng thử lại." |
| 9d.3 | | Lưu ý: theo NFR-PERF-02, mục tiêu là < 10 giây cho 100 NV × 300 ca |

### 5e. Chưa qua deadline đăng ký

| Bước | Actor | Hành động |
|------|-------|-----------|
| 5e.1 | Manager | Bấm Auto-Schedule khi chưa đến 18h Thứ 7 |
| 5e.2 | Hệ thống | Cảnh báo: "Nhân viên vẫn còn thể thay đổi lịch rảnh. Bạn có muốn tiếp tục?" |
| 5e.3 | Manager | "Tiếp tục" → chạy thuật toán với dữ liệu hiện tại. "Hủy" → quay lại. |

---

## 6. Hậu điều kiện (Postconditions)

### Sau auto-schedule thành công:
| # | Điều kiện |
|---|-----------|
| 1 | Các ca Open-shift đủ điều kiện được gán nhân viên dạng **draft** |
| 2 | Ca gán tay trước đó không bị thay đổi |
| 3 | Ca không đủ người vẫn ở Open-shift |
| 4 | Roster hiển thị draft (chưa publish — Staff chưa thấy) |
| 5 | Manager có thể sửa tay, reset, hoặc publish |

---

## 7. Yêu cầu chức năng liên quan

| FR | Tên | Vai trò trong UC-05 |
|----|-----|---------------------|
| FR-ROSTER-06 | Auto-Scheduling | Toàn bộ luồng chính |
| FR-ROSTER-07 | Cảnh báo xung đột | Kiểm tra constraint trong thuật toán + khi sửa tay |
| FR-ROSTER-03 | Tạo ca | Tiền điều kiện: phải có Open-shift |
| FR-ROSTER-04 | Sửa ca | Luồng phụ 4a: chỉnh tay sau auto |
| FR-ROSTER-08 | Publish Roster | Bước tiếp theo sau review (UC-06) |
| FR-AVAIL-01 | Overlap View | Dữ liệu input cho thuật toán |

---

## 8. Ghi chú kỹ thuật

### Thuật toán Greedy — Pseudocode

```
FUNCTION auto_schedule(week_start):
    INPUT:
        open_shifts = lấy tất cả ca ở hàng Open-shift của tuần
        availabilities = lấy lịch rảnh tất cả Staff active
        existing_shifts = lấy ca đã gán (tay hoặc auto trước đó)

    // Tính giờ đã gán cho mỗi Staff
    assigned_hours = {}
    FOR EACH shift IN existing_shifts:
        assigned_hours[shift.user_id] += shift.duration

    // Tính ngày liên tiếp đã làm
    consecutive_days = tính_ngày_liên_tiếp(existing_shifts)

    // Sort ca theo ưu tiên (khó fill trước)
    SORT open_shifts BY:
        1. Ca tối > Ca chiều > Ca sáng    // ca tối khó tìm người hơn
        2. Cuối tuần > Ngày thường         // cuối tuần ít người rảnh hơn

    assigned = []
    unassigned = []

    FOR EACH shift IN open_shifts:
        // Bước 1: Tìm Staff rảnh tại khung giờ này
        eligible = FILTER availabilities WHERE:
            - day_of_week == shift.day_of_week
            - start_time <= shift.start_time
            - end_time >= shift.end_time

        // Bước 2: Loại Staff vi phạm constraint
        eligible = FILTER eligible WHERE:
            - assigned_hours[staff] + shift.duration <= MAX_HOURS (48h)
            - khoảng_cách_ca_trước(staff, shift) >= MIN_REST (8h)
            - consecutive_days[staff] < MAX_CONSECUTIVE (6 ngày)
            - không có ca khác chồng giờ

        // Bước 3: Sort theo ít giờ nhất (cân bằng công bằng)
        SORT eligible BY assigned_hours[staff] ASC

        IF eligible is not empty:
            best_staff = eligible[0]
            GÁN shift → best_staff
            assigned_hours[best_staff] += shift.duration
            CẬP NHẬT consecutive_days[best_staff]
            assigned.append(shift)
        ELSE:
            unassigned.append(shift)

    RETURN { assigned, unassigned }
```

### Constraint Rules

| # | Constraint | Giá trị | Ghi chú |
|---|-----------|---------|---------|
| C1 | Max giờ/tuần | 48h | Theo luật lao động |
| C2 | Min nghỉ giữa 2 ca | 8h | Đảm bảo sức khỏe |
| C3 | Max ngày liên tiếp | 6 ngày | Phải có 1 ngày nghỉ/tuần |
| C4 | Không chồng giờ | — | 1 người không làm 2 ca cùng lúc |
| C5 | Phải rảnh | — | Chỉ gán vào khung giờ Staff đã đăng ký rảnh |

### Phân tích độ phức tạp

```
S = số ca trống (Open-shift)
N = số nhân viên (Staff)

Sorting: O(S log S)
Matching: O(S × N) cho mỗi ca duyệt danh sách Staff
Tổng: O(S × N)

Ước tính: S=300, N=100 → 30,000 phép so sánh → < 1 giây
```

### API Request/Response

**Request:**
```json
POST /api/shifts/auto-schedule
Authorization: Bearer <manager_token>
Content-Type: application/json

{
  "week_start": "2026-06-12"
}
```

**Response (200 OK):**
```json
{
  "assigned_shifts": [
    {
      "shift_id": 42,
      "date": "2026-06-12",
      "start_time": "18:00",
      "end_time": "23:00",
      "assigned_user_id": 7,
      "assigned_user_name": "Trần Thị B",
      "status": "draft"
    }
  ],
  "unassigned_shifts": [
    {
      "shift_id": 55,
      "date": "2026-06-14",
      "start_time": "08:00",
      "end_time": "13:00",
      "reason": "Không có nhân viên rảnh đủ điều kiện"
    }
  ],
  "summary": {
    "total_open": 45,
    "total_assigned": 41,
    "total_unassigned": 4,
    "execution_time_ms": 850
  },
  "warnings": [
    "Nguyễn Văn A đã gần tối đa 48h/tuần (44h)",
    "Ca tối Chủ Nhật (18h-2h) chỉ có 1 ứng viên"
  ]
}
```

---

## 9. Giao diện tham khảo

### Trước Auto-Schedule
- Roster view tuần: hàng Open-shift chứa nhiều ca xám
- Nút "Auto-Schedule" nổi bật trên toolbar (icon robot/magic wand)

[Hình 3.X: Roster trước khi chạy Auto-Schedule — CHỤP SAU]

### Sau Auto-Schedule (Draft)
- Ca được auto-gán hiển thị viền nét đứt hoặc màu khác (phân biệt với ca gán tay)
- Badge "Draft" hoặc "Auto" trên mỗi ca
- Panel tổng kết: "41/45 ca đã gán. 4 ca cần gán tay."
- Nút "Publish" và "Reset" hiện ra

[Hình 3.X: Roster sau khi chạy Auto-Schedule (draft) — CHỤP SAU]

### Warning Panel
- Sidebar hoặc toast hiện danh sách cảnh báo (ca không đủ người, NV gần max giờ)

[Hình 3.X: Panel cảnh báo sau Auto-Schedule — CHỤP SAU]

---

*Tài liệu này phục vụ cho phần phân tích Use Case chi tiết (Chương 3.2) và mô tả thuật toán Auto-Scheduling (Chương 3.6) trong báo cáo đồ án.*
