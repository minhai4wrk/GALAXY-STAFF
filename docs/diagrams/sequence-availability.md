# SD-02 — Sequence Diagram: Đăng ký lịch rảnh (Availability Grid)

**Use Case**: UC-02 — Đăng ký lịch rảnh
**Actor chính**: Staff (Manager cũng dùng được — BR-AV-06)
**Tham chiếu**: [UC-02-availability.md](../requirements/UC-02-availability.md) · [module-availability.md](../requirements/module-availability.md) · [activity-availability.md](activity-availability.md)

> Ký pháp UML: **lifeline**, `->>` synchronous message, `-->>` return message,
> `alt/else` + **guard** `[...]` cho nhánh rẽ, `loop` cho hành vi lặp, `opt` cho fragment tùy chọn.
> Điểm nhấn của sơ đồ: **thao tác chọn slot diễn ra hoàn toàn ở client** (không gọi API từng ô),
> chỉ khi bấm Save mới gửi **một** request batch upsert duy nhất.

---

## 1. Sơ đồ chính (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor S as Staff
    participant PG as AvailabilityPage<br/>(Overlap + Grid)
    participant Q as TanStack Query<br/>+ axios
    participant RT as availabilities_router<br/>(FastAPI)
    participant SV as availability_service
    participant DB as PostgreSQL<br/>(availabilities)

    S->>PG: Mở tab "Lịch rảnh"
    PG->>Q: GET /api/availabilities/overview?week_start=YYYY-MM-DD
    Q->>RT: Authorization Bearer token
    RT->>SV: get_overview(week_start, location_id)
    SV->>DB: SELECT ... FROM availabilities a<br/>JOIN availability_submissions s ON a.submission_id = s.id<br/>WHERE s.week_start = :ws GROUP BY a.day_of_week, a.start_time
    DB-->>SV: Số người rảnh theo từng slot
    SV-->>RT: OverviewResponse
    RT-->>Q: 200 { data: matrix 7 ngày x 36 slot }
    Q-->>PG: Cache theo queryKey ["availabilities","overview",week_start]
    PG-->>S: Hiển thị Overlap View (ô càng đậm = càng nhiều người rảnh)

    PG->>PG: Tính deadline tuần (18h00 Thứ 7 — BR-AV-03)
    PG-->>S: Countdown "Hạn đăng ký: còn X ngày Y giờ"

    alt [đã qua deadline] — FR-AVAIL-08
        PG-->>S: Nút "Edit Availability" bị disable<br/>"Đã hết hạn đăng ký cho tuần này"
    else [chưa qua deadline]
        S->>PG: Bấm "Edit Availability"
        PG->>Q: GET /api/availabilities?week_start=YYYY-MM-DD
        Q->>RT: HTTP request
        RT->>SV: get_my_slots(current_user.id, week_start)
        SV->>DB: SELECT a.* FROM availabilities a<br/>JOIN availability_submissions s ON a.submission_id = s.id<br/>WHERE s.user_id = :uid AND s.week_start = :ws
        DB-->>SV: Danh sách slot đã đăng ký (có thể rỗng)
        SV-->>RT: list[AvailabilityOut]
        RT-->>Q: 200 { data: slots, total }
        Q-->>PG: slots
        PG-->>S: Mở grid 7 cột x 36 hàng, tô sẵn slot cũ

        loop Với mỗi ô người dùng bấm / kéo chọn
            S->>PG: Click hoặc drag chọn / bỏ chọn slot
            PG->>PG: Cập nhật local state (useState) — KHÔNG gọi API
            PG-->>S: Ô đổi màu ngay lập tức
        end

        S->>PG: Bấm "Save Availability"
        PG->>PG: Đếm số ngày có ít nhất 1 slot

        opt [số ngày dưới 5] — BR-AV-04 (cảnh báo, không chặn)
            PG-->>S: Popup "Bạn chỉ đăng ký N ngày, nhập lý do"
            S->>PG: Nhập lý do rồi bấm "Vẫn lưu"
        end

        PG->>PG: Gom slot liền kề thành khoảng (start_time, end_time)
        PG->>Q: POST /api/availabilities<br/>{ week_start, slots[], reason? }
        Q->>RT: HTTP request
        RT->>RT: Pydantic validate: day_of_week 0-6,<br/>end_time sau start_time, week_start là Thứ 6
        RT->>SV: batch_upsert(user_id, payload)
        SV->>SV: Kiểm tra lại deadline phía server (BR-AV-07)

        alt [server phát hiện đã qua deadline]
            SV-->>RT: DeadlinePassedError
            RT-->>Q: 400 { detail: "Đã qua deadline đăng ký cho tuần này" }
            Q-->>PG: AxiosError 400
            PG-->>S: Toast lỗi, reload lại trạng thái khóa
        else [payload không hợp lệ]
            RT-->>Q: 422 { detail: lỗi từng field }
            Q-->>PG: AxiosError 422
            PG-->>S: Highlight ô sai, hiện thông báo
        else [hợp lệ]
            Note over SV,DB: Toàn bộ nằm trong MỘT transaction<br/>để tránh mất dữ liệu khi lưu nửa vời
            SV->>DB: BEGIN
            SV->>DB: INSERT INTO availability_submissions (user_id, week_start, total_days, reason)<br/>ON CONFLICT (user_id, week_start) DO UPDATE ... RETURNING id
            DB-->>SV: submission_id
            SV->>DB: DELETE FROM availabilities WHERE submission_id = :sid
            SV->>DB: INSERT INTO availabilities (bulk)<br/>— EXCLUDE gist chặn khung giờ chồng nhau
            SV->>DB: COMMIT
            DB-->>SV: Danh sách slot vừa lưu
            SV-->>RT: list[AvailabilityOut]
            RT-->>Q: 201 { data: slots, total }
            Q->>Q: invalidateQueries(["availabilities"])
            Q-->>PG: Dữ liệu mới (kể cả Overlap View)
            PG-->>S: Toast "Đã lưu lịch rảnh" + quay về Overlap View
        end
    end
