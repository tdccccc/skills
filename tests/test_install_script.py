import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class InstallScriptTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]

    def run_install(self, *args, env=None):
        claude_config_dir = Path(tempfile.mkdtemp(prefix="skills-install-test-")) / "claude"
        run_env = os.environ.copy()
        if env:
            run_env.update(env)
        run_env["CLAUDE_CONFIG_DIR"] = str(claude_config_dir)

        result = subprocess.run(
            ["bash", str(self.repo_root / "install.sh"), *args],
            cwd=self.repo_root,
            env=run_env,
            text=True,
            capture_output=True,
            check=False,
        )

        return result, claude_config_dir / "skills"

    def assert_claude_collection(self, skills_dir):
        # Skills whose install-targets include claude (current repo set).
        for skill_name in [
            "code-change-discipline",
            "helm",
            "technical-report",
            "tocodex",
            "grill-me",
            "grill-with-docs",
            "domain-modeling",
            "security-audit",
        ]:
            self.assertTrue(
                (skills_dir / skill_name / "SKILL.md").is_file(),
                msg=f"missing installed skill: {skill_name}",
            )

        # Removed / never present on the Claude install path.
        self.assertFalse((skills_dir / "codex-task-executor").exists())

        # No stray top-level shared/ or tools/: each skill is self-contained.
        self.assertFalse((skills_dir / "shared").exists())
        self.assertFalse((skills_dir / "tools").exists())

        # Self-contained supporting files install with their skills.
        for template_name in (
            "goal.md",
            "phase.md",
            "journal-entry.md",
            "intake-prompt.md",
        ):
            self.assertTrue(
                (skills_dir / "helm" / "templates" / template_name).is_file(),
                msg=f"missing helm template: {template_name}",
            )

        self.assertTrue(
            (skills_dir / "code-change-discipline" / "README.md").is_file()
        )

        technical_report = skills_dir / "technical-report"
        self.assertTrue((technical_report / "REFERENCE.md").is_file())
        self.assertTrue(
            (technical_report / "templates" / "technical-report.md").is_file()
        )
        self.assertTrue((skills_dir / "tocodex" / "SKILL.md").is_file())

    def test_installs_to_claude_code_by_default(self):
        result, claude_skills_dir = self.run_install()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_claude_collection(claude_skills_dir)

    def test_dest_override_installs_claude_skills(self):
        dest = Path(tempfile.mkdtemp(prefix="skills-dest-"))
        result = subprocess.run(
            ["bash", str(self.repo_root / "install.sh"), "--dest", str(dest)],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_claude_collection(dest)

    def test_link_mode_symlinks_skill_dirs(self):
        dest = Path(tempfile.mkdtemp(prefix="skills-link-"))
        result = subprocess.run(
            ["bash", str(self.repo_root / "install.sh"), "--dest", str(dest), "--link"],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        helm = dest / "helm"
        self.assertTrue(helm.is_symlink())
        self.assertEqual(helm.resolve(), (self.repo_root / "helm").resolve())
        self.assertTrue((helm / "SKILL.md").is_file())

    def test_unknown_option_fails(self):
        result, _ = self.run_install("--target", "codex")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown option: --target", result.stderr)

    def test_skips_skills_that_exclude_claude(self):
        # Build a temporary mini-repo so we don't mutate the real skill set.
        mini_repo = Path(tempfile.mkdtemp(prefix="skills-mini-repo-"))
        shutil.copy2(self.repo_root / "install.sh", mini_repo / "install.sh")
        os.chmod(mini_repo / "install.sh", 0o755)

        claude_skill = mini_repo / "claude-only"
        claude_skill.mkdir()
        (claude_skill / "SKILL.md").write_text(
            "---\n"
            "name: claude-only\n"
            "description: Included because install-targets is claude.\n"
            "install-targets: claude\n"
            "---\n",
            encoding="utf-8",
        )

        codex_skill = mini_repo / "codex-only"
        codex_skill.mkdir()
        (codex_skill / "SKILL.md").write_text(
            "---\n"
            "name: codex-only\n"
            "description: Excluded from Claude install.\n"
            "install-targets: codex\n"
            "---\n",
            encoding="utf-8",
        )

        both_skill = mini_repo / "both-skill"
        both_skill.mkdir()
        (both_skill / "SKILL.md").write_text(
            "---\n"
            "name: both-skill\n"
            "description: Included because install-targets is both.\n"
            "install-targets: both\n"
            "---\n",
            encoding="utf-8",
        )

        default_skill = mini_repo / "default-skill"
        default_skill.mkdir()
        (default_skill / "SKILL.md").write_text(
            "---\n"
            "name: default-skill\n"
            "description: Included because missing install-targets defaults to both.\n"
            "---\n",
            encoding="utf-8",
        )

        dest = Path(tempfile.mkdtemp(prefix="skills-filter-dest-"))
        result = subprocess.run(
            ["bash", str(mini_repo / "install.sh"), "--dest", str(dest)],
            cwd=mini_repo,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((dest / "claude-only" / "SKILL.md").is_file())
        self.assertTrue((dest / "both-skill" / "SKILL.md").is_file())
        self.assertTrue((dest / "default-skill" / "SKILL.md").is_file())
        self.assertFalse((dest / "codex-only").exists())
        self.assertIn("Skipping codex-only", result.stdout)

    def test_is_idempotent_without_force(self):
        dest = Path(tempfile.mkdtemp(prefix="skills-dest-"))
        result = subprocess.run(
            ["bash", str(self.repo_root / "install.sh"), "--dest", str(dest), "--no-force"],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )

        second = subprocess.run(
            ["bash", str(self.repo_root / "install.sh"), "--dest", str(dest), "--no-force"],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("already exists", second.stdout)

    def test_dry_run_does_not_write(self):
        dest = Path(tempfile.mkdtemp(prefix="skills-dry-"))
        result = subprocess.run(
            ["bash", str(self.repo_root / "install.sh"), "--dest", str(dest), "--dry-run"],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(dest.iterdir()), msg="dry-run should not create skill dirs")
        self.assertIn("helm", result.stdout)


class BootstrapScriptTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        if shutil.which("git") is None:
            self.skipTest("git is required for bootstrap tests")

    def make_source_repo(self):
        source_repo = Path(tempfile.mkdtemp(prefix="skills-source-repo-"))
        (source_repo / "demo-skill").mkdir()
        (source_repo / "demo-skill" / "SKILL.md").write_text(
            "---\n"
            "name: demo-skill\n"
            "description: Demo skill for bootstrap tests.\n"
            "---\n",
            encoding="utf-8",
        )
        shutil.copy2(self.repo_root / "install.sh", source_repo / "install.sh")
        os.chmod(source_repo / "install.sh", 0o755)

        subprocess.run(["git", "init"], cwd=source_repo, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-b", "main"], cwd=source_repo, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=source_repo, check=True, capture_output=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Test User",
                "-c",
                "user.email=test@example.com",
                "commit",
                "-m",
                "test(fixtures): initialize test repo",
                "-m",
                "Create a minimal source repository for bootstrap tests.\n\n"
                "The test validates clone and install behavior without network access.\n\n"
                "Verified by the bootstrap unittest.",
            ],
            cwd=source_repo,
            check=True,
            capture_output=True,
        )
        return source_repo

    def run_bootstrap(self, source_repo, repo_dir, *args, env_extra=None):
        env = os.environ.copy()
        env["SKILLS_REPO_URL"] = str(source_repo)
        env["SKILLS_REPO_DIR"] = str(repo_dir)
        if env_extra:
            env.update(env_extra)

        return subprocess.run(
            ["bash", str(self.repo_root / "bootstrap.sh"), *args],
            cwd=tempfile.mkdtemp(prefix="bootstrap-cwd-"),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_bootstrap_defaults_to_xdg_cache_and_claude_target(self):
        source_repo = self.make_source_repo()
        claude_config_dir = Path(tempfile.mkdtemp(prefix="bootstrap-claude-config-")) / "claude"
        xdg_cache_home = Path(tempfile.mkdtemp(prefix="bootstrap-xdg-cache-"))
        env = os.environ.copy()
        env["CLAUDE_CONFIG_DIR"] = str(claude_config_dir)
        env["XDG_CACHE_HOME"] = str(xdg_cache_home)
        env["SKILLS_REPO_URL"] = str(source_repo)
        # Leave SKILLS_REPO_DIR unset so bootstrap uses XDG cache default.

        result = subprocess.run(
            ["bash", str(self.repo_root / "bootstrap.sh")],
            cwd=tempfile.mkdtemp(prefix="bootstrap-cwd-"),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((xdg_cache_home / "tdccccc-skills" / ".git").is_dir())
        self.assertTrue((claude_config_dir / "skills" / "demo-skill" / "SKILL.md").is_file())

    def test_bootstrap_clones_repo_and_runs_installer(self):
        source_repo = self.make_source_repo()
        repo_dir = Path(tempfile.mkdtemp(prefix="skills-cache-")) / "repo"
        dest = Path(tempfile.mkdtemp(prefix="bootstrap-dest-"))

        result = self.run_bootstrap(source_repo, repo_dir, "--dest", str(dest))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((repo_dir / ".git").is_dir())
        self.assertTrue((dest / "demo-skill" / "SKILL.md").is_file())

    def test_bootstrap_updates_cached_repo_before_installing(self):
        source_repo = self.make_source_repo()
        repo_dir = Path(tempfile.mkdtemp(prefix="skills-cache-")) / "repo"
        dest = Path(tempfile.mkdtemp(prefix="bootstrap-dest-"))

        first = self.run_bootstrap(source_repo, repo_dir, "--dest", str(dest))
        self.assertEqual(first.returncode, 0, first.stderr)

        (source_repo / "second-skill").mkdir()
        (source_repo / "second-skill" / "SKILL.md").write_text(
            "---\n"
            "name: second-skill\n"
            "description: Second demo skill for bootstrap tests.\n"
            "---\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=source_repo, check=True, capture_output=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Test User",
                "-c",
                "user.email=test@example.com",
                "commit",
                "-m",
                "test(fixtures): add second skill",
                "-m",
                "Add a second fixture skill so the bootstrap update path has new content.\n\n"
                "The test validates cached repository updates without network access.\n\n"
                "Verified by the bootstrap unittest.",
            ],
            cwd=source_repo,
            check=True,
            capture_output=True,
        )

        second = self.run_bootstrap(source_repo, repo_dir, "--dest", str(dest))

        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertTrue((dest / "second-skill" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
