# SD-01 — Sequence Diagram: Đăng nhập / Refresh Token / Đăng xuất

**Use Case**: UC-01 — Đăng nhập / Đăng xuất
**Actor chính**: Manager, Staff
**Tham chiếu**: [UC-01-auth.md](../requirements/UC-01-auth.md) · [module-auth.md](../requirements/module-auth.md)

> Tuân thủ ký pháp UML Sequence Diagram: **lifeline** cho từng đối tượng, mũi tên liền `->>` là
> **synchronous message**, mũi tên nét đứt `-->>` là **return message**, khối `alt/else` là
> **combined fragment** với **guard** trong `[ngoặc vuông]`, `opt` là fragment tùy chọn.
> Thứ tự thời gian đọc từ **trên xuống dưới**.

---

## 1. Sơ đồ chính — Đăng nhập (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor U as Người dùng<br/>(Manager / Staff)
    participant FE as LoginPage<br/>(React)
    participant AX as axios instance<br/>(+ interceptor)
    participant RT as auth_router<br/>(FastAPI)
    participant SEC as security.py<br/>(bcrypt + JWT)
    participant DB as PostgreSQL<br/>(users)

    U->>FE: Truy cập URL hệ thống
    FE->>FE: Đọc access_token từ localStorage

    alt [đã có token] — luồng phụ 4a
        FE->>AX: GET /api/auth/me
        AX->>RT: Header Authorization Bearer token
        RT->>SEC: decode_token(token)
        SEC-->>RT: payload sub, role
        RT->>DB: SELECT * FROM users WHERE id = sub AND is_active
        DB-->>RT: user row
        RT-->>AX: 200 { data: user }
        AX-->>FE: user
        FE-->>U: Redirect Dashboard, bỏ qua trang Login
    else [chưa có token]
        FE-->>U: Hiển thị form Đăng nhập
    end

    U->>FE: Nhập email + mật khẩu, bấm "Đăng nhập"
    FE->>FE: Validate client (React Hook Form + Zod)

    alt [ô trống / email sai định dạng] — ngoại lệ 5f
        FE-->>U: Inline error, KHÔNG gọi API
    else [dữ liệu hợp lệ]
        FE->>AX: POST /api/auth/login { email, password }
        AX->>RT: HTTP request
        RT->>RT: Pydantic LoginRequest validate
        RT->>DB: SELECT * FROM users WHERE email = :email
        DB-->>RT: user row hoặc None
        RT->>SEC: verify_password(password, user.password_hash)
        SEC-->>RT: True / False

        alt [email không tồn tại HOẶC mật khẩu sai] — ngoại lệ 5a + 5b
            RT-->>AX: 401 { detail: "Email hoặc mật khẩu không đúng" }
            AX-->>FE: AxiosError 401
            FE-->>U: Lỗi đỏ dưới form (message chung, chống enumeration)
        else [is_active = false] — ngoại lệ 5c
            RT-->>AX: 403 { detail: "Tài khoản đã bị khóa..." }
            AX-->>FE: AxiosError 403
            FE-->>U: Lỗi "Liên hệ quản lý"
        else [xác thực thành công]
            RT->>SEC: create_access_token(sub, role) — TTL 30 phút
            RT->>SEC: create_refresh_token(sub) — TTL 7 ngày
            SEC-->>RT: access_token, refresh_token
            RT-->>AX: 200 { access_token, refresh_token, token_type, user }
            AX-->>FE: TokenPair + user
            FE->>FE: Lưu 2 token vào localStorage
            FE->>FE: authStore.setUser(user) — Zustand
            FE-->>U: Redirect /dashboard/manager hoặc /dashboard/staff
        end
    end

    opt [network error / timeout] — ngoại lệ 5e
        AX-->>FE: Network Error
        FE-->>U: "Không thể kết nối đến server..." (nút Login mở lại)
    end

    Note over RT,DB: password_hash KHÔNG BAO GIỜ xuất hiện<br/>trong response (NFR-SEC-02)
```

---

## 2. Sơ đồ phụ — Tự động refresh Access Token (luồng phụ 4b)

```mermaid
sequenceDiagram
    autonumber
    actor U as Người dùng
    participant FE as Page bất kỳ<br/>(TanStack Query)
    participant AX as axios interceptor
    participant RT as auth_router
    participant SEC as security.py
    participant API as API bảo vệ<br/>(vd: shifts_router)

    U->>FE: Thao tác bất kỳ (vd: xem Roster)
    FE->>AX: GET /api/shifts?date=...&view=week
    AX->>API: Authorization Bearer access_token (đã hết hạn)
    API->>SEC: decode_token()
    SEC-->>API: ExpiredSignatureError
    API-->>AX: 401 Unauthorized

    Note over AX: Response interceptor bắt 401<br/>và tự xử lý, không đẩy lỗi ra UI

    AX->>RT: POST /api/auth/refresh { refresh_token }
    RT->>SEC: decode_token(refresh_token)

    alt [refresh token còn hiệu lực]
        SEC-->>RT: payload sub
        RT->>SEC: create_access_token(sub, role)
        SEC-->>RT: access_token mới
        RT-->>AX: 200 { access_token }
        AX->>AX: Ghi đè localStorage, retry request gốc
        AX->>API: GET /api/shifts (token mới)
        API-->>AX: 200 { data: shifts }
        AX-->>FE: shifts
        FE-->>U: Hiển thị dữ liệu — người dùng không hề bị gián đoạn
    else [refresh token hết hạn] — ngoại lệ 5d
        SEC-->>RT: ExpiredSignatureError
        RT-->>AX: 401 Unauthorized
        AX->>AX: Xóa toàn bộ token, reset authStore
        AX-->>FE: Điều hướng bắt buộc
        FE-->>U: Về trang Login + "Phiên đăng nhập đã hết hạn"
    end
