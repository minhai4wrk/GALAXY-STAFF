# Đặc tả tương tác — Lưới đăng ký lịch rảnh (Availability Grid)

**Phục vụ**: FR-AVAIL-02 → FR-AVAIL-06 · Sprint 3 (S3-05 → S3-09)
**Vì sao cần tài liệu này**: kéo-thả là hạng mục UX khó nhất dự án và cũng là điểm nhấn khi demo.
Không chốt trước state machine thì lúc code sẽ mò, và mò kiểu này rất dễ ra một lưới "gần đúng" —
tô được nhưng kéo ngược thì sai, trên điện thoại thì cuộn trang loạn.

---

## 1. Hình học của lưới

| Thông số | Giá trị | Nguồn |
|----------|---------|-------|
| Số cột | 7 ngày, **Thứ 6 → Thứ 5** | BR-AV-01 |
| Số hàng | **36 ô**, mỗi ô 30 phút, từ 08:00 đến 02:00 hôm sau | BR-AV-02 |
| Tổng số ô | 252 | — |
| Chỉ số ô | `slot_index` 0 = 08:00–08:30 … 35 = 01:30–02:00 | — |
| Chỉ số ngày | `day_of_week` 0 = Thứ 6 … 6 = Thứ 5 | ERD |

**Quy đổi giữa ô và giờ**

```
slot_index -> giờ bắt đầu:  op_minute = slot_index * 30      (0 -> 08:00, 20 -> 18:00, 35 -> 01:30)
giờ -> slot_index:          slot_index = op_minute(t) / 30
```

`op_minute` là số phút tính từ 08:00 — trùng đúng khái niệm hàm SQL cùng tên ở backend.
Dùng chung một hệ quy chiếu cho cả hai tầng để không phải dịch qua lại.

> ⚠️ Ô cuối cùng kết thúc lúc **02:00**, không phải 02:30. Vòng lặp dựng lưới chạy
> `slot_index` từ 0 đến 35, và nhãn giờ kết thúc của ô cuối là `(35 + 1) * 30 = 1080` → 02:00.

---

## 2. Mô hình trạng thái phía client

```ts
// Lưu dạng Set các ô đang chọn, key = `${day_of_week}-${slot_index}`
type CellKey = `${number}-${number}`;

interface GridState {
  selected: Set<CellKey>;      // trạng thái đã chốt
  preview: Set<CellKey>;       // trạng thái tạm trong lúc kéo, chưa gộp vào selected
  drag: DragSession | null;
}

interface DragSession {
  mode: "paint" | "erase";     // quyết định NGAY ở ô đầu tiên, không đổi giữa chừng
  anchor: { day: number; slot: number };   // ô bắt đầu kéo
  current: { day: number; slot: number };  // ô con trỏ đang ở
}
```

**Vì sao tách `preview` khỏi `selected`**: người dùng kéo qua 20 ô rồi kéo ngược lại 10 ô. Nếu ghi
thẳng vào `selected` thì 10 ô kia đã bị đổi trạng thái và không hoàn tác được. Có `preview` thì
mỗi lần con trỏ di chuyển chỉ cần tính lại hình chữ nhật từ `anchor` đến `current`, `selected`
hoàn toàn không bị đụng cho tới khi thả chuột.

---

## 3. Máy trạng thái

```
        ┌──────────────────────────────────────────────┐
        │                    IDLE                      │
        └───────┬──────────────────────────────────────┘
                │ pointerdown trên ô (d, s)
                ▼
        mode = selected.has(d-s) ? "erase" : "paint"      ◄── quyết định MỘT LẦN
        anchor = current = (d, s)
        bắt pointer capture
                │
                ▼
        ┌──────────────────────────────────────────────┐
        │                  DRAGGING                    │
        │  pointermove -> current = ô dưới con trỏ      │
        │                 preview = hình chữ nhật       │
        │                           anchor..current     │
        └───────┬──────────────────────────────┬───────┘
                │ pointerup / pointercancel     │ phím Esc
                ▼                               ▼
        áp preview vào selected            huỷ preview
        theo `mode`                        selected giữ nguyên
                │                               │
                └───────────────┬───────────────┘
                                ▼
                              IDLE
```

### Quy tắc chốt

| # | Quy tắc | Lý do |
|---|---------|-------|
| R1 | `mode` quyết định tại ô **đầu tiên** và giữ nguyên suốt phiên kéo | Nếu tính lại theo từng ô, kéo qua vùng lẫn lộn sẽ nhấp nháy tô–xóa loạn xạ |
| R2 | Vùng ảnh hưởng là **hình chữ nhật** giữa `anchor` và `current`, không phải đường đi của con trỏ | Kéo nhanh làm sự kiện `pointermove` bị nhảy cóc, đi theo vệt sẽ bỏ sót ô ở giữa |
| R3 | Kéo được theo **cả hai chiều** (lên/xuống, trái/phải) | `anchor` không nhất thiết ở góc trên trái; luôn chuẩn hóa `min`/`max` trước khi duyệt |
| R4 | Thả chuột ngoài lưới vẫn kết thúc phiên kéo bình thường | Dùng `setPointerCapture` để không mất sự kiện `pointerup` |
| R5 | `Esc` giữa chừng thì huỷ toàn bộ preview | Lối thoát cho thao tác lỡ tay |
| R6 | Sau deadline: lưới chuyển sang **chỉ đọc**, không gắn handler | BR-AV-07 bắt enforce ở cả giao diện lẫn API |

