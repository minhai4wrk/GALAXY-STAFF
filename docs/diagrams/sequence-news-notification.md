# SD-05 — Sequence Diagram: Đăng thông báo nội bộ + Notification real-time

**Use Case**: UC-11 (Tạo bài thông báo) + UC-12 (Xem News Feed / Seen tracking) + FR-NOTIF-06
**Actor**: Manager (đăng bài) · Staff (đọc bài, nhận thông báo)
**Tham chiếu**: [module-news.md](../requirements/module-news.md) · [activity-news-post.md](activity-news-post.md)

> Ký pháp UML: `par` cho fan-out **song song** (ghi CSDL + push WebSocket),
> `alt/else` + guard `[...]`, `opt` cho fragment tùy chọn, `loop` cho polling fallback.
> Điểm nhấn: cơ chế **WebSocket push + fallback polling 30s** (BR-NW-08, NFR-REL-05)
> và **Seen tracking** chỉ ghi nhận khi Staff mở chi tiết bài (BR-NW-03).

---

## 1. Sơ đồ chính — Manager đăng bài + Staff nhận thông báo (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor M as Manager
    actor S as Staff<br/>(đang online)
    participant FM as NewsForm<br/>(React)
    participant RT as news_router<br/>(FastAPI)
    participant NV as news_service
    participant NS as notification_service
    participant WS as WebSocket manager
    participant DB as PostgreSQL

    Note over S,WS: Staff đã đăng nhập, client mở kết nối WebSocket sẵn
    S->>WS: WS CONNECT /ws/notifications?token=...
    WS->>WS: Xác thực token, lưu connection theo user_id
    WS-->>S: Connected

    M->>FM: Bấm "Tạo thông báo mới"
    FM-->>M: Form: tiêu đề, nội dung, ảnh (tùy chọn)
    M->>FM: Nhập nội dung, chọn ảnh, bấm "Đăng bài"
    FM->>FM: Validate client (React Hook Form + Zod)

    alt [thiếu tiêu đề hoặc nội dung]
        FM-->>M: Inline error, KHÔNG gọi API
    else [ảnh > 5MB] — BR-NW-04
        FM-->>M: "Kích thước ảnh vượt quá giới hạn"
    else [hợp lệ]
        FM->>RT: POST /api/news { title, content, image }
        RT->>RT: Depends(get_current_manager) — RBAC (BR-NW-01)

        alt [role = staff]
            RT-->>FM: 403 { detail: "Không có quyền tạo thông báo" }
            FM-->>M: Trang lỗi quyền
        else [role = manager]
            RT->>NV: create(payload, author_id)

            NV->>DB: INSERT INTO news_posts (author_id, title, content)
            DB-->>NV: post row (id)

            opt [có ảnh đính kèm — tối đa 3, BR-NW-04]
                NV->>NV: Lưu file, sinh danh sách image_url
                NV->>DB: INSERT INTO news_images (post_id, image_url, sort_order)<br/>— CHECK sort_order 0-2 giới hạn cứng 3 ảnh
                DB-->>NV: OK
            end
            NV->>DB: SELECT id FROM users WHERE is_active AND location_id = :loc
            DB-->>NV: Danh sách user_id cần nhận thông báo
            NV->>NS: notify_news_posted(user_ids, post.id, post.title)

            par Ghi thông báo vào CSDL (bền vững)
                NS->>DB: INSERT INTO notifications (bulk)<br/>type='news_posted', reference_id=post.id
                DB-->>NS: OK
            and Đẩy real-time cho người đang online
                NS->>WS: broadcast(user_ids, payload)
                WS-->>S: Message { type: 'news_posted', post_id, message }
                S->>S: Badge chuông +1 + toast góc phải (dưới 2 giây)
            end

            NS-->>NV: Đã gửi N thông báo
            NV-->>RT: NewsOut
            RT-->>FM: 201 { data: post }
            FM-->>M: Toast "Đã đăng thông báo" + bài hiện đầu feed
        end
    end

    opt [WebSocket không khả dụng] — fallback BR-NW-08 / NFR-REL-05
        loop Mỗi 30 giây
            S->>RT: GET /api/notifications
            RT->>DB: SELECT * FROM notifications<br/>WHERE user_id = :uid ORDER BY created_at DESC
            DB-->>RT: Danh sách thông báo
            RT-->>S: 200 { data: notifications, total }
            S->>S: Cập nhật badge số chưa đọc
        end
    end