```

---

## 3. Sơ đồ phụ — Đăng xuất

```mermaid
sequenceDiagram
    autonumber
    actor U as Người dùng
    participant FE as Header / Sidebar
    participant ST as authStore<br/>(Zustand)
    participant LS as localStorage

    U->>FE: Bấm avatar, chọn "Đăng xuất"
    FE-->>U: Popup xác nhận "Bạn có chắc muốn đăng xuất?"

    alt [xác nhận]
        U->>FE: Bấm "Xác nhận"
        FE->>LS: removeItem access_token, refresh_token
        FE->>ST: reset() — clear user + toàn bộ state
        FE-->>U: Redirect về trang Login
        Note over FE,LS: Không gọi API — JWT là stateless,<br/>token chỉ hết hiệu lực khi hết hạn (không có blacklist ở V1)
    else [hủy]
        FE-->>U: Đóng popup, giữ nguyên phiên
    end
```

---

## 4. Ánh xạ lifeline sang tầng kiến trúc

| Lifeline | Thành phần thực tế | Vị trí mã nguồn (dự kiến) |
|----------|--------------------|---------------------------|
| `FE` | React page + component | `frontend/src/pages/LoginPage.tsx` |
| `AX` | Axios instance + request/response interceptor | `frontend/src/lib/axios.ts` |
| `ST` | Zustand store lưu user hiện tại | `frontend/src/stores/authStore.ts` |
| `RT` | FastAPI router (`APIRouter`) | `backend/app/api/auth.py` |
| `SEC` | Hàm băm mật khẩu + tạo/verify JWT | `backend/app/core/security.py` |
| `DB` | SQLAlchemy async session → PostgreSQL | `backend/app/models/user.py` |

---

## 5. Phân tích luồng

### Luồng chính (Happy path)

| Bước | Message | Ghi chú |
|------|---------|---------|
| 1–2 | Truy cập URL, đọc localStorage | Route Guard phía FE (FR-AUTH-13) |
| 3–5 | Nhập thông tin, validate client | Chặn request rác lên server |
| 6–9 | `POST /api/auth/login`, tra cứu user | Index `UNIQUE(email)` giúp truy vấn nhanh |
| 10 | `verify_password()` bằng bcrypt | Cost factor ≥ 12 |
| 11–12 | Sinh cặp access + refresh token | HS256, TTL 30 phút / 7 ngày |
| 13–15 | Lưu token, set store, redirect theo role | Manager và Staff vào 2 dashboard khác nhau |

### Luồng ngoại lệ

| Ngoại lệ | Fragment | Xử lý |
|----------|----------|-------|
| Validation client (5f) | `alt [ô trống...]` | Inline error, không gọi API |
| Email sai / mật khẩu sai (5a, 5b) | `alt` nhánh 1 | Trả **cùng một** message 401 — chống enumeration attack |
| Tài khoản bị khóa (5c) | `alt` nhánh 2 | 403, gợi ý liên hệ quản lý |
| Lỗi mạng (5e) | `opt` | Toast, mở lại nút Đăng nhập |
| Access token hết hạn (4b) | Sơ đồ mục 2 | Interceptor tự refresh + retry, người dùng không thấy gì |
| Refresh token hết hạn (5d) | Sơ đồ mục 2, nhánh 2 | Xóa token, về Login |

### Điểm đúng chuẩn UML

- Mỗi lifeline là **một đối tượng có trách nhiệm riêng** (UI / HTTP client / router / service bảo mật / CSDL) — thể hiện đúng kiến trúc phân lớp, không gộp "Hệ thống" thành một khối chung.
- **Return message** (`-->>`) luôn đi kèm mã HTTP và payload, giúp đối chiếu trực tiếp với đặc tả API.
- Ba **combined fragment** lồng nhau (`alt` token → `alt` validate → `alt` xác thực) mô tả đủ 6 luồng ngoại lệ của UC-01 mà không cần vẽ thêm sơ đồ rời.
- **Note** dùng để ghi ràng buộc phi chức năng (NFR-SEC-02, JWT stateless) — thông tin không thể hiện được bằng message.
- Cơ chế refresh token được tách thành sơ đồ riêng vì nó là **luồng do interceptor tự khởi tạo**, không do actor kích hoạt.

---

## 6. Xuất hình cho báo cáo

Xem hướng dẫn chung ở [README.md](README.md). Tóm tắt:

1. **mermaid.live** (khuyên dùng): dán từng Mermaid block → *Actions → PNG* → lưu `out/sequence-login-1.png`, `-2.png`, `-3.png`.
2. **VS Code**: extension *Markdown Preview Mermaid Support* → Ctrl+Shift+V.
3. **draw.io**: Insert (+) → Advanced → Mermaid… (KHÔNG dùng *Edit Diagram* — ô đó chỉ nhận XML).

> Với sequence diagram nên export **SVG** rồi chèn vào Word, vì hình khá rộng, PNG dễ bị mờ khi co lại.

---

*Tài liệu phục vụ Chương 3.4 (Sequence Diagram) trong báo cáo đồ án.*