```

---

## 2. Sơ đồ phụ — Manager theo dõi tình hình đăng ký (FR-AVAIL-11)

```mermaid
sequenceDiagram
    autonumber
    actor M as Manager
    participant PG as AvailabilityStats
    participant Q as TanStack Query
    participant RT as availabilities_router
    participant SV as availability_service
    participant DB as PostgreSQL

    M->>PG: Mở tab "Thống kê đăng ký"
    PG->>Q: GET /api/availabilities/stats?week_start=YYYY-MM-DD
    Q->>RT: Bearer token
    RT->>RT: Depends(get_current_manager) — RBAC

    alt [role = staff]
        RT-->>Q: 403 { detail: "Không có quyền truy cập" }
        Q-->>PG: AxiosError 403
        PG-->>M: Trang báo lỗi quyền
    else [role = manager]
        RT->>SV: get_stats(week_start, location_id)
        SV->>DB: SELECT u.id, u.full_name, COUNT(DISTINCT a.day_of_week)<br/>FROM users u LEFT JOIN availabilities a ...
        DB-->>SV: Số ngày đã đăng ký của từng nhân viên
        SV->>SV: Phân loại: đã đăng ký đủ / dưới 5 ngày / chưa đăng ký
        SV-->>RT: StatsResponse
        RT-->>Q: 200 { data: stats }
        Q-->>PG: stats
        PG-->>M: Bảng "Đã đăng ký / Chưa đăng ký / dưới 5 ngày"
    end
