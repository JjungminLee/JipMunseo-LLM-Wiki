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
    new_lines=$(diff "$SNAPSHOT" "$CHANGELOG" 2>/dev/null | grep '^> ' | sed 's/^> //; s/^- //' | grep -v '^[[:space:]]*$')
    if [ -n "$new_lines" ]; then
      c_reset=$'\033[0m'
      c_rule=$'\033[38;5;73m'
      c_title=$'\033[1;38;5;117m'
      c_bullet=$'\033[38;5;150m'
      c_dim=$'\033[2;38;5;245m'
      rule="${c_rule}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${c_reset}"

      printf "\n%b\n" "$rule"
      printf "%b\n" "${c_title}  📚  JipMunSeo 위키 업데이트${c_reset}"
      printf "%b\n" "$rule"
      while IFS= read -r line; do
        printf "%b\n" "  ${c_bullet}▸${c_reset} ${line}"
      done <<< "$new_lines"
      printf "\n%b\n\n" "${c_dim}  전체 내역 → ${CHANGELOG}${c_reset}"
    fi
  fi

  cp "$CHANGELOG" "$SNAPSHOT"
fi
