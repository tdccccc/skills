import re
import unittest
from pathlib import Path


class CodeChangeDisciplineSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.skill_dir = cls.repo_root / "code-change-discipline"
        cls.skill = (cls.skill_dir / "SKILL.md").read_text(encoding="utf-8")
        cls.readme = (cls.skill_dir / "README.md").read_text(encoding="utf-8")
        cls.root_readme = (cls.repo_root / "README.md").read_text(encoding="utf-8")
        cls.helm_skill = (cls.repo_root / "helm" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        cls.phase_template = (
            cls.repo_root / "helm" / "templates" / "phase.md"
        ).read_text(encoding="utf-8")
        cls.helm_readme = (cls.repo_root / "helm" / "README.md").read_text(
            encoding="utf-8"
        )

    def assert_order(self, text, *phrases):
        positions = [text.index(phrase) for phrase in phrases]
        self.assertEqual(positions, sorted(positions), phrases)

    def section(self, text, heading):
        match = re.search(
            rf"^{re.escape(heading)}\n(?P<body>[\s\S]*?)(?=^##?\s|\Z)",
            text,
            flags=re.MULTILINE,
        )
        self.assertIsNotNone(match, heading)
        return match.group("body")

    def test_frontmatter_triggers_for_even_small_executable_changes(self):
        self.assertRegex(
            self.skill,
            r"\A---\nname: code-change-discipline\n(?:.*\n)*?install-targets: claude\n---\n",
        )
        frontmatter = self.skill.split("---", 2)[1]
        for phrase in (
            "source code",
            "tests",
            "executable configuration",
            "one-line and few-line fixes",
        ):
            self.assertIn(phrase, frontmatter)

    def test_behavior_changes_and_bug_fixes_are_strict_red_green(self):
        section = self.section(self.skill, "### Behavior changes and bug fixes")
        self.assert_order(
            section,
            "Write or adjust the smallest behavior test",
            "Run it before changing production logic",
            "Confirm an expected Red",
            "Write the minimum production change",
            "Run the same test and observe Green",
            "Refactor only while the tests stay Green",
            "Run relevant regression checks",
        )

    def test_invalid_red_cannot_be_used_as_tdd_evidence(self):
        section = self.section(self.skill, "### What counts as Red")
        for phrase in (
            "syntax or collection error",
            "broken fixture",
            "environment failure",
            "unrelated pre-existing failure",
            "expected compiler or type-checker failure",
            "Do not bypass the type system merely to turn",
            "already passes",
            "Do not damage a test to manufacture Red",
        ):
            self.assertIn(phrase, section)

    def test_refactors_and_optimizations_do_not_manufacture_red(self):
        refactor = self.section(self.skill, "### Behavior-preserving refactors")
        optimization = self.section(self.skill, "### Optimizations")
        self.assertIn("Green characterization or contract baseline", refactor)
        self.assertIn("Do not manufacture a Red", refactor)
        self.assertIn("correctness checks", optimization)
        self.assertIn("repeatable performance baseline", optimization)
        self.assertIn("Do not manufacture a functional Red", optimization)

    def test_exceptions_and_final_evidence_are_explicit(self):
        exceptions = self.section(self.skill, "## Exceptions")
        finish = self.section(self.skill, "## Finish with evidence")
        for phrase in (
            "test seam",
            "exploratory spike",
            "emergency repair",
            "reason",
            "compensating verification",
            "follow-up regression test",
            "Never claim an unobserved Red",
        ):
            self.assertIn(phrase, exceptions)
        for phrase in (
            "relevant regression checks",
            "diff and working-tree status",
            "observed results",
            "checks not run",
        ):
            self.assertIn(phrase, finish)

    def test_commit_ownership_stays_with_the_caller(self):
        section = self.section(self.skill, "## Workflow ownership")
        self.assertIn("does not authorize a commit", section)
        self.assertIn("upper-level workflow", section)
        self.assertIn("explicit user request", section)

    def test_helm_integrates_strategy_at_all_four_gates(self):
        plan = self.section(self.helm_skill, "### 2. Plan — write only the current phase")
        execute = self.section(self.helm_skill, "### 3. Execute")
        checkpoint = self.section(self.helm_skill, "### 4. Checkpoint")
        delegation = self.section(self.helm_skill, "## Delegation (subagents)")

        for phrase in (
            "change kind",
            "test strategy",
            "expected Red or Green baseline",
            "Green and regression checks",
            "horizontal testing task at the end",
        ):
            self.assertIn(phrase, plan)

        self.assertIn("`code-change-discipline`", execute)
        self.assert_order(
            execute,
            "expected Red",
            "minimum production change",
            "Green",
            "refactor",
            "regression",
            "Checkpoint",
        )

        for phrase in (
            "Red and Green evidence",
            "before-and-after Green evidence",
            "correctness and baseline/result evidence",
            "checks not run",
        ):
            self.assertIn(phrase, checkpoint)

        for phrase in (
            "test strategy",
            "target test",
            "expected Red or Green baseline",
            "observed Red, Green, and regression results",
            "checks not run",
        ):
            self.assertIn(phrase, delegation)

    def test_red_is_not_accepted_reported_checked_off_or_committed(self):
        execute = self.section(self.helm_skill, "### 3. Execute")
        self.assertIn(
            "An expected Red is unaccepted work: do not accept it, invoke "
            "`technical-report`, check off its task, or commit it.",
            execute,
        )
        self.assertRegex(
            self.helm_skill,
            r"accepted[\s\S]*?technical-report[\s\S]*?commit[\s\S]*?check (?:it )?off",
        )

    def test_phase_template_records_strategy_without_parallel_status(self):
        self.assert_order(
            self.phase_template,
            "## Outcome",
            "## Test strategy",
            "## Tasks",
            "## Verification",
        )
        for phrase in (
            "change kind",
            "strategy",
            "Red / baseline signal",
            "Green / regression checks",
            "exception",
        ):
            self.assertIn(phrase, self.phase_template)
        for forbidden in ("status:", "tdd-status", "test-status", "report-status"):
            self.assertNotIn(forbidden, self.phase_template)

    def test_helm_zcode_install_includes_both_independent_skills(self):
        self.assertIn(
            "skills/code-change-discipline ~/.agents/skills/code-change-discipline",
            self.helm_readme,
        )
        self.assertIn(
            "skills/technical-report ~/.agents/skills/technical-report",
            self.helm_readme,
        )

    def test_user_readme_is_short_and_user_focused(self):
        self.assertLessEqual(len(self.readme.splitlines()), 60)
        for phrase in (
            "一行小修",
            "## 它会做什么",
            "先写测试",
            "不会硬造失败测试",
            "## 怎么用",
            "## 与 Helm 的关系",
            "实际验证结果",
        ):
            self.assertIn(phrase, self.readme)
        for developer_detail in (
            "### 有效 Red",
            "test seam",
            "fixture",
            "type-checker",
        ):
            self.assertNotIn(developer_detail, self.readme)

    def test_root_readme_is_a_concise_user_entrypoint(self):
        self.assertLessEqual(len(self.root_readme.splitlines()), 100)
        self.assertIn(
            "[code-change-discipline](code-change-discipline/README.md)",
            self.root_readme,
        )
        for phrase in ("## 安装", "## 有哪些 skills", "## 怎么用", "## 更新与卸载"):
            self.assertIn(phrase, self.root_readme)
        for developer_detail in ("## Layout", "## Conventions", "Task records generated"):
            self.assertNotIn(developer_detail, self.root_readme)

    def test_helm_readme_is_a_concise_user_guide(self):
        self.assertLessEqual(len(self.helm_readme.splitlines()), 130)
        for phrase in (
            "多步骤",
            "## 怎么用",
            "## 它会怎么做",
            "## 会生成什么",
            "## 中途改方向",
            "不需要启用 Helm",
            "仍然遵守 `code-change-discipline`",
            "功能和 Bug",
            "纯重构和优化",
        ):
            self.assertIn(phrase, self.helm_readme)
        for developer_detail in (
            "execution report 返回",
            "report-status",
            "intake recon",
        ):
            self.assertNotIn(developer_detail, self.helm_readme)


if __name__ == "__main__":
    unittest.main()
