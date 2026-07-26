# USE CASE CHI TIẾT

## UC-01: Đăng nhập / Đăng xuất

| Hạng mục | Thông tin |
|----------|-----------|
| **Use Case ID** | UC-01 |
| **Tên** | Đăng nhập / Đăng xuất hệ thống |
| **Actor** | Manager, Staff |
| **Module** | Authentication |
| **Mức ưu tiên** | Must Have |
| **Phiên bản** | 1.0 |
| **Ngày tạo** | 08/05/2026 |

---

## 1. Mô tả ngắn

Người dùng (Manager hoặc Staff) sử dụng email và mật khẩu để đăng nhập vào hệ thống Galaxy Staff. Sau khi xác thực thành công, hệ thống cấp JWT token và chuyển hướng đến Dashboard phù hợp với vai trò. Người dùng có thể đăng xuất bất kỳ lúc nào để kết thúc phiên làm việc.

---

## 2. Tiền điều kiện (Preconditions)

| # | Điều kiện |
|---|-----------|
| 1 | Tài khoản người dùng đã được tạo bởi Manager (FR-AUTH-06) |
| 2 | Tài khoản ở trạng thái active (`is_active = true`) |
| 3 | Người dùng có trình duyệt web hỗ trợ (Chrome, Firefox, Edge, Safari) |
| 4 | Hệ thống backend đang hoạt động và kết nối database bình thường |

---

## 3. Luồng chính — Đăng nhập (Main Flow)

| Bước | Actor | Hành động |
|------|-------|-----------|
| 1 | Người dùng | Truy cập URL hệ thống Galaxy Staff |
| 2 | Hệ thống | Kiểm tra token trong localStorage. Không có token → hiển thị trang Login |
| 3 | Người dùng | Nhập email vào ô "Email" |
| 4 | Người dùng | Nhập mật khẩu vào ô "Mật khẩu" |
| 5 | Người dùng | Bấm nút "Đăng nhập" |
| 6 | Hệ thống | Gửi request `POST /api/auth/login` với body `{ email, password }` |
| 7 | Hệ thống | Tìm user theo email trong database |
| 8 | Hệ thống | So sánh mật khẩu nhập vào với `password_hash` bằng bcrypt.verify() |
| 9 | Hệ thống | Kiểm tra `is_active = true` |
| 10 | Hệ thống | Tạo access token (JWT, TTL 30 phút) chứa: `user_id`, `role`, `exp` |
| 11 | Hệ thống | Tạo refresh token (JWT, TTL 7 ngày) |
| 12 | Hệ thống | Trả về response: `{ access_token, refresh_token, token_type, user }` |
| 13 | Frontend | Lưu access token + refresh token vào localStorage |
| 14 | Frontend | Đọc `role` từ token payload |
| 15 | Frontend | Redirect đến Dashboard: Manager → `/dashboard/manager`, Staff → `/dashboard/staff` |
| 16 | Hệ thống | Hiển thị Dashboard với sidebar/navbar phù hợp role |

---

## 4. Luồng phụ (Alternative Flows)

### 4a. Đã đăng nhập — truy cập trang Login

| Bước | Actor | Hành động |
|------|-------|-----------|
| 2a.1 | Hệ thống | Phát hiện có token hợp lệ trong localStorage |
| 2a.2 | Hệ thống | Gọi `GET /api/auth/me` để xác minh token còn hiệu lực |
| 2a.3 | Hệ thống | Token hợp lệ → redirect ngay đến Dashboard (bỏ qua trang Login) |

### 4b. Access token hết hạn — tự động refresh

| Bước | Actor | Hành động |
|------|-------|-----------|
| b.1 | Frontend | Gửi API request → nhận response 401 (token expired) |
| b.2 | Frontend | Interceptor tự động gửi `POST /api/auth/refresh` với refresh token |
| b.3 | Hệ thống | Kiểm tra refresh token hợp lệ → tạo access token mới |
| b.4 | Frontend | Lưu access token mới, retry request ban đầu |
| b.5 | | Người dùng không bị gián đoạn, không cần đăng nhập lại |

