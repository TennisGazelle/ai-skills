#!/usr/bin/env bash
# demote.sh — move a global skill into a repo's .agents/skills/.
set -euo pipefail

usage() {
  echo "Usage: $0 <skill-name> <repo-path>" >&2
  echo "  Example: $0 doc-audit-custom ~/dev/my-project" >&2
  exit 1
}

[[ $# -eq 2 ]] || usage

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="$1"
REPO_PATH="$(cd "$2" && pwd)"
SRC="${REPO_ROOT}/skills/${SKILL_NAME}"
DEST="${REPO_PATH}/.agents/skills/${SKILL_NAME}"

if [[ ! -d "$SRC" ]] || [[ ! -f "${SRC}/SKILL.md" ]]; then
  echo "ERROR: global skill not found: ${SRC}/SKILL.md" >&2
  exit 1
fi

if [[ -e "$DEST" ]]; then
  echo "ERROR: destination already exists: $DEST" >&2
  exit 1
fi

echo "Demoting ${SKILL_NAME} from global catalog to ${REPO_PATH}..."
mkdir -p "${REPO_PATH}/.agents/skills"
mv "$SRC" "$DEST"

python3 "${REPO_ROOT}/scripts/sync-catalog.py"
echo "Demoted ${SKILL_NAME}. Repo copy: ${DEST}"
