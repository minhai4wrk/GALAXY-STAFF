# SD-03 — Sequence Diagram: Auto-Schedule + Publish lịch

**Use Case**: UC-05 (Auto-Scheduling) + UC-06 (Publish Roster)
**Actor chính**: Manager · **Actor phụ**: Staff (nhận thông báo)
**Tham chiếu**: [UC-05-auto-schedule.md](../requirements/UC-05-auto-schedule.md) · [module-roster.md](../requirements/module-roster.md) · [activity-auto-schedule.md](activity-auto-schedule.md)

> Ký pháp UML: `loop` cho vòng lặp greedy, `alt/else` + guard `[...]` cho nhánh rẽ,
> `par` cho các message **xảy ra song song** (fan-out thông báo), `-->>` cho return message.
> Sơ đồ này là góc nhìn **tương tác giữa các đối tượng** của cùng thuật toán đã mô tả
> bằng Activity Diagram AD-02 — hai sơ đồ bổ sung cho nhau, không thay thế nhau.

---

## 1. Sơ đồ chính — Auto-Schedule (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor M as Manager
    participant PG as RosterPage<br/>(React)
    participant Q as TanStack Query<br/>+ axios
    participant RT as shifts_router<br/>(FastAPI)
    participant AS as auto_scheduler<br/>(service, greedy)
    participant DB as PostgreSQL<br/>(shifts, availabilities)

    M->>PG: Mở tab Roster, chọn tuần
    PG->>Q: GET /api/shifts?date=YYYY-MM-DD&view=week
    Q->>RT: Bearer token
    RT->>DB: SELECT * FROM shifts WHERE location_id AND date BETWEEN ...
    DB-->>RT: Danh sách ca (open + đã gán)
    RT-->>Q: 200 { data: shifts, total }
    Q-->>PG: shifts
    PG-->>M: Lưới Roster 7 ngày

    M->>PG: Bấm "Auto-Schedule"

    alt [không có Open-shift nào]
        PG-->>M: "Không có ca trống. Hãy tạo ca trước."
    else [có Open-shift]
        opt [chưa qua deadline đăng ký lịch rảnh]
            PG-->>M: Cảnh báo "Nhân viên vẫn có thể đổi lịch rảnh. Tiếp tục?"
        end
        PG-->>M: Popup "Sẽ phân công X ca cho Y nhân viên. Tiếp tục?"

        alt [Manager hủy]
            PG-->>M: Đóng popup, không gọi API
        else [Manager xác nhận]
            PG-->>M: Spinner "Đang xếp ca tự động..."
            PG->>Q: POST /api/shifts/auto-schedule { week_start }
            Q->>RT: HTTP request
            RT->>RT: Depends(get_current_manager) — RBAC
            RT->>AS: run(week_start, location_id)

            AS->>DB: SELECT * FROM shifts<br/>WHERE assigned_user_id IS NULL AND week_start = :ws AND NOT is_deleted
            DB-->>AS: open_shifts
            AS->>DB: SELECT a.* FROM availabilities a<br/>JOIN availability_submissions s ON a.submission_id = s.id<br/>JOIN users u ON u.id = s.user_id AND u.is_active<br/>WHERE s.week_start = :ws
            DB-->>AS: availabilities

            alt [không có nhân viên nào đăng ký lịch rảnh]
                AS-->>RT: NoAvailabilityError
                RT-->>Q: 400 { detail: "Chưa có NV đăng ký lịch rảnh" }
                Q-->>PG: AxiosError 400
                PG-->>M: Ẩn spinner, toast lỗi
            else [có dữ liệu lịch rảnh]
                AS->>DB: SELECT giờ đã gán + ngày liên tiếp của từng NV
                DB-->>AS: assigned_hours, streak
                AS->>AS: Sort open_shifts theo ưu tiên<br/>(ca tối trước chiều trước sáng, cuối tuần trước ngày thường)

                loop Với mỗi ca trong open_shifts (tuần tự — greedy)
                    AS->>AS: Lọc NV rảnh đúng khung giờ ca (C5)
                    AS->>AS: Loại NV vi phạm C1–C4<br/>(≤48h/tuần, nghỉ ≥8h, ≤6 ngày liên tiếp, không chồng giờ)
                    alt [còn NV đủ điều kiện]
                        AS->>AS: Chọn NV có ÍT GIỜ NHẤT, cập nhật bộ đếm giờ/ngày
                    else [không còn ai]
                        AS->>AS: Đưa ca vào danh sách unassigned
                    end
                end

                Note over AS,DB: Chỉ ghi DB MỘT LẦN sau khi thuật toán xong<br/>để giảm số round-trip và giữ tính nguyên vẹn
                AS->>DB: BEGIN
                AS->>DB: UPDATE shifts SET assigned_user_id, assigned_at = NOW(),<br/>assignment_source = 'auto', status = 'draft'<br/>WHERE id IN (đã gán)
                AS->>DB: UPDATE shifts SET unassigned_reason = :lý_do<br/>WHERE id IN (unassigned)
                AS->>DB: COMMIT
                DB-->>AS: OK
                AS-->>RT: { assigned, unassigned, warnings }
                RT-->>Q: 200 { data: { assigned, unassigned, warnings } }

                alt [phản hồi quá 30 giây]
                    Q-->>PG: Timeout
                    PG-->>M: "Mất nhiều thời gian hơn dự kiến. Thử lại."
                else [nhận kịp]
                    Q->>Q: invalidateQueries(["shifts"])
                    Q-->>PG: Kết quả xếp ca
                    PG-->>M: Hiện draft (viền nét đứt, badge "Auto")<br/>+ tổng kết "Đã gán X/Y ca, Z ca không đủ người"
                end
            end
        end
    end
