#!/usr/bin/env python3
"""Initialize a TennisGazelle-style story backlog or scaffold its next story."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

STORY_RE = re.compile(r"^(\d{3})-(.+)\.md$")
README_TEMPLATE = """# Story Backlog

Local story files mirror GitHub issues one-to-one. GitHub is the external collaboration surface; this directory is the agent-friendly local copy for planning, status, and acceptance criteria.

## Naming

Use `NNN-kebab-slug.md`, where `NNN` is local recommended order. Keep the filename stable even if the GitHub title changes.

## Frontmatter

- `story`: stable local story id, matching `NNN`.
- `issue`: GitHub issue number, or `null` until created.
- `status`: `planned`, `in_progress`, `blocked`, `done`, or `wont_do`.
- `title`: GitHub issue title.
- `labels`: GitHub labels to apply when syncing.
- `sync.last_remote_updated`: last GitHub update timestamp, or `null`.
- `sync.content_sha256`: script-managed body hash, or `null`.

Stable identity is the filename plus `issue`, not the title.

## Commands

```bash
make stories-sync
```

The sync target pulls remote state first, then pushes local/new stories. Requires `gh` authenticated for this repository, Python 3, and PyYAML.
"""
MAKE_TARGET = """\n.PHONY: stories-sync\n\nstories-sync:\n\t@python3 scripts/sync_github_stories.py sync --force remote\n\t@python3 scripts/sync_github_stories.py push\n"""


def resolve_repo_root(value: Path | None) -> Path:
    if value is not None:
        return value.expanduser().resolve()
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False)
    if proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip()).resolve()
    return Path.cwd().resolve()


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    meta = yaml.safe_load(parts[1]) or {}
    return (meta if isinstance(meta, dict) else {}), parts[2].lstrip("\n")


def story_files(stories_dir: Path) -> list[Path]:
    result = []
    for path in stories_dir.glob("*.md") if stories_dir.is_dir() else []:
        if STORY_RE.match(path.name):
            result.append(path)
    return sorted(result, key=lambda path: int(STORY_RE.match(path.name).group(1)))


def slugify(title: str) -> str:
    text = title.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-") or "story"


def next_index(files: list[Path]) -> int:
    if not files:
        return 1
    return max(int(STORY_RE.match(path.name).group(1)) for path in files) + 1


def infer_body_style(recent: list[Path]) -> str:
    for path in reversed(recent[-3:]):
        _, body = parse_frontmatter(path)
        if "## User Story" in body:
            return "product"
        if "## Goal" in body or "## Why" in body or "## Tests" in body:
            return "research"
    return "product"


def format_story_id(index: int, previous: Any) -> Any:
    if isinstance(previous, str):
        return f"{index:03d}"
    return index


def infer_meta(files: list[Path], index: int, title: str, labels: list[str], phase: str | None) -> dict[str, Any]:
    if not files:
        return {
            "story": f"{index:03d}",
            "issue": None,
            "status": "planned",
            "title": title,
            "labels": labels,
            "sync": {"last_remote_updated": None, "content_sha256": None},
        }

    previous, _ = parse_frontmatter(files[-1])
    meta: dict[str, Any] = {}
    for key in previous:
        if key == "story":
            meta[key] = format_story_id(index, previous[key])
        elif key == "recommended_order":
            meta[key] = str(index) if isinstance(previous[key], str) else index
        elif key == "phase":
            if phase is not None:
                try:
                    meta[key] = int(phase) if isinstance(previous[key], int) else phase
                except ValueError:
                    meta[key] = phase
            else:
                meta[key] = previous[key]
        elif key == "issue":
            meta[key] = None
        elif key == "status":
            meta[key] = "planned"
        elif key == "title":
            meta[key] = title
        elif key == "labels":
            meta[key] = labels
        elif key == "sync":
            meta[key] = {"last_remote_updated": None, "content_sha256": None}
        else:
            # Unknown fields are part of the local schema, but their values may be
            # story-specific. Preserve the key with a neutral null for review.
            meta[key] = None

    # Ensure core fields exist even if an older story omitted one.
    if "story" not in meta:
        meta["story"] = f"{index:03d}"
    if "issue" not in meta:
        meta["issue"] = None
    if "title" not in meta:
        meta["title"] = title
    if "labels" not in meta:
        meta["labels"] = labels
    return meta


def render_body(title: str, style: str) -> str:
    if style == "research":
        return f"""# {title}\n\n## Goal\n\nTODO: state the concrete outcome.\n\n## Why\n\nTODO: explain why this work belongs now.\n\n## Scope\n\n- [ ] TODO\n\n## Tests\n\n- [ ] TODO\n\n## Acceptance criteria\n\n- [ ] TODO\n\n## Out of scope\n\n- TODO\n"""
    return f"""# {title}\n\n## User Story\n\nAs a ..., I want ..., so that ...\n\n## Acceptance Criteria\n\n- [ ] TODO\n\n## Notes\n\n- Link canonical docs instead of copying long context.\n"""


