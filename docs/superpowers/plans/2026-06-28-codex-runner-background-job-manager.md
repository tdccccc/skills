# Codex Runner Background Job Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local background job manager for Claude-to-Codex task execution with `start`, `status`, `result`, `cancel`, and audited `resume` support.

**Architecture:** Keep the existing Markdown task/report protocol as the source of truth, and add a thin Python stdlib runner under `tools/codex_runner/` plus a small executable wrapper under `tools/codex-runner/`. The runner records job state in `.codex-runs/<task-id>/run.json`, writes stdout/stderr logs, launches Codex in foreground or background, and lets Claude poll/cancel/read results while continuing the main conversation.

**Tech Stack:** Python 3 standard library (`argparse`, `json`, `pathlib`, `subprocess`, `os`, `signal`, `datetime`, `textwrap`, `unittest`), Codex CLI, Markdown skill files.

---

## Scope Check

This plan extends the existing `claude-codex-runner` / `codex-task-executor` workflow. It does not replace the current task contract and does not adopt the official `openai-codex` plugin runtime. It implements a repo-local runner with these commands:

```bash
tools/codex-runner/codex-runner start docs/tasks/<task-id>/task.md --background
tools/codex-runner/codex-runner status <task-id>
tools/codex-runner/codex-runner result <task-id>
tools/codex-runner/codex-runner cancel <task-id>
tools/codex-runner/codex-runner resume <task-id> --goal "<follow-up goal>"
```

`resume` means `resume-audited`: read the previous `task.md` and `codex-report.md`, create a new follow-up task directory, then optionally start it. It does not use native `codex resume` in this version.

## File Structure

- Create `tools/__init__.py`: makes `tools` importable for tests.
- Create `tools/codex_runner/__init__.py`: package marker and version string.
- Create `tools/codex_runner/runner.py`: core task parsing, state file handling, command construction, process launching, status refresh, result rendering, cancellation, and audited resume creation.
- Create `tools/codex_runner/cli.py`: `argparse` command interface for `start`, `worker`, `status`, `result`, `cancel`, and `resume`.
- Create `tools/codex-runner/codex-runner`: executable wrapper that calls `python3 -m tools.codex_runner.cli`.
- Create `tests/test_codex_runner.py`: unittest coverage for task parsing, command construction, foreground runs, background state files, result fallback, cancel behavior, and audited resume task generation.
- Modify `shared/codex-task-contract.md`: document `run.json`, lifecycle statuses, and background runner behavior.
- Modify `claude-codex-runner/SKILL.md`: mention the local runner as the preferred invocation layer.
- Modify `claude-codex-runner/references/runner-workflow.md`: replace direct `codex exec` as the default with `tools/codex-runner/codex-runner start`, while preserving direct `codex exec` as fallback.
- Modify `codex-task-executor/references/execution-protocol.md`: state that background runs are still single Codex tasks and must write the normal report.
- Modify `README.md`: add the runner tool to the package layout.

## Behavior Contract

### Run State

Each task run writes:

```text
<target-project>/.codex-runs/<task-id>/run.json
<target-project>/.codex-runs/<task-id>/stdout.log
<target-project>/.codex-runs/<task-id>/stderr.log
```

`run.json` schema:

```json
{
  "task_id": "2026-06-28-example",
  "task_path": "/abs/project/docs/tasks/2026-06-28-example/task.md",
  "target_project": "/abs/project",
  "run_dir": "/abs/project/.codex-runs/2026-06-28-example",
  "report_path": "/abs/project/docs/tasks/2026-06-28-example/codex-report.md",
  "status": "queued",
  "worker_pid": null,
  "codex_pid": null,
  "codex_pgid": null,
  "started_at": null,
  "finished_at": null,
  "exit_code": null,
  "provider": "",
  "sandbox": "workspace-write",
  "command": []
}
```

Statuses:

- `queued`: background worker has been created but Codex has not started.
- `running`: Codex process has started.
- `success`: Codex exited 0.
- `failed`: Codex exited non-zero or the worker failed.
- `cancelled`: user cancelled the run.
- `unknown`: state says running, but no process is alive and no final status was written.

### Command Construction

Default command:

```bash
codex -a never exec \
  -C "<target-project>" \
  -s "<sandbox>" \
  --skip-git-repo-check \
  --ephemeral \
  "<prompt>"
```

When `provider` is non-empty, add:

```bash
-p "<provider>"
```

The runner must pass `stdin=subprocess.DEVNULL`, not inherit stdin.

The runner must capture stdout/stderr into files instead of appending shell redirections to the command array.

## Task 1: Add Core Runner State And Task Parsing

