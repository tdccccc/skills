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
