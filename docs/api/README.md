# Đặc tả API — Galaxy Staff

**File chính**: [openapi.yaml](openapi.yaml) — OpenAPI 3.0.3, **45 endpoint** trên 36 path.
Đã kiểm bằng `openapi-spec-validator`: hợp lệ, không có `$ref` hỏng, không có `operationId` trùng.

---

## 1. Cách xem

| Cách | Lệnh | Ghi chú |
|------|------|---------|
| Swagger UI qua Docker | `docker compose --profile tools up -d swagger-ui` → http://localhost:8081 | Dùng chụp hình cho báo cáo |
| Swagger Editor online | Mở https://editor.swagger.io → File → Import file | Không cần cài gì |
| VS Code | Extension *OpenAPI (Swagger) Editor* | Xem trực tiếp trong IDE |
| Redoc (bản in đẹp) | `npx @redocly/cli preview-docs docs/api/openapi.yaml` | Cần mạng lần đầu |

Sau khi backend chạy, FastAPI tự sinh spec runtime tại http://localhost:8000/docs.
**Hai spec phải khớp nhau** — file này là hợp đồng thiết kế, `/docs` là hiện thực. Lệch nhau
nghĩa là code đi chệch thiết kế (hoặc thiết kế cần sửa).

---

## 2. Quy ước áp dụng cho toàn bộ endpoint

| Hạng mục | Quy tắc |
|----------|---------|
| Response thành công | `{ "data": T }` hoặc `{ "data": [T], "total": n }` |
| Response lỗi | `{ "detail": "câu tiếng Việt hiển thị được cho người dùng" }` |
| Phân trang | `?page=1&size=20` — `page` bắt đầu từ 1, `size` tối đa 100 |
| Xác thực | `Authorization: Bearer <access_token>` |
| Thời điểm | Mọi `date-time` là **UTC**. Rạp ở UTC+7 → frontend tự quy đổi khi hiển thị |
| Xóa | `204 No Content`, không trả body |

> ⚠️ `module-auth.md` viết `?limit=` cho `GET /api/users`, còn `.claude/rules/api.md` quy định `?size=`.
> Spec dùng **`size`** cho thống nhất toàn hệ thống. Nên sửa lại `module-auth.md` cho khớp.

---

## 3. Ánh xạ endpoint → yêu cầu chức năng

### Auth (5)
| Method | Path | FR |
|--------|------|-----|
| POST | `/api/auth/login` | FR-AUTH-01 |
| POST | `/api/auth/refresh` | FR-AUTH-03 |
| GET | `/api/auth/me` | FR-AUTH-04 |
| PUT | `/api/auth/change-password` | FR-AUTH-05 |
| POST | `/api/auth/register` | FR-AUTH-06 |

> **Không có `POST /api/auth/logout`** — đúng theo SD-01 mục 3: JWT stateless, đăng xuất chỉ xóa
> token phía client, không gọi API. Đây là quyết định có chủ ý, không phải bỏ sót.

### Users (5)
| Method | Path | FR |
|--------|------|-----|
| GET | `/api/users` | FR-AUTH-07 |
| GET | `/api/users/{id}` | FR-AUTH-08 |
| PUT | `/api/users/{id}` | FR-AUTH-09 |
| PATCH | `/api/users/{id}/status` | FR-AUTH-10 |
| POST | `/api/users/{id}/reset-password` | FR-AUTH-11 |

### Availabilities (4)
| Method | Path | FR |
|--------|------|-----|
| GET | `/api/availabilities` | FR-AVAIL-09, FR-AVAIL-10 |
| POST | `/api/availabilities` | FR-AVAIL-06, FR-AVAIL-07, FR-AVAIL-08 |
| GET | `/api/availabilities/overview` | FR-AVAIL-01 |
| GET | `/api/availabilities/stats` | FR-AVAIL-11 |

### Shifts (9)
| Method | Path | FR |
|--------|------|-----|
| GET | `/api/shifts` | FR-ROSTER-01, 02, 10 |
| POST | `/api/shifts` | FR-ROSTER-03, 07 |
| GET | `/api/shifts/{id}` | FR-ROSTER-01 (bổ sung) |
| PUT | `/api/shifts/{id}` | FR-ROSTER-04 |
| DELETE | `/api/shifts/{id}` | FR-ROSTER-05 |
| POST | `/api/shifts/auto-schedule` | FR-ROSTER-06 |
| POST | `/api/shifts/auto-schedule/reset` | UC-05 4b (bổ sung) |
| POST | `/api/shifts/publish` | FR-ROSTER-08 |
| POST | `/api/shifts/{id}/apply` | FR-ROSTER-09 |

