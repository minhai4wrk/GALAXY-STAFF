# PHÂN TÍCH YÊU CẦU CHỨC NĂNG CHI TIẾT

## Module: Authentication & User Management

| Hạng mục | Thông tin |
|----------|-----------|
| Hệ thống | Galaxy Staff – Hệ thống Quản lý Nhân sự Rạp Chiếu Phim |
| Module | Authentication & User Management |
| Phiên bản | 1.0 |
| Ngày tạo | 08/05/2026 |
| Tác giả | [Tên sinh viên] |

---

## 1. Tổng quan Module

Module Authentication & User Management chịu trách nhiệm xử lý toàn bộ quy trình xác thực người dùng và quản lý tài khoản trong hệ thống Galaxy Staff. Hệ thống phân biệt 2 vai trò chính:

- **Manager (Quản lý rạp):** Có toàn quyền quản trị hệ thống — tạo tài khoản nhân viên, xếp ca, duyệt yêu cầu, đăng thông báo.
- **Staff (Nhân viên):** Sử dụng hệ thống để đăng ký lịch rảnh, xem ca làm, trao đổi ca và nhận thông báo.

Cơ chế xác thực sử dụng **JSON Web Token (JWT)** kết hợp **bcrypt** để băm mật khẩu. Phân quyền theo mô hình **Role-based Access Control (RBAC)**.

---

## 2. Danh sách Yêu cầu Chức năng

---

### FR-AUTH-01: Đăng nhập hệ thống

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-01 |
| **Tên yêu cầu** | Đăng nhập hệ thống (Login) |
| **Mô tả chi tiết** | Người dùng nhập email và mật khẩu để đăng nhập. Hệ thống xác thực thông tin, nếu hợp lệ thì trả về cặp token (access token + refresh token). Access token có thời hạn ngắn (ví dụ 30 phút), refresh token có thời hạn dài hơn (ví dụ 7 ngày). Sau khi đăng nhập thành công, hệ thống chuyển hướng người dùng đến Dashboard tương ứng với role của họ. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Tài khoản đã được tạo bởi Manager và ở trạng thái active (`is_active = true`) |
| **Kết quả mong đợi** | - Đăng nhập thành công: trả về access token + refresh token, redirect đến Dashboard. <br> - Email không tồn tại: hiển thị lỗi "Email hoặc mật khẩu không đúng". <br> - Mật khẩu sai: hiển thị lỗi "Email hoặc mật khẩu không đúng" (không phân biệt để tránh lộ thông tin). <br> - Tài khoản bị vô hiệu hóa: hiển thị lỗi "Tài khoản đã bị khóa, vui lòng liên hệ quản lý". |
| **Mức ưu tiên** | **Must** |

**API tương ứng:** `POST /api/auth/login`

---

### FR-AUTH-02: Đăng xuất hệ thống

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-02 |
| **Tên yêu cầu** | Đăng xuất hệ thống (Logout) |
| **Mô tả chi tiết** | Người dùng bấm nút "Đăng xuất" trên giao diện. Hệ thống xóa token phía client (localStorage/cookie), hủy phiên đăng nhập hiện tại. Người dùng được chuyển về trang Login. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Người dùng đang trong trạng thái đã đăng nhập |
| **Kết quả mong đợi** | - Token bị xóa khỏi client. <br> - Redirect về trang Login. <br> - Client không còn token nên mọi request tiếp theo đều bị từ chối (401 Unauthorized). <br> - *Lưu ý:* JWT là stateless, V1 không có token blacklist — nếu access token cũ bị sao chép ra ngoài trước khi đăng xuất thì vẫn còn hiệu lực tối đa 30 phút (đến khi hết hạn). Ghi nhận trong phần "Hạn chế" của báo cáo. |
| **Mức ưu tiên** | **Must** |

---

