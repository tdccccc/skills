#!/usr/bin/env python3
"""Check the final artifact state of a Helm behavior-eval run.

Usage: python3 check_state.py <case-dir> <run-repo>

<case-dir> holds case.json and the pristine seed under repo/. <run-repo> is the
disposable copy the agent worked in. Only `state_checks` are verified here;
`hard_failures` still need a reviewer reading the transcript.
"""

import json
import re
import sys
from pathlib import Path

GOAL_STATUS = re.compile(r"^status:\s*(\S+)\s*$", re.MULTILINE)
PHASE_LINE = re.compile(r"^\s*\d+\.\s+P(\d+)\b.*\bstatus:\s*(\w+)\s*$", re.MULTILINE)
JOURNAL_ENTRY = re.compile(r"^## ", re.MULTILINE)

KNOWN_CHECKS = {
    "initiative_count",
    "goal_status_in",
    "phase_status_in",
    "active_phases",
    "journal_entries_min",
    "paths_exist",
    "paths_absent",
    "unchanged",
    "changed",
}


def goal_state(goal_text):
    """Return (goal status, {"P1": status, ...}) parsed from goal.md text."""
    status = GOAL_STATUS.search(goal_text)
    phases = {f"P{number}": state for number, state in PHASE_LINE.findall(goal_text)}
    return (status.group(1) if status else None), phases


def read_bytes(path):
    return path.read_bytes() if path.is_file() else None


def check(case_dir, run_repo):
    """Return failure messages; an empty list means every state check passed."""
    case_dir, run_repo = Path(case_dir), Path(run_repo)
    case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    checks = case["state_checks"]
    unknown = sorted(set(checks) - KNOWN_CHECKS)
    if unknown:
        return [f"unknown state check: {name}" for name in unknown]

    seed = case_dir / "repo"
    failures = []

    if "initiative_count" in checks:
        found = len(list(run_repo.glob("docs/helm/*/goal.md")))
        if found != checks["initiative_count"]:
            failures.append(f"initiatives: expected {checks['initiative_count']}, found {found}")

    if {"goal_status_in", "phase_status_in", "active_phases"} & set(checks):
        goal_path = run_repo / case["initiative"] / "goal.md"
        if not goal_path.is_file():
            failures.append(f"missing {case['initiative']}/goal.md")
        else:
            status, phases = goal_state(goal_path.read_text(encoding="utf-8"))
            allowed = checks.get("goal_status_in")
            if allowed is not None and status not in allowed:
                failures.append(f"goal status: expected one of {allowed}, found {status}")
            for phase, allowed in checks.get("phase_status_in", {}).items():
                if phases.get(phase) not in allowed:
                    failures.append(f"{phase} status: expected one of {allowed}, found {phases.get(phase)}")
            if "active_phases" in checks:
                active = sorted(phase for phase, state in phases.items() if state == "active")
                if len(active) != checks["active_phases"]:
                    failures.append(f"active phases: expected {checks['active_phases']}, found {active}")

    if "journal_entries_min" in checks:
        journal = run_repo / case["initiative"] / "journal.md"
        entries = len(JOURNAL_ENTRY.findall(journal.read_text(encoding="utf-8"))) if journal.is_file() else 0
        if entries < checks["journal_entries_min"]:
            failures.append(f"journal entries: expected at least {checks['journal_entries_min']}, found {entries}")

    for pattern in checks.get("paths_exist", []):
        if not any(run_repo.glob(pattern)):
            failures.append(f"expected a path matching {pattern}")
    for pattern in checks.get("paths_absent", []):
        matches = sorted(str(path.relative_to(run_repo)) for path in run_repo.glob(pattern))
        if matches:
            failures.append(f"unexpected paths matching {pattern}: {matches}")
    for relative in checks.get("unchanged", []):
        if read_bytes(run_repo / relative) != read_bytes(seed / relative):
            failures.append(f"{relative} changed but must stay as seeded")
    for relative in checks.get("changed", []):
        current = read_bytes(run_repo / relative)
        if current is None or current == read_bytes(seed / relative):
            failures.append(f"{relative} was expected to change")

    return failures


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    failures = check(argv[1], argv[2])
    for failure in failures:
        print(f"FAIL {failure}")
    if not failures:
        print("PASS all state checks")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
