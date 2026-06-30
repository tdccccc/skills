from __future__ import annotations

import json
import os
import re
import signal
import subprocess
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
        if line.startswith("## "):
            break
        if line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip()
    return metadata


def extract_report_path(text: str) -> str:
    matches = re.findall(r"Write report to:\s*\n\s*```text\s*\n([^`]+?)\n```", text, re.S)
    if matches:
        return matches[-1].strip()
    return ""


def parse_task_file(task_path: str | Path) -> dict[str, str]:
    path = Path(task_path).resolve()
    text = read_text(path)
    metadata = parse_metadata(text)
    task_id = metadata.get("task_id") or path.parent.name
    target_project_raw = metadata.get("target_project")
    if not target_project_raw:
        raise ValueError(
            f"Task file {path} is missing 'target_project' metadata. "
            "All task files must declare an absolute target_project path."
        )
    target_project = Path(target_project_raw).resolve()
    report_value = extract_report_path(text)
    if report_value:
        report_path = Path(report_value)
    else:
        report_path = Path("docs") / "tasks" / task_id / "codex-report.md"
        import warnings
        warnings.warn(
            f"Could not parse report path from {path}; "
            f"falling back to {report_path}",
            RuntimeWarning,
            stacklevel=2,
        )
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
    if ref.is_absolute():
        if ref.exists():
            return ref.resolve()
        raise FileNotFoundError(f"Absolute task reference not found: {reference}")
    else:
        # Resolve relative paths against the --cwd parameter, not the process cwd.
        ref_resolved = (base / ref).resolve()
        if ref_resolved.exists():
            return ref_resolved
    candidate = base / "docs" / "tasks" / str(reference) / "task.md"
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"Cannot resolve task reference: {reference}")


def slugify(text: str, max_words: int = 6) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    slug = "-".join(words[:max_words])
    return slug or "task"


def next_prompt_id(target_project: str, slug: str) -> str:
    date_part = utc_now()[:10]
    base = f"{date_part}-{slug}"
    tasks_dir = Path(target_project) / "docs" / "tasks"
    if not (tasks_dir / base).exists():
        return base
    index = 2
    while (tasks_dir / f"{base}-{index}").exists():
        index += 1
    return f"{base}-{index}"


def synthesize_task_file(
    prompt: str,
    project: str | Path | None = None,
    cwd: str | Path | None = None,
    task_kind: str = "implementation",
    mode: str = "semi-auto",
    sandbox: str = "workspace-write",
    provider: str = "",
    artifact_policy: str = "keep-report-only",
) -> Path:
    """Write a minimal but contract-compliant task file from a one-line prompt.

    The synthesized file lives under <project>/docs/tasks/<auto-id>/task.md so the
    rest of the runner (status/result/cancel/resume) works exactly as it does for
    hand-written task files.
    """
    goal = prompt.strip()
    if not goal:
        raise ValueError("prompt must not be empty")

    # Read-only sandbox implies analysis, not implementation — fix mismatched
    # defaults that would contradict the sandbox mode in the task contract.
    if sandbox == "read-only" and task_kind == "implementation":
        task_kind = "analysis"

    target_project = Path(project or cwd or os.getcwd()).resolve()
    task_id = next_prompt_id(str(target_project), slugify(goal))
    task_path = target_project / "docs" / "tasks" / task_id / "task.md"
    report_rel = f"docs/tasks/{task_id}/codex-report.md"
    text = "\n".join(
        [
            f"# Codex Task: {task_id}",
            "",
            f"task_id: {task_id}",
            f"target_project: {target_project}",
            f"task_kind: {task_kind}",
            f"mode: {mode}",
            f"sandbox: {sandbox}",
            f"provider: {provider}",
            f"artifact_policy: {artifact_policy}",
            "source: claude-code-prompt",
            "",
            "## Goal",
            "",
            goal,
            "",
            "## Scope",
            "",
            "Allowed:",
            "",
            "- Make the focused changes needed to satisfy the goal.",
            "- Promote valuable regression tests into the project's normal test directories.",
            "",
            "Out of scope:",
            "",
            "- Unrelated refactors.",
            "- `git add`.",
            "- `git commit`.",
            "",
            "## Constraints",
            "",
            "- Do not run `git add`.",
            "- Do not run `git commit`.",
            f"- Do not write temporary files outside `.codex-runs/{task_id}/`.",
            "- Inspect `git status --short` before editing; preserve existing user changes.",
            "- If changes contain multiple independent intents, suggest splitting commits.",
            "",
            "## Verification",
            "",
            "Commands:",
            "",
            "- Run the project's existing tests or build when applicable.",
            "",
            "Expected result:",
            "",
            "- The goal is complete and the final report explains verification.",
            "",
            "## Report",
            "",
            "Write report to:",
            "",
            "```text",
            report_rel,
            "```",
            "",
            "Write a report even on failure. If the sandbox is read-only, print the",
            "full report to stdout instead of writing the report file.",
            "",
        ]
    )
    write_text(task_path, text)
    return task_path.resolve()


