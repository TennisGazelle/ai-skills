#!/usr/bin/env bash
# ponytail-vendor-adapt.sh — re-apply local catalog adaptations after copying
# upstream SKILL.md files from lib/ponytail into skills/.
#
# Idempotent: safe to run after every submod-parity re-vendor.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SOURCE_BANNER='> **Source:** Vendored from [`lib/ponytail`](../../lib/ponytail) ([DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)). Refresh with `./scripts/submod-parity.sh`.'

PONYTAIL_SKILLS=(
  ponytail
  ponytail-review
  ponytail-audit
  ponytail-debt
  ponytail-gain
  ponytail-help
)

insert_source_banner() {
  local skill_md="$1"
  python3 - "$skill_md" "$SOURCE_BANNER" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
banner = sys.argv[2]
text = path.read_text(encoding="utf-8")
if "Vendored from [`lib/ponytail`]" in text:
    sys.exit(0)
if not text.startswith("---"):
    path.write_text(banner + "\n\n" + text, encoding="utf-8")
    sys.exit(0)
# Insert after closing --- of frontmatter
parts = text.split("---", 2)
if len(parts) < 3:
    path.write_text(banner + "\n\n" + text, encoding="utf-8")
    sys.exit(0)
# parts[0] is empty/prefix, parts[1] is yaml, parts[2] is body
body = parts[2].lstrip("\n")
path.write_text(f"---{parts[1]}---\n\n{banner}\n\n{body}", encoding="utf-8")
PY
}

for name in "${PONYTAIL_SKILLS[@]}"; do
  md="skills/${name}/SKILL.md"
  [[ -f "$md" ]] || { echo "SKIP adapt: missing $md" >&2; continue; }
  insert_source_banner "$md"
done

# Link platform-native reference on ladder rung 4
python3 - <<'PY'
from pathlib import Path
path = Path("skills/ponytail/SKILL.md")
text = path.read_text(encoding="utf-8")
needle = "4. **Native platform feature covers it?**"
ref = "See [references/platform-native.md](references/platform-native.md)."
if needle not in text:
    raise SystemExit("ponytail ladder rung 4 not found")
if "references/platform-native.md" not in text:
    old = (
        "4. **Native platform feature covers it?** "
        "`<input type=\"date\">` over a picker lib, CSS over JS, DB constraint over app code."
    )
    new = old + f" {ref}"
    if old not in text:
        raise SystemExit("ponytail rung 4 line text changed upstream; update adapt script")
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
PY

# Replace plugin Update section in help with submod-parity instructions
python3 - <<'PY'
from pathlib import Path
path = Path("skills/ponytail-help/SKILL.md")
text = path.read_text(encoding="utf-8")
new_update = """## Update

This catalog vendors ponytail from the `lib/ponytail` submodule. Refresh with:

```bash
./scripts/submod-parity.sh
```

Or invoke the `submod-parity` skill. That checks out the submodule branch matching
the parent branch (`master`↔`main` alias), re-copies skills into `skills/`, and
refreshes `CATALOG.md`. Do not use Claude Code `/plugin` marketplace update for
these vendored copies.
"""
import re
pattern = r"## Update\n\n.*?(?=\n## More\n)"
if "## Update" not in text:
    raise SystemExit("ponytail-help missing ## Update section")
if "submod-parity" in text and "./scripts/submod-parity.sh" in text.split("## Update", 1)[1].split("## More", 1)[0]:
    pass  # already adapted
else:
    text2, n = re.subn(pattern, new_update, text, count=1, flags=re.DOTALL)
    if n != 1:
        raise SystemExit("failed to replace ## Update in ponytail-help")
    path.write_text(text2, encoding="utf-8")
PY

echo "Adapted ponytail vendored skills under skills/"
