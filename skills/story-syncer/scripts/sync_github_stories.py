#!/usr/bin/env python3
"""Sync repository-local stories/*.md with GitHub issues via `gh`.

Portable version of the story sync tooling used by TennisGazelle/HexNets and
TennisGazelle/piggy-bank. It preserves repo-specific frontmatter keys and only
owns GitHub linkage fields: issue, title, labels, and sync.*.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

CHECKBOX_LINE = re.compile(r"^\s*-\s*\[([ xX])\]\s*")
DEFAULT_LABEL_COLOR = "ededed"
REPO_ROOT = Path.cwd()
STORIES_DIR = REPO_ROOT / "stories"
_REPO_LABEL_NAMES: set[str] | None = None


def resolve_repo_root(value: Path | None) -> Path:
    if value is not None:
        return value.expanduser().resolve()
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip()).resolve()
    return Path.cwd().resolve()


def gh_cli_repr(gh_args: list[str]) -> str:
    return "gh " + " ".join(repr(arg) if any(c.isspace() for c in arg) or not arg else arg for arg in gh_args)


def gh_failure_hints(combined: str) -> list[str]:
    text = combined.lower()
    hints: list[str] = []
    if any(
        marker in text
        for marker in (
            "network is unreachable",
            "no route to host",
            "connection refused",
            "connection reset",
            "connection timed out",
            "i/o timeout",
            "temporary failure in name resolution",
            "could not resolve host",
            "dial tcp",
            "tls: handshake",
            "certificate",
        )
    ):
        hints.append("Network: verify DNS/HTTPS first, e.g. `curl -I https://api.github.com`.")
    if any(marker in text for marker in ("401", "not logged in", "not authenticated", "bad credentials")):
        hints.append("Auth: run `gh auth login` and `gh auth status`; private repos may require repo scope/SSO.")
    if "403" in text or "permission" in text or "resource not accessible" in text:
        hints.append("Permissions: refresh token scopes or authorize organization SSO.")
    if ("404" in text or "not found" in text) and "label" not in text:
        hints.append("Repository: run `gh repo view` in the target repository and verify the selected remote.")
    if "label" in text and any(marker in text for marker in ("not found", "does not exist", "unknown", "invalid")):
        hints.append('Labels: inspect with `gh label list`; create manually with `gh label create "name" --color "ededed"`.')
    if "rate limit" in text:
        hints.append("Rate limit: retry later or authenticate for higher limits.")
    if not hints:
        hints.append("Re-run the same command with `GH_DEBUG=api` for verbose GitHub CLI traces.")
    return hints


def print_gh_failure(gh_args: list[str], proc: subprocess.CompletedProcess[str], *, context: str) -> None:
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    combined = f"{stdout}\n{stderr}".strip()
    print(f"error: gh failed ({context})", file=sys.stderr)
    print(f"  command: {gh_cli_repr(gh_args)}", file=sys.stderr)
    print(f"  exit code: {proc.returncode}", file=sys.stderr)
    if stdout:
        print("  --- stdout ---", file=sys.stderr)
        for line in stdout.splitlines():
            print(f"  {line}", file=sys.stderr)
    if stderr:
        print("  --- stderr ---", file=sys.stderr)
        for line in stderr.splitlines():
            print(f"  {line}", file=sys.stderr)
    print("  --- hints ---", file=sys.stderr)
    for hint in gh_failure_hints(combined):
        print(f"  - {hint}", file=sys.stderr)


def run_gh(gh_args: list[str], *, check: bool = True, context: str = "running gh") -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(["gh", *gh_args], cwd=REPO_ROOT, capture_output=True, text=True)
    if check and proc.returncode != 0:
        print_gh_failure(gh_args, proc, context=context)
        raise SystemExit(1)
    return proc


def parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    meta = yaml.safe_load(parts[1]) or {}
    if not isinstance(meta, dict):
        raise ValueError("story YAML frontmatter must be a mapping")
    body = parts[2]
    return meta, body[1:] if body.startswith("\n") else body


def dump_story(meta: dict[str, Any], body: str) -> str:
    head = yaml.safe_dump(meta, default_flow_style=False, allow_unicode=True, sort_keys=False).rstrip()
    return f"---\n{head}\n---\n\n{body.rstrip()}\n"


def normalize_body(text: str) -> str:
    return (text or "").replace("\r\n", "\n").strip()


def body_sha256(body: str) -> str:
    return hashlib.sha256(normalize_body(body).encode("utf-8")).hexdigest()


def checkbox_stats(text: str) -> tuple[int, int]:
    checked = total = 0
    for line in text.splitlines():
        match = CHECKBOX_LINE.match(line)
        if not match:
            continue
        total += 1
        checked += match.group(1).lower() == "x"
    return checked, total


def list_story_files(only: Path | None) -> list[Path]:
    if only is not None:
        path = only if only.is_absolute() else REPO_ROOT / only
        path = path.resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return [path]
    if not STORIES_DIR.is_dir():
        return []
    return sorted(STORIES_DIR.glob("[0-9][0-9][0-9]-*.md"))


def gh_issue_view_json(issue: int) -> dict[str, Any]:
    result = run_gh(
        ["issue", "view", str(issue), "--json", "title,body,labels,updatedAt"],
        context=f"loading issue #{issue}",
    )
    return json.loads(result.stdout)


def remote_label_names(remote: dict[str, Any]) -> list[str]:
    return [label["name"] for label in remote.get("labels") or []]


def gh_repo_label_names(*, refresh: bool = False) -> set[str]:
    global _REPO_LABEL_NAMES
    if refresh or _REPO_LABEL_NAMES is None:
        result = run_gh(["label", "list", "--json", "name", "-L", "500"], context="listing repository labels")
        _REPO_LABEL_NAMES = {row["name"] for row in json.loads(result.stdout)}
    return _REPO_LABEL_NAMES


def ensure_repo_labels(names: list[str], *, dry_run: bool) -> None:
    if not names:
        return
    existing = gh_repo_label_names()
    for name in sorted(set(names)):
        if name in existing:
            continue
        if dry_run:
            print(f"labels: would create {name!r}")
            continue
        run_gh(
            ["label", "create", name, "--color", DEFAULT_LABEL_COLOR, "--force"],
            context=f"creating repository label {name!r}",
        )
        existing.add(name)


def issue_push_needs(remote: dict[str, Any], *, title: str, body: str, labels: list[str]) -> tuple[bool, bool, bool]:
    return (
        title != remote.get("title"),
        normalize_body(body) != normalize_body(remote.get("body") or ""),
        set(remote_label_names(remote)) != set(labels),
    )


def sync_labels(issue: int, desired: list[str], current_names: list[str], *, dry_run: bool = False) -> None:
    ensure_repo_labels(desired, dry_run=dry_run)
    if dry_run:
        return
    want, have = set(desired), set(current_names)
    for label in sorted(want - have):
        run_gh(["issue", "edit", str(issue), "--add-label", label], context=f"adding label {label!r} to issue #{issue}")
    for label in sorted(have - want):
        run_gh(["issue", "edit", str(issue), "--remove-label", label], context=f"removing label {label!r} from issue #{issue}")


def sync_meta(meta: dict[str, Any], *, remote_updated: str, body: str) -> dict[str, Any]:
    meta = dict(meta)
    current = meta.get("sync")
    block = dict(current) if isinstance(current, dict) else {}
    block["last_remote_updated"] = remote_updated
    block["content_sha256"] = body_sha256(body)
    meta["sync"] = block
    return meta


def apply_remote_to_file(path: Path, remote: dict[str, Any], meta: dict[str, Any]) -> None:
    body = remote.get("body") or ""
    updated = dict(meta)
    updated["title"] = remote["title"]
    updated["labels"] = remote_label_names(remote)
    updated = sync_meta(updated, remote_updated=remote["updatedAt"], body=body)
    path.write_text(dump_story(updated, body), encoding="utf-8")


def write_temp_body_file(body: str) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".md",
        prefix=".story-body-",
        dir=REPO_ROOT,
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(body)
        return Path(tmp.name)


def cmd_pull(paths: list[Path], *, dry_run: bool) -> int:
    for path in paths:
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        issue = meta.get("issue")
        if issue is None:
            print(f"skip (no issue): {path.name}")
            continue
        if dry_run:
            print(f"pull: would update {path.name} from issue #{issue}")
            continue
        remote = gh_issue_view_json(int(issue))
        apply_remote_to_file(path, remote, meta)
        print(f"pulled: {path.name} <= issue #{issue}")
    return 0


def cmd_push(paths: list[Path], *, dry_run: bool) -> int:
    for path in paths:
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        title = str(meta.get("title") or "").strip()
        if not title:
            print(f"error: missing title in {path.name}", file=sys.stderr)
            return 1
        labels = list(meta.get("labels") or [])
        issue = meta.get("issue")

        if issue is None:
            if dry_run:
                print(f"push: would create issue from {path.name}")
                ensure_repo_labels(labels, dry_run=True)
                continue
            ensure_repo_labels(labels, dry_run=False)
            body_path = write_temp_body_file(body)
            try:
                command = ["issue", "create", "--title", title, "--body-file", str(body_path)]
                for label in labels:
                    command.extend(["--label", label])
                result = run_gh(command, context=f"creating issue from {path.name}")
            finally:
                body_path.unlink(missing_ok=True)
            match = re.search(r"/issues/(\d+)", result.stdout.strip())
            if not match:
                print(f"error: could not parse issue number from: {result.stdout.strip()}", file=sys.stderr)
                return 1
            new_issue = int(match.group(1))
            remote = gh_issue_view_json(new_issue)
            meta["issue"] = new_issue
            meta = sync_meta(meta, remote_updated=remote["updatedAt"], body=body)
            path.write_text(dump_story(meta, body), encoding="utf-8")
            print(f"created issue #{new_issue}: {path.name}")
            continue

        num = int(issue)
        remote = gh_issue_view_json(num)
        need_title, need_body, need_labels = issue_push_needs(remote, title=title, body=body, labels=labels)
        if dry_run:
            if not any((need_title, need_body, need_labels)):
                print(f"push: unchanged {path.name} (issue #{num})")
            else:
                if need_title or need_body:
                    print(f"push: would edit issue #{num} from {path.name}")
                if need_labels:
                    ensure_repo_labels(labels, dry_run=True)
                    print(f"push: would sync labels on #{num}: {sorted(set(labels))}")
            continue

        if need_title or need_body:
            body_path = write_temp_body_file(body)
            try:
                command = ["issue", "edit", str(num)]
                if need_title:
                    command.extend(["--title", title])
                if need_body:
                    command.extend(["--body-file", str(body_path)])
                run_gh(command, context=f"updating issue #{num} from {path.name}")
            finally:
                body_path.unlink(missing_ok=True)
        if need_labels:
            sync_labels(num, labels, remote_label_names(remote))

        remote2 = gh_issue_view_json(num)
        meta = sync_meta(meta, remote_updated=remote2["updatedAt"], body=body)
        path.write_text(dump_story(meta, body), encoding="utf-8")
        print(f"pushed: {path.name} => issue #{num}")
    return 0


def decide_sync_direction(local_body: str, remote_body: str, remote_updated: str, last_synced: str | None) -> str:
    local_checked, local_total = checkbox_stats(local_body)
    remote_checked, remote_total = checkbox_stats(remote_body or "")
    if remote_checked > local_checked:
        return "pull"
    if local_checked > remote_checked:
        return "push"
    if remote_total > local_total:
        return "pull"
    if local_total > remote_total:
        return "push"
    if normalize_body(local_body) == normalize_body(remote_body):
        return "push"
    if last_synced and remote_updated:
        if remote_updated > last_synced:
            return "pull"
        if last_synced > remote_updated:
            return "push"
    return "conflict"


def cmd_sync(paths: list[Path], *, dry_run: bool, force: str | None) -> int:
    for path in paths:
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        issue = meta.get("issue")
        if issue is None:
            print(f"sync: skip (no issue, use push to create): {path.name}")
            continue
        num = int(issue)
        remote = gh_issue_view_json(num)
        sync_block = meta.get("sync") if isinstance(meta.get("sync"), dict) else {}
        direction = decide_sync_direction(body, remote.get("body") or "", remote["updatedAt"], sync_block.get("last_remote_updated"))
        if force == "local":
            direction = "push"
        elif force == "remote":
            direction = "pull"
        if direction == "conflict":
            print(f"CONFLICT: {path.name} vs issue #{num}; use --force local or --force remote", file=sys.stderr)
            return 1
        if direction == "pull":
            if dry_run:
                print(f"sync: would pull GitHub -> {path.name} (issue #{num})")
            else:
                apply_remote_to_file(path, remote, meta)
                print(f"sync: pulled {path.name} <= issue #{num}")
        else:
            result = cmd_push([path], dry_run=dry_run)
            if result:
                return result
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync stories/*.md with GitHub issues.")
    parser.add_argument("--repo-root", type=Path, help="Target repository root; defaults to current git root")
    parser.add_argument("command", nargs="?", default="sync", choices=["pull", "push", "sync"])
    parser.add_argument("--only", type=Path, help="Restrict to one numbered story file")
    parser.add_argument("--issue", type=int, metavar="N", help="Restrict to the story linked to issue N")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", choices=["local", "remote"], help="For sync: always push local or pull remote")
    args = parser.parse_args()

    global REPO_ROOT, STORIES_DIR
    REPO_ROOT = resolve_repo_root(args.repo_root)
    STORIES_DIR = REPO_ROOT / "stories"

    try:
        paths = list_story_files(args.only)
    except FileNotFoundError as exc:
        print(f"No such story file: {exc}", file=sys.stderr)
        return 1
    if args.issue is not None:
        paths = [
            path
            for path in paths
            if parse_frontmatter(path.read_text(encoding="utf-8"))[0].get("issue") == args.issue
        ]
        if not paths:
            print(f"No story file linked to issue #{args.issue}", file=sys.stderr)
            return 1
    if not paths:
        print(f"No numbered story files in {STORIES_DIR}", file=sys.stderr)
        return 1

    if args.command == "pull":
        return cmd_pull(paths, dry_run=args.dry_run)
    if args.command == "push":
        return cmd_push(paths, dry_run=args.dry_run)
    return cmd_sync(paths, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
