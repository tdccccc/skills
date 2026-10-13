import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = REPO_ROOT / "tests" / "evals" / "helm"


def read(path):
    return path.read_text(encoding="utf-8")


def section(text, heading):
    """Return the body under `heading` up to the next heading of the same or higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    match = re.search(
        rf"^{re.escape(heading)}[^\n]*\n(?P<body>[\s\S]*?)(?=^#{{1,{level}}} |\Z)",
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group("body")


def load_grader():
    spec = importlib.util.spec_from_file_location(
        "helm_check_state", EVAL_DIR / "check_state.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HelmSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        skill_dir = REPO_ROOT / "helm"
        templates = skill_dir / "templates"
        cls.skill = read(skill_dir / "SKILL.md")
        cls.reference = read(skill_dir / "REFERENCE.md")
        cls.readme = read(skill_dir / "README.md")
        cls.goal_template = read(templates / "goal.md")
        cls.phase_template = read(templates / "phase.md")
        cls.journal_template = read(templates / "journal-entry.md")
        cls.intake_template = read(templates / "intake-prompt.md")
        cls.skill_names = {
            re.search(r"^name: (\S+)$", read(path), re.MULTILINE).group(1)
            for path in REPO_ROOT.glob("*/SKILL.md")
        }

    def test_description_targets_long_or_uncertain_work(self):
        description = self.skill.split("---", 2)[1]
        for phrase in (
            "span sessions",
            "uncertain",
            "Skip well-scoped work that fits one session",
        ):
            self.assertIn(phrase, description)

    def test_instructions_stay_lean(self):
        self.assertLessEqual(len(self.skill.split()), 2300)
        self.assertLessEqual(len(self.skill.split()) + len(self.reference.split()), 3700)

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
        artifacts = section(self.skill, "## Artifacts")
        for phrase in (
            "timezone-aware ISO 8601",
            "`revision: 1`",
            "increment `revision` once",
            "re-read status, owner, and revision",
        ):
            self.assertIn(phrase, artifacts)

    def test_status_invariants_tie_active_phase_to_active_goal(self):
        status = section(self.skill, "## Status")
        for phrase in (
            "carry no status field",
            "at most one `active` phase",
            "only while the goal is `active`",
        ):
            self.assertIn(phrase, status)

    def test_initiative_has_one_owner_and_one_active_phase(self):
        status = section(self.skill, "## Status")
        for phrase in (
            "One owner per initiative",
            "Do not advance different phases in parallel",
            "split it into separate initiatives",
        ):
            self.assertIn(phrase, status)
        self.assertIn("A handoff transfers the whole initiative", self.reference)
        resume = section(self.skill, "## Resume first")
        self.assertIn("unless another agent appears to be working on it right now", resume)

    def test_plan_only_requests_still_allow_helm_artifact_edits(self):
        execute = section(self.skill, "### 3. Execute")
        self.assertIn("Helm artifact edits stay in scope", execute)

    def test_starting_a_phase_reopens_a_closed_goal(self):
        start = section(self.reference, "### Start phase")
        self.assertRegex(start, r"`done` → `active`")
        self.assertRegex(start, r"`proposed` → `active`[^\n]*confirmed")
        self.assertRegex(start, r"`abandoned` → `active`[^\n]*confirm")
        revisit = section(self.reference, "## Revisit completed work")
        self.assertIn("Start `PM`", revisit)
        self.assertIn("reopens", revisit)
        self.assertIn("named initiative", section(self.skill, "## Resume first"))

    def test_l3_waits_when_the_revised_goal_needs_confirmation(self):
        steer = section(self.skill, "## Steer")
        l3 = section(self.reference, "### L3")
        for text in (steer, l3):
            self.assertRegex(text, r"`(?:status: )?proposed`")
            self.assertIn("no phase `active`", text)
            self.assertIn("stop until", text)
        self.assertNotRegex(l3, r"(?m)^\d+\. Resume execution\.$")

    def test_phase_completion_requires_phase_verification(self):
        complete = section(self.reference, "### Complete phase")
        self.assertIn("**Phase verification**", complete)
        self.assertIn("leave PN `active`", complete)
        self.assertIn("Phase verification", section(self.skill, "### 5. Complete"))
        self.assertIn("required before the phase is done", self.phase_template)

    def test_commits_require_recorded_authorization(self):
        frame = section(self.skill, "### 1. Frame")
        checkpoint = section(self.skill, "### 4. Checkpoint")
        self.assertIn("Commits:", self.goal_template)
        self.assertIn("default to `Commits: none`", frame)
        for phrase in (
            "only when goal.md Constraints authorize them",
            "isolated change",
            "remain uncommitted",
        ):
            self.assertIn(phrase, checkpoint)
        self.assertNotIn("approval for these scoped checkpoint commits", self.skill)
        self.assertIn("授权", self.readme)
        self.assertNotIn("默认把被接受的代码块和阶段转换分别提交", self.readme)

    def test_each_operation_is_one_logical_edit(self):
        preamble = self.reference.split("## Phase transitions", 1)[0]
        self.assertIn("one logical edit", preamble)
        self.assertIn("commit the touched artifacts once", preamble)
        for heading in (
            "### Start phase",
            "### Complete phase",
            "### Block phase",
            "### Supersede phase",
            "### L1",
            "### L2",
            "### L3",
            "## Revisit completed work",
            "## Handoff",
            "## Delegation contract",
        ):
            section(self.reference, heading)

    def test_design_interview_is_optional(self):
        frame = section(self.skill, "### 1. Frame")
        self.assertIn("ask focused questions directly", frame)
        self.assertIn("`grill-with-docs`", frame)
        self.assertNotIn("run `grill-with-docs` first", self.skill)

    def test_referenced_skills_exist(self):
        grill_with_docs = read(REPO_ROOT / "grill-with-docs" / "SKILL.md")
        references = set(re.findall(r"`([a-z]+(?:-[a-z]+)+)`", self.skill))
        references |= set(re.findall(r"`/([a-z]+(?:-[a-z]+)*)`", grill_with_docs))
        self.assertIn("code-change-discipline", references)
        self.assertLessEqual(references, self.skill_names)

    def test_completed_work_is_revisited_with_new_phase_ids(self):
        steer = section(self.skill, "## Steer")
        for phrase in (
            "Revisit completed work",
            "next unused integer",
            "Keep the old phase `done`",
            "`superseded`",
            "If the evidence changes Intent or Success criteria, it is L3",
        ):
            self.assertIn(phrase, steer)
        revisit = section(self.reference, "## Revisit completed work")
        for phrase in (
            "Preserve the completed phase file and ID",
            "Trace dependency impact through later phases",
            "docs(helm): revisit PN via PM",
        ):
            self.assertIn(phrase, revisit)
        self.assertIn("P1–P5 已完成后发现 P3 需要修正", self.readme)
        self.assertIn("创建 P6", self.readme)

    def test_phase_template_chunks_carry_lean_verification(self):
        chunks = re.split(r"^### Chunk \d+[^\n]*$", self.phase_template, flags=re.MULTILINE)[1:]
        self.assertGreaterEqual(len(chunks), 2)
        for chunk in chunks:
            for field in (
                "- change:",
                "- kind:",
                "- first signal:",
                "- checks:",
                "- [ ] accepted on observed evidence",
            ):
                self.assertIn(field, chunk)
        for retired in ("strategy:", "Red / baseline signal:", "Green check:", "regression checks:"):
            self.assertNotIn(retired, self.phase_template)

    def test_journal_entry_types_cover_lifecycle_events(self):
        for kind in ("L2 reshape", "L3 steer", "revisit", "handoff", "waiver"):
            self.assertIn(kind, self.journal_template)

    def test_architecture_map_is_not_part_of_helm(self):
        for path, text in (
            ("SKILL.md", self.skill),
            ("REFERENCE.md", self.reference),
            ("README.md", self.readme),
            ("templates/intake-prompt.md", self.intake_template),
        ):
            self.assertNotIn("architecture-map", text, path)


class HelmBehaviorEvalTests(unittest.TestCase):
    CASES = (
        "reopen-done-initiative",
        "l3-needs-confirmation",
        "phase-verification-gate",
        "small-task-skips-helm",
    )

    @classmethod
    def setUpClass(cls):
        cls.grader = load_grader()

    def copy_seed(self, case):
        workdir = Path(tempfile.mkdtemp(prefix=f"helm-eval-{case}-"))
        self.addCleanup(shutil.rmtree, workdir, ignore_errors=True)
        run_repo = workdir / "repo"
        shutil.copytree(EVAL_DIR / case / "repo", run_repo)
        return run_repo

    def test_cases_are_complete(self):
        self.assertTrue((EVAL_DIR / "README.md").is_file())
        for case in self.CASES:
            with self.subTest(case=case):
                case_dir = EVAL_DIR / case
                self.assertTrue(read(case_dir / "prompt.md").strip())
                contract = json.loads(read(case_dir / "case.json"))
                self.assertLessEqual(set(contract["state_checks"]), self.grader.KNOWN_CHECKS)
                self.assertTrue(contract["hard_failures"])
                self.assertTrue((case_dir / "repo").is_dir())

    def test_seed_initiatives_respect_status_invariants(self):
        goals = sorted(EVAL_DIR.glob("*/repo/docs/helm/*/goal.md"))
        self.assertTrue(goals)
        for goal in goals:
            with self.subTest(goal=str(goal.relative_to(EVAL_DIR))):
                status, phases = self.grader.goal_state(read(goal))
                self.assertIn(status, {"proposed", "active", "done", "abandoned"})
                active = [phase for phase, state in phases.items() if state == "active"]
                self.assertLessEqual(len(active), 1)
                if status != "active":
                    self.assertEqual(active, [])
                for phase, state in phases.items():
                    if state in {"active", "done"}:
                        number = int(phase[1:])
                        self.assertTrue(any((goal.parent / "phases").glob(f"{number:02d}-*.md")), phase)

    def test_untouched_seed_fails_every_case(self):
        for case in self.CASES:
            with self.subTest(case=case):
                self.assertTrue(self.grader.check(EVAL_DIR / case, self.copy_seed(case)))

    def test_reference_outcomes_pass_every_case(self):
        for case in self.CASES:
            with self.subTest(case=case):
                run_repo = self.copy_seed(case)
                getattr(self, "solve_" + case.replace("-", "_"))(run_repo)
                self.assertEqual(self.grader.check(EVAL_DIR / case, run_repo), [])

    def test_cli_exit_code_reports_failures(self):
        case = "small-task-skips-helm"
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                str(EVAL_DIR / "check_state.py"),
                str(EVAL_DIR / case),
                str(self.copy_seed(case)),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("FAIL greet.py was expected to change", result.stdout)

    # Scripted reference outcomes: the smallest edits a correct run would make.

    def replace(self, path, old, new):
        text = read(path)
        self.assertIn(old, text, path)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def append(self, path, text):
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)

    def solve_reopen_done_initiative(self, repo):
        initiative = repo / "docs" / "helm" / "2026-09-20-csv-export"
        self.replace(initiative / "goal.md", "status: done", "status: active")
        self.append(
            initiative / "goal.md",
            "3. P3 — Fields containing commas or quotes stay in one CSV column — status: active\n",
        )
        (initiative / "phases" / "03-csv-quoting.md").write_text(
            "# P3 — csv-quoting\n", encoding="utf-8"
        )
        self.append(initiative / "journal.md", "\n## 2026-10-13 — revisit — P2 export misses CSV quoting\n")

    def solve_l3_needs_confirmation(self, repo):
        initiative = repo / "docs" / "helm" / "2026-09-25-search-filters"
        self.replace(initiative / "goal.md", "status: active", "status: proposed")
        self.replace(
            initiative / "goal.md",
            "narrowed to one tag — status: active",
            "narrowed to one tag — status: superseded",
        )
        (initiative / "journal.md").write_text(
            "# Journal — search-filters\n\n## 2026-10-13 — L3 steer — date range replaces tag filter\n",
            encoding="utf-8",
        )

    def solve_phase_verification_gate(self, repo):
        self.replace(
            repo / "docs" / "helm" / "2026-10-02-slug-cli" / "phases" / "01-slug-cli.md",
            "## Phase verification",
            "### Chunk 3 — CLI prints the slug\n\n- [ ] accepted on observed evidence\n\n## Phase verification",
        )

    def solve_small_task_skips_helm(self, repo):
        self.replace(repo / "greet.py", "Hello", "Hi")
        self.replace(repo / "test_greet.py", "Hello", "Hi")


if __name__ == "__main__":
    unittest.main()
