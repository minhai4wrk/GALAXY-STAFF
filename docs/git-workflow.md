# Quy trình Git — Galaxy Staff

**Mô hình**: Git Flow rút gọn cho dự án 1 người (bỏ nhánh `release/*` và `hotfix/*` vì không có bản phát hành song song).

---

## 1. Cấu trúc nhánh

| Nhánh | Vai trò | Ai merge vào | Được xóa sau merge |
|-------|---------|--------------|--------------------|
| `main` | Mã ổn định, luôn deploy được lên Render | Chỉ từ `develop` | Không |
| `develop` | Nhánh tích hợp, tập hợp mọi tính năng của sprint | Từ `feature/*` | Không |
| `feature/<module>-<mô-tả>` | Một tính năng / một FR | — | ✅ Xóa sau khi merge |
| `docs/<mô-tả>` | Chỉ sửa tài liệu, không đụng mã | — | ✅ Xóa sau khi merge |
| `fix/<mô-tả>` | Sửa lỗi phát hiện trong sprint | — | ✅ Xóa sau khi merge |

```
main     ──●──────────────────●──────────────────●──  (tag v0.1, v0.2, v1.0)
            \                /                  /
develop  ────●────●────●────●────●────●────●───●───
              \   /      \   /      \   /
feature/       ●─●        ●─●        ●─●
```

**Quy tắc bất di bất dịch**: không bao giờ commit trực tiếp lên `main`. Mọi thay đổi đi qua `develop`.

---

## 2. Đặt tên nhánh

Định dạng: `<loại>/<module>-<mô-tả-ngắn-tiếng-anh>`

| Ví dụ đúng | Ví dụ sai |
|-----------|-----------|
| `feature/auth-jwt-login` | `feature/login` (thiếu module) |
| `feature/availability-grid` | `Feature/Availability_Grid` (hoa + gạch dưới) |
| `feature/roster-auto-schedule` | `feature/lam-lich` (tiếng Việt) |
| `fix/exchange-race-condition` | `bug1` |
| `docs/chapter4-design` | `update-docs` |

Module hợp lệ: `auth`, `availability`, `roster`, `exchange`, `news`, `notification`, `infra`.

---

## 3. Conventional Commits

Định dạng: `<type>(<scope>): <mô tả ngắn bằng tiếng Anh, thể mệnh lệnh>`

| Type | Dùng khi |
|------|----------|
| `feat` | Thêm tính năng mới |
| `fix` | Sửa lỗi |
| `docs` | Tài liệu, sơ đồ, báo cáo |
| `style` | Format, đặt tên, không đổi logic |
| `refactor` | Đổi cấu trúc mã, không đổi hành vi |
| `test` | Thêm/sửa test |
| `chore` | Cấu hình, dependency, Docker, CI |

```bash
# Đúng
feat(auth): add JWT login endpoint
fix(exchange): prevent two staff taking the same shift
docs(erd): update ERD to v2.0 with 11 tables
chore(infra): add docker compose for postgres and backend

# Sai
update code            # thiếu type
feat: thêm login       # mô tả tiếng Việt
feat(auth): Added JWT  # quá khứ + viết hoa
```

Thân commit (tùy chọn) dùng khi cần giải thích **vì sao**, viết tiếng Việt được:

```
fix(availability): compare times via op_minute instead of raw TIME

Ca tối 18h→2h có end_time < start_time nên so sánh TIME trực tiếp
luôn trả về sai. Đổi sang op_minute() (số phút tính từ 8h00).

Refs: BR-AV-02
```

---

## 4. Vòng đời một tính năng

```bash
# 1. Luôn xuất phát từ develop mới nhất
git checkout develop
git pull origin develop

# 2. Tạo nhánh tính năng
git checkout -b feature/auth-jwt-login

# 3. Code + commit nhỏ, thường xuyên
git add backend/app/api/auth.py backend/app/schemas/auth.py
git commit -m "feat(auth): add JWT login endpoint"

# 4. Viết test NGAY, commit riêng
git commit -m "test(auth): add login success and invalid credential cases"

# 5. Đẩy lên remote
git push -u origin feature/auth-jwt-login

# 6. Mở Pull Request feature/* -> develop trên GitHub, tự review rồi merge
#    (dùng Squash and merge để lịch sử develop gọn)

# 7. Dọn nhánh
git checkout develop && git pull origin develop
git branch -d feature/auth-jwt-login
git push origin --delete feature/auth-jwt-login
```

**Vì sao vẫn mở PR khi làm một mình**: PR để lại diff + mô tả — đây là bằng chứng quy trình để chụp vào báo cáo, và tự đọc lại diff bắt được khá nhiều lỗi ẩu.

---

## 5. Kết thúc sprint — merge lên `main`

```bash
git checkout main
git pull origin main
git merge --no-ff develop -m "chore(release): sprint 1 - auth, availability, news feed"
git tag -a v0.1.0 -m "Sprint 1: Auth + Availability + News Feed"
git push origin main --tags
```

Dùng `--no-ff` để giữ lại nút merge trên đồ thị — nhìn ra ranh giới sprint khi chụp `git log --graph` cho báo cáo.

| Tag | Mốc |
|-----|-----|
| `v0.1.0` | Hết Sprint 1 — Auth + Availability + News Feed |
| `v0.2.0` | Hết Sprint 2 — Roster + Auto-Schedule + Exchange |
| `v1.0.0` | Hết Sprint 3 — Test + Deploy + Báo cáo |

---

## 6. Checklist trước khi merge PR vào `develop`

- [ ] `ruff check .` và `ruff format --check .` sạch (backend)
- [ ] `npm run lint` sạch (frontend)
- [ ] `pytest app/tests -v` xanh toàn bộ
- [ ] Mỗi endpoint mới có tối thiểu 3 test: success, validation, auth
- [ ] Không có `.env`, `node_modules/`, `__pycache__/` lọt vào diff
- [ ] Không hardcode secret / URL / mật khẩu
- [ ] **Đã chụp screenshot** tính năng cho báo cáo

---

## 7. Thiết lập GitHub repo

```bash
# Cách A - có GitHub CLI
gh repo create galaxy-staff --private --source=. --remote=origin
git push -u origin main
git push -u origin develop

# Cách B - tạo repo trống trên github.com rồi:
git remote add origin https://github.com/<username>/galaxy-staff.git
git push -u origin main
git push -u origin develop
```

**Cấu hình nên bật trên GitHub** (Settings → Branches → Add rule):

| Nhánh | Thiết lập |
|-------|-----------|
| `main` | Require a pull request before merging · Không cho force push |
| `develop` | Không cho force push |

Đặt **default branch = `develop`** để PR mặc định trỏ đúng đích.

---

## 8. Những thứ TUYỆT ĐỐI không commit

`.env` · `CLAUDE.local.md` · `node_modules/` · `__pycache__/` · `venv/` · `backend/uploads/*` (ảnh người dùng) · file `.docx` tạm của Word (`~$*.docx`)

→ Đã liệt kê sẵn trong [.gitignore](../.gitignore).

Nếu lỡ commit secret: **đổi secret ngay**, đừng chỉ xóa commit — lịch sử Git vẫn giữ nội dung cũ.