### Chuẩn hóa hình chữ nhật

```ts
const dayFrom = Math.min(anchor.day, current.day);
const dayTo   = Math.max(anchor.day, current.day);
const slotFrom = Math.min(anchor.slot, current.slot);
const slotTo   = Math.max(anchor.slot, current.slot);
// duyệt d in [dayFrom..dayTo], s in [slotFrom..slotTo]
```

---

## 4. Sự kiện dùng Pointer Events, không dùng mouse/touch riêng

Dùng **một bộ** `pointerdown` / `pointermove` / `pointerup`, vì Pointer Events gộp chung chuột,
cảm ứng và bút. Viết hai nhánh `mouse*` và `touch*` riêng sẽ phải xử lý chuyện trình duyệt tự sinh
sự kiện chuột giả sau khi chạm — nguồn của lỗi "chạm một cái mà tô hai lần".

| Sự kiện | Xử lý |
|---------|-------|
| `pointerdown` | `e.currentTarget.setPointerCapture(e.pointerId)`, khởi tạo `DragSession`, `e.preventDefault()` |
| `pointermove` | Chỉ xử lý khi `drag !== null`. Lấy ô dưới con trỏ, cập nhật `current`, tính lại `preview` |
| `pointerup` | Áp `preview` vào `selected`, xoá `drag` |
| `pointercancel` | Xử lý y hệt `pointerup` (hệ điều hành có thể cướp pointer khi có cuộc gọi đến) |

**Trên thiết bị cảm ứng**: đặt `touch-action: none` cho vùng lưới, nếu không trình duyệt sẽ hiểu
thao tác kéo là cuộn trang và không gửi `pointermove`. Đặt `touch-action` **chỉ trên lưới**, để
người dùng vẫn cuộn được phần còn lại của trang.

Thêm class `no-select` (đã có trong `index.css`) để kéo chuột không bôi đen văn bản.

### Lấy ô dưới con trỏ

Không gắn handler `pointermove` lên từng ô trong 252 ô. Thay vào đó gắn **một** handler ở lưới cha
rồi tra ô qua `document.elementFromPoint(e.clientX, e.clientY)` và đọc `data-day` / `data-slot`:

```tsx
<div
  className="no-select grid"
  style={{ touchAction: "none" }}
  onPointerDown={handleDown}
  onPointerMove={handleMove}
  onPointerUp={handleUp}
>
  {cells.map((c) => (
    <div key={`${c.day}-${c.slot}`} data-day={c.day} data-slot={c.slot} />
  ))}
</div>
```

Lý do: 252 listener × 3 loại sự kiện là quá nhiều cho một thao tác kéo liên tục, và trên cảm ứng
thì `pointermove` **luôn** bắn về phần tử nhận `pointerdown` chứ không bắn về phần tử đang bị chạm —
nghĩa là handler gắn trên từng ô sẽ không bao giờ chạy khi kéo trên điện thoại.

---

## 5. Template-shift (FR-AVAIL-04)

Bốn mẫu ca, nhấn vào tiêu đề cột ngày để áp cho ngày đó:

| Mẫu | Khung giờ | slot_index |
|-----|-----------|-----------|
| Ca sáng | 08:00 – 13:00 | 0 – 9 |
| Ca chiều | 13:00 – 18:00 | 10 – 19 |
| Ca tối | 18:00 – 02:00 | 20 – 35 |
| Cả ngày | 08:00 – 02:00 | 0 – 35 |

Hành vi: **hợp nhất** (union) chứ không thay thế. Áp "Ca sáng" rồi áp tiếp "Ca tối" cho cùng một
ngày thì được cả hai khoảng, không mất khoảng trước. Muốn xoá thì kéo ngược hoặc dùng nút "Xoá ngày".

> Đây là chỗ tài liệu yêu cầu gốc nói *"template sẽ ghi đè lên"*. Chọn hợp nhất vì ghi đè khiến
> thao tác phổ biến nhất — đăng ký cả ca sáng lẫn ca tối trong một ngày — trở nên bất khả thi bằng
> template. **Ghi nhận đây là thay đổi có chủ ý so với FR-AVAIL-04.**

---

## 6. Gộp ô thành khung giờ khi lưu (FR-AVAIL-06)