```

---

## 2. Sơ đồ phụ — Staff đọc bài + Seen tracking (UC-12, BR-NW-03)

```mermaid
sequenceDiagram
    autonumber
    actor S as Staff
    participant FD as NewsFeedPage
    participant DT as NewsDetailPage
    participant Q as TanStack Query
    participant RT as news_router
    participant DB as PostgreSQL<br/>(news_posts, news_reads)

    S->>FD: Mở tab "Bảng tin"
    FD->>Q: GET /api/news?page=1&limit=20
    Q->>RT: Bearer token
    RT->>DB: SELECT p.*, (r.id IS NOT NULL) AS is_read,<br/>(p.updated_at IS NOT NULL) AS is_edited, thumbnail từ news_images<br/>FROM news_posts p LEFT JOIN news_reads r ON r.post_id=p.id AND r.user_id=:uid<br/>WHERE NOT p.is_deleted ORDER BY p.created_at DESC
    DB-->>RT: Danh sách bài + cờ đã đọc
    RT-->>Q: 200 { data: posts, total }
    Q-->>FD: posts
    FD-->>S: Feed mới nhất trước, bài chưa đọc có badge "Mới"

    Note over S,FD: Scroll qua bài KHÔNG tính là đã đọc (BR-NW-03)

    S->>FD: Click vào một bài
    FD->>DT: Điều hướng /news/:id
    DT->>Q: GET /api/news/{id}
    Q->>RT: Bearer token
    RT->>DB: SELECT * FROM news_posts WHERE id = :id AND NOT is_deleted

    alt [bài đã bị xóa mềm]
        DB-->>RT: None
        RT-->>Q: 404 { detail: "Bài viết không tồn tại" }
        Q-->>DT: AxiosError 404
        DT-->>S: Trang "Không tìm thấy bài viết"
    else [bài còn tồn tại]
        DB-->>RT: post
        RT-->>Q: 200 { data: post }
        Q-->>DT: post
        DT-->>S: Hiển thị đầy đủ tiêu đề, nội dung, ảnh

        DT->>Q: POST /api/news/{id}/read
        Q->>RT: Bearer token
        RT->>DB: INSERT INTO news_reads (post_id, user_id)<br/>ON CONFLICT (post_id, user_id) DO NOTHING
        DB-->>RT: OK (idempotent nhờ UNIQUE)
        RT-->>Q: 200 { data: { read_at } }
        Q->>Q: invalidateQueries(["news"])
        Q-->>DT: Feed sẽ bỏ badge "Mới" ở lần render sau
    end

    opt [Staff mở từ thông báo] — FR-NOTIF-02
        S->>Q: PUT /api/notifications/{id}/read
        Q->>RT: Bearer token
        RT->>DB: UPDATE notifications SET is_read = true WHERE id AND user_id
        DB-->>RT: OK
        RT-->>Q: 200
        Q-->>S: Badge chuông giảm 1
    end
```

---

## 3. Sơ đồ phụ — Manager xem ai đã đọc (FR-NEWS-06)

```mermaid
sequenceDiagram
    autonumber
    actor M as Manager
    participant PG as NewsDetailPage<br/>(view Manager)
    participant RT as news_router
    participant DB as PostgreSQL

    M->>PG: Mở bài viết, bấm "Xem lượt đọc"
    PG->>RT: GET /api/news/{id}/reads
    RT->>RT: Depends(get_current_manager)
    RT->>DB: SELECT u.full_name, r.read_at<br/>FROM users u LEFT JOIN news_reads r<br/>ON r.user_id = u.id AND r.post_id = :id<br/>WHERE u.is_active
    DB-->>RT: Danh sách đã đọc + chưa đọc
    RT-->>PG: 200 { data: { read: [...], unread: [...] } }
    PG-->>M: Hai danh sách "Đã đọc (N)" / "Chưa đọc (M)"
