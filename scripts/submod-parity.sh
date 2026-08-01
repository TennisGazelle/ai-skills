#!/usr/bin/env bash
# submod-parity.sh — sync each git submodule to the parent branch tip (exact
# name match, with master↔main alias), re-vendor mapped skill trees into
# skills/, re-apply local adaptations, and refresh CATALOG.md.
#
# Usage:
#   ./scripts/submod-parity.sh [--branch <name>] [--dry-run] [--no-vendor]
#
# Does not commit. Prints a parity report to stdout.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BRANCH_OVERRIDE=""
DRY_RUN=0
NO_VENDOR=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch)
      BRANCH_OVERRIDE="${2:-}"
      [[ -n "$BRANCH_OVERRIDE" ]] || { echo "ERROR: --branch needs a value" >&2; exit 1; }
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-vendor)
      NO_VENDOR=1
      shift
      ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "ERROR: unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -n "$BRANCH_OVERRIDE" ]]; then
  PARENT_BRANCH="$BRANCH_OVERRIDE"
else
  PARENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  if [[ "$PARENT_BRANCH" == "HEAD" ]]; then
    echo "ERROR: detached HEAD. Pass --branch <name> to choose the equivalent submodule branch." >&2
    exit 1
  fi
fi

alias_for() {
  case "$1" in
    master) echo main ;;
    main) echo master ;;
    *) echo "" ;;
  esac
}

# Resolve which remote branch name to use for a submodule path.
# Prints the branch name, or empty if none.
resolve_submodule_branch() {
  local sub_path="$1"
  local want="$PARENT_BRANCH"
  local alt
  alt="$(alias_for "$want")"

  # Prefer exact match on origin
  if git -C "$sub_path" rev-parse --verify --quiet "refs/remotes/origin/${want}" >/dev/null; then
    echo "$want"
    return 0
  fi
  if [[ -n "$alt" ]] && git -C "$sub_path" rev-parse --verify --quiet "refs/remotes/origin/${alt}" >/dev/null; then
    echo "$alt"
    return 0
  fi
  echo ""
}

vendor_ponytail() {
  local name
  for name in ponytail ponytail-review ponytail-audit ponytail-debt ponytail-gain ponytail-help; do
    mkdir -p "skills/${name}"
    cp "lib/ponytail/skills/${name}/SKILL.md" "skills/${name}/SKILL.md"
  done
  mkdir -p skills/ponytail/references
  cp lib/ponytail/docs/platform-native.md skills/ponytail/references/platform-native.md
  ./scripts/ponytail-vendor-adapt.sh
}

mapfile -t SUBMODULES < <(git config --file .gitmodules --get-regexp path | awk '{print $2}')

if [[ ${#SUBMODULES[@]} -eq 0 ]]; then
  echo "ERROR: no submodules in .gitmodules" >&2
  exit 1
fi

echo "## Submodule parity report"
echo
echo "- Parent branch: \`${PARENT_BRANCH}\`"
echo "- Dry run: ${DRY_RUN}"
echo

declare -a REPORT_ROWS=()
UPDATED_ANY=0

for sub in "${SUBMODULES[@]}"; do
  if [[ ! -d "$sub/.git" && ! -f "$sub/.git" ]]; then
    echo "### ${sub}"
    echo "- status: **skipped** — not initialized (run \`git submodule update --init\`)"
    echo
    REPORT_ROWS+=("${sub}|skipped|uninitialized|")
    continue
  fi

  old_sha="$(git -C "$sub" rev-parse HEAD)"
  echo "### ${sub}"
  echo "- old SHA: \`${old_sha:0:12}\`"

  if [[ "$DRY_RUN" -eq 0 ]]; then
    git -C "$sub" fetch --prune origin
  else
    # Still fetch so resolution reflects remotes; dry-run only skips checkout/vendor
    git -C "$sub" fetch --prune origin >/dev/null 2>&1 || true
  fi

  target_branch="$(resolve_submodule_branch "$sub")"
  if [[ -z "$target_branch" ]]; then
    alt="$(alias_for "$PARENT_BRANCH")"
    reason="no remote branch \`${PARENT_BRANCH}\`"
    [[ -n "$alt" ]] && reason+=" or alias \`${alt}\`"
    echo "- status: **skipped** — ${reason}"
    echo
    REPORT_ROWS+=("${sub}|skipped|${reason}|${old_sha:0:12}")
    continue
  fi

  target_sha="$(git -C "$sub" rev-parse "refs/remotes/origin/${target_branch}")"
  echo "- target branch: \`origin/${target_branch}\`"
  echo "- target SHA: \`${target_sha:0:12}\`"

  if [[ "$old_sha" == "$target_sha" ]]; then
    echo "- status: already at tip"
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    echo "- status: **would update** (dry-run)"
    UPDATED_ANY=1
  else
    git -C "$sub" checkout -B "$target_branch" "refs/remotes/origin/${target_branch}"
    # Stage submodule pointer change in parent index is left to the user;
    # working tree submodule SHA is updated by checkout above.
    new_sha="$(git -C "$sub" rev-parse HEAD)"
    echo "- status: **updated** \`${old_sha:0:12}\` → \`${new_sha:0:12}\`"
    UPDATED_ANY=1
  fi
  echo
  REPORT_ROWS+=("${sub}|ok|origin/${target_branch}|${old_sha:0:12}->${target_sha:0:12}")
done

if [[ "$NO_VENDOR" -eq 0 ]]; then
  echo "### Re-vendor"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "- skipped (dry-run): would copy \`lib/ponytail/skills/*\` → \`skills/\` and adapt"
  elif [[ -d lib/ponytail/skills ]]; then
    vendor_ponytail
    echo "- refreshed ponytail skills + platform-native reference + adaptations"
  else
    echo "- skipped: \`lib/ponytail/skills\` missing"
  fi
  echo
fi

if [[ "$DRY_RUN" -eq 0 ]]; then
  echo "### Catalog"
  if [[ -f ./scripts/sync-catalog.py ]]; then
    python3 ./scripts/sync-catalog.py
    echo "- ran \`python3 ./scripts/sync-catalog.py\`"
  else
    echo "- skipped: sync-catalog.py missing"
  fi
  echo
fi

echo "### Summary"
for row in "${REPORT_ROWS[@]}"; do
  IFS='|' read -r path status detail sha <<<"$row"
  echo "- \`${path}\`: ${status}${detail:+ — ${detail}}${sha:+ (${sha})}"
done
echo
echo "Does **not** commit. Review \`git status\` / \`git diff\` and commit when ready."
if [[ "$UPDATED_ANY" -eq 0 && "$DRY_RUN" -eq 0 ]]; then
  echo "No submodule SHA changes were needed (vendored files may still have been refreshed)."
fi