API nhận danh sách khung giờ `{day_of_week, start_time, end_time}`, không nhận danh sách ô. Trước khi
gửi phải gộp các ô liền nhau trong cùng một ngày thành một khoảng:

```
Với mỗi day_of_week:
  1. Lấy các slot_index đã chọn, sắp tăng dần
  2. Duyệt tuần tự, gộp các số liên tiếp thành đoạn [from..to]
  3. Mỗi đoạn -> { start_time: slot_to_time(from), end_time: slot_to_time(to + 1) }
```

Ví dụ ngày Thứ 6 chọn các ô `0,1,2,3, 20,21,22` cho ra hai khung: `08:00–10:00` và `18:00–19:30`.

**Bắt buộc phải gộp**, không được gửi 252 khung giờ rời rạc: ràng buộc `EXCLUDE` ở database sẽ từ
chối ngay hai khung liền kề nếu chúng chồng lấn, và quan trọng hơn — Overlap View đếm theo khung
giờ nên dữ liệu vụn sẽ làm truy vấn tổng hợp nặng lên vô ích.

Hàm quy đổi ngược:

```ts
function slotToTime(slotIndex: number): string {
  const totalMinutes = 8 * 60 + slotIndex * 30;   // 08:00 là mốc 0
  const hh = Math.floor(totalMinutes / 60) % 24;  // % 24 xử lý phần qua nửa đêm
  const mm = totalMinutes % 60;
  return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}
// slotToTime(0)  -> "08:00"
// slotToTime(20) -> "18:00"
// slotToTime(36) -> "02:00"   (giờ kết thúc của ô cuối)
```

---

## 7. Đếm ngày và cảnh báo dưới 5 ngày (FR-AVAIL-07)

```
total_days = số day_of_week có ÍT NHẤT MỘT ô được chọn
```

Đếm theo **ngày**, không theo số ô hay số giờ: đăng ký 30 phút vẫn tính là một ngày có đăng ký.

Khi bấm Lưu mà `total_days < 5`: hiện hộp thoại có ô nhập lý do, hai nút **"Gửi kèm lý do"** và
**"Bỏ qua"**. Cả hai đều lưu được — đây là cảnh báo, không phải chặn. Lý do nhập vào đi kèm trong
trường `reason` của request.

---

## 8. Trạng thái hiển thị của một ô

| Trạng thái | Giao diện | Ghi chú |
|-----------|-----------|---------|
| Trống | Nền trắng, viền xám nhạt | — |
| Đã chọn | Nền `primary`, chữ trắng | — |
| Preview tô | Nền `primary` mờ 60% | Chưa chốt, đang kéo |
| Preview xoá | Nền trắng viền đứt nét | Chưa chốt, đang kéo |
| Chỉ đọc (sau deadline) | Nền xám, `cursor: not-allowed` | Không gắn handler |

Mốc giờ tròn (mỗi 2 ô) kẻ đường ngang đậm hơn để mắt dễ định vị. Nhãn giờ chỉ hiện ở mốc tròn để
tránh chữ chồng nhau.

---

## 9. Đáp ứng trên điện thoại

Lưới 7 cột × 36 hàng không vừa màn hình dọc. Cách xử lý:

- **Cuộn ngang** cả lưới, cột nhãn giờ `position: sticky; left: 0` để luôn biết đang ở khung giờ nào.
- Ô cao tối thiểu **32px** để chạm chính xác; vùng chạm hiệu dụng đạt chuẩn 44px nhờ padding.
- Ưu tiên nút **(+)** ở đầu mỗi cột (FR-AVAIL-05) thay cho kéo-thả: mở form chọn giờ bắt đầu/kết thúc.
  Trên màn hình hẹp, nhập tay nhanh và chính xác hơn kéo-thả — kéo-thả giữ cho desktop.

---

## 10. Danh sách kiểm tra khi hiện thực hóa

- [ ] Kéo xuôi và kéo ngược đều đúng (R3)
- [ ] Kéo nhanh không bỏ sót ô ở giữa (R2)
- [ ] Bắt đầu kéo từ ô đã chọn thì vào chế độ xoá, và giữ chế độ đó suốt phiên (R1)
- [ ] Thả chuột bên ngoài lưới vẫn kết thúc sạch sẽ (R4)
- [ ] Trên điện thoại: kéo trong lưới không làm cuộn trang, kéo ngoài lưới vẫn cuộn được
- [ ] Ô cuối cùng hiển thị 01:30–**02:00**, không phải 02:30
- [ ] Gộp ô liền nhau đúng trước khi gửi lên API
- [ ] Sau deadline lưới chuyển chỉ đọc và API cũng từ chối
- [ ] Chọn dưới 5 ngày thì hiện hộp thoại nhập lý do, cả hai nút đều lưu được
- [ ] Đăng ký ca tối `18:00 → 02:00` lưu và tải lại đúng nguyên trạng
