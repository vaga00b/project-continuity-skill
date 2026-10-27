# Project memory formats

Adapt to existing project conventions. Use the single-file layout for small projects. For a project whose memory is difficult to navigate, use the overview plus topic files described in [scaling.md](scaling.md). Do not split files just because the codebase is large.

## Single-file layout

Keep the file concise and remove empty sections.

```markdown
# Project Memory

> Last updated: YYYY-MM-DD

## Project snapshot
- **Goal and scope:**
- **Current status:**
- **Key constraints:**
- **Architecture / key locations:**

## Decisions and requirements
- YYYY-MM-DD — **Decision/requirement:** ... **Reason/source:** ...

## Open questions and blockers
- ...

## Reusable repair lessons
- **When:** [symptom or context]
  - **Type:** Confirmed rule / user-led code change
  - **User-chosen change or confirmed rule:** ...
  - **Reason:** ... (only if stated or directly evidenced)
  - **Evidence:** [file path, diff, or user clarification, when available]
  - **Outcome / verification:** ... (say explicitly if no code change was needed or tests were not run)

## Next steps
1. ...

## Progress log
### YYYY-MM-DD — Milestone or change
- **Completed / learned:** ...
- **Impact on current state:** ...
- **Next:** ...
```

Use the local timezone/date convention of the project. A progress entry should capture only a meaningful change. Link relevant paths with repository-relative links when practical. For a decision that has been superseded, keep the original entry and add a newer entry that names the replacement and its reason; revise the current snapshot so it describes the active state.

