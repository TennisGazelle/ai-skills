#!/usr/bin/env bash
# promote.sh — move a repo-local skill into the global ai-skills catalog.
set -euo pipefail

usage() {
  echo "Usage: $0 <repo-path> <skill-name>" >&2
  echo "  Example: $0 ~/dev/my-project doc-audit-custom" >&2
  exit 1
}

[[ $# -eq 2 ]] || usage

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_PATH="$(cd "$1" && pwd)"
SKILL_NAME="$2"
SRC="${REPO_PATH}/.agents/skills/${SKILL_NAME}"
DEST="${REPO_ROOT}/skills/${SKILL_NAME}"

if [[ ! -d "$SRC" ]] || [[ ! -f "${SRC}/SKILL.md" ]]; then
  echo "ERROR: repo-local skill not found: ${SRC}/SKILL.md" >&2
  exit 1
fi

if [[ -e "$DEST" ]]; then
  echo "ERROR: global skill already exists: $DEST" >&2
  exit 1
fi

echo "Promoting ${SKILL_NAME} from ${REPO_PATH} to global catalog..."
mv "$SRC" "$DEST"

# Leave a symlink so the repo keeps working
mkdir -p "${REPO_PATH}/.agents/skills"
ln -s "${DEST}" "${REPO_PATH}/.agents/skills/${SKILL_NAME}"

python3 "${REPO_ROOT}/scripts/sync-catalog.py"
echo "Promoted ${SKILL_NAME}. Global copy: ${DEST}"
