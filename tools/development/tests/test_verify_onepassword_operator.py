from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import itertools
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools" / "development" / "verify_onepassword_operator.py"
SECRET_SENTINEL = "do-not-print-canary-value"


class FakeRunner:
    def __init__(self, *, fail_on: str | None = None) -> None:
        self.fail_on = fail_on
        self.calls: list[tuple[list[str], dict[str, object]]] = []
        self.secret_versions = iter(["11", "11", "12"])
        self.pod_uids = iter(["pod-old", "pod-old", "pod-new"])

    def __call__(self, args: list[str], **kwargs: object) -> SimpleNamespace:
        self.calls.append((list(args), dict(kwargs)))
        command = " ".join(args)
        if self.fail_on and self.fail_on in command:
            return SimpleNamespace(returncode=1, stdout="", stderr="simulated failure")
        if command.startswith("op vault get"):
            return SimpleNamespace(returncode=0, stdout=json.dumps({"id": "vault-id"}), stderr="")
        if command.startswith("op item get"):
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps(
                    {
                        "id": "item-id",
                        "fields": [{"id": "password", "label": "password", "value": SECRET_SENTINEL}],
                    }
                ),
                stderr="",
            )
        if "jsonpath={.metadata.resourceVersion}" in command:
            return SimpleNamespace(returncode=0, stdout=next(self.secret_versions), stderr="")
        if "jsonpath={.items[0].metadata.uid}" in command:
            return SimpleNamespace(returncode=0, stdout=next(self.pod_uids), stderr="")
        return SimpleNamespace(returncode=0, stdout="", stderr="")


@unittest.skipUnless(MODULE_PATH.exists(), "implementation module is not present yet")
class OnePasswordOperatorVerifierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("verify_onepassword_operator", MODULE_PATH)
        assert spec and spec.loader
        cls.verify = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.verify
        spec.loader.exec_module(cls.verify)

    def test_resolves_ids_validates_rotation_and_cleans_up_without_printing_value(self) -> None:
        runner = FakeRunner()
        output = io.StringIO()
        config = self.verify.Config(
            vault="Homelab Development",
            item="k8s--onepassword-system--canary",
            slug="example",
            kubeconfig=Path("/tmp/dev.kubeconfig"),
            timeout_seconds=900,
            keep=False,
            skip_rotation=False,
        )

        with contextlib.redirect_stdout(output):
            self.verify.verify(
                config,
                runner=runner,
                sleep=lambda _: None,
                refresh_token=lambda: "test-refresh",
            )

        commands = [" ".join(args) for args, _ in runner.calls]
        self.assertTrue(any(command.startswith("op vault get") for command in commands))
        self.assertTrue(any(command.startswith("op item get") for command in commands))
        self.assertTrue(any(command.startswith("op item edit item-id") for command in commands))
        self.assertTrue(
            any(
                "annotate onepassworditem/onepassword-canary "
                "homelab.petebeegle.com/refresh-request=test-refresh --overwrite" in command
                for command in commands
            )
        )
        self.assertTrue(any("wait kustomization/onepassword-operator" in command for command in commands))
        self.assertTrue(any("wait helmrelease/onepassword-operator" in command for command in commands))
        self.assertTrue(any("apply -f -" in command for command in commands))
        self.assertTrue(any("delete namespace onepassword-canary-example" in command for command in commands))
        self.assertNotIn(SECRET_SENTINEL, output.getvalue())
        self.assertIn("Secret resourceVersion: 11 -> 12", output.getvalue())
        self.assertIn("Pod UID: pod-old -> pod-new", output.getvalue())

    def test_failure_still_cleans_up(self) -> None:
        runner = FakeRunner(fail_on="wait onepassworditem")
        config = self._config()

        with self.assertRaises(self.verify.VerificationError):
            self.verify.verify(config, runner=runner, sleep=lambda _: None)

        commands = [" ".join(args) for args, _ in runner.calls]
        self.assertTrue(any("delete namespace onepassword-canary-example" in command for command in commands))

    def test_keep_skips_cleanup(self) -> None:
        runner = FakeRunner()
        config = self._config(keep=True, skip_rotation=True)

        self.verify.verify(config, runner=runner, sleep=lambda _: None)

        commands = [" ".join(args) for args, _ in runner.calls]
        self.assertFalse(any("delete namespace" in command for command in commands))

    def test_rotation_timeout_fails_and_cleans_up(self) -> None:
        runner = FakeRunner()
        runner.secret_versions = itertools.repeat("11")
        runner.pod_uids = itertools.repeat("pod-old")
        clock = iter([0.0, 0.0, 2.0])

        with self.assertRaisesRegex(self.verify.VerificationError, "timed out"):
            self.verify.verify(
                self._config(timeout_seconds=1),
                runner=runner,
                sleep=lambda _: None,
                monotonic=lambda: next(clock),
            )

        commands = [" ".join(args) for args, _ in runner.calls]
        self.assertTrue(any("delete namespace onepassword-canary-example" in command for command in commands))

    def test_cleanup_failure_is_a_verification_failure(self) -> None:
        runner = FakeRunner(fail_on="delete namespace")

        with self.assertRaisesRegex(self.verify.VerificationError, "command failed"):
            self.verify.verify(
                self._config(skip_rotation=True),
                runner=runner,
                sleep=lambda _: None,
            )

    def test_rejects_item_without_password_field_without_revealing_fields(self) -> None:
        runner = FakeRunner()

        def without_password(args: list[str], **kwargs: object) -> SimpleNamespace:
            result = runner(args, **kwargs)
            if " ".join(args).startswith("op item get"):
                return SimpleNamespace(
                    returncode=0,
                    stdout=json.dumps(
                        {"id": "item-id", "fields": [{"id": "other", "label": "other", "value": SECRET_SENTINEL}]}
                    ),
                    stderr="",
                )
            return result

        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(self.verify.VerificationError):
            self.verify.verify(self._config(), runner=without_password, sleep=lambda _: None)
        self.assertNotIn(SECRET_SENTINEL, output.getvalue())

    def _config(self, **overrides: object):
        values = {
            "vault": "Homelab Development",
            "item": "k8s--onepassword-system--canary",
            "slug": "example",
            "kubeconfig": Path("/tmp/dev.kubeconfig"),
            "timeout_seconds": 900,
            "keep": False,
            "skip_rotation": False,
        }
        values.update(overrides)
        return self.verify.Config(**values)


if __name__ == "__main__":
    unittest.main()
