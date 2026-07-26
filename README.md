# Galaxy Staff — Hệ thống Quản lý Nhân sự Rạp Chiếu Phim

Ứng dụng web thay thế quy trình xếp ca thủ công bằng Google Sheets + Messenger tại rạp chiếu phim:
nhân viên đăng ký lịch rảnh trên lưới kéo-thả, quản lý xếp ca tự động bằng thuật toán, mọi thông báo
và trao đổi ca diễn ra trên cùng một nền tảng.

> Đồ án cá nhân cấp đại học · Hạn nộp 05/10/2026 · Kế hoạch chi tiết: [about-project/tracker.md](about-project/tracker.md)

---

## 1. Tính năng chính

| Module | Nội dung |
|--------|----------|
| **Xác thực & Phân quyền** | JWT (access 30 phút + refresh 7 ngày), bcrypt cost 12, RBAC hai vai trò Manager / Staff |
| **Đăng ký lịch rảnh** | Lưới 7 ngày × 36 ô 30 phút, kéo-thả tô khung giờ, 4 mẫu ca sẵn, tự khóa lúc 18h00 Thứ 7 |
| **Overlap View** | Bản đồ nhiệt tổng hợp lịch rảnh toàn team, hover ra danh sách ai rảnh ai bận |
| **Lịch làm việc** | Xem theo ngày/tuần, xếp ca, cảnh báo xung đột (48h/tuần, nghỉ 8h, chồng ca), công bố lịch |
| **Xếp ca tự động** | Thuật toán greedy có ràng buộc, cân bằng giờ giữa nhân viên, kết quả ở dạng nháp để duyệt lại |
| **Trao đổi ca** | Pass ca kèm lời nhắn, nhận ca, quản lý duyệt, chống tranh chấp khi nhiều người cùng nhận |
| **Bảng tin & Thông báo** | Thông báo nội bộ có ảnh, theo dõi ai đã đọc, thông báo real-time qua WebSocket |

---

## 2. Công nghệ

| Tầng | Công nghệ |
|------|-----------|
| Backend | Python 3.11 · FastAPI · SQLAlchemy 2.0 · Alembic · Pydantic v2 |
| Database | PostgreSQL 16 (extension `btree_gist`) |
| Frontend | React 18 · TypeScript (strict) · Vite · Tailwind CSS · shadcn/ui |
| State | Zustand (global) · TanStack Query (server state) |
| Auth | python-jose · passlib + bcrypt |
| Hạ tầng | Docker Compose (dev) · Render (production) |
| Kiểm thử | pytest + httpx (backend) · Vitest (frontend) |
| Lint | Ruff (backend) · ESLint + Prettier (frontend) |

---

## 3. Chạy dự án

### Yêu cầu
Docker Desktop (đã bật) và cổng `5432`, `8000`, `5173` còn trống.

### Ba bước

```bash
git clone https://github.com/minhai4wrk/GALAXY-STAFF.git
cd GALAXY-STAFF
cp .env.example .env          # Windows: copy .env.example .env

docker compose up -d db backend
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

Xong. Mở http://localhost:8000/docs để thử API.

### Tài khoản mẫu

| Vai trò | Email | Mật khẩu | Ghi chú |
|---------|-------|----------|---------|
| Manager | `manager@galaxy.vn` | `GalaxyStaff@123` | Toàn quyền |
| Staff | `staff01@galaxy.vn` | `GalaxyStaff@123` | Bị ép đổi mật khẩu khi đăng nhập lần đầu |
| Staff | `staff02@galaxy.vn` … `staff11@galaxy.vn` | `GalaxyStaff@123` | Dùng bình thường |
| Staff | `staff12@galaxy.vn` | — | Đang bị vô hiệu hóa, dùng để thử luồng tài khoản khóa |

Dữ liệu mẫu gồm 42 ca của 2 tuần (tuần hiện tại đã công bố, tuần sau còn nháp và có 5 ca trống),
lịch rảnh của cả 12 nhân viên và 3 bài thông báo.

### Bật thêm dịch vụ

```bash
docker compose --profile frontend up -d    # giao diện React  -> http://localhost:5173
docker compose --profile tools up -d       # Adminer :8080 · Swagger UI :8081
```

### Các lệnh hay dùng

```bash
docker compose logs -f backend                        # xem log
docker compose exec backend pytest app/tests -v       # chạy test
docker compose exec backend ruff check app/ --fix     # lint backend
docker compose exec backend python -m app.seed --reset # tạo lại dữ liệu mẫu
docker compose exec db psql -U galaxy -d galaxy_staff # vào database

docker compose exec backend alembic revision -m "mô tả"  # tạo migration mới
docker compose exec backend alembic downgrade -1         # lùi 1 bước

