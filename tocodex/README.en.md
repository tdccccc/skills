# ToCodex

[中文文档](README.md)

Delegate tasks to Codex CLI from Claude Code, then summarize the results.

## Usage

Just one sentence:

```
You: Search arxiv astro-ph.CO for today's papers about gravitational waves
You: Convert this function to async
You: Add a password strength indicator to the login page
```

Claude will automatically:
1. Judge task complexity and generate an appropriate task.md
2. Call `codex exec` via Agent in the background
3. Read the report and summarize when done

Check progress: press **↓ arrow key** in Claude Code to view Agent live output.

## Task complexity

| Simple (minimal template) | Complex (full template) |
|---|---|
| Read-only / search / diagrams | Multi-file changes |
| Single file ≤ 50 lines | Single file > 50 lines |
| No tests/config/deps/security | Involves tests/config/deps/security |
| One-shot script | Needs verification steps |

## Task file structure

```
<project>/
  docs/
    tocodex/
      YYYY-MM-DD-slug/
        task.md
        report.md
        stdout.log
        stderr.log
```
