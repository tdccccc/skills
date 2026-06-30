# Claude Codex Runner

[中文文档](README.zh.md)

Delegate tasks to Codex CLI from Claude Code, then summarize the results.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash
```

## Usage

### Agent mode (default) — simple tasks

Search, diagrams, images, quick code changes — one sentence is enough. Claude Code uses the Agent tool to run `codex exec` in the background:

```
You: Search arxiv astro-ph.CO for today's new articles
You: Draw a mermaid sequence diagram of user login flow
You: Convert this function to async
```

The Agent notifies you when it finishes. You can also write a `docs/tasks/<task-id>/task.md` and reference it from the prompt.

### Runner mode — complex tasks

Multi-file refactors, precise scope constraints, tasks needing verification and follow-up. Write a task.md and manage with the runner:

```bash
R=~/.claude/skills/claude-codex-runner/tools/runner

# Start (background)
"$R" start docs/tasks/<task-id>/task.md --provider <profile>

# Check status
"$R" status <task-id>

# Read report
"$R" result <task-id>

# Resume
"$R" resume <task-id> --goal "<goal>" --start

# List tasks
"$R" list

# Cancel
"$R" cancel <task-id>
```
