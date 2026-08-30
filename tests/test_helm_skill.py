import re
import unittest
from pathlib import Path


class HelmSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.skill_dir = cls.repo_root / "helm"
        cls.skill = (cls.skill_dir / "SKILL.md").read_text(encoding="utf-8")
        cls.reference = (cls.skill_dir / "REFERENCE.md").read_text(encoding="utf-8")
        cls.readme = (cls.skill_dir / "README.md").read_text(encoding="utf-8")
        cls.goal_template = (cls.skill_dir / "templates" / "goal.md").read_text(
            encoding="utf-8"
        )
        cls.phase_template = (
            cls.skill_dir / "templates" / "phase.md"
        ).read_text(encoding="utf-8")
        cls.intake_template = (
            cls.skill_dir / "templates" / "intake-prompt.md"
        ).read_text(encoding="utf-8")

    def test_phase_ids_are_monotonic_integers(self):
        for phrase in (
            "Phase numbers are permanent and monotonic",
            "never reuse a number or add letter suffixes",
            "next unused integer",
        ):
            self.assertIn(phrase, self.skill)
        self.assertIn("Integer IDs are permanent and never reused", self.goal_template)
        self.assertIn("replacements take the next unused number", self.phase_template)
        for text in (self.skill, self.reference, self.goal_template, self.phase_template):
            self.assertNotRegex(text, r"01-b|P1b")

    def test_completed_work_is_revisited_with_new_phase_ids(self):
        for phrase in (
            "### Revisit completed work",
            "create a new phase under the next unused integer",
            "Keep the old phase `done`",
            "Change the old phase to `superseded`",
            "Re-evaluate every later phase",
            "If the evidence changes Intent or Success criteria, classify L3",
        ):
            self.assertIn(phrase, self.skill)
        for phrase in (
            "## Revisit completed work",
            "Preserve the completed phase file and ID",
            "Trace dependency impact through later phases",
            "docs(helm): revisit PN via PM",
        ):
            self.assertIn(phrase, self.reference)
        self.assertIn("P1–P5 已完成后发现 P3 需要修正", self.readme)
        self.assertIn("创建 P6", self.readme)

    def test_initiative_id_collision_keeps_human_readable_date(self):
        for phrase in (
            "do not add hours or minutes by default",
            "prefer a more specific semantic slug",
            "append `-02`, `-03`",
            "Never use a timestamp suffix merely to bypass Resume",
        ):
            self.assertIn(phrase, self.skill)
        self.assertIn("不会把小时分钟塞进目录名", self.readme)
        self.assertIn("最后才使用 `-02`、`-03`", self.readme)

    def test_artifacts_use_precise_timestamps_and_revisions(self):
        for template in (self.goal_template, self.phase_template):
            self.assertIn("created: {YYYY-MM-DDTHH:MM:SS±HH:MM}", template)
            self.assertIn("updated: {YYYY-MM-DDTHH:MM:SS±HH:MM}", template)
            self.assertIn("revision: 1", template)
            self.assertNotIn("updated: {YYYY-MM-DD}\n", template)
        for phrase in (
            "timezone-aware ISO 8601 timestamps",
            "Start at `revision: 1`",
            "increment that artifact's revision once",
            "re-read owner, status, revision",
        ):
            self.assertIn(phrase, self.skill)
        self.assertIn("## Metadata updates", self.reference)
        self.assertIn("Increment that file's integer `revision` once", self.reference)

    def test_initiative_has_one_owner_and_one_active_phase(self):
        self.assertIn(
            "An initiative has one owner and at most one active phase",
            self.skill,
        )
        self.assertIn("Do not advance different phases in parallel", self.skill)
        self.assertIn("split it into separate initiatives", self.skill)
        self.assertNotIn("Different phases may run in parallel", self.skill)
        self.assertIn("A handoff transfers the whole initiative", self.reference)

    def test_checkpoint_commits_are_default_but_can_be_disabled(self):
        checkpoint = re.search(
            r"\*\*Git sync — commit points:\*\*(?P<body>[\s\S]*?)(?=\n\*\*Surface)",
            self.skill,
        )
        self.assertIsNotNone(checkpoint)
        body = checkpoint.group("body")
        for phrase in (
            "commits are the default",
            "approval for these scoped checkpoint commits",
            "Respect an explicit preference to skip commits",
            "checkpoint remains uncommitted",
        ):
            self.assertIn(phrase, body)
        self.assertIn("默认把被接受的代码块和阶段转换分别提交", self.readme)

    def test_nested_transitions_commit_once_at_outer_boundary(self):
        for phrase in (
            "skip its commit",
            "outermost transition commits the complete state change once",
            "apply **Start** state changes without its standalone commit",
            "Commit once after the complete state change",
        ):
            self.assertIn(phrase, self.reference)

    def test_architecture_map_is_not_part_of_helm(self):
        for path, text in (
            ("SKILL.md", self.skill),
            ("REFERENCE.md", self.reference),
            ("README.md", self.readme),
            ("templates/intake-prompt.md", self.intake_template),
        ):
            self.assertNotIn("architecture-map", text, path)

    def test_each_chunk_has_its_own_test_strategy(self):
        self.assertIn("For every chunk", self.skill)
        self.assertIn("## Chunks", self.phase_template)
        chunk_headings = re.findall(r"^### Chunk \d+", self.phase_template, re.MULTILINE)
        self.assertGreaterEqual(len(chunk_headings), 2)
        for chunk in re.split(r"^### Chunk \d+[^\n]*$", self.phase_template, flags=re.MULTILINE)[1:]:
            for phrase in (
                "change kind:",
                "strategy:",
                "Red / baseline signal:",
                "Green check:",
                "regression checks:",
                "exception:",
            ):
                self.assertIn(phrase, chunk)


if __name__ == "__main__":
    unittest.main()