### 4c. Nhớ tài khoản (Remember me) — Tùy chọn

| Bước | Actor | Hành động |
|------|-------|-----------|
| c.1 | Người dùng | Tick checkbox "Nhớ tài khoản" trước khi đăng nhập |
| c.2 | Frontend | Lưu email vào localStorage (không lưu mật khẩu) |
| c.3 | | Lần đăng nhập sau, ô email tự động điền sẵn |

---

## 5. Luồng ngoại lệ (Exception Flows)

### 5a. Email không tồn tại

| Bước | Actor | Hành động |
|------|-------|-----------|
| 7a.1 | Hệ thống | Không tìm thấy user với email đã nhập |
| 7a.2 | Hệ thống | Trả về 401: `{ detail: "Email hoặc mật khẩu không đúng" }` |
| 7a.3 | Frontend | Hiển thị thông báo lỗi màu đỏ dưới form |
| 7a.4 | | Lưu ý: không phân biệt "email sai" hay "mật khẩu sai" để tránh lộ thông tin (enumeration attack) |

### 5b. Mật khẩu sai

| Bước | Actor | Hành động |
|------|-------|-----------|
| 8b.1 | Hệ thống | bcrypt.verify() trả về false |
| 8b.2 | Hệ thống | Trả về 401: `{ detail: "Email hoặc mật khẩu không đúng" }` |
| 8b.3 | Frontend | Hiển thị thông báo lỗi giống 5a (message chung) |

### 5c. Tài khoản bị vô hiệu hóa

| Bước | Actor | Hành động |
|------|-------|-----------|
| 9c.1 | Hệ thống | Tìm thấy user nhưng `is_active = false` |
| 9c.2 | Hệ thống | Trả về 403: `{ detail: "Tài khoản đã bị khóa, vui lòng liên hệ quản lý" }` |
| 9c.3 | Frontend | Hiển thị thông báo lỗi |

### 5d. Refresh token hết hạn

| Bước | Actor | Hành động |
|------|-------|-----------|
| b.3d.1 | Hệ thống | Refresh token không hợp lệ hoặc hết hạn |
| b.3d.2 | Hệ thống | Trả về 401 |
| b.3d.3 | Frontend | Xóa toàn bộ token khỏi localStorage |
| b.3d.4 | Frontend | Redirect về trang Login, hiển thị "Phiên đăng nhập đã hết hạn" |

### 5e. Lỗi mạng / Server không phản hồi

| Bước | Actor | Hành động |
|------|-------|-----------|
| 6e.1 | Frontend | Request timeout hoặc network error |
| 6e.2 | Frontend | Hiển thị "Không thể kết nối đến server. Vui lòng kiểm tra mạng và thử lại." |
| 6e.3 | | Nút "Đăng nhập" trở lại trạng thái bình thường (không disable) |

### 5f. Validation lỗi phía client

| Bước | Actor | Hành động |
|------|-------|-----------|
| 5f.1 | Người dùng | Bấm "Đăng nhập" khi ô email hoặc mật khẩu trống |
| 5f.2 | Frontend | Hiển thị inline error: "Vui lòng nhập email" / "Vui lòng nhập mật khẩu" |
| 5f.3 | | Không gửi request lên server (validate phía client trước) |

---

## 6. Luồng chính — Đăng xuất (Main Flow)

| Bước | Actor | Hành động |
|------|-------|-----------|
| 1 | Người dùng | Bấm vào avatar/tên → chọn "Đăng xuất" (hoặc bấm nút Đăng xuất trên sidebar) |
| 2 | Frontend | Hiển thị popup xác nhận: "Bạn có chắc muốn đăng xuất?" (tùy chọn) |
| 3 | Người dùng | Bấm "Xác nhận" |
| 4 | Frontend | Xóa access token + refresh token khỏi localStorage |
| 5 | Frontend | Clear toàn bộ state (Zustand store reset) |
| 6 | Frontend | Redirect về trang Login |
| 7 | Hệ thống | Mọi request tiếp theo từ client cũ bị từ chối (401) |

