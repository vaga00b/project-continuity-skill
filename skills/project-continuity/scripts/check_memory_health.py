#!/usr/bin/env python3
"""Read-only checks for project-memory links, size, index, and likely secrets."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\((<[^>]+>|(?:\\.|[^()\\])*(?:\([^()]*\)(?:\\.|[^()\\])*)*)\)")
SECRET_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("AWS-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("GitHub-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI-style-token", re.compile(r"\b(?:sk-(?:proj|svcacct)-[A-Za-z0-9_-]{24,}|sk-[A-Za-z0-9]{32,})\b")),
    ("Anthropic-style-token", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("Slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("Bearer-token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{20,}")),
    ("secret-like assignment", re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password|private[_-]?key)\b\s*[:=]\s*[\"']?([A-Za-z0-9_./+=-]{12,})")),
)
UNFILLED_DATE = re.compile(r"(?im)^>\s*Last updated:\s*YYYY-MM-DD\s*$")
PLACEHOLDERS = {"placeholder", "replace-me", "changeme", "redacted", "todo", "example", "none", "null"}


def markdown_files(root: Path, memory_file: Path) -> list[Path]:
    files = {memory_file}
    topic_dir = root / "project-memory"
    if topic_dir.is_dir():
        files.update(path for path in topic_dir.rglob("*.md") if path.is_file())
    return sorted(path for path in files if path.is_file())


def linked_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    else:
        target = target.split(maxsplit=1)[0] if target else ""
    return unquote(target)


def index_entry_count(lines: list[str]) -> int | None:
    start = None
    for index, line in enumerate(lines):
        if re.match(r"^#{1,6}\s+topic index\s*$", line, re.IGNORECASE):
            start = index + 1
            break
    if start is None:
        return None
    count = 0
    for line in lines[start:]:
        if re.match(r"^#{1,6}\s+", line):
            break
        if line.strip().startswith("|") and not re.match(r"^\s*\|?\s*:?-{3,}", line):
            count += 1
    return max(0, count - 1)  # Exclude the table header.


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project directory (default: current directory)")
    parser.add_argument("--memory-file", default="PROJECT_MEMORY.md", help="Overview/index file relative to project root")
    parser.add_argument("--max-index-entries", type=int, default=50, help="Warn above this many topic-index rows (default: 50)")
    parser.add_argument("--max-file-lines", type=int, default=500, help="Warn above this many lines in a memory file (default: 500)")
    args = parser.parse_args()

    try:
        root = args.project_root.expanduser().resolve(strict=True)
    except OSError as exc:
        print(f"ERROR: project root does not exist: {exc}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print("ERROR: --project-root must be a directory.", file=sys.stderr)
        return 2
    if args.max_index_entries < 0 or args.max_file_lines < 1:
        parser.error("limits must be non-negative, and --max-file-lines must be at least 1")

    memory_file = (root / args.memory_file).resolve()
    try:
        memory_file.relative_to(root)
    except ValueError:
        print("ERROR: --memory-file must stay inside the project root.", file=sys.stderr)
        return 2
    if not memory_file.is_file():
        print(f"ERROR: memory overview not found: {memory_file.relative_to(root)}")
        return 1

    findings = 0
    for file in markdown_files(root, memory_file):
        try:
            content = file.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print(f"ERROR: cannot read {file.relative_to(root)}: {exc}")
            findings += 1
            continue
        lines = content.splitlines()
        relative = file.relative_to(root)
        for match in UNFILLED_DATE.finditer(content):
            line_number = content.count("\n", 0, match.start()) + 1
            print(f"WARN: {relative}:{line_number} still has the starter date placeholder YYYY-MM-DD; replace it with the actual update date.")
            findings += 1
        if len(lines) > args.max_file_lines:
            print(f"WARN: {relative} has {len(lines)} lines (limit {args.max_file_lines}); consider splitting stable topics.")
            findings += 1

        for line_number, line in enumerate(lines, 1):
            for match in MARKDOWN_LINK.finditer(line):
                target = linked_target(match.group(1))
                parsed = urlsplit(target)
                if parsed.scheme or target.startswith("//") or not parsed.path:
                    continue
                linked_path = (file.parent / parsed.path).resolve()
                try:
                    linked_path.relative_to(root)
                except ValueError:
                    continue
                if not linked_path.exists():
                    print(f"ERROR: {relative}:{line_number} links to missing file {parsed.path}")
                    findings += 1

            for label, pattern in SECRET_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                if label == "secret-like assignment":
                    value = match.group(1).strip("\"'.,;:)")
                    if value.lower() in PLACEHOLDERS or len(value) < 16:
                        continue
                print(f"WARN: possible {label} at {relative}:{line_number}; value omitted. Review and remove or redact it if sensitive.")
                findings += 1
                break

        if file == memory_file:
            count = index_entry_count(lines)
            if count is not None and count > args.max_index_entries:
                print(f"WARN: topic index has {count} entries (limit {args.max_index_entries}); consolidate or archive topics.")
                findings += 1

    if findings:
        print(f"Memory health check found {findings} issue(s). No files were changed.")
        return 1
    print("Memory health check passed. No files were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