def run_dir_for(task: dict[str, str]) -> Path:
    return Path(task["target_project"]) / ".codex-runs" / task["task_id"]


def lock_path_for(task: dict[str, str]) -> Path:
    return run_dir_for(task) / ".lock"


def acquire_run_lock(task: dict[str, str], force: bool = False) -> bool:
    """Acquire an exclusive lock for this task's run directory.

    Returns True if acquired (or forced), False if another run is alive.
    """
    lock_file = lock_path_for(task)
    run_dir = run_dir_for(task)
    run_dir.mkdir(parents=True, exist_ok=True)
    if lock_file.exists() and not force:
        try:
            lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
            lock_pid = lock_data.get("pid")
            if lock_pid and pid_alive(lock_pid):
                return False  # another run is alive, refuse
        except (json.JSONDecodeError, OSError):
            pass  # stale lock, overwrite
    lock_file.write_text(
        json.dumps({"pid": os.getpid(), "started_at": utc_now()}, indent=2) + "\n",
        encoding="utf-8",
    )
    return True


def release_run_lock(task: dict[str, str]) -> None:
    lock_file = lock_path_for(task)
    try:
        lock_file.unlink(missing_ok=True)
    except OSError:
        pass


def ensure_codex_runs_ignored(target_project: str | Path) -> bool:
    """Ensure `.codex-runs/` is git-ignored in the target project.

    Uses `git check-ignore` to test, and uses the file only when the project
    is a git repo. Returns True if the file was created or appended to.
    No-op when already present or not a git repo.
    """
    project = Path(target_project)
    if not (project / ".git").exists():
        return False
    # Check via git first — more reliable than parsing .gitignore manually.
    try:
        subprocess.run(
            ["git", "check-ignore", "-q", ".codex-runs/"],
            cwd=project,
            check=True,
            capture_output=True,
        )
        return False  # already ignored
    except subprocess.CalledProcessError:
        pass  # not ignored yet, proceed
    gitignore = project / ".gitignore"
    entry = ".codex-runs/"
    current = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    separator = "" if current == "" or current.endswith("\n") else "\n"
    gitignore.write_text(f"{current}{separator}{entry}\n", encoding="utf-8")
    return True


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
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_state_by_task(task_path: str | Path) -> tuple[dict[str, str], dict[str, Any]]:
    task = parse_task_file(task_path)
    state_path = state_path_for(task)
    if not state_path.exists():
        raise FileNotFoundError(f"Run state not found: {state_path}")
    return task, json.loads(state_path.read_text(encoding="utf-8"))


def relative_to_project(path: str, target_project: str) -> str:
    try:
        return str(Path(path).resolve().relative_to(Path(target_project).resolve()))
    except ValueError:
        return str(path)


