# claude-security-audit

A Claude Code skill that audits your configuration for malicious hooks, MCP servers, and suspicious commands.

## Why

Claude Code's hooks system can execute arbitrary commands silently. A malicious project or plugin could inject hooks that exfiltrate your SSH keys, credentials, or other sensitive data. This skill helps you detect such threats.

## What it checks

| Location | What |
|----------|------|
| `~/.claude/settings.json` | hooks, MCP servers, dangerous settings |
| `~/.claude/skills/` | skill files for hidden commands |
| `~/.claude/plugins/` | plugin hooks |
| Project `.claude/` | project-level hooks and MCP configs |
| Project `CLAUDE.md` | instructions that bypass safety checks |

## Severity levels

- **CRITICAL** — Active data exfiltration (e.g., `curl` + reading SSH keys)
- **HIGH** — Dangerous commands or broad hooks
- **MEDIUM** — Suspicious but needs human judgment
- **LOW** — Informational

## Install as Claude Code skill

```bash
# Copy to your skills directory
git clone https://github.com/tdccccc/claude-security-audit.git ~/.claude/skills/security-audit
```

Then use `/security-audit` in Claude Code, or just say "check my security".

## Standalone usage

```bash
python3 scripts/scan.py                    # scan current directory
python3 scripts/scan.py /path/to/project   # scan specific project
```

## License

MIT
