from __future__ import annotations

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_SOURCE = REPO_ROOT / ".codex" / "scripts" / "prepare_development_smoke_secrets.sh"
STAGE_SOURCE = REPO_ROOT / ".codex" / "scripts" / "stage_implementation_secrets.sh"
INSTALL_SOURCE = REPO_ROOT / ".codex" / "scripts" / "install_implementation_secrets.sh"


class PrepareDevelopmentSmokeSecretsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="smoke-secrets-")
        self.root = Path(self.tempdir.name) / "source"
        self.clone = Path(self.tempdir.name) / "clone"
        self.second_clone = Path(self.tempdir.name) / "verifier"
        _init_repo(self.root, ignore_tfvars=True)
        _install_scripts(self.root)
        _init_repo(self.clone, ignore_tfvars=True)
        _init_repo(self.second_clone, ignore_tfvars=True)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_installs_development_tfvars_with_private_mode(self) -> None:
        _write_tfvars(self.root)

        result = _run(self.root, "example", str(self.clone))

        self.assertEqual(result.returncode, 0, result.stderr)
        installed = self.clone / "terraform" / "development" / "terraform.tfvars"
        self.assertEqual(installed.read_text(encoding="utf-8"), 'pm_api_url = "supersecret"\n')
        self.assertEqual(stat.S_IMODE(installed.stat().st_mode), 0o600)
        self.assertNotIn("supersecret", result.stdout)
        self.assertNotIn("supersecret", result.stderr)

    def test_installs_into_multiple_clones(self) -> None:
        _write_tfvars(self.root)

        result = _run(self.root, "example", str(self.clone), str(self.second_clone))

        self.assertEqual(result.returncode, 0, result.stderr)
        for clone in (self.clone, self.second_clone):
            installed = clone / "terraform" / "development" / "terraform.tfvars"
            self.assertTrue(installed.is_file())
            self.assertEqual(stat.S_IMODE(installed.stat().st_mode), 0o600)

    def test_fails_when_development_tfvars_is_missing(self) -> None:
        result = _run(self.root, "example", str(self.clone))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required ignored file is missing", result.stderr)
        self.assertFalse((self.clone / "terraform" / "development" / "terraform.tfvars").exists())

    def test_fails_when_development_tfvars_is_tracked(self) -> None:
        _write_tfvars(self.root)
        subprocess.run(
            ["git", "add", "-f", "terraform/development/terraform.tfvars"],
            cwd=self.root,
            check=True,
        )

        result = _run(self.root, "example", str(self.clone))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing tracked file", result.stderr)
        self.assertFalse((self.clone / "terraform" / "development" / "terraform.tfvars").exists())

    def test_fails_when_development_tfvars_is_not_ignored(self) -> None:
        shutil.rmtree(self.root)
        _init_repo(self.root, ignore_tfvars=False)
        _install_scripts(self.root)
        _write_tfvars(self.root)

        result = _run(self.root, "example", str(self.clone))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing non-ignored file", result.stderr)
        self.assertFalse((self.clone / "terraform" / "development" / "terraform.tfvars").exists())


def _init_repo(root: Path, *, ignore_tfvars: bool) -> None:
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "codex@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Codex"], cwd=root, check=True)
    (root / ".gitignore").write_text("*.tfvars\n" if ignore_tfvars else "", encoding="utf-8")
    (root / "README.md").write_text("# test\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore", "README.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "test: initialize"], cwd=root, check=True, stdout=subprocess.DEVNULL)


def _install_scripts(root: Path) -> None:
    script_dir = root / ".codex" / "scripts"
    script_dir.mkdir(parents=True, exist_ok=True)
    for source in (SCRIPT_SOURCE, STAGE_SOURCE, INSTALL_SOURCE):
        target = script_dir / source.name
        shutil.copy2(source, target)
        target.chmod(0o755)


def _write_tfvars(root: Path) -> None:
    tfvars = root / "terraform" / "development" / "terraform.tfvars"
    tfvars.parent.mkdir(parents=True, exist_ok=True)
    tfvars.write_text('pm_api_url = "supersecret"\n', encoding="utf-8")


def _run(root: Path, implementation: str, *clones: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("GIT_DIR", None)
    env.pop("GIT_WORK_TREE", None)
    return subprocess.run(
        [str(root / ".codex" / "scripts" / "prepare_development_smoke_secrets.sh"), implementation, *clones],
        cwd=root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


if __name__ == "__main__":
    unittest.main()
