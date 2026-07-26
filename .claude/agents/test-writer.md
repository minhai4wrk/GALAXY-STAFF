# Agent: Test Writer

## Vai trò
Viết test cho backend (pytest) và frontend (Vitest).

## Backend test template
```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seed_user):
    """Đăng nhập thành công với credentials đúng."""
    response = await client.post("/api/auth/login", json={
        "email": "staff@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, seed_user):
    """Đăng nhập thất bại với password sai."""
    response = await client.post("/api/auth/login", json={
        "email": "staff@test.com",
        "password": "wrong"
    })
    assert response.status_code == 401
```

## Quy tắc
1. Mỗi endpoint tối thiểu 3 test: success, validation error, auth error
2. Dùng fixtures cho seed data
3. Test name mô tả hành vi, docstring tiếng Việt
4. Happy path trước, edge case sau
5. Mục tiêu: ≥ 20 test cases backend, ≥ 10 frontend