### FR-AUTH-03: Làm mới token (Refresh Token)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-03 |
| **Tên yêu cầu** | Làm mới Access Token |
| **Mô tả chi tiết** | Khi access token hết hạn, frontend tự động gửi refresh token lên server để nhận access token mới mà không cần người dùng đăng nhập lại. Nếu refresh token cũng hết hạn thì buộc người dùng đăng nhập lại. |
| **Actor** | Both (Manager & Staff) — xử lý tự động bởi hệ thống |
| **Điều kiện tiên quyết** | Access token đã hết hạn, refresh token còn hiệu lực |
| **Kết quả mong đợi** | - Refresh token hợp lệ: trả về access token mới, người dùng tiếp tục sử dụng bình thường. <br> - Refresh token hết hạn hoặc không hợp lệ: redirect về trang Login. |
| **Mức ưu tiên** | **Should** |

**API tương ứng:** `POST /api/auth/refresh`

---

### FR-AUTH-04: Xem thông tin cá nhân

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-04 |
| **Tên yêu cầu** | Xem thông tin tài khoản hiện tại (Get Current User) |
| **Mô tả chi tiết** | Người dùng đã đăng nhập có thể xem thông tin cá nhân của mình: họ tên, email, role, chi nhánh rạp (location), trạng thái tài khoản, ngày tạo. Thông tin này thường hiển thị ở trang Profile hoặc sidebar/header. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Đã đăng nhập, có access token hợp lệ |
| **Kết quả mong đợi** | Trả về object chứa: `id`, `email`, `full_name`, `role`, `location`, `is_active`, `created_at`. Không trả về `password_hash`. |
| **Mức ưu tiên** | **Must** |

**API tương ứng:** `GET /api/auth/me`

---

### FR-AUTH-05: Đổi mật khẩu

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-05 |
| **Tên yêu cầu** | Đổi mật khẩu cá nhân |
| **Mô tả chi tiết** | Người dùng có thể tự đổi mật khẩu của mình. Phải nhập mật khẩu hiện tại để xác nhận, sau đó nhập mật khẩu mới (tối thiểu 8 ký tự) và xác nhận mật khẩu mới. Hệ thống kiểm tra mật khẩu cũ đúng hay không trước khi cập nhật. |
| **Actor** | Both (Manager & Staff) |
| **Điều kiện tiên quyết** | Đã đăng nhập |
| **Kết quả mong đợi** | - Mật khẩu cũ đúng + mật khẩu mới hợp lệ: cập nhật thành công, hiển thị thông báo "Đổi mật khẩu thành công". <br> - Mật khẩu cũ sai: hiển thị lỗi "Mật khẩu hiện tại không đúng". <br> - Mật khẩu mới không đủ mạnh: hiển thị yêu cầu cụ thể (tối thiểu 8 ký tự). |
| **Mức ưu tiên** | **Should** |

**API tương ứng:** `PUT /api/auth/change-password`

---

### FR-AUTH-06: Tạo tài khoản nhân viên mới

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-06 |
| **Tên yêu cầu** | Đăng ký tài khoản nhân viên (Register — Manager only) |
| **Mô tả chi tiết** | Chỉ Manager mới có quyền tạo tài khoản mới cho nhân viên. Manager nhập: email, họ tên, role (Manager hoặc Staff), chi nhánh rạp (location). Hệ thống tự động tạo mật khẩu mặc định (ví dụ: `GalaxyStaff@123`) hoặc Manager tự đặt mật khẩu ban đầu. Nhân viên sẽ đổi mật khẩu khi đăng nhập lần đầu. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập với role Manager |
| **Kết quả mong đợi** | - Email chưa tồn tại: tạo tài khoản thành công, mật khẩu được băm bằng bcrypt trước khi lưu. <br> - Email đã tồn tại: hiển thị lỗi "Email đã được sử dụng". <br> - Thiếu trường bắt buộc: hiển thị validation error cụ thể. |
| **Mức ưu tiên** | **Must** |

**API tương ứng:** `POST /api/auth/register`

---

