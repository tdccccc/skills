# Claude Codex Runner

[中文文档](README.zh.md)

Delegate coding tasks to Codex CLI from Claude Code, then summarize the results.

Two execution modes:

- **Agent mode** (default) — simple tasks: search, diagrams, quick code changes. Claude Code uses the Agent tool to run `codex exec` in the background.
- **Runner mode** — complex tasks: multi-file refactors, tasks needing precise scope constraints and verification. Uses a task file (`docs/tasks/<id>/task.md`) with background subprocess management, status polling, and resume support.

See `SKILL.md` for full usage.