---

## 7. Hậu điều kiện (Postconditions)

### Sau đăng nhập thành công:
| # | Điều kiện |
|---|-----------|
| 1 | Access token + refresh token được lưu trong localStorage |
| 2 | Người dùng ở trang Dashboard đúng role |
| 3 | Sidebar/navbar hiển thị menu phù hợp role (Manager thấy nhiều menu hơn Staff) |
| 4 | Mọi API request tiếp theo đều gửi kèm header `Authorization: Bearer <access_token>` |

### Sau đăng xuất:
| # | Điều kiện |
|---|-----------|
| 1 | Token bị xóa khỏi localStorage |
| 2 | Người dùng ở trang Login |
| 3 | Truy cập bất kỳ route nào đều bị redirect về Login |

---

## 8. Yêu cầu chức năng liên quan

| FR | Tên | Vai trò trong UC-01 |
|----|-----|---------------------|
| FR-AUTH-01 | Đăng nhập hệ thống | Luồng chính đăng nhập |
| FR-AUTH-02 | Đăng xuất hệ thống | Luồng chính đăng xuất |
| FR-AUTH-03 | Refresh Token | Luồng phụ 4b |
| FR-AUTH-04 | Xem thông tin cá nhân | Verify token qua `GET /api/auth/me` |
| FR-AUTH-12 | RBAC Middleware | Kiểm tra quyền mọi request sau đăng nhập |
| FR-AUTH-13 | Route Guard Frontend | Protect routes, redirect khi chưa đăng nhập |

---

## 9. Ghi chú kỹ thuật

### JWT Token Structure
```
Header: { alg: "HS256", typ: "JWT" }
Payload: {
  sub: "user_id",       // ID người dùng
  role: "manager|staff", // Vai trò
  exp: 1234567890,       // Thời gian hết hạn (Unix timestamp)
  iat: 1234567890        // Thời gian tạo
}
Signature: HMACSHA256(header + payload, SECRET_KEY)
```

### Thư viện sử dụng
| Thành phần | Thư viện | Ghi chú |
|------------|----------|---------|
| Tạo/verify JWT | `python-jose[cryptography]` | Backend |
| Băm mật khẩu | `passlib[bcrypt]` | Cost factor ≥ 12 |
| HTTP client | `axios` | Frontend, có interceptor cho refresh |
| State management | `zustand` | Lưu user info sau login |

### Cấu hình (từ .env)
```
JWT_SECRET_KEY=<random-string-64-chars>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### API Request/Response

**Login Request:**
```json
POST /api/auth/login
Content-Type: application/json

{
  "email": "staff01@galaxy.com",
  "password": "GalaxyStaff@123"
}
```

**Login Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "staff01@galaxy.com",
    "full_name": "Nguyễn Văn A",
    "role": "staff",
    "location_id": 1,
    "is_active": true
  }
}
```

**Login Error (401):**
```json
{
  "detail": "Email hoặc mật khẩu không đúng"
}
```

---

## 10. Giao diện tham khảo

### Trang Login
- Logo Galaxy Staff ở trên cùng
- Form login giữa màn hình: ô Email, ô Mật khẩu, checkbox "Nhớ tài khoản", nút "Đăng nhập"
- Thông báo lỗi hiển thị màu đỏ dưới form
- Background gradient hoặc hình ảnh rạp chiếu phim

[Hình 3.X: Giao diện trang đăng nhập — CHỤP SAU]

### Nút Đăng xuất
- Nằm ở dropdown khi click avatar/tên người dùng trên header
- Hoặc ở cuối sidebar (tùy layout)

[Hình 3.X: Vị trí nút đăng xuất trên giao diện — CHỤP SAU]

---

*Tài liệu này phục vụ cho phần phân tích Use Case chi tiết (Chương 3.2) trong báo cáo đồ án.*
