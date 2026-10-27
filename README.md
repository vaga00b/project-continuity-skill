# Project Continuity

An Agent Skill that helps coding assistants read project context before development and record decisions, progress, and blockers after meaningful work.

> **Platform status:** The workflow and helper scripts have been reviewed. Claude Code and Claude.ai have not been runtime-tested for this release. Claude.ai cannot read local files unless you attach them or add them to a Claude Project.

## Quick start

Install the skill for your assistant and invoke it at the start of a project conversation:

- **OpenAI Codex:** install the skill folder in a Codex skill directory, then type `$project-continuity`.
- **Claude Code:** install it in a Claude Code skill directory, then type `/project-continuity`.
- **Claude.ai:** use the same `skills/project-continuity/` folder and follow the upload steps below. Enable the skill, then ask Claude to use `project-continuity`. Provide the project files Claude needs to read or update.

For [installation details](#install), see below. See the FAQ for use across conversations.

## How it works

```text
Invoke the skill
      ↓
Read project instructions and relevant memory
      ↓
Work on the development task
      ↓
Identify durable decisions, progress, blockers, and user corrections
      ↓
Update the project snapshot and append a concise progress entry
      ↓
Review this task’s code changes and memory update; state which checks were and were not run
```

The skill carries project context forward. It does not record every message or monitor files between conversations.

## What it remembers

- Project goals, scope, architecture pointers, and constraints.
- Confirmed requirements, decisions, and why they were made.
- Current milestone, completed work, blockers, and next steps.
- User-confirmed corrections and reusable lessons, with evidence when available.
- Validation actually performed, including when tests were not run.

Keep project memory concise and editable. Small projects can use a root `PROJECT_MEMORY.md`; larger projects can use it as an overview and index, with topic notes under `project-memory/`. Record information that could affect work in the next few days or future sessions. Skip one-off discussion.

### What not to put in project memory

- Secrets, credentials, tokens, private keys, or unrelated personal information.
- Temporary debug output, full stack traces, or logs that have no lasting value.
- Unconfirmed ideas presented as decisions. Record them as open questions or proposals.
- Long design documents copied in full. Keep a short summary and link to the source document.
- A tentative user question as a confirmed requirement. Record a requirement only when the user or reliable project source confirms it.

## Who it's for

For developers and teams who use AI across conversations and need to carry forward project decisions, corrections, or other context.

## Resolve conflicts and maintain history

When memory conflicts with the current request or project files, check the relevant code, contract, and configuration. Update the current snapshot, mark the earlier decision as superseded, and record why. Append to the dated progress log; do not rewrite older entries.

The skill does not detect every stale decision or archive files automatically. If topic notes become hard to navigate, split or move the durable details, update the overview links, and label archived or superseded notes. Do not create a file for each task.

## Before you install

- The skill instructions and project memory use Markdown and the Agent Skills format. Each host defines its skill directory, invocation method, and project instruction files.
- **Codex** means OpenAI Codex. It loads skills from local skill directories. `agents/openai.yaml` provides Codex interface metadata: display name, description, and default prompt. Other hosts can ignore this file.
- **Claude Code** uses the skill and project instructions together. The skill defines the workflow; `CLAUDE.md` or another supported instruction file tells Claude Code to consult the shared project memory.
- The host must discover and load the skill before it can guide a task. Automatic selection is not guaranteed.
- Project memory is a Markdown file in the repository. Follow the repository's sharing rules and keep sensitive data out of it.
- Python 3 is required only to run the optional helper scripts.

## Install

All three platforms use the same `skills/project-continuity/` folder. The repository maintains one skill source; platform setup instructions are included in its `references/platforms.md`.

### OpenAI Codex

Copy `skills/project-continuity/` into either:

- User-level: `%USERPROFILE%\.codex\skills\project-continuity` on Windows, or `~/.codex/skills/project-continuity` on macOS/Linux.
- Project-level: `.agents/skills/project-continuity/` in the repository.

Invoke with `$project-continuity`. The `$` prefix is Codex's skill invocation syntax.

### Claude Code

Copy `skills/project-continuity/` into either:

- User-level: `%USERPROFILE%\.claude\skills\project-continuity` on Windows, or `~/.claude/skills/project-continuity` on macOS/Linux.
- Project-level: `.claude/skills/project-continuity/` in the repository.

Invoke with `/project-continuity`. The `/` prefix is Claude Code's skill command syntax. Project-level memory guidance belongs in the applicable `CLAUDE.md` or existing supported instruction file; the initializer handles common cases and documents its limits.

### Claude.ai

1. Enable **Code execution and file creation** (the label may vary by account or interface).
2. Download or clone this repository. Compress the `skills/project-continuity/` folder for upload, keeping `SKILL.md` directly inside the `project-continuity/` folder in the archive. Claude.ai requires a ZIP at its upload step; use this same source folder.
3. Open **Customize → Skills → + Create skill → Upload a skill**, upload the archive you just created, and enable the skill.
4. In a conversation, ask Claude to use `project-continuity`; attach the relevant project files or make them available through a Claude Project.

Claude.ai cannot use Claude Code's `/project-continuity` command or read local paths on your computer. Check the current [Claude Skills guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude) for account requirements and interface details.

## Quick project setup

1. Open a conversation with the repository as the working project. In Claude.ai, provide the files it needs.
2. Invoke the skill using the method for your host.
3. Ask it to read the project instructions and existing memory. If needed, initialize memory from information in the repository.
4. Give it a specific development task.
5. Before ending, review the code and memory changes from this task. Confirm the summary matches the saved files and states which checks ran.

The skill guides later tasks in the same conversation. See the FAQ for how to use it in a new conversation.

## Helper scripts

The helper scripts are optional and use only Python's standard library:

- `init_memory.py` creates project memory and host-specific instructions. It preserves existing memory and text outside its managed instruction block.
- `check_memory_health.py` is read-only. By default, it scans the overview and Markdown files under `project-memory/` for:
  - missing local Markdown links;
  - the unfilled `YYYY-MM-DD` starter date;
  - files over 500 lines and topic indexes over 50 rows;
  - common private-key and token patterns, without printing suspected secret values.

The health checker does **not** verify required sections, confirm that decisions are still current, or validate general Markdown syntax. It uses heuristics and is not a security scanner.

Run these commands from the installed skill folder. Replace `<skill-dir>` with that folder's path:

```shell
python <skill-dir>/scripts/init_memory.py --project-root . --platform codex
python <skill-dir>/scripts/check_memory_health.py --project-root .
```

For Claude Code, set the platform to `--platform claude`. On Windows, use `py -3` if `python` is unavailable. The repository file `skills/project-continuity/references/tools.md` lists all options.

## Disable or remove it

- Turn off the skill in the host's settings, or remove its folder from the skill directory.
- The project instructions and memory files remain when you disable the installed skill.
- To stop project-level reminders, remove this skill's marked block from the project instruction file. Keep the other project instructions.
- To remove project memory as well, review or back up `PROJECT_MEMORY.md` and the relevant `project-memory/` notes, then delete them yourself. The skill does not remove project files.

## FAQ

### Does invoking the skill once make it run forever?

No. The skill guides the assistant after loading; it does not run in the background. Invoke it in each new conversation unless the host reliably applies the project instructions.

### Does it update memory after every message?

No. It records decisions, milestones, blockers, and user corrections that may affect future work. Routine conversation stays out of memory.

### Does it treat old memory as more important than what I tell it now?

Follow your current instruction and the verified project source. The assistant should update memory, mark the old decision as superseded, and retain a short history.

### Does it remember across Claude.ai conversations?

Only if the memory files are available in that conversation or through the Project knowledge. Claude.ai cannot read folders on your computer.

## Feedback and contributions

Report bugs and suggestions in the GitHub repository where you found the skill. Include the host and version, steps to reproduce, expected and actual behavior, and any validation results. Do not include private project files, credentials, or conversation data.

## Package contents

```text
LICENSE
README.md
skills/project-continuity/
├── SKILL.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── references/
│   ├── format.md
│   ├── platforms.md
│   ├── scaling.md
│   └── tools.md
└── scripts/
    ├── check_memory_health.py
    └── init_memory.py
```

Use this same skill folder for all platforms. See the installation steps above for each host.

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](./LICENSE). It permits use, modification, and sharing for noncommercial purposes as defined by the license. Commercial use is not granted; contact the rights holder for separate permission. The full license text governs.



