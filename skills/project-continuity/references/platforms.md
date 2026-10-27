# Platform setup and compatibility

The skill's core workflow and project memory files use the open Agent Skills format and Markdown. Install the same skill folder into the host's skill directory. The host controls discovery, automatic selection, explicit invocation syntax, and project-level instructions; those behaviors are not portable merely by copying `SKILL.md`.

## Codex

- Personal installation: `~/.codex/skills/project-continuity/`
- Repository installation: `<repo>/.agents/skills/project-continuity/`
- Explicit invocation: `$project-continuity` (or select it from the skills UI)
- Project-level guidance: `AGENTS.md`
- `agents/openai.yaml` supplies Codex UI metadata and can be ignored by other hosts.

## Claude Code

- Personal installation: `~/.claude/skills/project-continuity/`
- Repository installation: `<repo>/.claude/skills/project-continuity/`
- Explicit invocation: `/project-continuity`; Claude Code may also select it automatically when relevant and allowed by its settings.
- Project-level guidance: `CLAUDE.md` or `.claude/CLAUDE.md`. The initializer prefers an existing root `CLAUDE.md`, then an existing `.claude/CLAUDE.md`, and with `--platform claude` updates it without adding an `AGENTS.md` import. Claude Code reads `AGENTS.md` and `.claude/AGENTS.md` by default (v2.1.277+) only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` applies in the working directory or above, so creating a new `CLAUDE.md` can hide them. When none applies, `--platform claude` updates a project-root `AGENTS.md` or `.claude/AGENTS.md` instead of creating a shadowing `CLAUDE.md`, and stops without changes if only a parent directory has an `AGENTS.md`. Some older sessions or configurations cannot read `AGENTS.md` at all. Use `--platform both` when both host files are required; the generated Claude file imports the root `AGENTS.md` with a relative `@.../AGENTS.md` reference, and it stops rather than hide another `AGENTS.md` it would not import. Existing inline imports (including `@./AGENTS.md`) are recognized, examples in code blocks, code spans, and HTML comments are not counted, and a `CLAUDE.md` symlink or hard link to `AGENTS.md` is updated only once without a self-import. See [Claude Code's AGENTS.md behavior](https://code.claude.com/docs/en/memory#agentsmd).
- Claude Code can read the `SKILL.md` and Markdown references, but does not use Codex's `agents/openai.yaml`.
- Claude Code also has built-in auto memory. Treat it as complementary: keep project requirements, shared decisions, and progress in the project's memory files, and avoid duplicating the same detailed note in both systems. See [Claude Code memory](https://code.claude.com/docs/en/memory).
- Claude Code's skill-directory substitution for bundled helper scripts is available in the loaded `SKILL.md` body. Executable commands are placed there; a separately loaded reference file or README must use a concrete path or a placeholder for the user to replace. See [Claude Code skill variables](https://code.claude.com/docs/en/skills#available-string-substitutions).

When the same repository is used with both Codex and Claude Code, add the same concise memory instruction to both `AGENTS.md` and `CLAUDE.md`, unless the repository already has an equivalent shared rule. Keep the memory itself in one shared `PROJECT_MEMORY.md` and optional `project-memory/` topic directory.

## Claude.ai

Use the same `project-continuity/` skill folder as Codex and Claude Code. Download or clone the repository and compress `skills/project-continuity/` only when uploading to Claude.ai; keep `SKILL.md` directly inside the `project-continuity/` folder in the archive. No separate Claude.ai source or prebuilt ZIP is maintained.

Enable Code execution and file creation, then open **Customize → Skills → + Create skill → Upload a skill** and upload the archive. Enable the skill and ask Claude to use `project-continuity`. See the current [Claude Skills guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude) for account requirements and interface details.

Provide project instructions, existing memory, and relevant project files in the conversation or Claude Project. Claude.ai cannot read local computer paths. Keep one shared project-memory record and make the latest saved version available in each conversation. Do not assume a local `AGENTS.md` or `CLAUDE.md` is loaded automatically. Run bundled helpers only against project files available in the execution environment, and return changed files to the user without claiming that local computer files were updated.

## Other Agent Skills-compatible hosts

The core `SKILL.md` and reference files can be reused where a host supports the Agent Skills format. Check that host's official documentation for skill directory, invocation, and project-instruction conventions. Adapt those integration details before claiming full host support. No background execution or guaranteed selection is provided by the format itself.

