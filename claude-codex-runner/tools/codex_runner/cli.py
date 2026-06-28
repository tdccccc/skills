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
    parse_task_file,
    refresh_status,
    render_result,
    resolve_task_reference,
    run_codex_foreground,
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


def command_resume(args: argparse.Namespace) -> int:
    task_path = resolve_task_reference(args.task, cwd=args.cwd)
    followup = create_audited_resume_task(task_path, goal=args.goal, start=False)
    print(json.dumps(followup, indent=2, sort_keys=True))
    if args.start:
        if args.background:
            return start_background(Path(followup["task_path"]), args.codex_bin)
        return run_codex_foreground(followup["task_path"], codex_bin=args.codex_bin)
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

    resume = sub.add_parser("resume")
    resume.add_argument("task")
    resume.add_argument("--goal", required=True)
    resume.add_argument("--start", action="store_true")
    resume.add_argument("--background", action="store_true")
    resume.add_argument("--codex-bin", default="codex")
    resume.set_defaults(func=command_resume)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