### FR-AUTH-07: Xem danh sách nhân viên

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-07 |
| **Tên yêu cầu** | Xem danh sách tất cả nhân viên |
| **Mô tả chi tiết** | Manager xem danh sách toàn bộ nhân viên trong hệ thống, bao gồm: họ tên, email, role, chi nhánh, trạng thái (active/inactive), ngày tạo. Hỗ trợ tìm kiếm theo tên/email và lọc theo role, trạng thái. Có phân trang nếu danh sách dài. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập với role Manager |
| **Kết quả mong đợi** | Trả về danh sách users với đầy đủ thông tin (trừ `password_hash`). Hỗ trợ query params: `?search=`, `?role=`, `?is_active=`, `?page=`, `?limit=`. |
| **Mức ưu tiên** | **Must** |

**API tương ứng:** `GET /api/users`

---

### FR-AUTH-08: Xem chi tiết một nhân viên

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-08 |
| **Tên yêu cầu** | Xem thông tin chi tiết của một nhân viên |
| **Mô tả chi tiết** | Manager bấm vào một nhân viên trong danh sách để xem thông tin chi tiết: họ tên, email, role, chi nhánh rạp, trạng thái, ngày tạo tài khoản. Có thể mở rộng thêm: tổng số giờ làm tuần này, số ca đã pass, v.v. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập với role Manager, user ID tồn tại |
| **Kết quả mong đợi** | Trả về object chứa đầy đủ thông tin nhân viên. Nếu user ID không tồn tại: trả về 404 Not Found. |
| **Mức ưu tiên** | **Must** |

**API tương ứng:** `GET /api/users/{id}`

---

### FR-AUTH-09: Cập nhật thông tin nhân viên

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-09 |
| **Tên yêu cầu** | Chỉnh sửa thông tin nhân viên |
| **Mô tả chi tiết** | Manager có thể cập nhật thông tin của nhân viên: họ tên, email, role, chi nhánh rạp. Không thể sửa `password_hash` qua endpoint này (dùng FR-AUTH-05 hoặc FR-AUTH-11). Staff cũng có thể cập nhật một số thông tin cá nhân của mình (họ tên) nhưng không thể tự đổi role. |
| **Actor** | Manager (toàn quyền), Staff (chỉ sửa thông tin cá nhân hạn chế) |
| **Điều kiện tiên quyết** | Đã đăng nhập. Manager: sửa bất kỳ ai. Staff: chỉ sửa chính mình. |
| **Kết quả mong đợi** | - Cập nhật thành công: trả về thông tin đã cập nhật. <br> - Email mới bị trùng: hiển thị lỗi "Email đã được sử dụng". <br> - Staff cố sửa role: trả về 403 Forbidden. <br> - User ID không tồn tại: trả về 404 Not Found. |
| **Mức ưu tiên** | **Must** |

**API tương ứng:** `PUT /api/users/{id}`

---

### FR-AUTH-10: Vô hiệu hóa / Kích hoạt tài khoản

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-10 |
| **Tên yêu cầu** | Vô hiệu hóa hoặc kích hoạt lại tài khoản nhân viên |
| **Mô tả chi tiết** | Manager có thể vô hiệu hóa tài khoản nhân viên (khi nghỉ việc, tạm ngưng,...) bằng cách chuyển `is_active` sang `false`. Nhân viên bị vô hiệu hóa không thể đăng nhập. Manager cũng có thể kích hoạt lại tài khoản khi cần. Không xóa vĩnh viễn dữ liệu (soft delete). |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập với role Manager. Không thể tự vô hiệu hóa chính mình. |
| **Kết quả mong đợi** | - Vô hiệu hóa thành công: `is_active = false`, nhân viên không thể đăng nhập. <br> - Kích hoạt thành công: `is_active = true`, nhân viên đăng nhập lại bình thường. <br> - Manager cố tự vô hiệu hóa mình: trả về lỗi 400 "Không thể vô hiệu hóa tài khoản của chính mình". |
| **Mức ưu tiên** | **Must** |

**API tương ứng:** `PATCH /api/users/{id}/status`

---

