#!/usr/bin/env bash
# bootstrap.sh — wire global skills into Cursor, Claude Code, and Codex.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${REPO_ROOT}/skills"
AGENTS_LINK="${HOME}/.agents/skills"
CLAUDE_LINK="${HOME}/.claude/skills"
CURSOR_LINK="${HOME}/.cursor/skills"

link_dir() {
  local target="$1"
  local link="$2"
  mkdir -p "$(dirname "$link")"
  if [[ -L "$link" ]]; then
    current="$(readlink -f "$link")"
    expected="$(readlink -f "$target")"
    if [[ "$current" == "$expected" ]]; then
      echo "OK: $link -> $target"
      return 0
    fi
    echo "Replacing existing symlink: $link (was -> $current)"
    rm "$link"
  elif [[ -e "$link" ]]; then
    echo "ERROR: $link exists and is not a symlink. Move it aside manually, then re-run." >&2
    exit 1
  fi
  ln -s "$target" "$link"
  echo "Linked: $link -> $target"
}

echo "ai-skills bootstrap"
echo "  repo:   $REPO_ROOT"
echo "  skills: $SKILLS_DIR"
echo

link_dir "$SKILLS_DIR" "$AGENTS_LINK"
link_dir "$SKILLS_DIR" "$CLAUDE_LINK"

# Cursor also reads ~/.cursor/skills; keep it in sync for older layouts.
link_dir "$SKILLS_DIR" "$CURSOR_LINK"

echo
echo "Done. Restart Cursor, Claude Code, and Codex to pick up skills."
echo "Run: python3 ${REPO_ROOT}/scripts/sync-catalog.py"