---

# Project Continuity（中文）

一种 Agent Skill，帮助 AI 编程助手在开发前读取项目背景，并在完成有意义的工作后记录决定、进度和阻塞。

> **平台状态：** 工作流程和辅助脚本已审阅；本版本尚未在 Claude Code 或 Claude.ai 中进行运行测试。Claude.ai 无法读取本地文件，除非你将文件附加到对话，或加入 Claude Project。

## 快速开始

先为你的助手安装 Skill，再在项目对话开始时调用：

- **OpenAI Codex：** 将 Skill 目录安装到 Codex 的技能目录，然后输入 `$project-continuity`。
- **Claude Code：** 将 Skill 目录安装到 Claude Code 的技能目录，然后输入 `/project-continuity`。
- **Claude.ai：** 使用同一个 `skills/project-continuity/` 文件夹，按下方步骤上传并启用，再请 Claude 使用 `project-continuity`。同时提供 Claude 需要读取或更新的项目文件。

[安装说明](#安装)见下文。跨对话的用法见常见问题。

## 工作闭环

```text
调用 Skill
   ↓
读取项目指引和相关记忆
   ↓
执行开发任务
   ↓
识别有长期价值的决定、进展、阻塞和用户修正
   ↓
更新项目概况并追加简短进度记录
   ↓
复核本次代码改动和记忆更新；说明实际做过和未做过的验证
```

Skill 会延续项目背景，供后续工作使用。它不会记录每条消息，也不会在不同对话之间监控文件。

## 它会记录什么

- 项目目标、范围、架构入口和限制条件。
- 已确认的要求、决定及其原因。
- 当前里程碑、已完成的工作、阻塞和下一步。
- 用户确认过的修正和可复用经验；有证据时一并记录。
- 实际完成的验证，包括没有运行测试的情况。

项目记忆应简明且可编辑。小项目可以使用根目录的 `PROJECT_MEMORY.md`；大型项目可以让它作为概览和索引，并把主题笔记放在 `project-memory/` 下。记录可能影响未来几天或后续会话工作的内容；一次性讨论不用记录。

### 不要写进项目记忆的内容

- 密钥、凭据、访问令牌、私钥，以及与项目无关的个人信息。
- 临时调试输出、完整报错堆栈，以及没有长期价值的日志。
- 不要把未确认的想法写成决定。将它们记为待确认问题或提案。
- 不要整篇复制设计文档。保留简短摘要，并链接到原文。
- 不要把用户试探性的问题当成已确认要求。只有用户或可靠的项目资料确认后，才记录为正式要求。

## 适合谁

适合在多个对话中使用 AI 助手、需要延续项目决定、修正经验或其他背景信息的开发者和团队。

## 冲突处理与历史维护

当记忆与当前请求或项目文件冲突时，核对相关代码、接口契约和配置。更新当前概况，将旧决定标记为已被取代，并记录原因。日期进度日志只追加，不改写旧记录。

Skill 不会自动检测所有过时决定，也不会自动归档文件。主题笔记难以查找时，可以拆分或移动详细内容，更新总览链接，并标记已归档或已被取代的笔记。不要为每个任务新建文件。

## 安装前先看

- Skill 指引和项目记忆使用 Markdown，并遵循 Agent Skills 格式。各平台分别规定 Skill 的安装目录、调用方式和项目指引文件。
- **Codex** 指 OpenAI Codex。它从本地技能目录加载 Skill。`agents/openai.yaml` 提供 Codex 界面元数据，包括显示名称、简介和默认提示；其他平台可以忽略这个文件。
- **Claude Code** 同时使用 Skill 和项目指引。Skill 定义工作流程；`CLAUDE.md` 或其他受支持的项目指引文件告诉 Claude Code 查阅共享项目记忆。
- 平台必须发现并加载 Skill，它才能指导任务。平台不一定会自动选择 Skill。
- 项目记忆是仓库里的 Markdown 文件。按仓库的共享约定处理，不要写入敏感信息。
- 只有运行可选辅助脚本时才需要 Python 3。

## 安装

三个平台都使用同一个 `skills/project-continuity/` 文件夹。仓库只维护一份 Skill 源码，平台配置说明包含在其中的 `references/platforms.md` 中。

### OpenAI Codex

将 `skills/project-continuity/` 复制到以下任一目录：

- 用户级：Windows 使用 `%USERPROFILE%\.codex\skills\project-continuity`；macOS/Linux 使用 `~/.codex/skills/project-continuity`。
- 项目级：将 Skill 放在仓库的 `.agents/skills/project-continuity/`。

使用 `$project-continuity` 调用。前缀 `$` 是 Codex 的 Skill 调用语法。

### Claude Code

将 `skills/project-continuity/` 复制到以下任一目录：

- 用户级：Windows 使用 `%USERPROFILE%\.claude\skills\project-continuity`；macOS/Linux 使用 `~/.claude/skills/project-continuity`。
- 项目级：将 Skill 放在仓库的 `.claude/skills/project-continuity/`。

使用 `/project-continuity` 调用。前缀 `/` 是 Claude Code 的 Skill 命令语法。项目记忆指引应写在适用的 `CLAUDE.md` 或现有项目指引文件中；初始化脚本会处理常见情况并说明自身限制。

### Claude.ai

1. 启用 **Code execution and file creation**。不同账户或界面版本的选项名称可能略有不同。
2. 下载或克隆本仓库，将 `skills/project-continuity/` 文件夹压缩用于上传。压缩包中的 `project-continuity/` 文件夹下应直接包含 `SKILL.md`。Claude.ai 的上传入口要求 ZIP，使用的仍是同一份源码文件夹。
3. 打开 **Customize → Skills → + Create skill → Upload a skill**，上传刚生成的压缩包并启用。
4. 对话时请 Claude 使用 `project-continuity`，并附上需要读取的项目文件，或通过 Claude Project 提供。

Claude.ai 不能使用 Claude Code 的 `/project-continuity` 命令，也不能读取电脑上的本地路径。账户要求和界面可能变化，请查看当前的 [Claude Skills 指南](https://support.claude.com/en/articles/12512180-use-skills-in-claude)。

## 项目快速上手

1. 在对话中打开仓库作为工作项目；使用 Claude.ai 时，提供所需文件。
2. 按对应平台的方式调用 Skill。
3. 让助手读取项目指引和现有记忆。项目尚未配置时，根据仓库中的信息初始化记忆。
4. 提出具体的开发任务。
5. 结束前检查本次代码和记忆改动。确认总结与保存的文件一致，并说明实际运行了哪些检查。

调用 Skill 后，它会继续指导本轮对话中的后续任务。新对话的使用方式见常见问题。

## 辅助脚本

两个辅助脚本都是可选项，只使用 Python 标准库：

- `init_memory.py`：创建项目记忆和平台专用指引。保留已有记忆，以及管理区块之外的文本。
- `check_memory_health.py`：只读检查。默认扫描项目概览和 `project-memory/` 下的 Markdown 文件，检查：
  - 是否存在指向缺失文件的本地 Markdown 链接；
  - 是否残留 `YYYY-MM-DD` 日期占位符；
  - 记忆文件是否超过 500 行，主题索引是否超过 50 项；
  - 是否出现常见私钥和令牌格式。检查结果不会显示疑似密钥值。

健康检查**不会**验证必需的记忆章节、确认决定是否仍然有效，也不会检查通用 Markdown 语法。它使用启发式规则，不是安全扫描器。

在已安装的 Skill 目录中运行下面的命令，并将 `<skill-dir>` 替换为实际目录路径：

```shell
python <skill-dir>/scripts/init_memory.py --project-root . --platform codex
python <skill-dir>/scripts/check_memory_health.py --project-root .
```

初始化 Claude Code 项目时，将平台参数改为 `--platform claude`。Windows 上若 `python` 不可用，可改用 `py -3`。所有参数见仓库中的 `skills/project-continuity/references/tools.md`。

## 禁用或移除

- 在平台的 Skill 设置中关闭它，或从技能目录移除它。
- 项目指引和记忆文件与已安装的 Skill 分开保存。关闭 Skill 不会删除这些文件。
- 若要停止项目级提醒，只移除项目指引文件中由本 Skill 管理的标记区块，保留其他指引。
- 若也要删除项目记忆，先检查或备份，再删除 `PROJECT_MEMORY.md` 和相关的 `project-memory/` 笔记。Skill 不会自动删除这些文件。

## 常见问题

### 调用一次，它就会一直运行吗？

不会。Skill 加载后会指导助手工作，但不会在后台运行。除非平台能持续应用项目指引，否则每个新对话都要重新调用。

### 每条消息后都会更新记忆吗？

不会。只记录可能影响后续工作的决定、里程碑、阻塞和用户修正，不记录日常对话。

### 如果旧记忆和我现在说的不一致，听谁的？

以你当前的指示和经过核实的项目资料为准。助手应更新记忆，将旧决定标记为已被取代，并保留简要历史。

### Claude.ai 会跨对话记住项目吗？

只有当前对话中提供了记忆文件，或文件已加入 Project 知识，Claude.ai 才能读取。它不能直接访问电脑上的文件夹。

## 反馈与贡献

在获取该 Skill 的 GitHub 仓库中报告问题或提交建议。说明使用的平台和版本、复现步骤、预期与实际结果，以及验证结果。不要公开私人项目文件、凭据或对话内容。

## 包含哪些文件

```text
LICENSE
README.md
skills/project-continuity/
├── SKILL.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── references/
│   ├── format.md
│   ├── platforms.md
│   ├── scaling.md
│   └── tools.md
└── scripts/
    ├── check_memory_health.py
    └── init_memory.py
```

各平台都使用这一个 Skill 文件夹，具体操作见上方安装说明。

## 许可证

本项目采用 [PolyForm Noncommercial License 1.0.0](./LICENSE)。该许可证允许非商业用途下使用、修改和分享。商业用途需要另行取得许可，具体以许可证全文为准。






