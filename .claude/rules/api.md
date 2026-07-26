# Quy tắc API

- URL: lowercase, dấu gạch ngang, số nhiều: `/api/shifts`, `/api/news`
- Response format thống nhất:
  - Success: `{ data: T }` hoặc `{ data: T[], total: number }`
  - Error: `{ detail: string }`
- Pagination: `?page=1&size=20`
- Filter: query params: `?date=2026-06-15&view=week`
- Auth: Bearer token trong header Authorization
- Status codes: 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found
- Mọi endpoint Manager-only phải dùng `Depends(get_current_manager)`