### Shift Applications (4 — toàn bộ là bổ sung)
| Method | Path | Vì sao cần |
|--------|------|-----------|
| GET | `/api/shift-applications` | Manager cần màn hình danh sách đơn chờ duyệt |
| PUT | `/api/shift-applications/{id}/approve` | FR-ROSTER-09 nói *"Manager approve"* nhưng không có endpoint |
| PUT | `/api/shift-applications/{id}/reject` | FR-ROSTER-09 nói *"Manager reject"* nhưng không có endpoint |
| DELETE | `/api/shift-applications/{id}` | ERD có `apply_status = cancelled` nhưng không đường nào tới trạng thái đó |

### Exchanges (6)
| Method | Path | FR |
|--------|------|-----|
| GET | `/api/exchanges` | FR-EXCHANGE-05, 06 |
| POST | `/api/exchanges` | FR-EXCHANGE-01 |
| DELETE | `/api/exchanges/{id}` | FR-EXCHANGE-01 (hủy pass) |
| POST | `/api/exchanges/{id}/take` | FR-EXCHANGE-02 |
| PUT | `/api/exchanges/{id}/approve` | FR-EXCHANGE-04 |
| PUT | `/api/exchanges/{id}/reject` | FR-EXCHANGE-04 |

### News (8)
| Method | Path | FR |
|--------|------|-----|
| GET | `/api/news` | FR-NEWS-02 |
| POST | `/api/news` | FR-NEWS-01 |
| POST | `/api/news/images` | BR-NW-04 (bổ sung) |
| GET | `/api/news/{id}` | FR-NEWS-03 |
| PUT | `/api/news/{id}` | FR-NEWS-04 |
| DELETE | `/api/news/{id}` | FR-NEWS-05 |
| POST | `/api/news/{id}/read` | FR-NEWS-03, BR-NW-03 |
| GET | `/api/news/{id}/reads` | FR-NEWS-06 |

### Notifications (3) + System (1)
| Method | Path | FR |
|--------|------|-----|
| GET | `/api/notifications` | FR-NOTIF-01 |
| PUT | `/api/notifications/{id}/read` | FR-NOTIF-02 |
| PUT | `/api/notifications/read-all` | FR-NOTIF-02 |
| GET | `/health` | NFR triển khai (bổ sung) |

**Không có trong OpenAPI**: `WS /ws/notifications?token=` (FR-NOTIF-06) — OpenAPI 3.0 không mô tả
được WebSocket. Đã ghi trong phần `description` của spec. Fallback là polling
`GET /api/notifications` mỗi 30 giây (BR-NW-08).

---

## 4. Lỗ hổng phát hiện khi viết spec

Viết đặc tả buộc phải trả lời câu hỏi *"client gọi cái gì để làm việc này?"* cho từng luồng,
nên lộ ra **8 chỗ tài liệu yêu cầu mô tả hành vi nhưng chưa có endpoint tương ứng**:

| # | Thiếu | Tài liệu đã hứa | Đã bổ sung |
|---|-------|-----------------|-----------|
| 1 | Duyệt đơn xin ca trống | FR-ROSTER-09: *"Manager approve: ca chuyển từ Open-shift xuống hàng của Staff"* · `notification_type.shift_apply_approved` đã tồn tại | `PUT /api/shift-applications/{id}/approve` |
| 2 | Từ chối đơn xin ca | FR-ROSTER-09 + `shift_apply_rejected` | `PUT /api/shift-applications/{id}/reject` |
| 3 | Xem danh sách đơn xin ca | Manager không có cách nào biết có đơn nào đang chờ | `GET /api/shift-applications` |
| 4 | Hủy đơn xin ca | ERD có `apply_status = cancelled` nhưng không API nào set được | `DELETE /api/shift-applications/{id}` |
| 5 | Reset Auto-Schedule | UC-05 4b: *"bấm Reset Auto-Schedule"* · cột `assignment_source` sinh ra chính vì việc này | `POST /api/shifts/auto-schedule/reset` |
| 6 | Upload ảnh bài viết | BR-NW-04: tối đa 3 ảnh, 5MB/ảnh · bảng `news_images` đã có | `POST /api/news/images` |
| 7 | Xem chi tiết một ca | FR-ROSTER-01: *"Click vào thanh ca → xem chi tiết"* · FR-ROSTER-10 cần danh sách đồng nghiệp cùng ca | `GET /api/shifts/{id}` |
| 8 | Healthcheck | Docker healthcheck + giám sát trên Render đều cần | `GET /health` |

