# /new-feature $feature_name $module

Scaffold tính năng mới:

1. Backend:
   - Tạo `backend/app/models/$feature_name.py`
   - Tạo `backend/app/schemas/$feature_name.py`
   - Tạo `backend/app/api/$feature_name.py`
   - Tạo `backend/app/tests/test_$feature_name.py`
   - Đăng ký router trong main.py

2. Frontend:
   - Tạo `frontend/src/types/$feature_name.ts`
   - Tạo `frontend/src/services/$feature_name.service.ts`
   - Tạo `frontend/src/hooks/use${FeatureName}.ts`
   - Tạo `frontend/src/pages/${FeatureName}Page.tsx`

3. Tạo Alembic migration nếu có model mới