```

---

## 4. Ánh xạ lifeline sang tầng kiến trúc

| Lifeline | Thành phần thực tế | Vị trí mã nguồn (dự kiến) |
|----------|--------------------|---------------------------|
| `FM` / `FD` / `DT` | Form tạo bài, feed, chi tiết bài | `frontend/src/pages/NewsFormPage.tsx`, `NewsFeedPage.tsx`, `NewsDetailPage.tsx` |
| `Q` | Hook TanStack Query + axios service | `frontend/src/hooks/useNews.ts`, `services/news.service.ts` |
| `RT` | FastAPI router (news + notifications) | `backend/app/api/news.py`, `backend/app/api/notifications.py` |
| `NV` | Nghiệp vụ bài viết (tạo/sửa/xóa mềm) | `backend/app/services/news_service.py` |
| `NS` | Sinh + phát thông báo | `backend/app/services/notification_service.py` |
| `WS` | Quản lý connection theo `user_id` | `backend/app/api/notifications.py` (WebSocket endpoint) |
| `DB` | `news_posts`, `news_reads`, `notifications` | `backend/app/models/news.py`, `notification.py` |

---

## 5. Phân tích luồng

### Luồng chính (Happy path)

| Bước | Message | Ghi chú |
|------|---------|---------|
| 1–3 | Staff mở kết nối WebSocket khi vào app | Xác thực bằng token trong query param |
| 4–8 | Manager nhập bài + validate client | Chặn ảnh > 5MB ngay ở client |
| 9–15 | `POST /api/news`, RBAC, lưu bài | Chỉ Manager (BR-NW-01) |
| 16–17 | Lấy danh sách người nhận | Chỉ user `is_active` cùng rạp |
| 18–22 | Fan-out `par`: ghi CSDL + push WebSocket | Ghi CSDL đảm bảo không mất thông báo khi offline |
| 23–25 | Trả 201, bài hiện đầu feed | Feed sắp xếp mới nhất trước (BR-NW-02) |

### Luồng ngoại lệ

| Ngoại lệ | Fragment | Xử lý |
|----------|----------|-------|
| Thiếu tiêu đề / nội dung | `alt` nhánh 1 | Inline error, không gọi API |
| Ảnh vượt 5MB | `alt` nhánh 2 | Thông báo giới hạn (BR-NW-04) |
| Staff gọi API tạo bài | `alt [role = staff]` | 403 nhờ `Depends(get_current_manager)` |
| WebSocket đứt / không khả dụng | `opt` + `loop` 30 giây | Fallback polling, chức năng không bị mất (NFR-REL-05) |
| Bài đã bị xóa mềm | `alt [bài đã bị xóa mềm]` | 404, không lộ nội dung |
| Staff mở lại bài đã đọc | `ON CONFLICT DO NOTHING` | Không tạo bản ghi trùng nhờ `UNIQUE(post_id, user_id)` |

### Điểm đúng chuẩn UML

- Khối `par` tương ứng trực tiếp với **fork/join** đã vẽ trong Activity Diagram AD-04: lưu thông báo vào CSDL và đẩy WebSocket là hai luồng độc lập. Việc vẫn ghi CSDL dù đã push real-time là **có chủ ý** — thông báo phải còn đó khi Staff offline lúc bài được đăng.
- Lifeline `WS` tách riêng khỏi `RT` vì WebSocket là **kênh truyền khác** với HTTP request/response: message từ `WS` sang `S` không có return message, thể hiện đúng bản chất **một chiều, do server chủ động push**.
- `loop` polling nằm trong `opt` chứ không nằm ở luồng chính — đúng ngữ nghĩa "chỉ dùng khi nhánh chính không khả dụng", không phải chạy song song với WebSocket.
- Seen tracking được vẽ thành **message riêng sau khi đã render nội dung** (`DT->>Q: POST .../read`), thể hiện chính xác BR-NW-03: ghi nhận khi mở chi tiết, không phải khi scroll qua feed.
- Truy vấn feed dùng `LEFT JOIN news_reads` trong **một** message — cho thấy cờ "đã đọc" được tính ngay trong truy vấn, tránh N+1 query khi feed có nhiều bài.
- Sơ đồ mục 3 dùng `LEFT JOIN` từ `users` để lấy được **cả danh sách chưa đọc** — điều mà truy vấn thẳng trên `news_reads` không làm được.

---

## 6. Xuất hình cho báo cáo

Xem [README.md](README.md).

> Ba sơ đồ ở trên nên chèn thành ba hình riêng trong báo cáo (đăng bài / đọc bài / thống kê lượt đọc),
> vì mỗi sơ đồ tương ứng một use case khác nhau.

---

*Tài liệu phục vụ Chương 3.4 (Sequence Diagram) trong báo cáo đồ án.*
