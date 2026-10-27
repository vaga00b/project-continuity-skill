#!/usr/bin/env python3
"""Initialize project memory without overwriting existing project content."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys


START_MARKER = "<!-- project-memory:begin -->"
END_MARKER = "<!-- project-memory:end -->"


def guidance(memory_file: str) -> str:
    return f"""{START_MARKER}
## Project memory

At the start of each development task, read `{memory_file}` and any linked notes relevant to the task before planning or editing. Before finishing, record meaningful decisions, milestones, blockers, and the next step. Verify saved files before claiming changes are complete.
{END_MARKER}"""


FENCE_OPEN = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")


def strip_fenced_blocks(text: str) -> str:
    """Drop fenced code blocks, including indented, longer, and unclosed fences.

    An opening fence runs until a closing fence of the same character that is at
    least as long, or to the end of the file when it is never closed.
    """
    kept: list[str] = []
    fence_char = ""
    fence_length = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if not fence_char:
            opening = FENCE_OPEN.match(content)
            # A backtick fence cannot carry backticks in its info string; that is a code span.
            if opening and not (opening.group(1)[0] == "`" and "`" in opening.group(2)):
                fence_char = opening.group(1)[0]
                fence_length = len(opening.group(1))
                continue
            kept.append(line)
        elif re.match(rf"^[ \t]*{re.escape(fence_char)}{{{fence_length},}}[ \t]*$", content):
            fence_char = ""
    return "".join(kept)


def strip_comments_and_code_spans(text: str) -> str:
    """Remove closed HTML comments and same-line code spans in the order they appear."""
    pieces: list[str] = []
    index = 0
    length = len(text)
    while index < length:
        if text.startswith("<!--", index):
            end = text.find("-->", index + 4)
            if end != -1:
                index = end + 3
                continue
        elif text[index] == "`":
            run_end = index
            while run_end < length and text[run_end] == "`":
                run_end += 1
            run = run_end - index
            line_end = text.find("\n", run_end)
            line_end = length if line_end == -1 else line_end
            closing = re.search(r"(?<!`)" + "`" * run + r"(?!`)", text[run_end:line_end])
            if closing:
                index = run_end + closing.end()
                continue
            pieces.append(text[index:run_end])
            index = run_end
            continue
        pieces.append(text[index])
        index += 1
    return "".join(pieces)


def has_markdown_import(text: str, import_target: str) -> bool:
    """Recognize active Markdown imports while ignoring code blocks, code spans, and HTML comments."""
    active = strip_comments_and_code_spans(strip_fenced_blocks(text))
    return re.search(rf"(?<![\w./])@(?:\./)?{re.escape(import_target)}(?![\w.-])", active) is not None


def starter_memory(layout: str) -> str:
    topic_index = ""
    if layout == "structured":
        topic_index = """## Topic index

Add a row when you create a durable topic note. Read only notes relevant to the current task.

| Topic | Read when | File |
|---|---|---|

"""
    return f"""# Project Memory

> Last updated: YYYY-MM-DD

## Project snapshot
- **Goal and scope:**
- **Current status:**
- **Key constraints:**
- **Architecture / key locations:**

{topic_index}## Decisions and requirements
-

## Open questions and blockers
-

## Reusable repair lessons
-

## Next steps
1.

## Progress log
"""


def ensure_topic_index(path: Path) -> bool:
    """Add the structured-memory index section without replacing existing notes."""
    text = path.read_bytes().decode("utf-8")
    if "## Topic index" in text:
        return False
    newline = "\r\n" if "\r\n" in text else "\n"
    section = """## Topic index

Add a row when you create a durable topic note. Read only notes relevant to the current task.

| Topic | Read when | File |
|---|---|---|

