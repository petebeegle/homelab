from __future__ import annotations

import base64
import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools/development/verify_onepassword_outage_retention.py"
SENTINEL = "outage-secret-sentinel"


@unittest.skipUnless(MODULE_PATH.exists(), "implementation module is not present yet")
class OnePasswordOutageRetentionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("verify_onepassword_outage_retention", MODULE_PATH)
        assert spec and spec.loader
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def config(self):
        return self.module.Config(
            slug="example",
            kubeconfig=Path("/tmp/dev.config"),
            namespace="cert-manager",
            item="cloudflare-api-token-onepassword",
            secret="cloudflare-api-token-onepassword",
            timeout_seconds=60,
        )

    def runner(self, *, mutate_secret: bool = False):
        calls: list[tuple[list[str], dict[str, object]]] = []
        item_states = iter([True, False, True])
        operator_states = iter([False, True])
        secret_calls = 0

        def run(args: list[str], **kwargs: object):
            nonlocal secret_calls
            calls.append((list(args), dict(kwargs)))
            command = " ".join(args)
            if "get onepassworditem" in command:
                ready = next(item_states)
                body = {"status": {"conditions": [{"type": "Ready", "status": str(ready).lower().title()}]}}
                return SimpleNamespace(returncode=0, stdout=json.dumps(body), stderr="")
            if "get secret" in command:
                secret_calls += 1
                value = SENTINEL if not mutate_secret or secret_calls == 1 else "changed"
                body = {
                    "metadata": {"uid": "secret-uid", "resourceVersion": str(secret_calls)},
                    "data": {"token": base64.b64encode(value.encode()).decode()},
                }
                return SimpleNamespace(returncode=0, stdout=json.dumps(body), stderr="")
            if "-n onepassword-system get pod" in command:
                ready = next(operator_states)
                body = {
                    "items": [{
                        "metadata": {"uid": "operator-pod"},
                        "status": {"conditions": [{"type": "Ready", "status": str(ready).lower().title()}]},
                    }]
                }
                return SimpleNamespace(returncode=0, stdout=json.dumps(body), stderr="")
            if "get pod" in command:
                body = {
                    "items": [{
                        "metadata": {"uid": "pod-uid"},
                        "status": {"conditions": [{"type": "Ready", "status": "True"}]},
                    }]
                }
                return SimpleNamespace(returncode=0, stdout=json.dumps(body), stderr="")
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        return run, calls

    def test_proves_retention_and_recovers_without_printing_secret(self) -> None:
        runner, calls = self.runner()
        sleeps: list[float] = []
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.module.verify(
                self.config(), runner=runner, sleep=sleeps.append, refresh_token=iter(["fail", "recover"]).__next__
            )
        commands = [" ".join(args) for args, _ in calls]
        manifests = [kwargs.get("input", "") for args, kwargs in calls if "apply" in args]
        self.assertTrue(any("kind: CiliumNetworkPolicy" in manifest for manifest in manifests))
        self.assertTrue(any("name: onepassword-connect" in manifest for manifest in manifests))
        self.assertTrue(any("- kube-apiserver" in manifest for manifest in manifests))
        self.assertIn(self.module.NETWORK_POLICY_SETTLE_SECONDS, sleeps)
        self.assertTrue(any("refresh-request=fail" in command for command in commands))
        self.assertTrue(any("refresh-request=recover" in command for command in commands))
        self.assertEqual(1, sum("delete pod" in command for command in commands))
        self.assertTrue(any("delete ciliumnetworkpolicy onepassword-outage-example" in command for command in commands))
        self.assertTrue(any("delete deployment onepassword-outage-example" in command for command in commands))
        self.assertNotIn(SENTINEL, output.getvalue())
        self.assertIn("operator unavailable while vault egress was blocked", output.getvalue())
        self.assertIn("retained generated Secret and ready consumer", output.getvalue())
        self.assertIn("OnePasswordItem recovered", output.getvalue())

    def test_changed_secret_fails_but_still_removes_policy_and_consumer(self) -> None:
        runner, calls = self.runner(mutate_secret=True)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(
            self.module.VerificationError, "changed during outage"
        ):
            self.module.verify(
                self.config(), runner=runner, sleep=lambda _: None, refresh_token=iter(["fail", "recover"]).__next__
            )
        commands = [" ".join(args) for args, _ in calls]
        self.assertTrue(any("delete ciliumnetworkpolicy" in command for command in commands))
        self.assertTrue(any("delete deployment" in command for command in commands))

    def test_rejects_unsafe_names_before_mutation(self) -> None:
        runner, calls = self.runner()
        with self.assertRaises(self.module.VerificationError):
            self.module.verify(
                self.module.Config("BAD", Path("/tmp/dev"), "cert-manager", "item", "secret", 60),
                runner=runner,
            )
        self.assertEqual([], calls)


if __name__ == "__main__":
    unittest.main()