### FR-AUTH-11: Reset mật khẩu nhân viên

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-11 |
| **Tên yêu cầu** | Manager đặt lại mật khẩu cho nhân viên |
| **Mô tả chi tiết** | Khi nhân viên quên mật khẩu, Manager có thể reset mật khẩu về giá trị mặc định (ví dụ: `GalaxyStaff@123`). Sau đó nhân viên tự đổi mật khẩu mới khi đăng nhập. Do đây là hệ thống nội bộ rạp chiếu phim nên không cần flow reset qua email — nhân viên liên hệ trực tiếp quản lý. |
| **Actor** | Manager |
| **Điều kiện tiên quyết** | Đã đăng nhập với role Manager |
| **Kết quả mong đợi** | - Reset thành công: mật khẩu nhân viên được đặt về giá trị mặc định, băm bằng bcrypt. <br> - User ID không tồn tại: trả về 404. |
| **Mức ưu tiên** | **Should** |

**API tương ứng:** `POST /api/users/{id}/reset-password`

---

### FR-AUTH-12: Phân quyền truy cập API (RBAC Middleware)

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-12 |
| **Tên yêu cầu** | Phân quyền truy cập theo vai trò (RBAC) |
| **Mô tả chi tiết** | Mọi API endpoint (trừ login) đều yêu cầu JWT token hợp lệ trong header `Authorization: Bearer <token>`. Middleware kiểm tra: (1) Token có hợp lệ và chưa hết hạn không, (2) User có role phù hợp với endpoint không. Ví dụ: endpoint tạo user chỉ Manager mới gọi được, endpoint đăng ký lịch rảnh thì cả Manager và Staff đều gọi được. |
| **Actor** | Hệ thống (tự động kiểm tra) |
| **Điều kiện tiên quyết** | Request phải chứa header `Authorization: Bearer <access_token>` |
| **Kết quả mong đợi** | - Token hợp lệ + đúng role: cho phép truy cập. <br> - Không có token: trả về 401 Unauthorized. <br> - Token hết hạn: trả về 401 Unauthorized. <br> - Token hợp lệ nhưng sai role: trả về 403 Forbidden. |
| **Mức ưu tiên** | **Must** |

---

### FR-AUTH-13: Route Guard phía Frontend

| Mục | Nội dung |
|-----|---------|
| **Mã yêu cầu** | FR-AUTH-13 |
| **Tên yêu cầu** | Bảo vệ route phía client (Protected Routes) |
| **Mô tả chi tiết** | Frontend kiểm tra token trước khi cho phép truy cập các trang nội bộ. Nếu chưa đăng nhập → redirect về Login. Nếu đã đăng nhập nhưng truy cập trang không đúng role (ví dụ Staff truy cập trang quản lý nhân viên) → redirect về Dashboard hoặc hiển thị trang 403. Trang Login sẽ tự redirect về Dashboard nếu đã đăng nhập. |
| **Actor** | Hệ thống Frontend (tự động) |
| **Điều kiện tiên quyết** | Không có |
| **Kết quả mong đợi** | - Chưa đăng nhập → redirect `/login`. <br> - Đã đăng nhập, truy cập `/login` → redirect `/dashboard`. <br> - Staff truy cập route Manager-only → redirect hoặc hiển thị 403. |
| **Mức ưu tiên** | **Must** |

---

## 3. Ma trận Phân quyền (RBAC Matrix)

Bảng 1: Ma trận phân quyền theo vai trò cho module Auth & User Management