def build_prompt(task: dict[str, str]) -> str:
    task_rel = relative_to_project(task["task_path"], task["target_project"])
    report_rel = relative_to_project(task["report_path"], task["target_project"])
    sandbox = task.get("sandbox", "workspace-write")
    if sandbox == "read-only":
        # A read-only sandbox cannot create the report file, so ask Codex to
        # return the full structured report on stdout instead. The runner
        # captures stdout and `result` surfaces it when no report file exists.
        output_contract = (
            "Do not write any files; the sandbox is read-only.\n"
            "Print your full structured report to stdout as your final message, then exit."
        )
    else:
        output_contract = f"Write {report_rel}, then exit."
    return textwrap.dedent(
        f"""
        <task>
        Execute {task_rel} in {task['target_project']}.
        </task>

        <execution_contract>
        Follow the Codex task contract included in the task file context. The task file is authoritative.
        Use sandbox {sandbox}. Do not stage or commit unless the task explicitly allows it.
        </execution_contract>

        <output_contract>
        {output_contract}
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


def prepare_run_files(task: dict[str, str], force: bool = False) -> dict[str, Any]:
    run_dir_for(task).mkdir(parents=True, exist_ok=True)
    if not acquire_run_lock(task, force=force):
        raise RuntimeError(
            f"Task {task['task_id']} is already running (lock held). "
            "Use --force to override."
        )
    ensure_codex_runs_ignored(task["target_project"])
    state = build_initial_state(task)
    existing_path = state_path_for(task)
    if existing_path.exists():
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
        state["worker_pid"] = existing.get("worker_pid")
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
    try:
        with stdout_path_for(task).open("w", encoding="utf-8") as stdout_f, stderr_path_for(task).open("w", encoding="utf-8") as stderr_f:
            process = subprocess.Popen(
                command,
                cwd=task["target_project"],
                stdin=subprocess.DEVNULL,
                stdout=stdout_f,
                stderr=stderr_f,
                start_new_session=True,
                text=True,
            )
            state["codex_pid"] = process.pid
            try:
                state["codex_pgid"] = os.getpgid(process.pid)
            except ProcessLookupError:
                state["codex_pgid"] = None
            write_state(task, state)
            exit_code = process.wait()
        state["exit_code"] = exit_code
        state["finished_at"] = utc_now()
        state["status"] = STATUS_SUCCESS if exit_code == 0 else STATUS_FAILED
        write_state(task, state)
        release_run_lock(task)
        return exit_code
    except Exception:
        state["exit_code"] = 1
        state["finished_at"] = utc_now()
        state["status"] = STATUS_FAILED
        write_state(task, state)
        release_run_lock(task)
        raise


def run_codex_foreground_stream(task_path: str | Path, codex_bin: str = "codex") -> int:
    """Run Codex in foreground, streaming stdout to the terminal in real-time.

    Same as run_codex_foreground but tee stdout so the caller sees progress.
    """
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
    try:
        with stdout_path_for(task).open("w", encoding="utf-8") as stdout_f:
            process = subprocess.Popen(
                command,
                cwd=task["target_project"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                text=True,
            )
            state["codex_pid"] = process.pid
            try:
                state["codex_pgid"] = os.getpgid(process.pid)
            except ProcessLookupError:
                state["codex_pgid"] = None
            write_state(task, state)

            # Stream stdout to terminal and tee to log file simultaneously.
            for line in process.stdout:
                print(line, end="", flush=True)
                stdout_f.write(line)
            stdout_f.flush()

            exit_code = process.wait()
        state["exit_code"] = exit_code
        state["finished_at"] = utc_now()
        state["status"] = STATUS_SUCCESS if exit_code == 0 else STATUS_FAILED
        write_state(task, state)
        release_run_lock(task)
        return exit_code
    except Exception:
        state["exit_code"] = 1
        state["finished_at"] = utc_now()
        state["status"] = STATUS_FAILED
        write_state(task, state)
        release_run_lock(task)
        raise


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


def pid_start_time(pid: int) -> float | None:
    """Get the start time of a process (Unix timestamp).

    Returns None if the process doesn't exist or can't be read.
    """
    try:
        # Linux /proc is fast and precise.
        with open(f"/proc/{pid}/stat", "r") as f:
            fields = f.read().split()
            # Field 21 (0-indexed) is starttime in jiffies since boot.
            start_jiffies = int(fields[21])
        # Convert jiffies to seconds since boot, then to Unix time.
        with open("/proc/stat", "r") as f:
            for line in f:
                if line.startswith("btime "):
                    boot_time = int(line.split()[1])
                    break
        clock_ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
        return boot_time + (start_jiffies / clock_ticks)
    except (OSError, IndexError, ValueError, KeyError):
        return None


def validate_pid(pid: int, since_stamp: str | None) -> bool:
    """Check if a PID is alive AND matches the expected start time.

    This reduces the risk of acting on a recycled PID.
    """
    if not pid_alive(pid):
        return False
    if not since_stamp:
        return True  # no timestamp to compare, fall back to basic check
    try:
        import datetime as dt
        expected = dt.datetime.fromisoformat(since_stamp).timestamp()
        actual = pid_start_time(pid)
        if actual is None:
            return True  # can't verify, be permissive
        # Allow a small window (5s) before the expected time — the process
        # may have started slightly before we recorded the timestamp.
        return abs(actual - expected) < 5
    except (ValueError, TypeError):
        return True


def refresh_status(task_path: str | Path) -> dict[str, Any]:
    task, state = read_state_by_task(task_path)
    updated = False
    running_worker = state.get("worker_pid") and validate_pid(int(state["worker_pid"]), state.get("started_at"))
    running_codex = state.get("codex_pid") and validate_pid(int(state["codex_pid"]), state.get("started_at"))
    if state.get("status") == STATUS_RUNNING and not running_worker and not running_codex:
        state["status"] = STATUS_UNKNOWN
        state["finished_at"] = state.get("finished_at") or utc_now()
        updated = True
    elif state.get("status") == STATUS_QUEUED and state.get("worker_pid") and not running_worker:
        state["status"] = STATUS_UNKNOWN
        state["finished_at"] = state.get("finished_at") or utc_now()
        updated = True

    # Always attach recent log output so status checks are informative.
    state["recent_log"] = tail_text(stdout_path_for(task), limit=2000)

    if updated:
        write_state(task, state)
    return state


def list_tasks(project_dir: str | Path) -> list[dict[str, Any]]:
    """Scan a project for all known tasks (created but not yet completed, plus finished ones).

    Returns a list of state dicts sorted by creation time (most recent first).
    """
    project = Path(project_dir).resolve()
    tasks_dir = project / "docs" / "tasks"
    results: list[dict[str, Any]] = []
    if not tasks_dir.is_dir():
        return results

    for task_dir in sorted(tasks_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        task_file = task_dir / "task.md"
        if not task_file.is_file():
            continue
        try:
            task = parse_task_file(task_file)
        except Exception:
            continue
        state_path = state_path_for(task)
        if state_path.exists():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
            except Exception:
                state = {"status": "unknown"}
        else:
            state = {"status": "never_run"}
        state["task_id"] = task["task_id"]
        state["task_path"] = str(task_file)
        state["report_path"] = task.get("report_path", "")
        results.append(state)

    # Sort by started_at descending, then finished_at descending, then task_id.
    def sort_key(s: dict) -> str:
        return s.get("started_at") or s.get("finished_at") or s.get("task_id", "")

    results.sort(key=sort_key, reverse=True)
    return results


def tail_text(path: Path, limit: int = 4000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[-limit:]


def full_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def render_result(task: dict[str, str]) -> str:
    report_path = Path(task["report_path"])
    if report_path.exists():
        return report_path.read_text(encoding="utf-8")
    # Read-only tasks print the report to stdout — read the full content
    # (no tail truncation) so the report is never cut off.
    stdout = full_text(stdout_path_for(task))
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
    all_pids: list[int] = []

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
        all_pids.append(int(worker_pid))

    # Wait up to 5 seconds for graceful exit, then escalate to SIGKILL.
    if all_pids:
        import time
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            alive = [p for p in all_pids if pid_alive(p)]
            if not alive:
                break
            time.sleep(0.5)
        else:
            # Escalate: processes still alive after timeout.
            if pgid:
                try:
                    os.killpg(int(pgid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
            for p in all_pids:
                try:
                    os.kill(p, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    state["status"] = STATUS_CANCELLED
    state["finished_at"] = utc_now()
    write_state(task, state)
    release_run_lock(task)
    return state


def next_followup_id(old_task_id: str, target_project: str) -> str:
    date_part = utc_now()[:10]
    slug = old_task_id
    if re.match(r"^\d{4}-\d{2}-\d{2}-", slug):
        slug = slug[11:]
    base = f"{date_part}-{slug}-followup"
    tasks_dir = Path(target_project) / "docs" / "tasks"
    index = 1
    while (tasks_dir / f"{base}-{index}").exists():
        index += 1
    return f"{base}-{index}"


def create_audited_resume_task(task_path: str | Path, goal: str, start: bool = False) -> dict[str, str]:
    del start
    previous = parse_task_file(task_path)
    new_task_id = next_followup_id(previous["task_id"], previous["target_project"])
    new_dir = Path(previous["target_project"]) / "docs" / "tasks" / new_task_id
    new_dir.mkdir(parents=True, exist_ok=True)
    new_task_path = new_dir / "task.md"
    report_rel = f"docs/tasks/{new_task_id}/codex-report.md"

    # Copy previous artifacts as separate files to avoid nested backtick issues.
    previous_task_source = read_text(Path(previous["task_path"]))
    write_text(new_dir / "previous-task.md", previous_task_source)

    report_path = Path(previous["report_path"])
    if report_path.exists():
        write_text(new_dir / "previous-report.md", report_path.read_text(encoding="utf-8"))
    else:
        write_text(new_dir / "previous-report.md", "Previous Codex report was not found.")

    text = "\n".join(
        [
            f"# Codex Task: Follow up {previous['task_id']}",
            "",
            f"task_id: {new_task_id}",
            f"target_project: {previous['target_project']}",
            f"task_kind: {previous.get('task_kind', 'implementation')}",
            f"mode: {previous.get('mode', 'semi-auto')}",
            f"sandbox: {previous.get('sandbox', 'workspace-write')}",
            f"provider: {previous.get('provider', '')}",
            f"artifact_policy: {previous.get('artifact_policy', 'keep-report-only')}",
            "source: claude-code",
            "",
            "## Goal",
            "",
            goal,
            "",
            "## Context",
            "",
            f"Previous task: {previous['task_id']}",
            f"Previous task file: docs/tasks/{new_task_id}/previous-task.md",
            f"Previous report file: docs/tasks/{new_task_id}/previous-report.md",
            "",
            "## Scope",
            "",
            "Allowed:",
            "",
            "- Continue only from the previous task and report.",
            "- Keep changes within the previous task's declared scope unless this follow-up goal narrows it further.",
            "",
            "Out of scope:",
            "",
            "- Native `codex resume`.",
            "- Unrelated refactors.",
            "- `git add`.",
            "- `git commit`.",
            "",
            "## Constraints",
            "",
            "- Do not run `git add`.",
            "- Do not run `git commit`.",
            f"- Do not write temporary files outside `.codex-runs/{new_task_id}/`.",
            "- Preserve unrelated user changes.",
            "",
            "## Verification",
            "",
            "Commands:",
            "",
            "- Use the previous task's verification commands unless this follow-up goal provides a narrower command.",
            "",
            "Expected result:",
            "",
            "- The follow-up goal is complete and the final report explains verification.",
            "",
            "## Report",
            "",
            "Write report to:",
            "",
            "```text",
            report_rel,
            "```",
            "",
        ]
    )
    write_text(new_task_path, text)
    return parse_task_file(new_task_path)
