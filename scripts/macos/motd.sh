#!/bin/bash
# JipMunSeo iTerm MOTD — CHANGELOG.md에 새로 추가된 줄이 있으면 새 터미널을 열 때 보여준다.
# 실행하지 말고 ~/.zshrc에서 source할 것:
#   export JIPMUNSEO_ROOT="$HOME/JipMunseo-LLM-Wiki"
#   [ -f "$JIPMUNSEO_ROOT/scripts/macos/motd.sh" ] && source "$JIPMUNSEO_ROOT/scripts/macos/motd.sh"

REPO_ROOT="${JIPMUNSEO_ROOT:-$HOME/JipMunseo-LLM-Wiki}"
CHANGELOG="$REPO_ROOT/CHANGELOG.md"
SNAPSHOT_DIR="$REPO_ROOT/.local"
SNAPSHOT="$SNAPSHOT_DIR/changelog_snapshot.txt"

if [ -f "$CHANGELOG" ]; then
  mkdir -p "$SNAPSHOT_DIR"

  if [ -f "$SNAPSHOT" ]; then
    new_lines=$(diff "$SNAPSHOT" "$CHANGELOG" 2>/dev/null | grep '^> ' | sed 's/^> //' | grep -v '^[[:space:]]*$')
    if [ -n "$new_lines" ]; then
      echo ""
      echo "=== JipMunSeo 위키 업데이트 ==="
      echo "$new_lines" | sed 's/^/  /'
      echo "(전체 내역: $CHANGELOG)"
      echo ""
    fi
  fi

  cp "$CHANGELOG" "$SNAPSHOT"
fi
