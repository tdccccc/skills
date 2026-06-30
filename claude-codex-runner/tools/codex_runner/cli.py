from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from .runner import (
    cancel_task,
    create_audited_resume_task,
    list_tasks,
    parse_task_file,
    prepare_run_files,
    refresh_status,
    render_result,
    release_run_lock,
    resolve_task_reference,
    run_dir_for,
    run_codex_foreground,
    stderr_path_for,
    synthesize_task_file,
    write_run_lock,
    write_state,
)


def wait_for_startup_gate(path: str | None, timeout_seconds: float = 30.0) -> None:
    if not path:
        return
    gate = Path(path)
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if gate.exists():
            gate.unlink(missing_ok=True)
            return
        time.sleep(0.05)
    raise TimeoutError(f"Timed out waiting for worker startup gate: {gate}")


def start_background(task_path: Path, codex_bin: str) -> int:
    task = parse_task_file(task_path)
    state = prepare_run_files(task)
    startup_gate = run_dir_for(task) / ".worker-start"
    startup_gate.unlink(missing_ok=True)
    command = [
        sys.executable,
        "-m",
        "codex_runner.cli",
        "worker",
        str(task_path),
        "--codex-bin",
        codex_bin,
        "--startup-gate",
        str(startup_gate),
    ]
    pkg_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(pkg_root)
    try:
        with stderr_path_for(task).open("w", encoding="utf-8") as stderr_f:
            worker = subprocess.Popen(
                command,
                cwd=task["target_project"],
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=stderr_f,
                start_new_session=True,
                text=True,
            )
        state["worker_pid"] = worker.pid
        write_state(task, state)
        write_run_lock(task, worker.pid)
        startup_gate.write_text("ready\n", encoding="utf-8")
    except Exception:
        release_run_lock(task)
        raise
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def command_start(args: argparse.Namespace) -> int:
    if args.prompt is not None:
        if args.task is not None:
            print("error: provide either a task reference or --prompt, not both", file=sys.stderr)
            return 2
        task_path = synthesize_task_file(
            args.prompt,
            project=args.project,
            sandbox=args.sandbox,
            provider=args.provider,
        )
        print(f"Synthesized task file: {task_path}", file=sys.stderr)
    elif args.task is not None:
        task_path = resolve_task_reference(args.task)
    else:
        print("error: start requires a task reference or --prompt", file=sys.stderr)
        return 2

    return start_background(task_path, args.codex_bin)


def command_worker(args: argparse.Namespace) -> int:
    wait_for_startup_gate(args.startup_gate)
    return run_codex_foreground(args.task, codex_bin=args.codex_bin)


def command_status(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task)
    state = refresh_status(task_path)
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def command_result(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task)
    task = parse_task_file(task_path)
    print(render_result(task))
    return 0


def command_list(args: argparse.Namespace) -> int:
    project = Path(args.project or os.getcwd()).resolve()
    tasks = list_tasks(project)
    if not tasks:
        print("No tasks found.")
        return 0
    print(json.dumps(tasks, indent=2, sort_keys=True))
    return 0


def command_cancel(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task)
    state = cancel_task(task_path)
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def command_resume(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task)
    followup = create_audited_resume_task(task_path, goal=args.goal)
    print(json.dumps(followup, indent=2, sort_keys=True))
    if args.start:
        return start_background(Path(followup["task_path"]), args.codex_bin)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex-runner")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Start a Codex task in background")
    start.add_argument("task", nargs="?", default=None)
    start.add_argument("--prompt", default=None, help="one-line task; synthesizes a task file instead of reading one")
    start.add_argument("--project", default=None, help="target project dir for --prompt (default: current directory)")
    start.add_argument("--sandbox", default="workspace-write", help="Codex sandbox for --prompt (default: workspace-write)")
    start.add_argument("--provider", default="", help="Codex provider profile for --prompt")
    start.add_argument("--codex-bin", default="codex")
    start.set_defaults(func=command_start)

    worker = sub.add_parser("worker")
    worker.add_argument("task")
    worker.add_argument("--codex-bin", default="codex")
    worker.add_argument("--startup-gate", default=None)
    worker.set_defaults(func=command_worker)

    status = sub.add_parser("status", help="Check task status (includes recent log output)")
    status.add_argument("task")
    status.set_defaults(func=command_status)

    result = sub.add_parser("result", help="Print task report")
    result.add_argument("task")
    result.set_defaults(func=command_result)

    list_parser = sub.add_parser("list", help="List all tasks in the project")
    list_parser.add_argument("--project", default=None, help="project directory (default: current directory)")
    list_parser.set_defaults(func=command_list)

    cancel = sub.add_parser("cancel", help="Cancel a running task")
    cancel.add_argument("task")
    cancel.set_defaults(func=command_cancel)

    resume = sub.add_parser("resume", help="Create a follow-up task (--start to run it in background)")
    resume.add_argument("task")
    resume.add_argument("--goal", required=True)
    resume.add_argument("--start", action="store_true", help="start the follow-up immediately in background")
    resume.add_argument("--codex-bin", default="codex")
    resume.set_defaults(func=command_resume)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        return args.func(args)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except (ValueError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
