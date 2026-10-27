---
name: project-continuity
description: Maintain durable context and progress notes for software projects across tasks and coding sessions. Use during any project development task to check and apply existing project memory, and when the user asks to record, recall, or track project information.
metadata:
  short-description: Keep project context and progress current
---

# Project Continuity

Keep important project decisions and progress available across context switches. The record should help the next work session act accurately, not become a transcript.

## Every project task

- If the user invokes this skill at the start of a conversation, keep it active for the rest of that conversation. Do not ask them to invoke it again for later development tasks in the same conversation. Apply the read, consult, and update workflow to each relevant task and milestone until the conversation ends.
- At the start of every software project task, inspect project guidance and look for the established project memory before planning or editing. Read it and use its relevant requirements, decisions, constraints, and next steps throughout the task.
- When this skill is explicitly invoked for a project that is not configured yet, bootstrap it in that same turn: identify the host's project-instruction mechanism, add a focused instruction to consult and update project memory, and create or initialize the project's memory file from reliable context already available. Invocation for project setup counts as a request to configure the project. If an instruction file already exists, preserve unrelated content and make only a non-duplicating, focused update. For the Codex and Claude Code file names and installation/invocation differences, read [references/platforms.md](references/platforms.md). For another Agent Skills-compatible host, use its documented project-instruction mechanism; do not assume a platform-specific filename or command.
- For first-time setup, use the `init_memory.py` helper when available. Pass the current project root, chosen `single` or `structured` layout, host platform, and any established non-default memory path. Do not rely on `auto` to create an instruction file; select the host explicitly. The script preserves existing memory and unrelated instruction content. Text inside its marked guidance block is managed by the script and may be replaced on rerun; keep custom instructions outside the markers. Use the platform-specific command below and see [references/tools.md](references/tools.md) for options. If the script stops because it found an existing memory file, rerun with that path in `--memory-file`; use `--force-new-memory` only when the user wants a separate memory file. If it stops because a new `CLAUDE.md` would hide an `AGENTS.md`, follow its message instead of overriding it.
- If the project has no memory file, create one when project context can be usefully carried forward. Seed it only with reliable information from the user's instructions and repository; mark unknowns as unknown and do not invent a roadmap. For a trivial, one-off change with no durable context, skip creating an empty file.
- When the user asks to record, remember, summarize, or follow up project information, update the project memory as part of that request, even if the change would otherwise be too small to log.
- When the user corrects an implementation, edits the proposed fix, or clarifies how an issue should behave, capture the reusable lesson in project memory when it is likely to help with a similar future issue. Record the symptom or context, the user's chosen or confirmed rule, any stated reason, and the outcome or validation if known. Distinguish a confirmed requirement from an actual code repair: if the current code already complies, say that no behavior change was needed instead of implying a fix was made.
- If the user has edited project files during the task, inspect the relevant available diff or file changes before continuing, preserve those edits, and distinguish them from agent-authored changes. Attribute a repair choice to the user only when the conversation or visible changes support that attribution; otherwise ask or leave the author/reason unspecified.
- When available, record concise evidence for a reusable lesson, such as the relevant file path, visible diff, or explicit user statement. State whether the outcome was tested; never imply a test passed when it was not run.
- Before solving a related issue, search the recorded lessons for similar symptoms and approaches. Reuse a lesson when it fits the current evidence, and verify the fix against the current code rather than applying it mechanically.
- Before claiming a code or documentation change is complete, inspect the saved source files and confirm they contain the claimed change. Compare the final summary and project memory with the on-disk implementation. If the implementation is absent or incomplete, report it as pending and record the actual state; never infer completion from a plan, intention, or earlier assistant summary.
- After initializing or meaningfully updating project memory, run the health-check helper when practical for either layout. It is read-only; review and fix reported issues without copying any detected secret values into chat or logs. Use the platform-specific command below.
- Recheck it before consequential decisions or changes that depend on earlier constraints, and when a conflict or apparent reversal appears.
- After completing a meaningful milestone, changing an agreed decision, discovering a durable constraint, or identifying a blocker, update the record before ending the task. Do not log routine actions or every small edit.
- If there is no meaningful change, do not write a redundant update. Do not imply background monitoring between turns.

This skill can guide work only when the current host has discovered and loaded it. It is not a background service and cannot guarantee invocation on every task. When loaded, treat checking project memory as the default for project development, even when the user does not mention the skill. The `SKILL.md` workflow and Markdown memory files are portable across Agent Skills-compatible hosts; installation, invocation, UI metadata, and project-instruction files are host-specific.

