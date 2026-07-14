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
./install.sh --no-force        # Skip skills that already exist (default replaces them)
./install.sh --dest /path/to/skills
./install.sh --dry-run
```

With the one-line installer, pass installer options after `bash -s --`:

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash -s -- --no-force
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash -s -- --target both
```

Restart Claude Code and/or Codex after installing or updating skills.

## Uninstall

To remove this repository's skills, manually delete the skill directories from
Claude Code's skills directory and/or Codex's skills directory.

If upgrading from the previous skill name, remove
`~/.claude/skills/claude-codex-runner` after installing `tocodex` to avoid
keeping both versions active:

```bash
# List installed skills from this repo
ls -d ~/.claude/skills/*/
ls -d ~/.codex/skills/*/

# Delete the ones belonging to this repository
rm -rf ~/.claude/skills/tocodex ~/.claude/skills/codex-task-executor \
       ~/.claude/skills/grill-me ~/.claude/skills/security-audit
# Repeat for ~/.codex/skills/ as needed
```

Restart Claude Code and/or Codex to drop the removed skills.

## Skills

The install target for each skill is shown in parentheses.

- `tocodex/` (claude) delegates well-scoped tasks to Codex CLI via Agent and summarizes the results.
- `codex-task-executor/` (codex) tells Codex how to execute Claude-generated task packages and write structured reports.
- `grill-me/` (claude) interviews you relentlessly via multiple-choice popups to stress-test a plan or design until every decision is resolved.
- `grill-with-docs/` (claude) combines grilling with domain modeling, creating ADRs and glossary as you go. Adapted from [mattpocock/skills](https://github.com/mattpocock/skills).
- `domain-modeling/` (claude) builds and sharpens a project's domain model, terminology, and ADRs. Adapted from [mattpocock/skills](https://github.com/mattpocock/skills).
- `security-audit/` (claude) audits Claude Code configuration for malicious hooks, MCP servers, and suspicious commands.

## Tools

- `security-audit/scripts/scan.py` runs the standalone Claude Code security scan.

## Layout

```text
skills/
  README.md
  bootstrap.sh
  install.sh
  tocodex/
    SKILL.md
    README.md
    README.zh.md
  codex-task-executor/
    SKILL.md
    references/
      execution-protocol.md
      report-template.md
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
- Imported third-party skills may keep their upstream `LICENSE` and `README.md`.
- Each skill is self-contained: all files it needs live inside its own directory so it installs as a single unit.
- Task records generated in target projects use `docs/tocodex/<task-id>/`.
- Codex execution logs (`stdout.log`, `stderr.log`) live alongside task files under `docs/tocodex/<task-id>/`.
