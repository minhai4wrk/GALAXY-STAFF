"""Soát ký tự < và > lọt vào block mermaid trước khi export.

Mermaid hiểu `<` là mở thẻ HTML, còn bộ phân tích sequenceDiagram từ chối luôn cả `>`
(flowchart thì tha nếu nằm trong dấu nháy — chính sự khác biệt này khiến lỗi khó phát hiện:
4 activity diagram vẫn ra ảnh trong khi 3 sequence diagram chết).

Chạy:  python docs/diagrams/check_mermaid.py
Trả về mã 1 nếu tìm thấy vi phạm, dùng được trong script export hoặc CI.
"""

import re
import sys
from pathlib import Path

# Console Windows mặc định là cp1252, không in được tiếng Việt và sẽ ném UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DOCS = Path(__file__).resolve().parents[1]
# `<br/>` là thẻ duy nhất mermaid cho phép; các mẫu còn lại là cú pháp mũi tên
ALLOWED = re.compile(r"<br\s*/?>|--?>>?|-->|<<|\|>")


def main() -> int:
    """Quét mọi block mermaid trong docs/ và in ra các dòng có ký tự nguy hiểm."""
    violations: list[str] = []

    for path in sorted(DOCS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for block in re.finditer(r"```mermaid\n(.*?)```", text, re.S):
            first_line = text[: block.start()].count("\n") + 2
            body = block.group(1)
            lines = body.split("\n")
            # Loại sơ đồ quyết định mức độ khoan dung: sequenceDiagram khắt khe hơn flowchart
            kind = next((ln.strip() for ln in lines if ln.strip()), "")
            is_sequence = kind.startswith("sequenceDiagram")

            for offset, line in enumerate(lines):
                rel = path.relative_to(DOCS.parent)
                where = f"  {rel}:{first_line + offset}  {line.strip()[:88]}"

                if re.search(r"[<>]", ALLOWED.sub("", line)):
                    violations.append(f"[< >]{where}")

                # `;` là dấu kết thúc câu lệnh của mermaid. Trong sequenceDiagram, một dấu `;`
                # nằm giữa câu chữ sẽ cắt đôi dòng và phần sau trở thành cú pháp rác.
                # Riêng dòng `classDef ...;` của flowchart là hợp lệ nên bỏ qua.
                if is_sequence and ";" in line:
                    violations.append(f"[ ; ]{where}")

    if violations:
        print(f"Tìm thấy {len(violations)} dòng có ký tự nguy hiểm trong block mermaid:")
        print("\n".join(violations))
        print("\nThay < > bằng chữ (trước/sau/quá) hoặc ký hiệu ≤ ≥ →. Thay ; bằng dấu phẩy.")
        return 1

    print("Không có ký tự nguy hiểm lọt vào block mermaid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
