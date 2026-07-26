# /seed-data

Tạo hoặc reset mock data:

1. Chạy `alembic upgrade head`
2. Chạy script `backend/scripts/seed.py`:
   - 1 Manager account (manager@galaxy.com / admin123)
   - 12 Staff accounts (staff01~12@galaxy.com / staff123)
   - 1 Location: "Galaxy CineX - Hanoi Centre"
   - Availability data: 2 tuần, random 60-80% slots available
   - 20 shifts mẫu (mix assigned + open)
   - 5 news posts mẫu
   - 3 shift exchange mẫu (pending, approved, rejected)
3. Hiển thị tóm tắt data đã seed