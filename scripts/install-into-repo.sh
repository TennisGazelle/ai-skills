#!/usr/bin/env bash
# install-into-repo.sh — wire ai-skills (mounted as a submodule at
# .agents/ai-skills) into a consuming repo's .agents/skills/ and .claude/skills.
#
# Usage: ./.agents/ai-skills/scripts/install-into-repo.sh [consuming-repo-root]
#   Defaults to the current directory. Safe to re-run: updates stale symlinks,
#   prunes symlinks for skills removed upstream, and never touches real
#   (repo-local) skill directories.
set -euo pipefail

SUBMODULE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${SUBMODULE_ROOT}/skills"
TARGET_ROOT="$(cd "${1:-.}" && pwd)"
AGENTS_SKILLS="${TARGET_ROOT}/.agents/skills"
CLAUDE_DIR="${TARGET_ROOT}/.claude"

if [[ "$SUBMODULE_ROOT" != "${TARGET_ROOT}/.agents/ai-skills" ]]; then
  echo "WARNING: ai-skills is at ${SUBMODULE_ROOT}, not ${TARGET_ROOT}/.agents/ai-skills." >&2
  echo "         The documented convention is: git submodule add <url> .agents/ai-skills" >&2
fi

mkdir -p "$AGENTS_SKILLS"

# Link each global skill into .agents/skills/<name>
linked=0
for skill_path in "$SKILLS_DIR"/*/; do
  [[ -d "$skill_path" ]] || continue
  name="$(basename "$skill_path")"
  link="${AGENTS_SKILLS}/${name}"
  # Relative target from .agents/skills/ into the submodule
  rel_target="../ai-skills/skills/${name}"

  if [[ -L "$link" ]]; then
    if [[ "$(readlink "$link")" == "$rel_target" ]]; then
      linked=$((linked + 1))
      continue
    fi
    echo "Updating symlink: .agents/skills/${name}"
    rm "$link"
  elif [[ -e "$link" ]]; then
    echo "SKIP: .agents/skills/${name} exists and is not a symlink (repo-local skill?)" >&2
    continue
  fi
  ln -s "$rel_target" "$link"
  linked=$((linked + 1))
done

# Prune symlinks pointing into the submodule whose skill no longer exists
for entry in "$AGENTS_SKILLS"/*; do
  [[ -L "$entry" ]] || continue
  target="$(readlink "$entry")"
  case "$target" in
    ../ai-skills/skills/*)
      if [[ ! -e "$entry" ]]; then
        echo "Pruning stale symlink: .agents/skills/$(basename "$entry")"
        rm "$entry"
      fi
      ;;
  esac
done

# Claude Code reads .claude/skills — point it at .agents/skills
claude_link="${CLAUDE_DIR}/skills"
claude_target="../.agents/skills"
if [[ -L "$claude_link" ]]; then
  if [[ "$(readlink "$claude_link")" != "$claude_target" ]]; then
    echo "Updating symlink: .claude/skills"
    rm "$claude_link"
    ln -s "$claude_target" "$claude_link"
  fi
elif [[ -e "$claude_link" ]]; then
  echo "SKIP: .claude/skills exists and is not a symlink; move it aside to adopt the shared layout." >&2
else
  mkdir -p "$CLAUDE_DIR"
  ln -s "$claude_target" "$claude_link"
fi

echo
echo "Done. ${linked} global skill(s) linked into .agents/skills/."
echo "Commit .agents/ (and .claude/skills) so collaborators get the wiring."