""".replace("\n", newline)
    marker = "## Decisions and requirements"
    if marker in text:
        position = text.index(marker)
        text = text[:position] + section + text[position:]
    else:
        text = text.rstrip() + newline * 2 + section
    path.write_bytes(text.encode("utf-8"))
    return True


def add_guidance(path: Path, memory_file: str, import_target: str | None = None, label: str | None = None) -> tuple[str, str]:
    label = label or path.name
    existed = path.exists()
    try:
        text = path.read_bytes().decode("utf-8") if existed else ""
    except (OSError, UnicodeError, RuntimeError) as exc:
        return "error", f"Cannot read {label}: {exc}"

    # Keep the file's own line endings; only text this script adds follows them.
    newline = "\r\n" if "\r\n" in text else "\n"
    managed_block = guidance(memory_file).replace("\n", newline)
    original_text = text
    if import_target and not has_markdown_import(text, import_target):
        text = f"@{import_target}{newline}{newline}" + text

    start_count = text.count(START_MARKER)
    end_count = text.count(END_MARKER)
    if start_count != end_count or start_count > 1:
        return "error", f"Managed project-memory markers are inconsistent in {label}; left unchanged."
    if start_count == 1:
        start = text.index(START_MARKER)
        end_start = text.index(END_MARKER)
        if end_start < start:
            return "error", f"Managed project-memory markers are out of order in {label}; left unchanged."
        end = end_start + len(END_MARKER)
        updated = text[:start] + managed_block + text[end:]
        if updated == original_text:
            return "unchanged", f"Project-memory guidance already current in {label}."
    else:
        updated = text.rstrip()
        if updated:
            updated += newline * 2
        updated += managed_block + newline

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(updated.encode("utf-8"))
    except OSError as exc:
        return "error", f"Cannot write {label}: {exc}"
    return "created" if not existed else "updated", f"Added project-memory guidance to {label}."


def counting_claude_files(root: Path) -> list[Path]:
    """CLAUDE files that make Claude Code stop reading AGENTS.md (working directory and above)."""
    try:
        home = Path.home().resolve()
    except (OSError, RuntimeError):
        home = None
    found: list[Path] = []
    for directory in (root, *root.parents):
        for relative in ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md"):
            if relative == ".claude/CLAUDE.md" and home is not None and directory == home:
                continue  # the user-level file does not count
            candidate = directory / relative
            if candidate.is_file():
                found.append(candidate)
    return found


def readable_agents_files(root: Path) -> list[Path]:
    """AGENTS.md files Claude Code reads by default when no CLAUDE file applies."""
    found: list[Path] = []
    for directory in (root, *root.parents):
        for relative in ("AGENTS.md", ".claude/AGENTS.md"):
            candidate = directory / relative
            if candidate.is_file():
                found.append(candidate)
    return found


def shadow_error(root: Path, shadowed: list[Path]) -> str:
    shown = ", ".join(Path(os.path.relpath(path, root)).as_posix() for path in shadowed)
    example = Path(os.path.relpath(shadowed[0], root)).as_posix()
    return (
        f"ERROR: creating a CLAUDE.md here would stop Claude Code from reading {shown}; no files were changed. "
        f"Add the guidance to that file yourself, or create a CLAUDE.md that imports it (for example `@{example}`) "
        "and rerun, or use --platform none."
    )


def select_instruction_files(root: Path, platform: str) -> tuple[tuple[Path, ...], bool, tuple[str, ...], str | None]:
    """Return (files to update, import AGENTS.md into the Claude file, INFO notices, error)."""
    agents_file = root / "AGENTS.md"
    dot_agents_file = root / ".claude" / "AGENTS.md"
    claude_candidates = (root / "CLAUDE.md", root / ".claude" / "CLAUDE.md")

    relevant = {
        "auto": (agents_file, dot_agents_file, *claude_candidates),
        "codex": (agents_file,),
        "claude": (*claude_candidates, agents_file, dot_agents_file),
        "both": (agents_file, dot_agents_file, *claude_candidates),
        "none": (),
    }[platform]
    for path in relevant:
        if path.is_symlink() and not path.exists():
            return (), False, (), f"ERROR: {path.relative_to(root).as_posix()} is a dangling symlink; fix or remove it first; no files were changed."

    existing_claude_file = next((path for path in claude_candidates if path.exists()), None)
    claude_file = existing_claude_file or claude_candidates[0]
    notices: list[str] = []

    if platform == "auto":
        files_list: list[Path] = []
        for path in (agents_file, existing_claude_file):
            if path is not None and path.exists() and not any(same_file(path, prior) for prior in files_list):
                files_list.append(path)
        files = tuple(files_list)
        if not files:
            notices.append("No recognized project instruction file found; pass --platform codex, claude, or both to create one.")
        return files, False, tuple(notices), None
    if platform == "none":
        return (), False, (), None
    if platform == "codex":
        return (agents_file,), False, (), None
    if platform == "claude":
        if existing_claude_file is not None:
            # Do not import AGENTS.md merely because the Claude host was selected:
            # a user's existing CLAUDE.md may intentionally contain different guidance.
            return (existing_claude_file,), False, (), None
        shared = next((path for path in (agents_file, dot_agents_file) if path.exists()), None)
        if counting_claude_files(root):
            # Another CLAUDE file (for example CLAUDE.local.md or one in a parent directory) already
            # applies, so Claude Code is not reading AGENTS.md; a new CLAUDE.md shadows nothing more.
            if shared is not None:
                notices.append(
                    "Another CLAUDE file already applies, so Claude Code is not reading "
                    f"{shared.relative_to(root).as_posix()}; the new CLAUDE.md does not import it. "
                    "Use --platform both to import AGENTS.md."
                )
            return (claude_file,), False, tuple(notices), None
        if shared is not None:
            notices.append(
                f"No CLAUDE.md was created because current Claude Code reads {shared.relative_to(root).as_posix()} by default "
                "when no CLAUDE file applies. If this Claude Code session cannot load AGENTS.md, use --platform both to create "
                "a CLAUDE.md that imports the existing file."
            )
            return (shared,), False, tuple(notices), None
        shadowed = readable_agents_files(root)
        if shadowed:
            return (), False, (), shadow_error(root, shadowed)
        return (claude_file,), False, (), None

    # `both`: maintain Codex guidance and make Claude's file import shared AGENTS.md.
    if existing_claude_file is not None and agents_file.exists() and same_file(existing_claude_file, agents_file):
        return (agents_file,), False, ("CLAUDE.md resolves to AGENTS.md; updated the shared file once and skipped a self-import.",), None
    if existing_claude_file is None and not counting_claude_files(root):
        shadowed = [path for path in readable_agents_files(root) if path != agents_file]
        if shadowed:
            return (), False, (), shadow_error(root, shadowed)
    return (agents_file, claude_file), True, (), None


def same_file(first: Path, second: Path) -> bool:
    try:
        if first.resolve() == second.resolve():
            return True
    except (OSError, RuntimeError):
        pass
    try:
        return first.samefile(second)
    except OSError:
        return False


def validate_instruction_file(root: Path, path: Path) -> str | None:
    if path.is_symlink() and not path.exists():
        return f"ERROR: instruction path is a dangling symlink: {path.name}; no files were changed."
    try:
        path.resolve().relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return f"ERROR: instruction path escapes the project root: {path}; no files were changed."
    if not path.exists():
        return None
    if not path.is_file():
        return f"ERROR: instruction path is not a file: {path.name}; no files were changed."
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return f"ERROR: cannot read {path.name}: {exc}; no files were changed."
    starts = [match.start() for match in re.finditer(re.escape(START_MARKER), text)]
    ends = [match.start() for match in re.finditer(re.escape(END_MARKER), text)]
    if len(starts) != len(ends) or len(starts) > 1:
        return f"ERROR: managed project-memory markers are inconsistent in {path.name}; no files were changed."
    if starts and ends[0] < starts[0]:
        return f"ERROR: managed project-memory markers are out of order in {path.name}; no files were changed."
    return None


def existing_memory_pointer_conflict(root: Path, target: Path) -> str | None:
    """Prevent changing a managed pointer away from another existing memory file."""
    candidates = (root / "AGENTS.md", root / "CLAUDE.md", root / ".claude" / "CLAUDE.md")
    for instruction_file in candidates:
        if not instruction_file.is_file():
            continue
        try:
            instruction_file.resolve().relative_to(root)
        except (OSError, RuntimeError, ValueError):
            continue
        try:
            text = instruction_file.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        start = text.find(START_MARKER)
        end = text.find(END_MARKER)
        if start < 0 or end < start:
            continue
        managed = text[start:end]
        match = re.search(r"read `([^`]+)` and any linked notes", managed)
        if not match:
            continue
        try:
            previous = (root / match.group(1)).resolve()
        except (OSError, RuntimeError):
            continue
        try:
            previous.relative_to(root)
        except ValueError:
            continue
        if previous != target and previous.is_file():
            return (
                f"ERROR: {instruction_file.relative_to(root).as_posix()} still points to existing memory "
                f"{previous.relative_to(root).as_posix()}; refusing to create or switch to "
                f"{target.relative_to(root).as_posix()} and leave an orphaned copy. "
                "Move the existing memory file first or rerun with its current --memory-file path."
            )
    return None


def find_existing_memory_files(root: Path, target: Path) -> list[Path]:
    """Find likely existing project memory files before creating a competing one."""
    names = {"PROJECT_MEMORY.md", "PROJECT_CONTEXT.md"}
    skipped_dirs = {
        ".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules",
        "vendor", "build", "dist", "target", "__pycache__", ".next",
        ".tox", ".nox", ".cache", ".pytest_cache", ".mypy_cache", ".gradle",
        ".terraform", "coverage", "Pods",
    }
    found: list[Path] = []
    for current, directories, filenames in os.walk(root, topdown=True, followlinks=False):
        directories[:] = [name for name in directories if name not in skipped_dirs]
        for name in filenames:
            if name not in names:
                continue
            candidate_path = Path(current) / name
            try:
                candidate = candidate_path.resolve()
                candidate.relative_to(root)
            except (OSError, RuntimeError, ValueError):
                continue
            if candidate != target and candidate.is_file():
                found.append(candidate)
    return sorted(set(found))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project directory (default: current directory)")
    parser.add_argument("--memory-file", default="PROJECT_MEMORY.md", help="Project-relative overview/index path (default: PROJECT_MEMORY.md)")
    parser.add_argument("--layout", choices=("single", "structured"), default="single", help="Memory layout (default: single)")
    parser.add_argument("--platform", choices=("auto", "codex", "claude", "both", "none"), default="auto", help="Project instruction file(s) to update (default: existing files only)")
    parser.add_argument(
        "--force-new-memory",
        action="store_true",
        help="Create the memory file even when other PROJECT_MEMORY.md/PROJECT_CONTEXT.md files exist (for example per-package memory in a monorepo)",
    )
    args = parser.parse_args()

    try:
        root = args.project_root.expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: project root does not exist: {exc}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print("ERROR: --project-root must be a directory.", file=sys.stderr)
        return 2

    if not args.memory_file.strip():
        print("ERROR: --memory-file must name a file inside the project root.", file=sys.stderr)
        return 2
    requested_memory_file = Path(args.memory_file)
    if requested_memory_file.is_absolute():
        print("ERROR: --memory-file must be a path relative to --project-root.", file=sys.stderr)
        return 2
    try:
        memory_file = (root / requested_memory_file).resolve()
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: cannot resolve --memory-file: {exc}", file=sys.stderr)
        return 2
    try:
        memory_relative = memory_file.relative_to(root)
    except ValueError:
        print("ERROR: --memory-file must stay inside the project root.", file=sys.stderr)
        return 2
    if memory_file == root:
        print("ERROR: --memory-file must name a file, not the project root directory.", file=sys.stderr)
        return 2
    memory_display_path = memory_relative.as_posix()
    if memory_file.exists() and not memory_file.is_file():
        print(f"ERROR: --memory-file is not a file: {memory_display_path}; no files were changed.", file=sys.stderr)
        return 2

    instruction_files, import_agents, notices, select_error = select_instruction_files(root, args.platform)
    for notice in notices:
        print(f"INFO: {notice}")
    if select_error:
        print(select_error, file=sys.stderr)
        return 1
    for instruction_file in instruction_files:
        issue = validate_instruction_file(root, instruction_file)
        if issue:
            print(issue, file=sys.stderr)
            return 1
    pointer_conflict = existing_memory_pointer_conflict(root, memory_file)
    if pointer_conflict:
        print(pointer_conflict, file=sys.stderr)
        return 1
    if not memory_file.exists():
        existing_memories = find_existing_memory_files(root, memory_file)
        if existing_memories:
            paths = ", ".join(path.relative_to(root).as_posix() for path in existing_memories)
            if args.force_new_memory:
                print(
                    f"INFO: other project memory file(s) exist ({paths}); creating {memory_display_path} "
                    "because --force-new-memory was given."
                )
            else:
                print(
                    f"ERROR: found existing project memory file(s): {paths}. "
                    "Use --memory-file with the established path, or pass --force-new-memory if a separate "
                    "memory file is intended (for example per-package memory); no files were changed.",
                    file=sys.stderr,
                )
                return 1

    if memory_file.exists():
        print(f"PRESERVED: {memory_display_path} already exists; its existing notes were not overwritten.")
        if args.layout == "structured":
            try:
                if ensure_topic_index(memory_file):
                    print(f"UPDATED: added a topic index to {memory_display_path} for the structured layout.")
                else:
                    print(f"UNCHANGED: {memory_display_path} already has a topic index.")
            except (OSError, UnicodeError) as exc:
                print(f"ERROR: cannot update the topic index: {exc}", file=sys.stderr)
                return 2
    else:
        try:
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            memory_file.write_text(starter_memory(args.layout), encoding="utf-8")
            print(f"CREATED: {memory_display_path} ({args.layout} layout)")
        except OSError as exc:
            print(f"ERROR: cannot create {memory_display_path}: {exc}", file=sys.stderr)
            return 2

    if args.layout == "structured":
        for folder in ("decisions", "bugs", "modules", "patterns"):
            (root / "project-memory" / folder).mkdir(parents=True, exist_ok=True)
        print("READY: project-memory/{decisions,bugs,modules,patterns}/")

    errors = 0
    for path in instruction_files:
        import_target = None
        if import_agents and path.name == "CLAUDE.md":
            import_target = "AGENTS.md" if path.parent == root else "../AGENTS.md"
        status, message = add_guidance(path, memory_display_path, import_target, path.relative_to(root).as_posix())
        print(f"{status.upper()}: {message}")
        errors += status == "error"
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
