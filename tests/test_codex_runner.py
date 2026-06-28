import sys
import tempfile
import unittest
from pathlib import Path

# The runner package is self-contained inside the claude-codex-runner skill.
# Mirror the wrapper's PYTHONPATH injection so tests import it without install.
_PKG_ROOT = Path(__file__).resolve().parents[1] / "claude-codex-runner" / "tools"
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from codex_runner.runner import (
    build_initial_state,
    build_codex_command,
    build_prompt,
    create_audited_resume_task,
    ensure_codex_runs_ignored,
    parse_task_file,
    render_result,
    resolve_task_reference,
    run_dir_for,
    stderr_path_for,
    stdout_path_for,
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
        _root, task_path = CodexRunnerParsingTests().make_project()
        task = parse_task_file(task_path)
        run_dir_for(task).mkdir(parents=True)
        stdout_path_for(task).write_text("stdout summary\n", encoding="utf-8")
        stderr_path_for(task).write_text("stderr detail\n", encoding="utf-8")

        rendered = render_result(task)

        self.assertIn("Report not found", rendered)
        self.assertIn("stdout summary", rendered)
        self.assertIn("stderr detail", rendered)


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
        self.assertEqual(
            followup["report_path"],
            str(root / "docs" / "tasks" / followup["task_id"] / "codex-report.md"),
        )
        text = followup_path.read_text(encoding="utf-8")
        self.assertIn("Previous task", text)
        self.assertIn("2026-06-28-example", text)
        self.assertIn("Run the final verification", text)
        self.assertIn("Add final verification", text)


class CodexRunnerReadOnlyPromptTests(unittest.TestCase):
    def base_task(self, sandbox):
        return {
            "task_path": "/p/docs/tasks/t/task.md",
            "target_project": "/p",
            "report_path": "/p/docs/tasks/t/codex-report.md",
            "sandbox": sandbox,
            "task_id": "t",
        }

    def test_read_only_prompt_requests_stdout_report(self):
        prompt = build_prompt(self.base_task("read-only"))
        self.assertIn("Do not write any files", prompt)
        self.assertIn("Print your full structured report to stdout", prompt)
        self.assertNotIn("Write docs/tasks/t/codex-report.md", prompt)

    def test_workspace_write_prompt_requests_report_file(self):
        prompt = build_prompt(self.base_task("workspace-write"))
        self.assertIn("Write docs/tasks/t/codex-report.md, then exit.", prompt)


class CodexRunnerGitignoreTests(unittest.TestCase):
    def make_git_project(self):
        root = Path(tempfile.mkdtemp(prefix="codex-runner-gi-"))
        (root / ".git").mkdir()
        return root

    def test_creates_gitignore_in_git_repo_when_missing(self):
        root = self.make_git_project()

        changed = ensure_codex_runs_ignored(root)

        self.assertTrue(changed)
        self.assertEqual((root / ".gitignore").read_text(encoding="utf-8"), ".codex-runs/\n")

    def test_appends_entry_preserving_existing_content(self):
        root = self.make_git_project()
        (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")

        changed = ensure_codex_runs_ignored(root)

        self.assertTrue(changed)
        self.assertEqual(
            (root / ".gitignore").read_text(encoding="utf-8"),
            "__pycache__/\n.codex-runs/\n",
        )

    def test_no_op_when_entry_already_present(self):
        root = self.make_git_project()
        (root / ".gitignore").write_text(".codex-runs/\n", encoding="utf-8")

        changed = ensure_codex_runs_ignored(root)

        self.assertFalse(changed)

    def test_skips_when_not_a_git_repo(self):
        root = Path(tempfile.mkdtemp(prefix="codex-runner-nogit-"))

        changed = ensure_codex_runs_ignored(root)

        self.assertFalse(changed)
        self.assertFalse((root / ".gitignore").exists())