```

---

## 2. Sơ đồ phụ — Publish lịch + fan-out thông báo (UC-06)

```mermaid
sequenceDiagram
    autonumber
    actor M as Manager
    actor S as Staff<br/>(nhiều người)
    participant PG as RosterPage
    participant Q as axios
    participant RT as shifts_router
    participant SV as shift_service
    participant NS as notification_service
    participant WS as WebSocket manager
    participant DB as PostgreSQL

    M->>PG: Review bản draft, bấm "Publish"
    PG-->>M: Popup "Lịch sẽ được gửi tới toàn bộ nhân viên. Xác nhận?"
    M->>PG: Xác nhận
    PG->>Q: POST /api/shifts/publish { week_start }
    Q->>RT: Bearer token
    RT->>RT: Depends(get_current_manager)
    RT->>SV: publish(week_start, location_id)
    SV->>DB: UPDATE shifts SET status = 'published', published_at = NOW()<br/>WHERE week_start = :ws AND status = 'draft'
    DB-->>SV: Số ca đã publish
    SV->>NS: notify_roster_published(user_ids, week_start)

    par Ghi thông báo vào CSDL
        NS->>DB: INSERT INTO notifications (bulk)<br/>type='roster_published', reference_date=:week_start, message<br/>— dùng reference_date vì publish không trỏ tới 1 ca cụ thể
        DB-->>NS: OK
    and Đẩy real-time cho người đang online
        NS->>WS: broadcast(user_ids, payload)
        WS-->>S: Toast "Lịch tuần mới đã được công bố" + badge chuông +1
    end

    NS-->>SV: Đã gửi N thông báo
    SV-->>RT: PublishResult
    RT-->>Q: 200 { data: { published_count } }
    Q-->>PG: Kết quả
    PG-->>M: Toast "Đã công bố lịch tuần" + ca đổi sang viền liền

    opt [Staff offline / WebSocket không khả dụng] — fallback BR-NW-08
        S->>Q: GET /api/notifications (polling 30 giây)
        Q->>RT: Bearer token
        RT->>DB: SELECT * FROM notifications WHERE user_id AND is_read = false
        DB-->>RT: Danh sách thông báo
        RT-->>Q: 200 { data: notifications, total }
        Q-->>S: Badge chuông cập nhật khi mở app
    end
