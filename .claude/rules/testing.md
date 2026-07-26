# Quy tắc Testing

- Backend: pytest + httpx AsyncClient
- Frontend: Vitest + React Testing Library
- Mỗi API endpoint: tối thiểu 3 test (success, validation, auth)
- Test file đặt cạnh source: `tests/test_<module>.py`
- Fixtures trong `conftest.py`: db session, client, seed users
- KHÔNG mock database — dùng test database thật (Docker)
- Naming: `test_<action>_<expected_result>`