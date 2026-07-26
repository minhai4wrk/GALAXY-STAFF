#!/usr/bin/env bash
# Xuất toàn bộ sơ đồ mermaid trong docs/ ra PNG và SVG để chèn vào báo cáo Word.
#
# Chạy:  bash docs/diagrams/export.sh
# Yêu cầu: Node.js (mermaid-cli tự tải về qua npx ở lần chạy đầu, khá lâu)
#
# Mỗi file .md có thể chứa nhiều block mermaid; mermaid-cli đánh số theo thứ tự
# xuất hiện, ví dụ sequence-login-1.png, sequence-login-2.png...

set -uo pipefail   # KHÔNG dùng -e: một sơ đồ lỗi không được làm hỏng cả mẻ export

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="$ROOT/docs/diagrams/out"
CONF="$ROOT/docs/diagrams/mermaid.json"

mkdir -p "$OUT"

# Soát trước ký tự < > và ; — chúng làm mermaid chết với thông báo rất khó đọc
if ! python "$ROOT/docs/diagrams/check_mermaid.py"; then
  echo "Dừng export. Sửa các dòng trên trước đã."
  exit 1
fi
echo

failed=()

render() {
  local src="$1" name="$2" fmt="$3"
  # Nền trắng để chèn vào Word không lộ ô trong suốt; scale 3 cho nét khi phóng to
  if ! npx -y @mermaid-js/mermaid-cli@11 \
        -i "$src" -o "$OUT/$name.$fmt" \
        -c "$CONF" -b white --scale 3 --quiet 2>"$OUT/.err"; then
    failed+=("$name.$fmt")
    echo "   lỗi $fmt — xem chi tiết:"
    head -4 "$OUT/.err" | sed 's/^/     /'
  fi
}

shopt -s nullglob
for src in "$ROOT"/docs/diagrams/*.md "$ROOT"/docs/erd.md; do
  base="$(basename "$src" .md)"
  [ "$base" = "README" ] && continue
  grep -q '```mermaid' "$src" || continue

  echo "→ $base"
  render "$src" "$base" png
  render "$src" "$base" svg
done

rm -f "$OUT/.err"

echo
png_count=$(ls "$OUT"/*.png 2>/dev/null | wc -l)
svg_count=$(ls "$OUT"/*.svg 2>/dev/null | wc -l)
echo "Xong: $png_count file PNG, $svg_count file SVG trong docs/diagrams/out/"

if [ ${#failed[@]} -gt 0 ]; then
  echo "Có ${#failed[@]} mục lỗi: ${failed[*]}"
  exit 1
fi