**Files:**
- Create: `tools/__init__.py`
- Create: `tools/codex_runner/__init__.py`
- Create: `tools/codex_runner/runner.py`
- Create: `tests/test_codex_runner.py`

- [ ] **Step 1: Write failing tests for task parsing and run-state paths**

Create `tests/test_codex_runner.py` with these initial tests:

```python
import json
import tempfile
import unittest
from pathlib import Path

from tools.codex_runner.runner import (
    build_initial_state,
    parse_task_file,
    resolve_task_reference,
)


class CodexRunnerParsingTests(unittest.TestCase):
    def make_project(self):
        root = Path(tempfile.mkdtemp(prefix="codex-runner-test-"))
        task_dir = root / "docs" / "tasks" / "2026-06-28-example"
        task_dir.mkdir(parents=True)
        task_path = task_dir / "task.md"
        task_path.write_text(
            "\n".join(
                [
                    "# Codex Task: Example",
                    "",
                    "task_id: 2026-06-28-example",
                    f"target_project: {root}",
                    "task_kind: implementation",
                    "mode: semi-auto",
                    "sandbox: workspace-write",
                    "provider: kimi",
                    "artifact_policy: keep-report-only",
                    "source: claude-code",
                    "",
                    "## Goal",
                    "",
                    "Append one line to README.md.",
                    "",
                    "## Report",
                    "",
                    "Write report to:",
                    "",
                    "```text",
                    "docs/tasks/2026-06-28-example/codex-report.md",
                    "```",
                ]
            ),
            encoding="utf-8",
        )
        return root, task_path

    def test_parse_task_file_extracts_metadata_and_report_path(self):
        root, task_path = self.make_project()

        task = parse_task_file(task_path)

        self.assertEqual(task["task_id"], "2026-06-28-example")
        self.assertEqual(task["target_project"], str(root))
        self.assertEqual(task["task_kind"], "implementation")
        self.assertEqual(task["sandbox"], "workspace-write")
        self.assertEqual(task["provider"], "kimi")
        self.assertEqual(
            task["report_path"],
            str(root / "docs" / "tasks" / "2026-06-28-example" / "codex-report.md"),
        )

    def test_build_initial_state_uses_codex_runs_directory(self):
        root, task_path = self.make_project()
        task = parse_task_file(task_path)

        state = build_initial_state(task)

        self.assertEqual(state["task_id"], "2026-06-28-example")
        self.assertEqual(state["target_project"], str(root))
        self.assertEqual(
            state["run_dir"],
            str(root / ".codex-runs" / "2026-06-28-example"),
        )
        self.assertEqual(state["status"], "queued")
        self.assertEqual(state["provider"], "kimi")
        self.assertEqual(state["sandbox"], "workspace-write")

    def test_resolve_task_reference_accepts_task_id(self):
        root, task_path = self.make_project()

        resolved = resolve_task_reference("2026-06-28-example", cwd=root)

        self.assertEqual(resolved, task_path)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