**Bài học lặp lại lần thứ hai**: đợt audit ERD trước cũng tìm ra thiếu sót theo đúng cách này —
đi từ từng FR/BR rồi hỏi *"dữ liệu này lưu ở đâu?"*. Lần này đổi câu hỏi thành
*"client gọi API nào?"* và lại lòi ra 8 chỗ. Đọc xuôi tài liệu rồi đoán xem thiếu gì thì không
bao giờ phát hiện được.

> ✅ **Đã đồng bộ ngược vào tài liệu yêu cầu** (26/07/2026): bảng "Tổng hợp API Endpoints"
> của [module-roster.md](../requirements/module-roster.md) và
> [module-news.md](../requirements/module-news.md) đã có đủ 8 endpoint, ma trận phân quyền của
> module Roster đã thêm 3 dòng cho luồng duyệt đơn xin ca, và
> [non-functional.md](../requirements/non-functional.md) đã thêm NFR-DEPLOY-06 (healthcheck) +
> NFR-DEPLOY-07 (đặc tả OpenAPI) — tổng NFR từ 37 lên 39.

---

## 5. Ba quyết định thiết kế đáng chú ý

### 5.1. Trùng giờ khi nhận ca dùng cơ chế xác nhận hai bước
BR-EX-05 nói *"cảnh báo, cho phép tiếp tục"*. REST không có khái niệm "cảnh báo" — chỉ có thành
công hoặc lỗi. Cách giải: `POST /api/exchanges/{id}/take` lần đầu trả **409 kèm mô tả xung đột**;
frontend hiện popup; người dùng đồng ý thì gọi lại với `confirm_conflict = true`. Cùng logic này
áp dụng cho `override_reason` khi Manager xếp ca vi phạm ràng buộc.

### 5.2. `POST /api/news/{id}/read` tách khỏi `GET /api/news/{id}`
BR-NW-03 quy định *"đã đọc ghi nhận khi Staff mở chi tiết bài"*. Nếu gộp vào `GET` thì Manager
xem trước bài của chính mình cũng bị tính là đã đọc, và mọi lần prefetch của TanStack Query đều
làm sai số liệu. Tách riêng thì `GET` giữ đúng tính chất chỉ-đọc của HTTP.

### 5.3. Lưới Overlap View chỉ trả ô có người
7 ngày × 36 ô = 252 ô mỗi tuần. Trả đủ 252 ô kèm mảng `user_ids` rỗng làm payload phình vô ích;
NFR yêu cầu render dưới 1 giây cho 50 nhân viên. Ô vắng mặt trong `cells` nghĩa là không ai rảnh —
frontend mặc định tô trắng.

---

## 6. Khi bắt đầu code backend

Thứ tự theo `CLAUDE.md`: model → schema → router → đăng ký vào `main.py` → test.

Spec này là nguồn sự thật cho **schema Pydantic**: mỗi `components.schemas.X` tương ứng một class
trong `backend/app/schemas/`. Giữ nguyên tên trường để `/docs` do FastAPI sinh ra trùng khớp với
file này — lệch tên là dấu hiệu code đã đi chệch thiết kế.

**Lưu ý khi khai báo route trong FastAPI**: đăng ký đường dẫn tĩnh **trước** đường dẫn có tham số,
nếu không `/api/shifts/auto-schedule` sẽ bị `/api/shifts/{id}` nuốt mất và báo lỗi ép kiểu int.

```python
# Đúng thứ tự
@router.post("/auto-schedule")       # tĩnh - khai báo trước
@router.post("/auto-schedule/reset")
@router.post("/publish")
@router.get("/{id}")                 # có tham số - khai báo sau
```

Ba chỗ dính bẫy này: `/api/shifts/*`, `/api/notifications/read-all` (đứng trước `/{id}/read`),
`/api/news/images` (đứng trước `/{id}`).
