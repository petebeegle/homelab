from __future__ import annotations

import json
import os
import shlex
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_PATH = REPO_ROOT / ".codex" / "hooks" / "terraform_plan.sh"


class TerraformPlanHookTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.bin_dir = self.root / "bin"
        self.log_path = self.root / "terraform.log"
        self.bin_dir.mkdir()
        self._write_fake_terraform()
        self._init_repo()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_uninitialized_selected_root_blocks_apply(self) -> None:
        self._write_terraform_root("terraform/production")

        result = self._run_hook("terraform apply")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("run terraform init before apply", result.stderr)
        self.assertFalse(self.log_path.exists())

    def test_initialized_selected_root_runs_plan_before_apply(self) -> None:
        root = self._write_terraform_root("terraform/production")
        (root / ".terraform").mkdir()

        result = self._run_hook("terraform apply")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.log_path.read_text(encoding="utf-8").strip(),
            f"{root}|plan -detailed-exitcode -input=false -no-color",
        )

    def test_targeted_chdir_apply_ignores_unrelated_uninitialized_roots(self) -> None:
        target = self._write_terraform_root("terraform/production")
        (target / ".terraform").mkdir()
        self._write_terraform_root("terraform/external/grafana")

        result = self._run_hook("terraform -chdir=terraform/production apply")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.log_path.read_text(encoding="utf-8").strip(),
            f"{target}|plan -detailed-exitcode -input=false -no-color",
        )

    def test_targeted_chdir_space_apply_uses_target_root(self) -> None:
        target = self._write_terraform_root("terraform/production")
        (target / ".terraform").mkdir()
        self._write_terraform_root("terraform/external/grafana")

        result = self._run_hook("terraform -chdir terraform/production apply")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.log_path.read_text(encoding="utf-8").strip(),
            f"{target}|plan -detailed-exitcode -input=false -no-color",
        )

    def test_plan_failure_blocks_apply(self) -> None:
        root = self._write_terraform_root("terraform/production")
        (root / ".terraform").mkdir()

        result = self._run_hook("terraform apply", extra_env={"TF_FAKE_EXIT": "1"})

        self.assertEqual(result.returncode, 1)
        self.assertIn("terraform plan failed", result.stderr)
        self.assertEqual(
            self.log_path.read_text(encoding="utf-8").strip(),
            f"{root}|plan -detailed-exitcode -input=false -no-color",
        )

    def _init_repo(self) -> None:
        subprocess.run(["git", "init"], cwd=self.root, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(
            ["git", "config", "user.email", "codex@example.invalid"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(["git", "config", "user.name", "Codex"], cwd=self.root, check=True)
        (self.root / "README.md").write_text("# test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "-m", "test: initialize"],
            cwd=self.root,
            check=True,
            stdout=subprocess.DEVNULL,
        )

    def _write_terraform_root(self, relative_path: str) -> Path:
        root = self.root / relative_path
        root.mkdir(parents=True, exist_ok=True)
        (root / "main.tf").write_text("terraform {}\n", encoding="utf-8")
        return root

    def _write_fake_terraform(self) -> None:
        terraform = self.bin_dir / "terraform"
        terraform.write_text(
            textwrap.dedent(
                f"""\
                #!/usr/bin/env bash
                printf '%s|%s\\n' "$PWD" "$*" >> {shlex.quote(str(self.log_path))}
                exit "${{TF_FAKE_EXIT:-0}}"
                """
            ),
            encoding="utf-8",
        )
        terraform.chmod(terraform.stat().st_mode | stat.S_IXUSR)

    def _run_hook(
        self,
        command: str,
        *,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}{os.pathsep}{env['PATH']}"
        if extra_env:
            env.update(extra_env)

        return subprocess.run(
            ["bash", str(HOOK_PATH)],
            cwd=self.root,
            input=json.dumps({"command": command}),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

if __name__ == "__main__":
    unittest.main()
