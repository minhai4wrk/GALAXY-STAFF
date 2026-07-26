#!/bin/bash
# Lưu trạng thái trước khi compact context

echo "=== PRE-COMPACT STATE $(date) ===" >> .claude/compact-log.md
echo "Current branch: $(git branch --show-current)" >> .claude/compact-log.md
echo "Last 3 commits:" >> .claude/compact-log.md
git log --oneline -3 >> .claude/compact-log.md
echo "Modified files:" >> .claude/compact-log.md
git status --short >> .claude/compact-log.md
echo "---" >> .claude/compact-log.md