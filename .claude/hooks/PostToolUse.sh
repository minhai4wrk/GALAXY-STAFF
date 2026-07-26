#!/bin/bash
# Tự động format code sau khi Claude sửa file

FILE="$1"
EXT="${FILE##*.}"

case "$EXT" in
  py)
    ruff format "$FILE" 2>/dev/null
    ruff check --fix "$FILE" 2>/dev/null
    ;;
  ts|tsx|js|jsx)
    npx prettier --write "$FILE" 2>/dev/null
    ;;