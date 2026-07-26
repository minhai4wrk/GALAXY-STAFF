# Diagrams — Galaxy Staff

Các sơ đồ UML phục vụ Chương 3 (Phân tích & Thiết kế hệ thống) của báo cáo đồ án.

## Công cụ

- **Mermaid** — text-based, render trực tiếp trong VS Code (extension *Markdown Preview Mermaid Support*).
- Nguồn diagram nằm trong code block ` ```mermaid ... ``` ` của từng file `.md`.
- PNG/SVG export đặt trong `out/` (dùng cho báo cáo `.docx`).

## Xuất ảnh cho báo cáo

```bash
bash docs/diagrams/export.sh
```

Xuất toàn bộ sơ đồ ra PNG (scale 3, nền trắng) và SVG vào `out/`. File có nhiều sơ đồ sẽ được
đánh số theo thứ tự xuất hiện, ví dụ `sequence-login-1.png`, `sequence-login-2.png`.

> ⚠️ **Ba ký tự làm mermaid chết**: `<`, `>` và `;`.
> Script tự chạy `check_mermaid.py` trước khi render nên sẽ dừng ngay và chỉ đúng dòng vi phạm.
> Chạy riêng bước kiểm tra: `python docs/diagrams/check_mermaid.py`
>
> Điểm khó chịu: **flowchart tha còn sequenceDiagram thì không**. Nên có thể xảy ra chuyện
> 4 activity diagram xuất ảnh bình thường trong khi các sequence diagram chết hàng loạt —
> và thông báo lỗi của cả hai trường hợp đều chỉ là `got 'INVALID'`.
> Thay bằng chữ (`trước`, `sau`, `quá`), ký hiệu `≤ ≥ →`, hoặc dấu phẩy thay cho `;`.

## Danh sách sơ đồ

### Use Case Diagrams

| File | Phạm vi |
|------|---------|
| [usecase-overview.md](usecase-overview.md) | Tổng quan toàn hệ thống — 2 actor × 13 use case |
| [usecase-auth.md](usecase-auth.md) | Module Authentication & User Management |
| [usecase-availability.md](usecase-availability.md) | Module Availability |
| [usecase-roster.md](usecase-roster.md) | Module Roster & Scheduling |
| [usecase-exchange.md](usecase-exchange.md) | Module Shift Exchange |
| [usecase-news.md](usecase-news.md) | Module News & Notification |

### Activity Diagrams

| File | Luồng |
|------|-------|
| [activity-availability.md](activity-availability.md) | Đăng ký lịch rảnh (UC-02) |
| [activity-auto-schedule.md](activity-auto-schedule.md) | Auto-Scheduling + Publish (UC-05 + UC-06) |
| [activity-shift-exchange.md](activity-shift-exchange.md) | Pass / Nhận / Duyệt ca — swimlane (UC-08+09+10) |
| [activity-news-post.md](activity-news-post.md) | Tạo thông báo nội bộ (UC-11) |

### Sequence Diagrams

| File | Luồng | Số sơ đồ |
|------|-------|----------|
| [sequence-login.md](sequence-login.md) | Đăng nhập / Refresh token / Đăng xuất (UC-01) | 3 |
| [sequence-availability.md](sequence-availability.md) | Đăng ký lịch rảnh + Thống kê đăng ký (UC-02) | 2 |
| [sequence-auto-schedule.md](sequence-auto-schedule.md) | Auto-Schedule + Publish lịch (UC-05 + UC-06) | 2 |
| [sequence-shift-exchange.md](sequence-shift-exchange.md) | Pass / Nhận / Duyệt ca + Optimistic locking (UC-08+09+10) | 2 |
| [sequence-news-notification.md](sequence-news-notification.md) | Đăng tin, Seen tracking, WebSocket notification (UC-11 + UC-12) | 3 |

## Quy ước phong cách

- Theme: `neutral` (đen / trắng / xám) — formal, không màu mè.
- Font: Segoe UI / Arial 14px.
- Notation UML: `<<include>>`, `<<extend>>` cho UCD; ●/◉/◇/▭ cho AD; lifeline + `alt`/`opt`/`loop`/`par` cho SD.
- Lifeline trong SD đặt theo **tầng kiến trúc**: Actor → Page (React) → axios/TanStack Query → Router (FastAPI) → Service → PostgreSQL.
- SD nên export **SVG** (hình rộng, PNG dễ mờ khi co lại trong Word).

## Render PNG cho báo cáo

```bash
# Cài 1 lần
npm i -g @mermaid-js/mermaid-cli

# Export tất cả diagram
mmdc -i usecase-overview.md -o out/usecase-overview.png -t neutral -b transparent --width 1600
```
