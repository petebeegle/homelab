from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools/development/verify_onepassword_certificate.py"


@unittest.skipUnless(MODULE_PATH.exists(), "implementation module is not present yet")
class OnePasswordCertificateVerifierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("verify_onepassword_certificate", MODULE_PATH)
        assert spec and spec.loader
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def runner(self, *, fail_on: str | None = None):
        calls: list[tuple[list[str], dict[str, object]]] = []

        def run(args: list[str], **kwargs: object):
            calls.append((list(args), dict(kwargs)))
            if fail_on and fail_on in " ".join(args):
                return SimpleNamespace(returncode=1, stdout="", stderr="secret-sentinel")
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        return run, calls

    def config(self):
        return self.module.Config(
            slug="example",
            kubeconfig=Path("/tmp/dev.config"),
            domain="dev.lab.petebeegle.com",
            timeout_seconds=600,
        )

    def test_issues_staging_certificate_and_always_removes_namespace(self) -> None:
        runner, calls = self.runner()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.module.verify(self.config(), runner=runner)
        commands = [" ".join(args) for args, _ in calls]
        self.assertTrue(any("apply -f -" in command for command in commands))
        self.assertTrue(any("wait certificate/onepassword-cutover" in command for command in commands))
        self.assertTrue(any("delete namespace onepassword-certificate-example" in command for command in commands))
        manifest = next(kwargs["input"] for args, kwargs in calls if "apply" in args)
        self.assertIn("issuerRef:\n    kind: ClusterIssuer\n    name: cloudflare-staging", manifest)
        self.assertIn("onepassword-example.dev.lab.petebeegle.com", manifest)
        self.assertNotIn("secret-sentinel", output.getvalue())

    def test_wait_failure_still_removes_namespace_without_displaying_output(self) -> None:
        runner, calls = self.runner(fail_on="wait certificate")
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(self.module.VerificationError):
            self.module.verify(self.config(), runner=runner)
        self.assertTrue(any("delete namespace" in " ".join(args) for args, _ in calls))
        self.assertNotIn("secret-sentinel", output.getvalue())

    def test_rejects_unsafe_slug_before_mutation(self) -> None:
        runner, calls = self.runner()
        with self.assertRaises(self.module.VerificationError):
            self.module.verify(
                self.module.Config("BAD", Path("/tmp/dev.config"), "example.com", 60),
                runner=runner,
            )
        self.assertEqual([], calls)


if __name__ == "__main__":
    unittest.main()