cd frontend && npm run dev      # chạy frontend ngoài Docker
cd frontend && npm run build    # build production
```

---

## 4. Cấu trúc thư mục

```
GALAXY_STAFF/
├── backend/
│   ├── app/
│   │   ├── api/          # Router theo module
│   │   ├── core/         # config · database · security · deps
│   │   ├── models/       # 11 SQLAlchemy model
│   │   ├── schemas/      # Pydantic request/response
│   │   ├── services/     # Nghiệp vụ (auto_scheduler, notification)
│   │   ├── tests/        # pytest
│   │   ├── seed.py       # Dữ liệu mẫu
│   │   └── main.py
│   └── alembic/versions/ # Migration
├── frontend/src/
│   ├── components/  pages/  hooks/  services/  stores/  types/  lib/
├── docker/postgres/init/ # Script khởi tạo database
├── docs/
│   ├── requirements/     # 55 yêu cầu chức năng · 39 phi chức năng · 14 use case
│   ├── diagrams/         # 6 use case · 4 activity · 12 sequence diagram
│   ├── api/              # openapi.yaml — 45 endpoint
│   ├── erd.md            # ERD 11 bảng + lý do từng quyết định thiết kế
│   └── git-workflow.md
└── about-project/        # Charter · kế hoạch triển khai
```

---

## 5. Ba quy ước dễ hiểu sai nhất

Đây là các quyết định thiết kế **cố ý**, không phải thiếu sót. Đọc kỹ trước khi sửa code liên quan.

### 5.1. Ca làm việc vắt qua nửa đêm là chuyện bình thường
Rạp mở 08:00 đến 02:00 sáng hôm sau. Bảng `shifts` vì thế dùng `start_at`/`end_at` kiểu
`TIMESTAMPTZ` chứ **không** tách thành `date + start_time + end_time` — nếu tách, ca 18h→2h sẽ có
giờ kết thúc nhỏ hơn giờ bắt đầu và mọi phép tính thời lượng, tổng giờ tuần, khoảng nghỉ đều sai.

Riêng `availabilities` vẫn dùng kiểu `TIME` vì lịch rảnh là mẫu lặp theo tuần, không gắn ngày cụ thể.
Ở đó `end_time` **được phép nhỏ hơn** `start_time`, và mọi so sánh phải đi qua hàm SQL `op_minute()`
(đổi giờ đồng hồ sang số phút tính từ 08:00 — `08:00 → 0`, `18:00 → 600`, `02:00 → 1080`).

### 5.2. "Ca trống" là `assigned_user_id IS NULL`, không phải một trạng thái
Cột `shifts.status` chỉ có hai giá trị `draft` và `published`. Ca trống và ca đã công bố là hai
khái niệm **có thể cùng đúng một lúc** (nhân viên chỉ đăng ký nhận ca trống sau khi lịch đã công bố),
nên chúng phải nằm ở hai cột khác nhau. Việc khóa ca khi đang trao đổi cũng vậy — đó là cột `is_locked`.

### 5.3. Mọi thời điểm lưu theo UTC
Server production chạy UTC còn rạp ở UTC+7. Mọi cột thời điểm là `TIMESTAMPTZ` lưu UTC, frontend tự
quy đổi khi hiển thị. Khi đối chiếu ca với lịch rảnh, **phải** đổi `start_at` về giờ địa phương của rạp
trước khi tính `op_minute` — quên bước này là nguồn sai lệch 7 tiếng.

---

## 6. Tài liệu

| Tài liệu | Nội dung |
|----------|----------|
| [docs/erd.md](docs/erd.md) | ERD 11 bảng, phân tích 3NF, **17 quyết định thiết kế kèm lý do** |
| [docs/api/openapi.yaml](docs/api/openapi.yaml) | Đặc tả 45 endpoint — hợp đồng giữa backend và frontend |
| [docs/api/README.md](docs/api/README.md) | Ánh xạ endpoint sang yêu cầu chức năng, cách xem spec |
| [docs/requirements/](docs/requirements/) | 55 yêu cầu chức năng, 39 phi chức năng, 14 use case |
| [docs/diagrams/](docs/diagrams/) | Use case, activity và sequence diagram |
| [docs/git-workflow.md](docs/git-workflow.md) | Quy tắc nhánh và commit |
| [about-project/tracker.md](about-project/tracker.md) | Kế hoạch 10 tuần, tiêu chí nghiệm thu từng sprint |

Sau khi backend chạy, FastAPI tự sinh tài liệu API tại http://localhost:8000/docs.
Bản này phải khớp với `docs/api/openapi.yaml` — lệch nhau nghĩa là code đã đi chệch thiết kế.

---

## 7. Giới hạn đã biết của phiên bản 1

Ghi lại minh bạch, sẽ trình bày trong phần "Hạn chế" của báo cáo:

- **Đăng xuất không thu hồi được token**: JWT là stateless và V1 chưa có bảng `refresh_tokens`,
  nên access token bị lộ trước khi đăng xuất vẫn còn hiệu lực tối đa 30 phút.
- **Không có bảng nhật ký thao tác**: việc quản lý ghi đè cảnh báo xếp ca chỉ lưu ở cột
  `shifts.override_reason` và log ứng dụng, chưa có màn hình tra cứu lịch sử.
- **Tỉ lệ đã đọc không chụp lại tại thời điểm đăng bài**: mẫu số của "8/12 đã đọc" tính theo số nhân
  viên đang hoạt động lúc truy vấn, nên thay đổi hồi tố nếu thêm hoặc khóa tài khoản sau đó.
- **Chỉ vận hành một rạp**: bảng `locations` đã có sẵn để mở rộng nhưng giao diện đa cụm rạp chưa làm.
- **Không kéo-thả xếp ca ở Roster**: đã cắt sang Version 2 để dồn thời gian cho thuật toán xếp ca tự động.
  Vẫn giữ kéo-thả ở màn hình đăng ký lịch rảnh.
- **Đổi ca hai chiều (swap)**: dời sang Version 2, V1 chỉ có pass ca và nhận ca.
- **`react-router-dom` 7.18.1 còn 2 advisory mức cao** liên quan tới chế độ RSC. Dự án dùng SPA thuần
  nên không nằm trong phạm vi ảnh hưởng; các bản thấp hơn còn nhiều lỗ hổng hơn hẳn. Sẽ nâng cấp khi
  có bản vá.

---

## 8. Hướng phát triển

Ứng dụng di động native (Flutter) · Push notification qua FCM · Đổi ca hai chiều · Module tính lương ·
Quản lý đa cụm rạp · Xếp ca bằng học máy thay cho thuật toán tham lam.
