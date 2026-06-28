# Personal Skills

This repository is a personal skills package for Claude Code and Codex workflows.

## Install

Quick install:

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash
```

This downloads `bootstrap.sh`, then asks which tool(s) to install for —
Claude Code, Codex, or both — *before* cloning anything, so choosing Cancel
costs nothing. After you choose, it clones or updates this repository under
`${XDG_CACHE_HOME:-$HOME/.cache}/tdccccc-skills` and runs `install.sh` from
that cached repository.

Clone this repository and run the installer:

```bash
git clone <repo-url> personal-skills
cd personal-skills
./install.sh
```

The `--target` you choose selects which tools to install into. Each skill can
declare an `install-targets:` field in its `SKILL.md` frontmatter (`claude`,
`codex`, or `both`); the installer copies a skill into the chosen target only
when that skill's `install-targets` includes it. A skill without the field
defaults to `both`. Each skill is self-contained: any helper scripts, tools,
and reference docs it needs live inside its own directory and are copied along
with it, so there are no top-level shared directories.

Targets:

```bash
./install.sh                   # Ask which tool(s) to install for; default Claude Code
./install.sh --target claude   # ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills
./install.sh --target codex    # ${CODEX_HOME:-$HOME/.codex}/skills
./install.sh --target both
```

For local development, install with symlinks instead of copies:

```bash
./install.sh --link
```

Useful options:

```bash
./install.sh --force           # Replace existing installed directories
./install.sh --dest /path/to/skills
./install.sh --dry-run
```

With the one-line installer, pass installer options after `bash -s --`:

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash -s -- --force
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash -s -- --target both
```

Restart Claude Code and/or Codex after installing or updating skills.

## Uninstall

Remove this repository's skills from the cloned checkout:

```bash
./uninstall.sh                 # Ask which target; Enter selects Claude Code
./uninstall.sh --target claude
./uninstall.sh --target codex
./uninstall.sh --target both
```

Only directories this repository installs are removed, looked up by name: the
current skills plus legacy names from older layouts (`shared`, `tools`). Skills
from other sources in the same directory are never touched.

Preview before deleting, or skip the confirmation prompt:

```bash
./uninstall.sh --target both --dry-run
./uninstall.sh --target both --yes
./uninstall.sh --dest /path/to/skills
```

## Skills

The install target for each skill is shown in parentheses.

- `article-summary/` (claude) summarizes astronomy and academic papers into structured Chinese notes.
- `claude-codex-runner/` (claude) lets Claude Code package a task and invoke Codex CLI for one-shot execution.
- `codex-task-executor/` (codex) tells Codex how to execute Claude-generated task packages and write structured reports.
- `grill-me/` (claude) interviews you relentlessly via multiple-choice popups to stress-test a plan or design until every decision is resolved.
- `security-audit/` (claude) audits Claude Code configuration for malicious hooks, MCP servers, and suspicious commands.

## Shared Protocols

- `claude-codex-runner/references/codex-task-contract.md` defines the task and report contract. `claude-codex-runner` reads it directly; when invoking Codex, Claude injects the contract text into the prompt so `codex-task-executor` can follow it without bundling its own copy.

## Tools

- `claude-codex-runner/tools/codex-runner/codex-runner` starts, polls, reads, cancels, and resumes Codex task runs.
- `security-audit/scripts/scan.py` runs the standalone Claude Code security scan.

Common commands:

```bash
claude-codex-runner/tools/codex-runner/codex-runner start docs/tasks/<task-id>/task.md --background
claude-codex-runner/tools/codex-runner/codex-runner status <task-id>
claude-codex-runner/tools/codex-runner/codex-runner result <task-id>
claude-codex-runner/tools/codex-runner/codex-runner cancel <task-id>
claude-codex-runner/tools/codex-runner/codex-runner resume <task-id> --goal "<follow-up goal>"
```

## Layout

```text
skills/
  README.md
  bootstrap.sh
  install.sh
  uninstall.sh
  claude-codex-runner/
    SKILL.md
    references/
      task-template.md
      runner-workflow.md
      codex-task-contract.md
    tools/
      codex-runner/
        codex-runner
      codex_runner/
        cli.py
        runner.py
  codex-task-executor/
    SKILL.md
    references/
      execution-protocol.md
      report-template.md
  article-summary/
    SKILL.md
    references/
      summary-template.md
  grill-me/
    SKILL.md
  security-audit/
    SKILL.md
    scripts/
      scan.py
    LICENSE
    README.md
```

## Conventions

- Each skill directory contains one `SKILL.md`.
- A skill's `SKILL.md` frontmatter may set `install-targets:` to `claude`, `codex`, or `both` to control where it installs; omitting it defaults to `both`.
- Supporting instructions and templates live in `references/`.
- Bundled executables for a skill live in that skill's `scripts/`.
- Imported third-party skills may keep their upstream `LICENSE` and `README.md`.
- Each skill is self-contained: any helper scripts, tools, and reference docs it needs live inside its own directory so it installs as a single unit.
- Task records generated in target projects use `docs/tasks/<task-id>/`.
- Temporary Codex execution artifacts in target projects use `.codex-runs/<task-id>/` and should be ignored by Git.
