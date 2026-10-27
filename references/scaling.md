# Scaling project memory

Use this layout when one `PROJECT_MEMORY.md` has become difficult to navigate, or when a project has many independent modules and recurring decisions. A large repository alone is not a reason to split memory; prefer the simplest layout that keeps relevant facts easy to find.

## Layout

Keep `PROJECT_MEMORY.md` at the project root as the short overview and routing index. Keep detailed, durable notes in a `project-memory/` directory:

```text
PROJECT_MEMORY.md                 # Current project snapshot and topic index
project-memory/
  decisions/                      # Confirmed architecture/product decisions
  bugs/                            # Resolved recurring bugs and evidence
  modules/                         # Cross-cutting module behavior and constraints
  patterns/                        # Reusable implementation and repair lessons
```

Follow an existing project documentation convention when one already serves this purpose. Do not create duplicate memory systems.

## Overview and index

Keep the root file useful to read at every task start. Include:

- project goal, current milestone, and next step;
- critical constraints and high-level architecture pointers;
- links to topic files, each with a short `Read when` cue;
- a concise dated progress log for meaningful milestones.

Example index:

```markdown
## Topic index
| Topic | Read when | File |
|---|---|---|
| Ticket serialization | Changing API response fields or fallback behavior | [modules/ticket-serialization.md](project-memory/modules/ticket-serialization.md) |
| Optional display values | Handling missing, null, or empty strings | [patterns/optional-display-values.md](project-memory/patterns/optional-display-values.md) |
```

Avoid repeating the full contents of a topic file in the overview. The overview routes to detail; it is not a transcript.

## Read by relevance

At task start, read project guidance and the root overview/index. Search the index using the task's module, symptom, API area, or decision. Read only the matching topic files before planning. Read multiple entries when the task spans modules, and read older or superseded notes only when needed to resolve a conflict or understand history. Always verify relevant behavior against current source files.

If no index entry matches, inspect the code and continue normally. Add a topic note only if the task produces durable knowledge. Do not guess which note applies.

## Update and split

When recording a meaningful result, update the detailed note closest to the topic and add or revise its index row. Keep the overview's current snapshot accurate and its progress log concise. If a note covers unrelated topics or becomes unwieldy, split it along stable module or subject boundaries and repair the index links. Preserve evidence and mark replaced decisions as superseded rather than silently deleting history.

Do not create a file per task or per conversation. Do not add scripts or strict size limits unless repeated maintenance problems show they are needed. Keep secrets out of every memory file.