```

---

## 3. Ánh xạ lifeline sang tầng kiến trúc

| Lifeline | Thành phần thực tế | Vị trí mã nguồn (dự kiến) |
|----------|--------------------|---------------------------|
| `PG` | Trang Roster + lưới ca | `frontend/src/pages/RosterPage.tsx` |
| `RT` | FastAPI router | `backend/app/api/shifts.py` |
| `AS` | Thuật toán greedy xếp ca | `backend/app/services/auto_scheduler.py` |
| `SV` | Nghiệp vụ ca làm (tạo/sửa/publish) | `backend/app/services/shift_service.py` |
| `NS` | Sinh + phát thông báo | `backend/app/services/notification_service.py` |
| `WS` | Quản lý kết nối WebSocket theo user | `backend/app/api/notifications.py` (WebSocket endpoint) |

---

## 4. Phân tích luồng

### Luồng chính (Happy path)

| Bước | Message | Ghi chú |
|------|---------|---------|
| 1–8 | Load Roster tuần | Index `shifts(location_id, date)` |
| 9–14 | Kiểm tra tiền điều kiện ở client + xác nhận | Tránh gọi API vô ích |
| 15–20 | `POST /api/shifts/auto-schedule`, nạp dữ liệu | 3 truy vấn đọc, nạp một lần vào bộ nhớ |
| 21–22 | Tính giờ đã gán + sắp xếp ca theo độ khó | Ca khó fill được xét trước |
| 23–28 | Vòng `loop` greedy | Độ phức tạp `O(S x N)` — S số ca, N số nhân viên |
| 29–33 | Ghi kết quả trong 1 transaction | Ca được gán chuyển sang `draft` |
| 34–39 | Trả kết quả, invalidate cache, hiện draft | Manager review trước khi publish |

### Vòng lặp Greedy (lõi thuật toán)

```
SORT open_shifts theo ưu tiên (ca khó fill trước)
FOR shift IN open_shifts:                       ← loop
    eligible = NV rảnh đúng khung giờ            ← C5
    eligible = loại NV vi phạm C1–C4
    IF eligible khác rỗng:
        gán NV ít giờ nhất, cập nhật bộ đếm
    ELSE:
        đưa shift vào unassigned
RETURN { assigned, unassigned, warnings }
```

| # | Constraint | Giá trị |
|---|-----------|---------|
| C1 | Số giờ tối đa mỗi tuần | 48h |
| C2 | Nghỉ tối thiểu giữa 2 ca | 8h |
| C3 | Số ngày liên tiếp tối đa | 6 ngày |
| C4 | Không chồng giờ | — |
| C5 | Phải đã đăng ký rảnh khung giờ đó | — |

### Luồng ngoại lệ

| Ngoại lệ | Fragment | Xử lý |
|----------|----------|-------|
| Không có Open-shift | `alt` ngoài cùng | Thông báo ở client, không gọi API |
| Chưa qua deadline đăng ký | `opt` | Cảnh báo nhưng vẫn cho chạy |
| Manager hủy ở popup | `alt [Manager hủy]` | Kết thúc, không gọi API |
| Không ai đăng ký lịch rảnh | `alt [không có nhân viên...]` | 400, toast lỗi |
| Một số ca không đủ người | `alt [không còn ai]` trong `loop` | Gom vào `unassigned` — **không phải lỗi**, báo trong tổng kết |
| Timeout > 30s | `alt [phản hồi quá 30 giây]` | Toast, Manager thử lại |
| Staff offline khi publish | `opt` ở sơ đồ mục 2 | Fallback polling 30s (BR-NW-08) |

### Điểm đúng chuẩn UML

- Toàn bộ thuật toán greedy nằm trong các **self-message** của `AS` (`AS->>AS`), thể hiện đây là tính toán **trong bộ nhớ**, không phải một chuỗi truy vấn CSDL trong vòng lặp — đây chính là lý do tránh được vấn đề N+1 query.
- Message ghi CSDL được đặt **sau** khối `loop` kèm Note giải thích, cho thấy quyết định thiết kế "tính xong mới ghi một lần".
- Fragment `par` ở sơ đồ mục 2 diễn tả đúng ngữ nghĩa fork/join của Activity Diagram AD-04: lưu thông báo vào CSDL và đẩy WebSocket là **hai việc song song**, không phụ thuộc nhau.
- Lifeline `S` (Staff) trong sơ đồ mục 2 **không do Manager gọi trực tiếp** mà nhận message từ `WS` — thể hiện đúng bản chất push của WebSocket.
- Nhánh `opt` polling ở cuối cho thấy cơ chế graceful degradation (NFR-REL-05) mà vẫn giữ cùng một API `GET /api/notifications`.

---

## 5. Xuất hình cho báo cáo

Xem [README.md](README.md). Sơ đồ mục 1 khá dài — nên export **SVG**, hoặc khi chèn vào Word thì đặt ở **trang ngang (landscape)** cho dễ đọc.

---

*Tài liệu phục vụ Chương 3.4 (Sequence Diagram) và mô tả thuật toán (Chương 3.6) trong báo cáo đồ án.*
