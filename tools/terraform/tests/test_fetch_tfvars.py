from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.terraform.tests.test_state_backends import TERRAFORM, roots


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "tools" / "terraform" / "fetch_tfvars.sh"
ROOTS = [str(root.relative_to(TERRAFORM)) for root in roots()]

# Plays `op document get <title> --vault <vault> --out-file <path>`: logs the call and writes
# "secret for <title>" unless the title is listed in $FAKE_OP_MISSING.
FAKE_OP = r"""#!/usr/bin/env bash
echo "$*" >> "$FAKE_LOG"
[ "$1 $2" = "document get" ] || exit 64
title="$3"; shift 3
out=""
while [ $# -gt 0 ]; do
  case "$1" in
    --out-file) out="$2"; shift 2 ;;
    *) shift ;;
  esac
done
case ",$FAKE_OP_MISSING," in *",$title,"*) echo "[ERROR] \"$title\" isn't a document" >&2; exit 1 ;; esac
printf 'secret for %s\n' "$title" > "$out"
chmod 600 "$out"
"""


class FetchTfvarsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / "tools" / "terraform").mkdir(parents=True)
        shutil.copy(SCRIPT, self.tmp / "tools" / "terraform" / "fetch_tfvars.sh")
        for root in ROOTS:
            (self.tmp / "terraform" / root).mkdir(parents=True)
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        (bin_dir / "op").write_text(FAKE_OP, encoding="utf-8")
        (bin_dir / "op").chmod(0o755)
        self.log = self.tmp / "op.log"
        self.log.touch()
        self.env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "FAKE_LOG": str(self.log)}

    def run_script(self, *args: str, missing: str = "") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(self.tmp / "tools" / "terraform" / "fetch_tfvars.sh"), *args],
            env={**self.env, "FAKE_OP_MISSING": missing},
            capture_output=True,
            text=True,
        )

    def tfvars(self, root: str) -> Path:
        return self.tmp / "terraform" / root / "terraform.tfvars"

    def test_fetches_every_root_from_the_cluster_bootstrap_vault(self) -> None:
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        for root in ROOTS:
            with self.subTest(root=root):
                self.assertEqual(self.tfvars(root).read_text(), f"secret for Terraform tfvars {root}\n")
                self.assertEqual(self.tfvars(root).stat().st_mode & 0o777, 0o600)
        calls = self.log.read_text().splitlines()
        self.assertEqual(len(calls), len(ROOTS))
        for root, call in zip(ROOTS, calls):
            self.assertTrue(call.startswith(f"document get Terraform tfvars {root} --vault cluster bootstrap "), call)

    def test_never_prints_the_contents(self) -> None:
        result = self.run_script()
        self.assertNotIn("secret for", result.stdout + result.stderr)

    def test_keeps_a_file_that_is_already_there(self) -> None:
        self.tfvars("production").write_text("local edits\n")
        result = self.run_script("production", "development")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tfvars("production").read_text(), "local edits\n")
        self.assertIn("production: kept", result.stdout)
        self.assertNotIn("Terraform tfvars production", self.log.read_text())
        self.assertTrue(self.tfvars("development").exists())

    def test_a_missing_document_fails_and_leaves_no_file(self) -> None:
        result = self.run_script("external/grafana", "external/nexus", missing="Terraform tfvars external/grafana")
        self.assertEqual(result.returncode, 1)
        self.assertIn("external/grafana", result.stderr)
        self.assertFalse(self.tfvars("external/grafana").exists())
        self.assertTrue(self.tfvars("external/nexus").exists(), "the other roots are still fetched")

    def test_an_unknown_root_is_refused_before_anything_is_fetched(self) -> None:
        result = self.run_script("production", "unifi")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unifi", result.stderr)
        self.assertEqual(self.log.read_text(), "")


if __name__ == "__main__":
    unittest.main()
