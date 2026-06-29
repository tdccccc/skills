import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class InstallScriptTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        if shutil.which("script") is None:
            self.script_command = None
        else:
            self.script_command = shutil.which("script")

    def run_install(self, *args):
        codex_home = Path(tempfile.mkdtemp(prefix="skills-install-test-")) / "codex"
        claude_config_dir = Path(tempfile.mkdtemp(prefix="skills-install-test-")) / "claude"
        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        env["CLAUDE_CONFIG_DIR"] = str(claude_config_dir)

        result = subprocess.run(
            ["bash", str(self.repo_root / "install.sh"), *args],
            cwd=self.repo_root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        return result, codex_home / "skills", claude_config_dir / "skills"

    def assert_claude_collection(self, skills_dir):
        # Skills whose install-targets include claude.
        for skill_name in [
            "claude-codex-runner",
            "grill-me",
            "security-audit",
        ]:
            self.assertTrue((skills_dir / skill_name / "SKILL.md").is_file())

        # codex-only skill must not land on the claude side.
        self.assertFalse((skills_dir / "codex-task-executor").exists())

        # No stray top-level shared/ or tools/: each skill is self-contained,
        # so its support files live nested inside the skill directory.
        self.assertFalse((skills_dir / "shared").exists())
        self.assertFalse((skills_dir / "tools").exists())
        self.assertTrue(
            (skills_dir / "claude-codex-runner" / "references" / "codex-task-contract.md").is_file()
        )
        self.assertTrue(
            (skills_dir / "claude-codex-runner" / "tools" / "codex-runner" / "codex-runner").is_file()
        )

    def assert_codex_collection(self, skills_dir):
        # Only the codex-targeted skill installs here.
        self.assertTrue((skills_dir / "codex-task-executor" / "SKILL.md").is_file())
        for skill_name in [
            "claude-codex-runner",
            "grill-me",
            "security-audit",
        ]:
            self.assertFalse((skills_dir / skill_name).exists())
        self.assertFalse((skills_dir / "shared").exists())
        self.assertFalse((skills_dir / "tools").exists())

    def test_installs_to_claude_code_by_default(self):
        result, codex_skills_dir, claude_skills_dir = self.run_install()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_claude_collection(claude_skills_dir)
        self.assertFalse(codex_skills_dir.exists())

    def test_default_tty_prompt_accepts_both_targets(self):
        if self.script_command is None:
            self.skipTest("script is required for tty prompt tests")
        codex_home = Path(tempfile.mkdtemp(prefix="skills-install-test-")) / "codex"
        claude_config_dir = Path(tempfile.mkdtemp(prefix="skills-install-test-")) / "claude"
        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        env["CLAUDE_CONFIG_DIR"] = str(claude_config_dir)

        result = subprocess.run(
            [
                "bash",
                "-c",
                f"printf 'y\\n' | script -qfec {str(self.repo_root / 'install.sh')} /dev/null",
            ],
            cwd=self.repo_root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_codex_collection(codex_home / "skills")
        self.assert_claude_collection(claude_config_dir / "skills")

    def test_installs_to_codex_when_target_is_codex(self):
        result, codex_skills_dir, claude_skills_dir = self.run_install("--target", "codex")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_codex_collection(codex_skills_dir)
        self.assertFalse(claude_skills_dir.exists())

    def test_installs_to_both_targets(self):
        result, codex_skills_dir, claude_skills_dir = self.run_install("--target", "both")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_codex_collection(codex_skills_dir)
        self.assert_claude_collection(claude_skills_dir)

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

    def run_bootstrap(self, source_repo, repo_dir, codex_home, *args):
        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        env["SKILLS_REPO_URL"] = str(source_repo)
        env["SKILLS_REPO_DIR"] = str(repo_dir)

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
        codex_home = Path(tempfile.mkdtemp(prefix="bootstrap-codex-home-")) / "codex"
        claude_config_dir = Path(tempfile.mkdtemp(prefix="bootstrap-claude-config-")) / "claude"
        xdg_cache_home = Path(tempfile.mkdtemp(prefix="bootstrap-xdg-cache-"))
        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        env["CLAUDE_CONFIG_DIR"] = str(claude_config_dir)
        env["XDG_CACHE_HOME"] = str(xdg_cache_home)
        env["SKILLS_REPO_URL"] = str(source_repo)

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
        self.assertFalse((codex_home / "skills").exists())

    def test_bootstrap_clones_repo_and_runs_installer(self):
        source_repo = self.make_source_repo()
        repo_dir = Path(tempfile.mkdtemp(prefix="skills-cache-")) / "repo"
        codex_home = Path(tempfile.mkdtemp(prefix="bootstrap-codex-home-"))
        dest = Path(tempfile.mkdtemp(prefix="bootstrap-dest-"))

        result = self.run_bootstrap(source_repo, repo_dir, codex_home, "--dest", str(dest))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((repo_dir / ".git").is_dir())
        self.assertTrue((dest / "demo-skill" / "SKILL.md").is_file())

    def test_bootstrap_updates_cached_repo_before_installing(self):
        source_repo = self.make_source_repo()
        repo_dir = Path(tempfile.mkdtemp(prefix="skills-cache-")) / "repo"
        codex_home = Path(tempfile.mkdtemp(prefix="bootstrap-codex-home-"))
        dest = Path(tempfile.mkdtemp(prefix="bootstrap-dest-"))

        first = self.run_bootstrap(source_repo, repo_dir, codex_home, "--dest", str(dest))
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

        second = self.run_bootstrap(source_repo, repo_dir, codex_home, "--dest", str(dest))

        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertTrue((dest / "second-skill" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
