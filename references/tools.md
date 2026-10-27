# Project memory scripts

Both scripts use only the Python standard library and do not access the network. They accept `--project-root` so they can run from any working directory.

## Initialize memory

Use the command for the current host. Claude Code substitutes its skill-directory token only in the loaded `SKILL.md` body, not in this reference or the README. The executable Claude Code commands are therefore included directly in `SKILL.md`; if copying a command from this reference, replace `<skill-dir>` with the actual installation directory.

Codex (replace `<skill-dir>` with the installed skill directory; use `py -3` on Windows if `python` is unavailable):

```shell
python <skill-dir>/scripts/init_memory.py --project-root . --platform codex
```

Claude Code on macOS/Linux (replace `<skill-dir>` manually when using this reference outside the loaded skill body):

```shell
python3 <skill-dir>/scripts/init_memory.py --project-root . --platform claude
```

Claude Code on Windows PowerShell (use `py -3` if `python` is unavailable):

```powershell
python <skill-dir>/scripts/init_memory.py --project-root . --platform claude
```

`--layout single` is the default. Use `--layout structured` when the project needs topic files; it creates the overview/index and `project-memory/decisions/`, `bugs/`, `modules/`, and `patterns/` directories at the project root.

`--memory-file` accepts a project-relative file path and defaults to `PROJECT_MEMORY.md`. Use it to reuse an established memory file elsewhere in the project, for example `--memory-file docs/PROJECT_MEMORY.md`. The path must stay inside the project root and must not name a directory. The generated project-instruction block points to the selected path. When using a non-root overview with topic files, keep topic links relative to that overview and the topic directory at the project root. The script refuses to switch a managed instruction pointer away from another existing memory file; move the file first or keep using its current path. It also checks instruction markers before creating or changing memory files, avoiding a partial initialization when markers are malformed.

If the selected path does not exist, the initializer searches for existing `PROJECT_MEMORY.md` and `PROJECT_CONTEXT.md` files outside common dependency, build, and cache directories. If it finds one elsewhere, it stops and asks you to pass that established path instead of creating a competing memory file. Pass `--force-new-memory` only when a separate file is intended, for example per-package memory in a monorepo; it does not bypass the check that stops a managed instruction pointer from being switched away from an existing memory file.

`--platform` accepts `codex`, `claude`, `both`, `auto`, or `none`. `auto` updates only existing instruction files; it intentionally creates none when no recognized file exists.

For `claude`, an existing root `CLAUDE.md` is preferred, then `.claude/CLAUDE.md`; it is updated without adding an `AGENTS.md` import. A new `CLAUDE.md` can change what Claude Code reads: by default it reads `AGENTS.md` and `.claude/AGENTS.md` (in the working directory and above) only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` applies. So:

- If none applies and the project root has `AGENTS.md` (or `.claude/AGENTS.md`), the script updates that file instead of creating a `CLAUDE.md` that would shadow it.
- If none applies and only a parent directory has an `AGENTS.md`, the script stops without changing files. Add the guidance to that file yourself, or create a `CLAUDE.md` that imports it (for example `@../AGENTS.md`) and rerun.
- If another CLAUDE file such as `CLAUDE.local.md` or a parent `CLAUDE.md` already applies, `AGENTS.md` is not being read anyway, so the script creates `CLAUDE.md` and says that it does not import `AGENTS.md`.

Use `--platform both` when both host files are needed. The Claude file imports the root `AGENTS.md` with a relative reference unless the two names are the same file (a symlink or hard link, which is updated once) or an equivalent import already exists. `both` stops without changing files if a new `CLAUDE.md` would hide a `.claude/AGENTS.md` or a parent `AGENTS.md` that it does not import. A dangling symlink among the instruction files is an error.

Imports are recognized when written inline as `@AGENTS.md` or `@./AGENTS.md`. The script treats text inside fenced code blocks (including indented, longer, or unclosed fences), inline code spans, and HTML comments as an example, not an import. How Claude Code itself treats HTML comments in imports is not documented, so verify it in a real session.

Existing project memory is never overwritten. The script replaces only its marked guidance block, preserves surrounding instructions, and keeps each file's existing line endings. Do not put custom text inside the markers; it is managed and may be replaced on rerun.

New memory files are starter templates. The agent must fill their date and seed useful project facts from reliable repository/user context; do not leave template placeholders as if they were current facts.

## Check memory health

Codex (replace `<skill-dir>` with the installed skill directory):

```shell
python <skill-dir>/scripts/check_memory_health.py --project-root .
```

Claude Code on macOS/Linux (replace `<skill-dir>` manually when using this reference outside the loaded skill body):

```shell
python3 <skill-dir>/scripts/check_memory_health.py --project-root .
```

Claude Code on Windows PowerShell:

```powershell
python <skill-dir>/scripts/check_memory_health.py --project-root .
```

The check is read-only. It checks the overview and topic Markdown files for missing local links, long files, oversized topic indexes, and likely secret values. Reports include only the file and line for possible secrets; the suspected value is never printed. These checks are heuristic, not a complete secret scanner, and findings need human review. It does not automatically redact content.

Defaults are 50 topic-index entries and 500 lines per memory file. Adjust them with `--max-index-entries` and `--max-file-lines`. Use `--memory-file` for an established overview path other than `PROJECT_MEMORY.md`; the topic scan still uses the root `project-memory/` directory.

The process exits with status 1 if it finds a missing file or any warning, 2 for invalid command arguments or an inaccessible root, and 0 if no issue is found. A clean result does not verify that the memory is factually or semantically consistent with the project.
