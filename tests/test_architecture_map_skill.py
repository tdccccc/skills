import ast
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ArchitectureMapSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.skill_dir = cls.repo_root / "architecture-map"
        cls.eval_dir = cls.repo_root / "tests" / "evals" / "architecture-map"
        cls.skill = (cls.skill_dir / "SKILL.md").read_text(encoding="utf-8")
        cls.reference = (cls.skill_dir / "REFERENCE.md").read_text(encoding="utf-8")
        cls.template = (
            cls.skill_dir / "templates" / "architecture-map.html"
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
            r"\A---\nname: architecture-map\n(?:.*\n)*?install-targets: claude\n---\n",
        )
        self.assertIn("`REFERENCE.md`", self.skill)
        self.assertIn("`templates/architecture-map.html`", self.skill)
        self.assertTrue((self.skill_dir / "REFERENCE.md").is_file())
        self.assertTrue(
            (self.skill_dir / "templates" / "architecture-map.html").is_file()
        )
        self.assertFalse(
            (self.skill_dir / "templates" / "architecture-map.md").exists()
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

    def test_capability_proof_levels_and_active_wiring_are_explicit(self):
        levels = (
            "**Declared**",
            "**Configurable**",
            "**Selected**",
            "**Invoked**",
            "**Externally active**",
        )
        positions = [self.reference.index(level) for level in levels]
        self.assertEqual(positions, sorted(positions))

        active_loop = (
            "executable entry",
            "registration / composition",
            "selected configuration or provider",
            "concrete caller with actual arguments",
            "concrete callee / host adapter",
            "state, output, or external effect",
        )
        for node in active_loop:
            self.assertIn(node, self.reference)
        self.assertIn("A report claim cannot exceed its proved level", self.reference)
        self.assertIn("does not prove that behavior is active", self.reference)
        self.assertIn("Omit ordinary `Declared` / `Configurable` alternatives", self.reference)
        self.assertIn("Mention one in operation evidence only when", self.skill)

    def test_cross_component_contract_checks_both_ends(self):
        required = (
            "producer/caller and consumer/callee",
            "argument order, flags, defaults",
            "method, path, headers, query, payload",
            "serialization, framing, key shape, and version",
            "exit codes, stdout, and stderr",
            "does not prove the callee accepts",
            "does not prove the caller selects or invokes",
        )
        for phrase in required:
            self.assertIn(phrase, self.reference)

    def test_strong_semantics_require_counter_evidence(self):
        required = (
            "Streaming / incremental processing",
            "Atomic / transactional / race-free / quota",
            "Idempotent / exactly-once / ordered",
            "Timeout / cancellation",
            "Secrets / secure storage / authentication coverage",
            "fallback",
            "bypass",
            "degraded mode",
            "fail-open/fail-closed",
            "buffering/materialization",
            "non-atomic operation",
            "narrow the wording",
            "return `blocked`",
        )
        for phrase in required:
            self.assertIn(phrase, self.reference)

    def test_init_requires_runtime_topology(self):
        init_section = self.skill.split("### `init`", 1)[1].split("### `update`", 1)[0]
        required = (
            "deployable unit",
            "composition root",
            "process / worker / replica",
            "local versus shared state",
            "cross-component communication",
        )
        for phrase in required:
            self.assertIn(phrase, init_section)

        self.assertIn("independent services, extensions, workers", self.reference)
        self.assertIn("process, thread, worker, host, replica", self.reference)
        self.assertIn("process-local, host-local, or shared state", self.reference)
        self.assertIn("environment variable proves configuration intent only", self.reference)
        self.assertIn("startup/composition path reads it", self.reference)

    def test_claim_scope_and_quantifiers_are_calibrated(self):
        required = (
            "instance; request or job; key or tenant; process or worker; host or replica; service; deployment; environment",
            "process-local or per-key lock does not prove cross-worker atomicity",
            "one middleware, route group, adapter, or entry does not prove all requests",
            "a streaming flag does not prove end-to-end incremental delivery",
            "Avoid `all`, `every`, `always`, `never`, `global`",
        )
        for phrase in required:
            self.assertIn(phrase, self.reference)

    def test_report_uses_one_canonical_home_per_mechanism(self):
        required = (
            "one fact, one canonical home",
            "overview diagram: compact system shape only",
            "runtime flows: step-by-step execution",
            "Explain a mechanism in detail once",
        )
        for phrase in required:
            self.assertIn(phrase, self.reference)

        self.assertIn(
            '<script type="application/json" id="report-data">',
            self.template,
        )
        self.assertIn("`report-data` block", self.skill)
        self.assertIn("never modifies template code", self.skill)

    def test_unverified_is_optional_and_not_a_status(self):
        self.assertIn("status: updated | no-impact | blocked", self.skill)
        self.assertIn("optionally add", self.skill)
        self.assertIn("unverified: <material uncertainty", self.skill)
        self.assertIn("Omit this field when empty", self.skill)
        self.assertIn("never emit `unverified: none`", self.skill)
        self.assertIn("must not enter the architecture map report", self.skill)
        self.assertIn("`unverified` is not a fourth status", self.skill)
        self.assertIn("In a full `init` / `audit`", self.skill)
        self.assertIn("requires `blocked`", self.skill)
        self.assertIn("In scoped `update`", self.skill)
        self.assertIn("return `blocked` instead", self.skill)
        self.assertNotIn("status: updated | no-impact | blocked | unverified", self.skill)

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

    def test_template_is_a_data_driven_single_file(self):
        block = re.search(
            r'<script type="application/json" id="report-data">(.*?)</script>',
            self.template,
            flags=re.S,
        )
        self.assertIsNotNone(block, msg="template must carry a report-data block")
        data = json.loads(block.group(1))
        for key in ("title", "summary", "modules", "edges", "sections"):
            self.assertIn(key, data, msg=f"missing top-level key: {key}")

        allowed_fields = {
            "id",
            "label",
            "parent",
            "layer",
            "summary",
            "detail",
            "notes",
            "evidence",
        }
        modules_by_id = {}
        for module in data["modules"]:
            self.assertIn("id", module)
            self.assertTrue(
                set(module) <= allowed_fields,
                msg=f"unknown module field in {module['id']}",
            )
            self.assertIn(
                module["layer"],
                {"entry", "core", "data", "infra", "external", "frontend"},
                msg=f"invalid layer in {module['id']}",
            )
            modules_by_id[module["id"]] = module
        self.assertEqual(
            len(data["modules"]), len(modules_by_id), msg="duplicate module ids"
        )

        parent_ids = {
            module["parent"] for module in data["modules"] if "parent" in module
        }
        self.assertTrue(
            parent_ids <= set(modules_by_id), msg="parent references missing module"
        )

        def depth(mid):
            levels = 0
            while "parent" in modules_by_id[mid]:
                mid = modules_by_id[mid]["parent"]
                levels += 1
            return levels

        self.assertLessEqual(
            max(depth(mid) for mid in modules_by_id),
            2,
            msg="example data exceeds three levels",
        )

        for edge in data["edges"]:
            self.assertIn(edge["from"], modules_by_id, msg="edge from missing module")
            self.assertIn(edge["to"], modules_by_id, msg="edge to missing module")
            self.assertIn(edge.get("kind", "flow"), {"flow", "dep"})

        for section in data["sections"]:
            self.assertIn("title", section)
            for block in section.get("blocks", []):
                self.assertIn(block["type"], {"p", "bullets", "code", "anchors"})

        for element in (
            '<svg id="canvas">',
            'id="panel"',
            'id="breadcrumb"',
            'id="tabs"',
            'id="legend"',
            'id="search"',
        ):
            self.assertIn(element, self.template, msg=f"missing fixed element {element}")
        self.assertNotRegex(
            self.template,
            r'(?:src|href)\s*=\s*["\']https?://',
            msg="template must work offline without external dependencies",
        )

    def test_template_behavior_smoke_suite(self):
        script = self.repo_root / "tests" / "test_architecture_map_template.mjs"
        try:
            result = subprocess.run(
                ["node", str(script)],
                cwd=self.repo_root,
                text=True,
                capture_output=True,
                check=False,
            )
        except FileNotFoundError:
            self.skipTest("node is not available")
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 2 and "SKIP" in output:
            self.skipTest("jsdom is not available")
        self.assertEqual(result.returncode, 0, output)

    def test_behavior_eval_fixtures_preserve_hard_cases(self):
        expected_files = {
            "unwired-helper": {
                "app.py",
                "legacy_transform.py",
                "fast_helper.py",
                "test_fast_helper.py",
                "seed-report.html",
                "prompt.md",
                "case.json",
            },
            "buffered-stream": {
                "main.py",
                "gateway.py",
                "http_adapter.py",
                "seed-report.html",
                "prompt.md",
                "case.json",
            },
            "incompatible-cli-contract": {
                "main.py",
                "api.py",
                "service.py",
                "worker_cli.py",
                "seed-report.html",
                "prompt.md",
                "case.json",
            },
            "per-key-lock-kv-quota": {
                "app.py",
                "quota.py",
                "routes.py",
                "deployment.yaml",
                "prompt.md",
                "case.json",
            },
            "unrelated-tests-change": {
                "app.py",
                "test_app.py",
                "seed-report.html",
                "prompt.md",
                "case.json",
            },
            "insisted-update-no-report": {
                "app.py",
                "prompt.md",
                "case.json",
            },
            "renamed-handler": {
                "app.py",
                "seed-report.html",
                "prompt.md",
                "case.json",
            },
        }

        for case_name, files in expected_files.items():
            case_dir = self.eval_dir / case_name
            self.assertTrue(case_dir.is_dir(), msg=f"missing eval: {case_name}")
            for file_name in files:
                self.assertTrue(
                    (case_dir / file_name).is_file(),
                    msg=f"missing {case_name}/{file_name}",
                )

            prompt = (case_dir / "prompt.md").read_text(encoding="utf-8")
            self.assertIn("disposable fixture copy", prompt)
            self.assertNotIn("Do not edit fixture files", prompt)

            seed = case_dir / "seed-report.html"
            if seed.is_file():
                seed_block = re.search(
                    r'<script type="application/json" id="report-data">(.*?)</script>',
                    seed.read_text(encoding="utf-8"),
                    flags=re.S,
                )
                self.assertIsNotNone(
                    seed_block, msg=f"missing report-data block in {case_name}"
                )
                self.assertIn("modules", json.loads(seed_block.group(1)))

            contract = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
            self.assertIn(contract["mode"], {"init", "update", "audit"})
            self.assertIn(contract["expected_status"], {"updated", "no-impact", "blocked"})
            for field in ("expected_facts", "hard_failures"):
                self.assertTrue(contract[field], msg=f"empty {case_name}.{field}")
            self.assertIsInstance(contract["forbidden_claims"], list)

        unwired = (self.eval_dir / "unwired-helper" / "app.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("from legacy_transform import transform", unwired)
        self.assertNotIn("fast_helper", unwired)

        buffered = (self.eval_dir / "buffered-stream" / "http_adapter.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("complete_body = await response.read()", buffered)

        cli_case = self.eval_dir / "incompatible-cli-contract"
        caller = (cli_case / "service.py").read_text(encoding="utf-8")
        callee = (cli_case / "worker_cli.py").read_text(encoding="utf-8")
        cli_entry = (cli_case / "main.py").read_text(encoding="utf-8")
        self.assertIn("handle_export()", cli_entry)
        self.assertIn('"--format"', caller)
        self.assertIn('"--out"', caller)
        self.assertIn("allow_abbrev=False", callee)
        self.assertIn('"--output-format"', callee)
        self.assertNotIn('add_argument("--format"', callee)

        cli_result = subprocess.run(
            [sys.executable, "-B", "main.py"],
            cwd=cli_case,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(cli_result.returncode, 0, cli_result.stderr)
        self.assertTrue(cli_result.stdout.startswith("502:"), cli_result.stdout)
        self.assertIn("unrecognized arguments", cli_result.stdout)

        quota_case = self.eval_dir / "per-key-lock-kv-quota"
        app = (quota_case / "app.py").read_text(encoding="utf-8")
        quota = (quota_case / "quota.py").read_text(encoding="utf-8")
        routes = (quota_case / "routes.py").read_text(encoding="utf-8")
        deployment = (quota_case / "deployment.yaml").read_text(encoding="utf-8")
        self.assertIn("kv = FileKV", app)
        self.assertIn("gate = QuotaGate(kv)", app)
        self.assertIn("handle_client(reader, writer, gate)", app)
        self.assertNotIn("WORKERS", app)
        self.assertIn("await self.kv.get", quota)
        self.assertIn("await self.kv.set", quota)
        self.assertIn("except OSError", quota)
        self.assertNotIn("gate.allow", routes.split("async def admin_request", 1)[1])
        self.assertIn("replicas: 3", deployment)
        self.assertIn("selector:", deployment)
        self.assertIn('value: "4"', deployment)
        self.assertIn('command: ["python", "app.py"]', deployment)
        self.assertIn('accessModes: ["ReadWriteMany"]', deployment)

        quota_file = Path(tempfile.mkdtemp(prefix="quota-fixture-test-")) / "quota.json"
        quota_script = (
            "import asyncio\n"
            "from pathlib import Path\n"
            "from quota import FileKV, QuotaGate\n"
            "class FailingKV:\n"
            "    async def get(self, key): raise OSError('offline')\n"
            "    async def set(self, key, value): raise AssertionError('unreachable')\n"
            "async def check():\n"
            f"    gate = QuotaGate(FileKV(Path({str(quota_file)!r})), limit=2)\n"
            "    assert await gate.allow('tenant') is True\n"
            "    assert await gate.allow('tenant') is True\n"
            "    assert await gate.allow('tenant') is False\n"
            "    assert await QuotaGate(FailingKV()).allow('tenant') is True\n"
            "asyncio.run(check())\n"
        )
        quota_result = subprocess.run(
            [sys.executable, "-B", "-c", quota_script],
            cwd=quota_case,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(quota_result.returncode, 0, quota_result.stderr)

        for source_path in self.eval_dir.glob("*/*.py"):
            ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))

    def test_helm_uses_specialized_handoff_after_acceptance(self):
        required_phrases = (
            "After accepting each meaningful implementation chunk",
            "invoke the independent **`architecture-map`** skill",
            "If maintenance was explicitly enabled but no report exists yet",
            "invoke its `init` mode for the first handoff",
            "Helm must not pre-filter",
            "edit the architecture map directly",
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
            "skills/architecture-map ~/.agents/skills/architecture-map",
            self.helm_readme,
        )


if __name__ == "__main__":
    unittest.main()