python3 -m unittest tests.test_codex_runner -v
```

Expected: FAIL with `ModuleNotFoundError` or import errors for `tools.codex_runner.runner`.

- [ ] **Step 3: Add package markers**

Create `tools/__init__.py`:

```python
"""Local tools package for personal skills."""
```

Create `tools/codex_runner/__init__.py`:

```python
"""Codex runner background job manager."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Implement task parsing and initial state**

Create `tools/codex_runner/runner.py` with these functions and behavior:

```python
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"
STATUS_UNKNOWN = "unknown"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_metadata(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith("## "):
            break
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\\s*(.*)$", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip()
    return metadata


def extract_report_path(text: str) -> str:
    match = re.search(r"Write report to:\\s*\\n\\s*```text\\s*\\n([^`]+?)\\n```", text, re.S)
    if match:
        return match.group(1).strip()
    return ""


def parse_task_file(task_path: str | Path) -> dict[str, str]:
    path = Path(task_path).resolve()
    text = read_text(path)
    metadata = parse_metadata(text)
    task_id = metadata.get("task_id") or path.parent.name
    target_project = Path(metadata.get("target_project") or path.parents[3]).resolve()
    report_value = extract_report_path(text)
    report_path = Path(report_value) if report_value else Path("docs") / "tasks" / task_id / "codex-report.md"
    if not report_path.is_absolute():
        report_path = target_project / report_path
    return {
        "task_id": task_id,
        "task_path": str(path),
        "target_project": str(target_project),
        "task_kind": metadata.get("task_kind", "implementation"),
        "mode": metadata.get("mode", "semi-auto"),
        "sandbox": metadata.get("sandbox", "workspace-write"),
        "provider": metadata.get("provider", ""),
        "artifact_policy": metadata.get("artifact_policy", "keep-report-only"),
        "report_path": str(report_path.resolve()),
    }


def resolve_task_reference(reference: str | Path, cwd: str | Path | None = None) -> Path:
    ref = Path(reference)
    base = Path(cwd or os.getcwd()).resolve()
    if ref.exists():
        return ref.resolve()
    candidate = base / "docs" / "tasks" / str(reference) / "task.md"
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"Cannot resolve task reference: {reference}")


def run_dir_for(task: dict[str, str]) -> Path:
    return Path(task["target_project"]) / ".codex-runs" / task["task_id"]


def state_path_for(task: dict[str, str]) -> Path:
    return run_dir_for(task) / "run.json"


def stdout_path_for(task: dict[str, str]) -> Path:
    return run_dir_for(task) / "stdout.log"


def stderr_path_for(task: dict[str, str]) -> Path:
    return run_dir_for(task) / "stderr.log"


def build_initial_state(task: dict[str, str]) -> dict[str, Any]:
    run_dir = run_dir_for(task)
    return {
        "task_id": task["task_id"],
        "task_path": task["task_path"],
        "target_project": task["target_project"],
        "run_dir": str(run_dir),
        "report_path": task["report_path"],
        "status": STATUS_QUEUED,
        "worker_pid": None,
        "codex_pid": None,
        "codex_pgid": None,
        "started_at": None,
        "finished_at": None,
        "exit_code": None,
        "provider": task.get("provider", ""),
        "sandbox": task.get("sandbox", "workspace-write"),
        "command": [],
    }


def write_state(task: dict[str, str], state: dict[str, Any]) -> None:
    path = state_path_for(task)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\\n", encoding="utf-8")


def read_state_by_task(task_path: str | Path) -> tuple[dict[str, str], dict[str, Any]]:
    task = parse_task_file(task_path)
    state_path = state_path_for(task)
    if not state_path.exists():
        raise FileNotFoundError(f"Run state not found: {state_path}")
    return task, json.loads(state_path.read_text(encoding="utf-8"))
```

- [ ] **Step 5: Run tests and verify they pass**

Run:

```bash
python3 -m unittest tests.test_codex_runner -v
```

Expected: 3 tests pass.

- [ ] **Step 6: Commit Task 1**

Run:

```bash
git add tools tests/test_codex_runner.py
git diff --staged
git commit -m "feat(codex-runner): add task state parsing"
```

Expected: commit succeeds with task parsing and state helpers only.

## Task 2: Implement Start, Worker, Status, Result, And Cancel

**Files:**
- Modify: `tools/codex_runner/runner.py`
- Create: `tools/codex_runner/cli.py`
- Create: `tools/codex-runner/codex-runner`
- Modify: `tests/test_codex_runner.py`

- [ ] **Step 1: Add tests for command construction and foreground result fallback**

Append to `tests/test_codex_runner.py`:

```python
from tools.codex_runner.runner import (
    build_codex_command,
    render_result,
    run_codex_foreground,
)


class CodexRunnerCommandTests(unittest.TestCase):
    def test_build_codex_command_includes_profile_sandbox_and_target_project(self):
        root, task_path = CodexRunnerParsingTests().make_project()
        task = parse_task_file(task_path)

        command, prompt = build_codex_command(task, codex_bin="codex")

        self.assertEqual(command[:3], ["codex", "-a", "never"])
        self.assertIn("exec", command)
        self.assertIn("-p", command)
        self.assertIn("kimi", command)
        self.assertIn("-C", command)
        self.assertIn(str(root), command)
        self.assertIn("-s", command)
        self.assertIn("workspace-write", command)
        self.assertIn("--skip-git-repo-check", command)
        self.assertIn("--ephemeral", command)
        self.assertIn("<execution_contract>", prompt)
        self.assertIn("docs/tasks/2026-06-28-example/task.md", prompt)

    def test_result_falls_back_to_logs_when_report_is_missing(self):
        root, task_path = CodexRunnerParsingTests().make_project()
        task = parse_task_file(task_path)
        run_dir_for(task).mkdir(parents=True)
        stdout_path_for(task).write_text("stdout summary\\n", encoding="utf-8")
        stderr_path_for(task).write_text("stderr detail\\n", encoding="utf-8")

        rendered = render_result(task)

        self.assertIn("Report not found", rendered)
        self.assertIn("stdout summary", rendered)
        self.assertIn("stderr detail", rendered)
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
python3 -m unittest tests.test_codex_runner -v
```

Expected: FAIL with missing `build_codex_command`, `render_result`, or `run_codex_foreground`.

- [ ] **Step 3: Add command construction, foreground execution, result rendering, and cancellation helpers**

Append these functions to `tools/codex_runner/runner.py`:

```python
def relative_to_project(path: str, target_project: str) -> str:
    try:
        return str(Path(path).resolve().relative_to(Path(target_project).resolve()))
    except ValueError:
        return str(path)


def build_prompt(task: dict[str, str]) -> str:
    task_rel = relative_to_project(task["task_path"], task["target_project"])
    report_rel = relative_to_project(task["report_path"], task["target_project"])
    return textwrap.dedent(
        f"""
        <task>
        Execute {task_rel} in {task['target_project']}.
        </task>

        <execution_contract>
        Follow the Codex task contract included in the task file context. The task file is authoritative.
        Use sandbox {task['sandbox']}. Do not stage or commit unless the task explicitly allows it.
        </execution_contract>

        <output_contract>
        Write {report_rel}, then exit.
        </output_contract>

        <action_safety>
        Keep changes tightly scoped. Preserve unrelated user work. Put temporary files under .codex-runs/{task['task_id']}/.
        </action_safety>
        """
    ).strip()


def build_codex_command(task: dict[str, str], codex_bin: str = "codex") -> tuple[list[str], str]:
    prompt = build_prompt(task)
    command = [
        codex_bin,
        "-a",
        "never",
        "exec",
        "-C",
        task["target_project"],
        "-s",
        task.get("sandbox", "workspace-write"),
        "--skip-git-repo-check",
        "--ephemeral",
    ]
    provider = task.get("provider", "").strip()
    if provider:
        command.extend(["-p", provider])
    command.append(prompt)
    return command, prompt


def prepare_run_files(task: dict[str, str]) -> dict[str, Any]:
    run_dir_for(task).mkdir(parents=True, exist_ok=True)
    state = build_initial_state(task)
    write_state(task, state)
    return state


def run_codex_foreground(task_path: str | Path, codex_bin: str = "codex") -> int:
    task = parse_task_file(task_path)
    state = prepare_run_files(task)
    command, _prompt = build_codex_command(task, codex_bin=codex_bin)
    state.update(
        {
            "status": STATUS_RUNNING,
            "started_at": utc_now(),
            "command": command,
        }
    )
    write_state(task, state)
    with stdout_path_for(task).open("w", encoding="utf-8") as stdout, stderr_path_for(task).open("w", encoding="utf-8") as stderr:
        process = subprocess.Popen(
            command,
            cwd=task["target_project"],
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
            text=True,
        )
        state["codex_pid"] = process.pid
        state["codex_pgid"] = os.getpgid(process.pid)
        write_state(task, state)
        exit_code = process.wait()
    state["exit_code"] = exit_code
    state["finished_at"] = utc_now()
    state["status"] = STATUS_SUCCESS if exit_code == 0 else STATUS_FAILED
    write_state(task, state)
    return exit_code


def pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def refresh_status(task_path: str | Path) -> dict[str, Any]:
    task, state = read_state_by_task(task_path)
    if state.get("status") == STATUS_RUNNING and not pid_alive(state.get("worker_pid")) and not pid_alive(state.get("codex_pid")):
        state["status"] = STATUS_UNKNOWN
        state["finished_at"] = state.get("finished_at") or utc_now()
        write_state(task, state)
    return state


def tail_text(path: Path, limit: int = 4000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[-limit:]


def render_result(task: dict[str, str]) -> str:
    report_path = Path(task["report_path"])
    if report_path.exists():
        return report_path.read_text(encoding="utf-8")
    stdout = tail_text(stdout_path_for(task))
    stderr = tail_text(stderr_path_for(task))
    return "\n".join(
        [
            f"# Codex Result: {task['task_id']}",
            "",
            f"Report not found: {report_path}",
            "",
            "## stdout",
            "",
            "```text",
            stdout,
            "```",
            "",
            "## stderr",
            "",
            "```text",
            stderr,
            "```",
        ]
    )


def cancel_task(task_path: str | Path) -> dict[str, Any]:
    task, state = read_state_by_task(task_path)
    pgid = state.get("codex_pgid")
    worker_pid = state.get("worker_pid")
    if pgid:
        try:
            os.killpg(int(pgid), signal.SIGTERM)
        except ProcessLookupError:
            pass
    if worker_pid and pid_alive(int(worker_pid)):
        try:
            os.kill(int(worker_pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
    state["status"] = STATUS_CANCELLED
    state["finished_at"] = utc_now()
    write_state(task, state)
    return state
```

- [ ] **Step 4: Add CLI commands**

Create `tools/codex_runner/cli.py`:

```python
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .runner import (
    build_initial_state,
    cancel_task,
    parse_task_file,
    read_state_by_task,
    refresh_status,
    render_result,
    resolve_task_reference,
    run_codex_foreground,
    state_path_for,
    write_state,
)


def start_background(task_path: Path, codex_bin: str) -> int:
    task = parse_task_file(task_path)
    state = build_initial_state(task)
    state["worker_pid"] = None
    write_state(task, state)
    command = [
        sys.executable,
        "-m",
        "tools.codex_runner.cli",
        "worker",
        str(task_path),
        "--codex-bin",
        codex_bin,
    ]
    worker = subprocess.Popen(
        command,
        cwd=Path(__file__).resolve().parents[2],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        text=True,
    )
    state["worker_pid"] = worker.pid
    write_state(task, state)
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def command_start(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task, cwd=args.cwd)
    if args.background:
        return start_background(task_path, args.codex_bin)
    return run_codex_foreground(task_path, codex_bin=args.codex_bin)


def command_worker(args: argparse.Namespace) -> int:
    return run_codex_foreground(args.task, codex_bin=args.codex_bin)


def command_status(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task, cwd=args.cwd)
    state = refresh_status(task_path)
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def command_result(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task, cwd=args.cwd)
    task = parse_task_file(task_path)
    print(render_result(task))
    return 0


def command_cancel(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task, cwd=args.cwd)
    state = cancel_task(task_path)
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex-runner")
    parser.add_argument("--cwd", default=os.getcwd())
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("task")
    start.add_argument("--background", action="store_true")
    start.add_argument("--codex-bin", default="codex")
    start.set_defaults(func=command_start)

    worker = sub.add_parser("worker")
    worker.add_argument("task")
    worker.add_argument("--codex-bin", default="codex")
    worker.set_defaults(func=command_worker)

    status = sub.add_parser("status")
    status.add_argument("task")
    status.set_defaults(func=command_status)

    result = sub.add_parser("result")
    result.add_argument("task")
    result.set_defaults(func=command_result)

    cancel = sub.add_parser("cancel")
    cancel.add_argument("task")
    cancel.set_defaults(func=command_cancel)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Add executable wrapper**

Create `tools/codex-runner/codex-runner`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec python3 -m tools.codex_runner.cli "$@"
```

Then run:

```bash
chmod +x tools/codex-runner/codex-runner
```

- [ ] **Step 6: Run tests**

Run:

```bash
python3 -m unittest tests.test_codex_runner -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit Task 2**

Run:

```bash
git add tools tests/test_codex_runner.py
git diff --staged
git commit -m "feat(codex-runner): manage codex background jobs"
```

Expected: commit succeeds with start/status/result/cancel support.

## Task 3: Implement Audited Resume

**Files:**
- Modify: `tools/codex_runner/runner.py`
- Modify: `tools/codex_runner/cli.py`
- Modify: `tests/test_codex_runner.py`

- [ ] **Step 1: Add failing test for audited resume task creation**

Append to `tests/test_codex_runner.py`:

```python
from tools.codex_runner.runner import create_audited_resume_task


class CodexRunnerResumeTests(unittest.TestCase):
    def test_create_audited_resume_task_writes_followup_task(self):
        root, task_path = CodexRunnerParsingTests().make_project()
        report_path = root / "docs" / "tasks" / "2026-06-28-example" / "codex-report.md"
        report_path.write_text(
            "# Codex Report: Example\n\n## Risks / Follow-ups\n\n- Add final verification.\n",
            encoding="utf-8",
        )

        followup = create_audited_resume_task(
            task_path,
            goal="Run the final verification and fix any scoped failure.",
            start=False,
        )

        followup_path = Path(followup["task_path"])
        self.assertTrue(followup_path.exists())
        self.assertNotEqual(followup["task_id"], "2026-06-28-example")
        text = followup_path.read_text(encoding="utf-8")
        self.assertIn("Previous task", text)
        self.assertIn("2026-06-28-example", text)
        self.assertIn("Run the final verification", text)
        self.assertIn("Add final verification", text)
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
python3 -m unittest tests.test_codex_runner -v
```

Expected: FAIL with missing `create_audited_resume_task`.

- [ ] **Step 3: Add audited resume implementation**

Append to `tools/codex_runner/runner.py`:

```python
def next_followup_id(old_task_id: str, target_project: str) -> str:
    date_part = utc_now()[:10]
    slug = old_task_id
    if re.match(r"^\\d{4}-\\d{2}-\\d{2}-", slug):
        slug = slug[11:]
    base = f"{date_part}-{slug}-followup"
    tasks_dir = Path(target_project) / "docs" / "tasks"
    index = 1
    while (tasks_dir / f"{base}-{index}").exists():
        index += 1
    return f"{base}-{index}"


def create_audited_resume_task(task_path: str | Path, goal: str, start: bool = False) -> dict[str, str]:
    previous = parse_task_file(task_path)
    previous_task_text = read_text(Path(previous["task_path"]))
    report_path = Path(previous["report_path"])
    previous_report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else "Previous Codex report was not found."
    new_task_id = next_followup_id(previous["task_id"], previous["target_project"])
    new_dir = Path(previous["target_project"]) / "docs" / "tasks" / new_task_id
    new_task_path = new_dir / "task.md"
    report_rel = f"docs/tasks/{new_task_id}/codex-report.md"
    text = textwrap.dedent(
        f"""
        # Codex Task: Follow up {previous['task_id']}

        task_id: {new_task_id}
        target_project: {previous['target_project']}
        task_kind: {previous.get('task_kind', 'implementation')}
        mode: {previous.get('mode', 'semi-auto')}
        sandbox: {previous.get('sandbox', 'workspace-write')}
        provider: {previous.get('provider', '')}
        artifact_policy: {previous.get('artifact_policy', 'keep-report-only')}
        source: claude-code

        ## Goal

        {goal}

        ## Context

        Previous task: {previous['task_id']}
        Previous task file: docs/tasks/{previous['task_id']}/task.md
        Previous report file: docs/tasks/{previous['task_id']}/codex-report.md

        ## Previous Report

        ```markdown
        {previous_report_text.strip()}
        ```

        ## Previous Task

        ```markdown
        {previous_task_text.strip()}
        ```

        ## Scope

        Allowed:

        - Continue only from the previous task and report.
        - Keep changes within the previous task's declared scope unless this follow-up goal narrows it further.

        Out of scope:

        - Native `codex resume`.
        - Unrelated refactors.
        - `git add`.
        - `git commit`.

        ## Constraints

        - Do not run `git add`.
        - Do not run `git commit`.
        - Do not write temporary files outside `.codex-runs/{new_task_id}/`.
        - Preserve unrelated user changes.

        ## Verification

        Commands:

        - Use the previous task's verification commands unless this follow-up goal provides a narrower command.

        Expected result:

        - The follow-up goal is complete and the final report explains verification.

        ## Report

        Write report to:

        ```text
        {report_rel}
        ```
        """
    ).strip() + "\n"
    write_text(new_task_path, text)
    return parse_task_file(new_task_path)
```

- [ ] **Step 4: Add `resume` CLI command**

Modify `tools/codex_runner/cli.py` imports to include:

```python
    create_audited_resume_task,
```

Add command function:

```python
def command_resume(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task, cwd=args.cwd)
    followup = create_audited_resume_task(task_path, goal=args.goal, start=False)
    print(json.dumps(followup, indent=2, sort_keys=True))
    if args.start:
        return start_background(Path(followup["task_path"]), args.codex_bin) if args.background else run_codex_foreground(followup["task_path"], codex_bin=args.codex_bin)
    return 0
```

Add parser section:

```python
    resume = sub.add_parser("resume")
    resume.add_argument("task")
    resume.add_argument("--goal", required=True)
    resume.add_argument("--start", action="store_true")
    resume.add_argument("--background", action="store_true")
    resume.add_argument("--codex-bin", default="codex")
    resume.set_defaults(func=command_resume)
```

- [ ] **Step 5: Run tests**

Run:

```bash
python3 -m unittest tests.test_codex_runner -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit Task 3**

Run:

```bash
git add tools tests/test_codex_runner.py
git diff --staged
git commit -m "feat(codex-runner): add audited resume tasks"
```

Expected: commit succeeds with audited resume support.

## Task 4: Document Runner Integration In Skills

**Files:**
- Modify: `README.md`
- Modify: `shared/codex-task-contract.md`
- Modify: `claude-codex-runner/SKILL.md`
- Modify: `claude-codex-runner/references/runner-workflow.md`
- Modify: `codex-task-executor/references/execution-protocol.md`

- [ ] **Step 1: Update README layout**

Modify `README.md` layout to include:

```text
  tools/
    codex-runner/
      codex-runner
    codex_runner/
      cli.py
      runner.py
```

Add convention:

```markdown
- `tools/codex-runner/codex-runner` manages background Codex runs for task files.
```

- [ ] **Step 2: Update shared contract**

Add section `## Background Runner` to `shared/codex-task-contract.md`:

```markdown
## Background Runner

Claude Code should prefer the local runner when background execution, status, result, cancel, or audited resume is needed:

```bash
tools/codex-runner/codex-runner start docs/tasks/<task-id>/task.md --background
tools/codex-runner/codex-runner status <task-id>
tools/codex-runner/codex-runner result <task-id>
tools/codex-runner/codex-runner cancel <task-id>
tools/codex-runner/codex-runner resume <task-id> --goal "<follow-up goal>"
```

The runner records state in `.codex-runs/<task-id>/run.json` and logs in `.codex-runs/<task-id>/stdout.log` and `.codex-runs/<task-id>/stderr.log`.

Audited resume creates a new task directory under `docs/tasks/<new-task-id>/`; it does not use native `codex resume`.
```

- [ ] **Step 3: Update Claude runner skill and workflow**

In `claude-codex-runner/SKILL.md`, add:

```markdown
- Background runner: use `tools/codex-runner/codex-runner` for start/status/result/cancel/resume-audited.
```

In `runner-workflow.md`, add a new section before direct Codex invocation:

```markdown
## 8. Use Background Runner When Needed

Use the local runner when the user wants Claude to continue the main conversation while Codex works:

```bash
tools/codex-runner/codex-runner start docs/tasks/<task-id>/task.md --background
```

Check status:

```bash
tools/codex-runner/codex-runner status <task-id>
```

Read result:

```bash
tools/codex-runner/codex-runner result <task-id>
```

Cancel:

```bash
tools/codex-runner/codex-runner cancel <task-id>
```

Create audited follow-up:

```bash
tools/codex-runner/codex-runner resume <task-id> --goal "<follow-up goal>"
```
```

Renumber later sections so direct `codex exec` is clearly labeled as fallback or foreground-only.

- [ ] **Step 4: Update Codex executor protocol**

Add to `codex-task-executor/references/execution-protocol.md`:

```markdown
## Background Runs

The background runner changes process management only. Codex still executes one task file, writes one `codex-report.md`, and exits.

Do not manage background status from inside Codex. The runner owns `run.json`, stdout logs, stderr logs, cancellation, and audited resume task creation.
```

- [ ] **Step 5: Verify docs mention all commands**

Run:

```bash
rg "start docs/tasks/<task-id>/task.md --background|status <task-id>|result <task-id>|cancel <task-id>|resume <task-id>" README.md shared claude-codex-runner codex-task-executor
```

Expected: matches appear in shared contract and Claude runner workflow.

- [ ] **Step 6: Commit Task 4**

Run:

```bash
git add README.md shared claude-codex-runner codex-task-executor
git diff --staged
git commit -m "docs(codex-runner): document background task workflow"
```

Expected: commit succeeds with documentation updates only.

## Task 5: End-To-End Dry Run

**Files:**
- Create during verification only: `/tmp/codex-runner-bg-smoke/`
- Use fake Codex binary inside `/tmp/codex-runner-bg-smoke/fake-codex`

- [ ] **Step 1: Create disposable project and fake Codex**

Run:

```bash
mkdir -p /tmp/codex-runner-bg-smoke/bin
cd /tmp/codex-runner-bg-smoke
git init
printf '# Smoke\n' > README.md
cat > bin/fake-codex <<'SH'
#!/usr/bin/env bash
set -euo pipefail
prompt="${@: -1}"
task_path="$(printf '%s\n' "$prompt" | sed -n 's/.*Execute \(docs\/tasks\/[^ ]*\/task.md\).*/\1/p' | head -n1)"
report_path="$(dirname "$task_path")/codex-report.md"
mkdir -p "$(dirname "$report_path")"
cat > "$report_path" <<'MD'
# Codex Report: Fake

task_id: smoke
status: success
mode: semi-auto
sandbox: workspace-write
provider:
artifact_policy: keep-report-only

## Summary

Fake Codex completed.
MD
printf 'fake codex stdout\n'
SH
chmod +x bin/fake-codex
```

Expected: fake Codex executable exists.

- [ ] **Step 2: Create smoke task**

Run:

```bash
cd /tmp/codex-runner-bg-smoke
mkdir -p docs/tasks/2026-06-28-bg-smoke
cat > docs/tasks/2026-06-28-bg-smoke/task.md <<EOF
# Codex Task: Background Smoke

task_id: 2026-06-28-bg-smoke
target_project: /tmp/codex-runner-bg-smoke
task_kind: implementation
mode: semi-auto
sandbox: workspace-write
provider:
artifact_policy: keep-report-only
source: claude-code

## Goal

Run fake Codex and write a report.

## Scope

Allowed:

- README.md

Out of scope:

- git add
- git commit

## Constraints

- Do not run \`git add\`.
- Do not run \`git commit\`.

## Verification

Commands:

- test -f docs/tasks/2026-06-28-bg-smoke/codex-report.md

Expected result:

- The report exists.

## Report

Write report to:

\`\`\`text
docs/tasks/2026-06-28-bg-smoke/codex-report.md
\`\`\`
EOF
```

Expected: task file exists.

- [ ] **Step 3: Start background run**

Run from the skills repository:

```bash
tools/codex-runner/codex-runner --cwd /tmp/codex-runner-bg-smoke start 2026-06-28-bg-smoke --background --codex-bin /tmp/codex-runner-bg-smoke/bin/fake-codex
```

Expected: JSON state prints with `status` initially `queued` and `worker_pid` set.

- [ ] **Step 4: Check status and result**

Run:

```bash
sleep 1
tools/codex-runner/codex-runner --cwd /tmp/codex-runner-bg-smoke status 2026-06-28-bg-smoke
tools/codex-runner/codex-runner --cwd /tmp/codex-runner-bg-smoke result 2026-06-28-bg-smoke
```

Expected: status is `success`, and result includes `Fake Codex completed`.

- [ ] **Step 5: Verify audited resume**

Run:

```bash
tools/codex-runner/codex-runner --cwd /tmp/codex-runner-bg-smoke resume 2026-06-28-bg-smoke --goal "Continue from the fake report and confirm no source edits are needed."
find /tmp/codex-runner-bg-smoke/docs/tasks -maxdepth 2 -name task.md | sort
```

Expected: a new follow-up `task.md` appears under `/tmp/codex-runner-bg-smoke/docs/tasks/<new-task-id>/task.md`.

- [ ] **Step 6: Verify cancellation path with sleeping fake Codex**

Run:

```bash
cat > /tmp/codex-runner-bg-smoke/bin/sleep-codex <<'SH'
#!/usr/bin/env bash
sleep 30
SH
chmod +x /tmp/codex-runner-bg-smoke/bin/sleep-codex
tools/codex-runner/codex-runner --cwd /tmp/codex-runner-bg-smoke start 2026-06-28-bg-smoke --background --codex-bin /tmp/codex-runner-bg-smoke/bin/sleep-codex
sleep 1
tools/codex-runner/codex-runner --cwd /tmp/codex-runner-bg-smoke cancel 2026-06-28-bg-smoke
tools/codex-runner/codex-runner --cwd /tmp/codex-runner-bg-smoke status 2026-06-28-bg-smoke
```

Expected: final status is `cancelled`.

## Task 6: Final Verification And Commit

**Files:**
- Verify all files created or modified by Tasks 1 through 4.

- [ ] **Step 1: Run full unit tests**

Run:

```bash
python3 -m unittest tests.test_codex_runner -v
```

Expected: all tests pass.

- [ ] **Step 2: Verify CLI help**

Run:

```bash
tools/codex-runner/codex-runner --help
tools/codex-runner/codex-runner start --help
tools/codex-runner/codex-runner resume --help
```

Expected: commands show help text and exit 0.

- [ ] **Step 3: Verify docs and protocol references**

Run:

```bash
rg "run.json|stdout.log|stderr.log|resume-audited|audited resume|codex-runner start|codex-runner status|codex-runner result|codex-runner cancel" README.md shared claude-codex-runner codex-task-executor tools tests
```

Expected: matches appear in docs, runner code, and tests.

- [ ] **Step 4: Check working tree**

Run:

```bash
git status --short
git diff --stat
```

Expected: only planned files are modified.

- [ ] **Step 5: Commit final verification fixes if needed**

If any small fixes were made after previous commits, run:

```bash
git add README.md shared claude-codex-runner codex-task-executor tools tests
git diff --staged
git commit -m "test(codex-runner): verify background workflow"
```

Expected: commit succeeds only if there were additional fixes. If there are no changes, skip this commit.

## Self-Review

- Spec coverage: The plan covers `start`, `status`, `result`, `cancel`, and audited `resume`; foreground and background runs; state files; stdout/stderr logs; cancellation; result fallback; follow-up task creation; skill documentation integration; and dry-run verification.
- Placeholder scan: The plan intentionally avoids draft-marker text and unresolved requirement markers. Template-like strings are concrete command examples or task-file literals.
- Type consistency: The same `task_id`, `task_path`, `target_project`, `run_dir`, `report_path`, `status`, `worker_pid`, `codex_pid`, `codex_pgid`, `provider`, and `sandbox` fields are used in tests, runner state, CLI behavior, and documentation.

Plan complete and saved to `docs/superpowers/plans/2026-06-28-codex-runner-background-job-manager.md`. Two execution options:

1. Subagent-Driven (recommended) - dispatch a fresh subagent per task, review between tasks, fast iteration
2. Inline Execution - execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
