from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_SOURCE = REPO_ROOT / "terraform" / "scripts" / "install-flux-bootstrap-secrets.sh"
TOKEN_SENTINEL = "canary-service-account-token-value"


class FluxBootstrapSecretsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="flux-bootstrap-secrets-")
        self.root = Path(self.tempdir.name)
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        self.log = self.root / "commands.log"
        self.age_key = self.root / "keys.agekey"
        self.age_key.write_text("AGE-SECRET-KEY-test-only\n", encoding="utf-8")
        self.script = self.root / "install-flux-bootstrap-secrets.sh"
        if SCRIPT_SOURCE.exists():
            shutil.copy2(SCRIPT_SOURCE, self.script)
            self.script.chmod(0o755)
        self._write_executable(
            "kubectl",
            """#!/usr/bin/env bash
set -euo pipefail
printf 'kubectl %s\n' "$*" >> "$FAKE_COMMAND_LOG"
for arg in "$@"; do
  if [[ "$arg" == --from-file=token=* ]]; then
    token_file="${arg#--from-file=token=}"
    printf 'token-file-mode=%s\n' "$(stat -c '%a' "$token_file")" >> "$FAKE_COMMAND_LOG"
    printf 'token-file-path=%s\n' "$token_file" >> "$FAKE_COMMAND_LOG"
  fi
done
if [[ "${1:-}" == "apply" ]]; then
  cat >/dev/null
fi
if [[ "$*" == *"-o yaml"* ]]; then
  printf '%s\n' 'apiVersion: v1' 'kind: Secret' 'metadata: {}'
fi
""",
        )
        self._write_executable(
            "op",
            """#!/usr/bin/env bash
set -euo pipefail
printf 'op %s\n' "$*" >> "$FAKE_COMMAND_LOG"
if [[ "${FAKE_EMPTY_OP_TOKEN:-false}" != "true" ]]; then
  printf '%s' "$FAKE_OP_TOKEN"
fi
""",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_dual_mode_installs_both_secrets_without_exposing_token(self) -> None:
        result = self._run(
            FLUX_BOOTSTRAP_SECRET_PROVIDER="dual",
            OP_SERVICE_ACCOUNT_TOKEN_REF="op://Homelab Bootstrap/development/token",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        log = self.log.read_text(encoding="utf-8")
        self.assertIn("secret generic sops-age", log)
        self.assertIn("secret generic onepassword-service-account-token", log)
        self.assertIn("op read --no-newline op://Homelab Bootstrap/development/token", log)
        self.assertIn("token-file-mode=600", log)
        self.assertNotIn(TOKEN_SENTINEL, result.stdout)
        self.assertNotIn(TOKEN_SENTINEL, result.stderr)
        token_path = re.search(r"^token-file-path=(.+)$", log, re.MULTILINE)
        self.assertIsNotNone(token_path)
        self.assertFalse(Path(token_path.group(1)).exists())

    def test_default_mode_remains_sops_only(self) -> None:
        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        log = self.log.read_text(encoding="utf-8")
        self.assertIn("secret generic sops-age", log)
        self.assertNotIn("onepassword-service-account-token", log)
        self.assertNotIn("op read", log)

    def test_onepassword_mode_does_not_require_age_key(self) -> None:
        self.age_key.unlink()

        result = self._run(
            FLUX_BOOTSTRAP_SECRET_PROVIDER="onepassword",
            OP_SERVICE_ACCOUNT_TOKEN_REF="op://bootstrap/development/token",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        log = self.log.read_text(encoding="utf-8")
        self.assertNotIn("sops-age", log)
        self.assertIn("onepassword-service-account-token", log)

    def test_unknown_mode_fails_before_cluster_changes(self) -> None:
        result = self._run(FLUX_BOOTSTRAP_SECRET_PROVIDER="mystery")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported bootstrap secret provider", result.stderr)
        self.assertFalse(self.log.exists())

    def test_empty_onepassword_token_fails_without_applying_secret(self) -> None:
        result = self._run(
            FLUX_BOOTSTRAP_SECRET_PROVIDER="onepassword",
            OP_SERVICE_ACCOUNT_TOKEN_REF="op://bootstrap/development/token",
            FAKE_EMPTY_OP_TOKEN="true",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("returned an empty value", result.stderr)
        log = self.log.read_text(encoding="utf-8")
        self.assertNotIn("onepassword-service-account-token", log)
        self.assertNotIn(TOKEN_SENTINEL, result.stderr)

    def test_dual_mode_is_idempotent(self) -> None:
        overrides = {
            "FLUX_BOOTSTRAP_SECRET_PROVIDER": "dual",
            "OP_SERVICE_ACCOUNT_TOKEN_REF": "op://bootstrap/development/token",
        }

        first = self._run(**overrides)
        second = self._run(**overrides)

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        log = self.log.read_text(encoding="utf-8")
        self.assertEqual(log.count("secret generic sops-age"), 2)
        self.assertEqual(log.count("secret generic onepassword-service-account-token"), 2)
        self.assertGreaterEqual(log.count("kubectl apply -f -"), 6)

    def test_missing_age_key_fails_before_cluster_changes(self) -> None:
        self.age_key.unlink()

        result = self._run(FLUX_BOOTSTRAP_SECRET_PROVIDER="sops")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SOPS Age key is missing or empty", result.stderr)
        self.assertFalse(self.log.exists())

    def test_invalid_onepassword_reference_fails_before_token_read(self) -> None:
        result = self._run(
            FLUX_BOOTSTRAP_SECRET_PROVIDER="onepassword",
            OP_SERVICE_ACCOUNT_TOKEN_REF="not-a-secret-reference",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be an op:// secret reference", result.stderr)
        self.assertFalse(self.log.exists())

    def _write_executable(self, name: str, body: str) -> None:
        path = self.bin_dir / name
        path.write_text(body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def _run(self, **overrides: str) -> subprocess.CompletedProcess[str]:
        self.assertTrue(self.script.exists(), f"missing implementation script: {SCRIPT_SOURCE}")
        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{self.bin_dir}:{env['PATH']}",
                "FAKE_COMMAND_LOG": str(self.log),
                "FAKE_OP_TOKEN": TOKEN_SENTINEL,
                "SOPS_AGE_KEY_FILE": str(self.age_key),
            }
        )
        env.update(overrides)
        return subprocess.run(
            [str(self.script)],
            cwd=self.root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


if __name__ == "__main__":
    unittest.main()
