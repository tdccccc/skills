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
    create_audited_resume_task,
    list_tasks,
    parse_task_file,
    refresh_status,
    render_result,
    resolve_task_reference,
    run_codex_foreground,
    run_codex_foreground_stream,
    synthesize_task_file,
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
        "codex_runner.cli",
        "worker",
        str(task_path),
        "--codex-bin",
        codex_bin,
    ]
    # The package root is the tools/ dir that holds codex_runner/. Inject it via
    # PYTHONPATH so the worker imports without depending on its working directory.
    pkg_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{pkg_root}{os.pathsep}{existing}" if existing else str(pkg_root)
    worker = subprocess.Popen(
        command,
        cwd=task["target_project"],
        env=env,
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
    """Start a Codex task in background (default)."""
    if args.prompt is not None:
        if args.task is not None:
            print("error: provide either a task reference or --prompt, not both", file=sys.stderr)
            return 2
        task_path = synthesize_task_file(
            args.prompt,
            project=args.project,
            cwd=args.cwd,
            sandbox=args.sandbox,
            provider=args.provider,
        )
        print(f"Synthesized task file: {task_path}", file=sys.stderr)
    elif args.task is not None:
        task_path = resolve_task_reference(args.task, cwd=args.cwd)
    else:
        print("error: start requires a task reference or --prompt", file=sys.stderr)
        return 2

    return start_background(task_path, args.codex_bin)


def command_start_fg(args: argparse.Namespace) -> int:
    """Start a Codex task in foreground (streaming output)."""
    if args.prompt is not None:
        if args.task is not None:
            print("error: provide either a task reference or --prompt, not both", file=sys.stderr)
            return 2
        task_path = synthesize_task_file(
            args.prompt,
            project=args.project,
            cwd=args.cwd,
            sandbox=args.sandbox,
            provider=args.provider,
        )
        print(f"Synthesized task file: {task_path}", file=sys.stderr)
    elif args.task is not None:
        task_path = resolve_task_reference(args.task, cwd=args.cwd)
    else:
        print("error: start-fg requires a task reference or --prompt", file=sys.stderr)
        return 2

    return run_codex_foreground_stream(task_path, codex_bin=args.codex_bin)


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


def command_list(args: argparse.Namespace) -> int:
    """List all tasks in the project, most recent first."""
    project = Path(args.project or args.cwd).resolve()
    tasks = list_tasks(project)
    if not tasks:
        print("No tasks found.")
        return 0
    print(json.dumps(tasks, indent=2, sort_keys=True))
    return 0


def command_cancel(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task, cwd=args.cwd)
    state = cancel_task(task_path)
    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


def command_resume(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task, cwd=args.cwd)
    followup = create_audited_resume_task(task_path, goal=args.goal, start=False)
    print(json.dumps(followup, indent=2, sort_keys=True))
    if args.start:
        if args.foreground:
            return run_codex_foreground_stream(followup["task_path"], codex_bin=args.codex_bin)
        return start_background(Path(followup["task_path"]), args.codex_bin)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex-runner")
    parser.add_argument("--cwd", default=os.getcwd())
    sub = parser.add_subparsers(dest="command", required=True)

    # start — default background
    start = sub.add_parser("start", help="Start a Codex task in background")
    start.add_argument("task", nargs="?", default=None)
    start.add_argument("--prompt", default=None, help="one-line task; synthesizes a task file instead of reading one")
    start.add_argument("--project", default=None, help="target project dir for --prompt (default: --cwd)")
    start.add_argument("--sandbox", default="workspace-write", help="Codex sandbox for --prompt (default: workspace-write)")
    start.add_argument("--provider", default="", help="Codex provider profile for --prompt")
    start.add_argument("--codex-bin", default="codex")
    start.set_defaults(func=command_start)

    # start-fg — foreground with streaming output
    start_fg = sub.add_parser("start-fg", help="Start a Codex task in foreground (streaming output)")
    start_fg.add_argument("task", nargs="?", default=None)
    start_fg.add_argument("--prompt", default=None, help="one-line task; synthesizes a task file instead of reading one")
    start_fg.add_argument("--project", default=None, help="target project dir for --prompt (default: --cwd)")
    start_fg.add_argument("--sandbox", default="workspace-write", help="Codex sandbox for --prompt (default: workspace-write)")
    start_fg.add_argument("--provider", default="", help="Codex provider profile for --prompt")
    start_fg.add_argument("--codex-bin", default="codex")
    start_fg.set_defaults(func=command_start_fg)

    # worker — internal, used by start_background
    worker = sub.add_parser("worker")
    worker.add_argument("task")
    worker.add_argument("--codex-bin", default="codex")
    worker.set_defaults(func=command_worker)

    status = sub.add_parser("status", help="Check task status (includes recent log output)")
    status.add_argument("task")
    status.set_defaults(func=command_status)

    result = sub.add_parser("result", help="Print task report")
    result.add_argument("task")
    result.set_defaults(func=command_result)

    list_parser = sub.add_parser("list", help="List all tasks in the project")
    list_parser.add_argument("--project", default=None, help="project directory (default: --cwd)")
    list_parser.set_defaults(func=command_list)

    cancel = sub.add_parser("cancel", help="Cancel a running task")
    cancel.add_argument("task")
    cancel.set_defaults(func=command_cancel)

    resume = sub.add_parser("resume", help="Create a follow-up task (--start to run it)")
    resume.add_argument("task")
    resume.add_argument("--goal", required=True)
    resume.add_argument("--start", action="store_true", help="start the follow-up immediately (default: background)")
    resume.add_argument("--foreground", action="store_true", help="with --start, run in foreground instead of background")
    resume.add_argument("--codex-bin", default="codex")
    resume.set_defaults(func=command_resume)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