```

---

## 3. Ánh xạ lifeline sang tầng kiến trúc

| Lifeline | Thành phần thực tế | Vị trí mã nguồn (dự kiến) |
|----------|--------------------|---------------------------|
| `PG` | Page + grid component | `frontend/src/pages/AvailabilityPage.tsx`, `components/AvailabilityGrid.tsx` |
| `Q` | Custom hook bọc TanStack Query + axios | `frontend/src/hooks/useAvailabilities.ts`, `services/availability.service.ts` |
| `RT` | FastAPI router | `backend/app/api/availabilities.py` |
| `SV` | Business logic: deadline, batch upsert, thống kê | `backend/app/services/availability_service.py` |
| `DB` | Bảng `availabilities` | `backend/app/models/availability.py` |

---

## 4. Phân tích luồng

### Luồng chính (Happy path)

| Bước | Message | Ghi chú |
|------|---------|---------|
| 1–9 | Load Overlap View | 1 query GROUP BY, không N+1 |
| 10–11 | Tính + hiển thị countdown deadline | FR-AVAIL-13, tính ở client theo BR-AV-03 |
| 13–21 | Mở grid, load slot cũ | Cho phép sửa thay vì nhập lại từ đầu |
| 22–24 | Vòng `loop` chọn slot | **Chỉ đổi local state** — điểm quan trọng về hiệu năng |
| 25–29 | Gom slot + gửi 1 request batch | Giảm 36×7 request tiềm năng xuống còn 1 |
| 30–40 | Validate 2 lớp, upsert trong transaction | Upsert `availability_submissions` (UNIQUE `user_id, week_start` enforce BR-AV-05) rồi delete-then-insert các khung giờ con; `reason` lưu ở bảng submission theo FR-AVAIL-07 |
| 41–43 | Invalidate cache | Overlap View tự cập nhật, không cần reload trang |

### Luồng ngoại lệ

| Ngoại lệ | Fragment | Xử lý |
|----------|----------|-------|
| Đã qua deadline khi mở trang | `alt [đã qua deadline]` | Disable nút Edit ngay ở UI |
| Deadline trôi qua **trong lúc** đang chỉnh sửa | `alt [server phát hiện...]` | Server trả 400 — UI không phải nguồn tin cậy duy nhất (BR-AV-07) |
| Đăng ký dưới 5 ngày | `opt [số ngày dưới 5]` | Cảnh báo + nhập lý do, **vẫn cho lưu** (BR-AV-04) |
| Payload sai định dạng | `alt [payload không hợp lệ]` | 422 kèm chi tiết từng field |
| Staff gọi API thống kê | Sơ đồ mục 2, nhánh 403 | `Depends(get_current_manager)` |

### Điểm đúng chuẩn UML

- Fragment `loop` bao quanh thao tác chọn ô, kèm message **tự gọi chính mình** (`PG->>PG`) — thể hiện rõ đây là xử lý nội bộ client, hoàn toàn không có message nào chạy sang backend trong vòng lặp.
- Hai lớp validate (Pydantic ở `RT`, nghiệp vụ ở `SV`) được vẽ thành **hai message riêng** thay vì gộp, phản ánh đúng nguyên tắc "router chỉ validate cấu trúc, service kiểm tra nghiệp vụ".
- **Note** đặt ngang `SV`–`DB` để khoanh vùng transaction — thứ mà bản thân chuỗi message không diễn tả được.
- Nhánh kiểm tra deadline xuất hiện **hai lần** (client và server) là có chủ ý, thể hiện nguyên tắc *never trust the client*.
- Việc `Q` (TanStack Query) là một lifeline độc lập cho thấy tầng cache nằm giữa UI và HTTP — giải thích được vì sao Overlap View tự làm mới sau khi lưu.

---

## 5. Xuất hình cho báo cáo

Xem [README.md](README.md). Khuyến nghị export **SVG** cho sơ đồ mục 1 (khá dài, PNG dễ mờ khi co vào Word).

---

*Tài liệu phục vụ Chương 3.4 (Sequence Diagram) trong báo cáo đồ án.*