| Chức năng | Manager | Staff |
|-----------|---------|-------|
| Đăng nhập (FR-AUTH-01) | ✅ | ✅ |
| Đăng xuất (FR-AUTH-02) | ✅ | ✅ |
| Refresh token (FR-AUTH-03) | ✅ | ✅ |
| Xem thông tin cá nhân (FR-AUTH-04) | ✅ | ✅ |
| Đổi mật khẩu cá nhân (FR-AUTH-05) | ✅ | ✅ |
| Tạo tài khoản mới (FR-AUTH-06) | ✅ | ❌ |
| Xem danh sách nhân viên (FR-AUTH-07) | ✅ | ❌ |
| Xem chi tiết nhân viên (FR-AUTH-08) | ✅ | ❌ |
| Cập nhật thông tin nhân viên (FR-AUTH-09) | ✅ (tất cả) | ✅ (chỉ bản thân) |
| Vô hiệu hóa tài khoản (FR-AUTH-10) | ✅ | ❌ |
| Reset mật khẩu (FR-AUTH-11) | ✅ | ❌ |

---

## 4. Tổng hợp API Endpoints

Bảng 2: Danh sách API endpoints cho module Auth & User Management

| Method | Endpoint | Mô tả | Quyền truy cập | Yêu cầu liên quan |
|--------|----------|-------|----------------|-------------------|
| `POST` | `/api/auth/login` | Đăng nhập | Public | FR-AUTH-01 |
| `POST` | `/api/auth/refresh` | Làm mới access token | Authenticated | FR-AUTH-03 |
| `GET` | `/api/auth/me` | Xem thông tin cá nhân | Authenticated | FR-AUTH-04 |
| `PUT` | `/api/auth/change-password` | Đổi mật khẩu | Authenticated | FR-AUTH-05 |
| `POST` | `/api/auth/register` | Tạo tài khoản mới | Manager only | FR-AUTH-06 |
| `GET` | `/api/users` | Danh sách nhân viên | Manager only | FR-AUTH-07 |
| `GET` | `/api/users/{id}` | Chi tiết nhân viên | Manager only | FR-AUTH-08 |
| `PUT` | `/api/users/{id}` | Cập nhật thông tin | Manager / Self | FR-AUTH-09 |
| `PATCH` | `/api/users/{id}/status` | Vô hiệu hóa / kích hoạt | Manager only | FR-AUTH-10 |
| `POST` | `/api/users/{id}/reset-password` | Reset mật khẩu | Manager only | FR-AUTH-11 |

---

## 5. Quy tắc Nghiệp vụ (Business Rules)

| Mã | Quy tắc | Ghi chú |
|----|---------|---------|
| BR-01 | Mật khẩu phải được băm bằng bcrypt trước khi lưu vào DB | Không bao giờ lưu plain-text |
| BR-02 | Email là duy nhất trong toàn hệ thống | Unique constraint trên bảng `users` |
| BR-03 | Không xóa cứng tài khoản, chỉ soft-delete qua `is_active` | Bảo toàn dữ liệu lịch sử (ca làm, lịch rảnh cũ) |
| BR-04 | Manager không thể tự vô hiệu hóa chính mình | Tránh trường hợp hệ thống không còn ai quản trị |
| BR-05 | Access token hết hạn sau 30 phút, Refresh token sau 7 ngày | Cấu hình trong `.env`, không hardcode |
| BR-06 | Thông báo lỗi đăng nhập không phân biệt email sai hay mật khẩu sai | Chống enumeration attack |
| BR-07 | Staff chỉ xem/sửa thông tin của chính mình | Kiểm tra `user_id` từ token khớp với `{id}` trong URL |

---

## 6. Yêu cầu Phi chức năng liên quan

| Hạng mục | Yêu cầu |
|----------|---------|
| **Bảo mật** | JWT token sử dụng thuật toán HS256, secret key từ biến môi trường. Bcrypt với cost factor ≥ 12. |
| **Hiệu năng** | API login phản hồi < 300ms. API danh sách users hỗ trợ phân trang để tránh query nặng. |
| **Validation** | Email đúng format (RFC 5322). Mật khẩu tối thiểu 8 ký tự. Họ tên không được rỗng. |
| **Logging** | Ghi log các sự kiện: đăng nhập thành công/thất bại, tạo tài khoản, vô hiệu hóa tài khoản. |

---

*Tài liệu này phục vụ cho phần Phân tích yêu cầu (Chương 3.2) trong báo cáo đồ án.*