def dump_story(meta: dict[str, Any], body: str) -> str:
    head = yaml.safe_dump(dict(meta), default_flow_style=False, allow_unicode=True, sort_keys=False).rstrip()
    return f"---\n{head}\n---\n\n{body.rstrip()}\n"


def install_sync_tool(repo_root: Path, *, dry_run: bool) -> list[Path]:
    changed: list[Path] = []
    target = repo_root / "scripts" / "sync_github_stories.py"
    source = Path(__file__).resolve().parents[2] / "story-syncer" / "scripts" / "sync_github_stories.py"
    if not target.exists():
        if not source.is_file():
            print(f"warning: sibling story-syncer script not found at {source}; sync tool not copied", file=sys.stderr)
        else:
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                target.chmod(target.stat().st_mode | 0o111)
            changed.append(target)

    makefile = repo_root / "Makefile"
    current = makefile.read_text(encoding="utf-8") if makefile.exists() else ""
    if re.search(r"(?m)^stories-sync\s*:", current) is None:
        new_text = current.rstrip() + ("\n" if current.strip() else "") + MAKE_TARGET.lstrip("\n")
        if not dry_run:
            makefile.write_text(new_text.rstrip() + "\n", encoding="utf-8")
        changed.append(makefile)
    return changed


def initialize(repo_root: Path, *, dry_run: bool) -> list[Path]:
    stories = repo_root / "stories"
    readme = stories / "README.md"
    changed: list[Path] = []
    if not readme.exists():
        if not dry_run:
            stories.mkdir(parents=True, exist_ok=True)
            readme.write_text(README_TEMPLATE, encoding="utf-8")
        changed.append(readme)
    changed.extend(install_sync_tool(repo_root, dry_run=dry_run))
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize stories/ or scaffold the next numbered story.")
    parser.add_argument("--repo-root", type=Path, help="Target repository root; defaults to current git root")
    parser.add_argument("--title", help="Story title; omit with --init-only")
    parser.add_argument("--labels", default="", help="Comma-separated labels")
    parser.add_argument("--phase", help="Phase value when the local schema uses phase")
    parser.add_argument("--body-style", choices=["auto", "product", "research"], default="auto")
    parser.add_argument("--init-only", action="store_true", help="Initialize stories/tooling but do not create a story")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = resolve_repo_root(args.repo_root)
    stories = repo_root / "stories"
    was_missing = not stories.is_dir()
    changed = initialize(repo_root, dry_run=args.dry_run) if was_missing else []

    if args.init_only:
        for path in changed:
            print(f"{'would create' if args.dry_run else 'created'}: {path.relative_to(repo_root)}")
        return 0
    if not args.title:
        parser.error("--title is required unless --init-only is used")

    files = story_files(stories) if stories.is_dir() else []
    index = next_index(files)
    labels = [item.strip() for item in args.labels.split(",") if item.strip()]
    style = infer_body_style(files) if args.body_style == "auto" else args.body_style
    meta = infer_meta(files, index, args.title.strip(), labels, args.phase)
    filename = f"{index:03d}-{slugify(args.title)}.md"
    target = stories / filename
    if target.exists():
        print(f"error: target already exists: {target}", file=sys.stderr)
        return 1

    body = render_body(args.title.strip(), style)
    if args.dry_run:
        print(f"would create: {target.relative_to(repo_root)}")
        print(dump_story(meta, body))
        return 0

    stories.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_story(meta, body), encoding="utf-8")
    print(f"created: {target.relative_to(repo_root)}")
    if was_missing:
        for path in changed:
            if path != target:
                print(f"initialized: {path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