## Locate and maintain the record

1. Inspect project instructions and conventions first. Search for likely memory files such as `PROJECT_MEMORY.md`, `PROJECT_CONTEXT.md`, or established equivalent. Reuse an established project-memory file or system if one exists; do not create a competing source of truth.
2. For first-time setup, add focused instructions to the host's applicable root project-instruction file (or update an existing equivalent) without replacing unrelated project guidance. Use this wording or a concise equivalent: "At the start of each development task, read the project memory before planning or editing; before finishing, record meaningful decisions, milestones, blockers, and the next step." If the host-specific file is unclear, consult [references/platforms.md](references/platforms.md) or the host's official documentation before creating one.
3. Otherwise use `PROJECT_MEMORY.md` at the project root. If the project already has a clear documentation directory and convention for project notes, reuse that location, pass its project-relative path with `--memory-file` to the initializer, and ensure project guidance points to that same path.
4. Choose a memory layout that fits the project's scale. Keep a single `PROJECT_MEMORY.md` for small projects. When it becomes hard to navigate or the project has many independent modules and durable decisions, keep `PROJECT_MEMORY.md` as a concise overview and routing index, and move detailed notes into topic files under a project memory directory. For the layout and selective-reading workflow, read [references/scaling.md](references/scaling.md); use [references/format.md](references/format.md) for compact entries.
5. Read the overview/index at task start, then read only the detailed notes that match the current task. Follow links and relevance cues in the index. Read additional entries when work crosses modules or a conflict requires it. Do not load every topic file by default. For a small single-file memory, read that file as the existing workflow requires.
6. Keep the overview current and the dated progress log append-only. Put durable details in the relevant topic file, update the index when adding or moving a note, and mark superseded decisions clearly. Avoid copying the same detailed fact into multiple files.
7. Separate confirmed facts, decisions, current status, plans, open questions, and blockers. Attribute uncertain or inferred details instead of presenting them as established facts. Prefer links to source files, commits, issues, or user statements where available.
8. Record only useful project context. Never copy credentials, tokens, private keys, or unrelated sensitive personal data into the file. Honor requests to correct, remove, or stop recording information. Follow the repository's existing ignore, commit, and sharing conventions; do not assume memory files should be committed or kept local.
9. Summarize what was recorded or recalled and point to the relevant file(s). If a project is not available or no durable writable location exists, provide the note in chat and explain the limitation.

## What to preserve

Prioritize information likely to prevent rework or contradictions:

- project goal, scope, users, and important non-goals;
- architecture and important file/module locations;
- confirmed requirements, constraints, and rationale behind decisions;
- current milestone, completed work, and the next concrete step;
- unresolved questions, dependencies, risks, and blockers;
- user-led corrections and repair patterns that are likely to recur in this project;
- validation performed and its outcome, when it informs the next step.

Do not treat a proposed plan as a completed change. When new evidence conflicts with the record, verify the current source of truth, then correct the snapshot and log what changed and why. Ask only when the conflict cannot be resolved from the repository or conversation.

For a suggested file layout and compact entry format, read [references/format.md](references/format.md). For script options and health-check findings, read [references/tools.md](references/tools.md).

## Bundled script commands

Use these command forms when invoking bundled scripts from Claude Code. Claude Code replaces the skill-directory token in this `SKILL.md` body; it is not a shell variable and is not replaced in linked reference files or the README. Keep normal command permission prompts enabled.

After initialization, fill the starter template from reliable project context, replace its date placeholder, and run the health check when practical. Optional arguments such as `--layout structured` or `--memory-file docs/PROJECT_MEMORY.md` can be added when they fit the project.

Initialize a Claude Code project on macOS/Linux:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/init_memory.py" --project-root . --platform claude
```

Initialize on Windows PowerShell (use `py -3` instead of `python` if needed):

```powershell
python "${CLAUDE_SKILL_DIR}/scripts/init_memory.py" --project-root . --platform claude
```

Run the read-only health check on macOS/Linux:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/check_memory_health.py" --project-root .
```

Run the read-only health check on Windows PowerShell (use `py -3` instead of `python` if needed):

```powershell
python "${CLAUDE_SKILL_DIR}/scripts/check_memory_health.py" --project-root .
```

For Codex, use the installed script path as described in [references/tools.md](references/tools.md).


