# /ship

Chạy trước khi commit:

1. Backend: `cd backend && ruff check . && pytest tests/ -v --tb=short`
2. Frontend: `cd frontend && npx tsc --noEmit && npx eslint src/ && npx vitest run`
3. Nếu pass hết → hiển thị git diff --stat
4. Đề xuất commit message theo Conventional Commits
5. HỎI xác nhận trước khi commit