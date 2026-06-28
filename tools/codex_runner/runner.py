from __future__ import annotations

import json
import os
import re
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
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip()
    return metadata


def extract_report_path(text: str) -> str:
    match = re.search(r"Write report to:\s*\n\s*```text\s*\n([^`]+?)\n```", text, re.S)
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
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_state_by_task(task_path: str | Path) -> tuple[dict[str, str], dict[str, Any]]:
    task = parse_task_file(task_path)
    state_path = state_path_for(task)
    if not state_path.exists():
        raise FileNotFoundError(f"Run state not found: {state_path}")
    return task, json.loads(state_path.read_text(encoding="utf-8"))
