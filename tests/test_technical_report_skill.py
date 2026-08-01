import re
import unittest
from pathlib import Path


class TechnicalReportSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.skill_dir = cls.repo_root / "technical-report"
        cls.skill = (cls.skill_dir / "SKILL.md").read_text(encoding="utf-8")
        cls.reference = (cls.skill_dir / "REFERENCE.md").read_text(encoding="utf-8")
        cls.template = (
            cls.skill_dir / "templates" / "technical-report.md"
        ).read_text(encoding="utf-8")
        cls.helm_skill = (cls.repo_root / "helm" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        cls.helm_readme = (cls.repo_root / "helm" / "README.md").read_text(
            encoding="utf-8"
        )
        cls.intake_prompt = (
            cls.repo_root / "helm" / "templates" / "intake-prompt.md"
        ).read_text(encoding="utf-8")

    def test_frontmatter_and_supporting_files(self):
        self.assertRegex(
            self.skill,
            r"\A---\nname: technical-report\n(?:.*\n)*?install-targets: claude\n---\n",
        )
        self.assertIn("`REFERENCE.md`", self.skill)
        self.assertIn("`templates/technical-report.md`", self.skill)
        self.assertTrue((self.skill_dir / "REFERENCE.md").is_file())
        self.assertTrue(
            (self.skill_dir / "templates" / "technical-report.md").is_file()
        )

    def test_modes_and_result_contract_are_explicit(self):
        for mode in ("`init`", "`update`", "`audit`"):
            self.assertIn(mode, self.skill)
        for status in ("`updated`", "`no-impact`", "`blocked`"):
            self.assertIn(status, self.skill)

        self.assertIn("status: updated | no-impact | blocked", self.skill)
        self.assertIn("scope: <verified implementation/report scope>", self.skill)
        self.assertRegex(
            self.skill,
            r"first Helm synchronization[\s\S]*?→ `init`[\s\S]*?"
            r"explicit `update` or `audit`[\s\S]*?→ `blocked`",
        )
        self.assertIn("it never claims that unexamined sections were audited", self.skill)
        self.assertIn("For `update` + `no-impact`", self.skill)
        self.assertIn("Never state or imply that the report is accurate as a whole", self.skill)
        self.assertIn("A `blocked` run must not leave", self.skill)

    def test_current_implementation_and_evidence_contract(self):
        combined = self.skill + self.reference
        required_phrases = (
            "verified current implementation",
            "production source code and executable configuration",
            "Documentation as navigation, not proof",
            "A diff alone is not sufficient evidence",
            "replace or remove stale statements in place",
            "The final text describes this resulting system",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, combined)

    def test_change_process_prompt_and_rationale_are_excluded(self):
        combined = self.skill + self.reference
        required_boundaries = (
            "the transition from an old implementation to a new one",
            "why a change was requested",
            "the user's prompt",
            "Helm goals, phases, checkpoints",
            "attempted, rejected, superseded, or reverted approaches",
            "changelogs, decision history, roadmaps, TODOs",
        )
        for boundary in required_boundaries:
            self.assertIn(boundary, combined)

    def test_template_contains_only_current_state_sections(self):
        headings = re.findall(r"^## (.+)$", self.template, flags=re.MULTILINE)
        expected = [
            "Scope and System Overview",
            "Runtime and Technology Stack",
            "Frameworks and Responsibilities",
            "Architecture and Module Boundaries",
            "Entry Points, Interfaces, and Runtime Flows",
            "Data and State",
            "Key Implementation Mechanisms",
            "External Integrations and Executable Configuration",
            "Build, Test, Deployment, and Operations",
            "Security and Failure Behavior",
        ]
        self.assertEqual(headings, expected)

        forbidden_patterns = (
            r"\bchanges?\b",
            r"\bhistory\b",
            r"\brationale\b",
            r"\bdecisions?\b",
            r"\bprompts?\b",
            r"\bplans?\b",
            r"\broadmap\b",
            r"\blogs?\b",
            r"\btodos?\b",
            r"\bfollow-ups?\b",
        )
        for heading in headings:
            normalized = heading.casefold()
            self.assertFalse(
                any(re.search(pattern, normalized) for pattern in forbidden_patterns),
                msg=f"process/history heading in report template: {heading}",
            )

    def test_helm_uses_specialized_handoff_after_acceptance(self):
        required_phrases = (
            "After accepting each meaningful implementation chunk",
            "invoke the independent **`technical-report`** skill",
            "If maintenance was explicitly enabled but no report exists yet",
            "invoke its `init` mode for the first handoff",
            "Helm must not pre-filter",
            "edit the technical report directly",
            "`updated`",
            "`no-impact`",
            "`blocked`",
            "a missing handoff and `blocked` both prevent Close",
            "do not trigger a duplicate whole-report sweep",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, self.helm_skill)

    def test_helm_intake_reads_report_selectively(self):
        self.assertIn("Do not load a long report in full by default", self.helm_skill)
        self.assertIn("read only the overview and sections relevant", self.intake_prompt)
        self.assertIn("Do not read the whole report by default", self.intake_prompt)
        self.assertIn("judge its update impact, or", self.intake_prompt)

    def test_helm_zcode_install_includes_specialized_skill(self):
        self.assertIn("skills/helm ~/.agents/skills/helm", self.helm_readme)
        self.assertIn(
            "skills/technical-report ~/.agents/skills/technical-report",
            self.helm_readme,
        )


if __name__ == "__main__":
    unittest.main()
