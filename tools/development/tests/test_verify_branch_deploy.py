from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools" / "development" / "verify_branch_deploy.py"

spec = importlib.util.spec_from_file_location("verify_branch_deploy", MODULE_PATH)
verify = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["verify_branch_deploy"] = verify
spec.loader.exec_module(verify)


READY_HTTPROUTE = """{
  "status": {
    "parents": [
      {
        "conditions": [
          {"type": "Accepted", "status": "True"},
          {"type": "ResolvedRefs", "status": "True"}
        ]
      }
    ]
  }
}"""


TEMPLATE = """---
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: branch-${branch_slug}
  namespace: flux-system
spec:
  suspend: true
  ref:
    branch: ${branch_name}
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: branch-whoami-${branch_slug}
  namespace: flux-system
spec:
  suspend: true
  sourceRef:
    name: branch-${branch_slug}
"""


class FakeRunner:
    quiet = True

    def __init__(self, *, plan_returncode: int = 0, fail_on_rollout: bool = False, timeout_on: str | None = None) -> None:
        self.plan_returncode = plan_returncode
        self.fail_on_rollout = fail_on_rollout
        self.timeout_on = timeout_on
        self.calls: list[tuple[list[str], dict[str, object]]] = []

    def __call__(self, args: list[str], **kwargs: object) -> SimpleNamespace:
        self.calls.append((args, kwargs))
        command = " ".join(args)
        if self.timeout_on and self.timeout_on in command:
            raise subprocess.TimeoutExpired(args, kwargs.get("timeout"))
        if args[0] == "terraform" and "plan" in args:
            return SimpleNamespace(returncode=self.plan_returncode, stdout="")
        if self.fail_on_rollout and "rollout status" in command:
            return SimpleNamespace(returncode=1, stdout="")
        if args[-2:] == ["-o", "json"]:
            return SimpleNamespace(returncode=0, stdout=READY_HTTPROUTE)
        return SimpleNamespace(returncode=0, stdout="")

    @property
    def commands(self) -> list[list[str]]:
        return [call[0] for call in self.calls]


class VerifyBranchDeployTest(unittest.TestCase):
    def test_slug_validation_accepts_dns_safe_slug(self) -> None:
        self.assertEqual(verify.validate_slug("example-change"), "example-change")
        self.assertEqual(verify.validate_slug("a1"), "a1")

    def test_slug_validation_rejects_non_deterministic_or_dns_unsafe_slug(self) -> None:
        for slug in ("Example", "-example", "example-", "example_change", "a" * 57):
            with self.subTest(slug=slug):
                with self.assertRaises(argparse.ArgumentTypeError):
                    verify.validate_slug(slug)

    def test_template_rendering_substitutes_branch_and_unsuspends_flux_objects(self) -> None:
        rendered = verify.render_activation_template(TEMPLATE, branch="codex/example-change", slug="example-change")

        self.assertIn("name: branch-example-change", rendered)
        self.assertIn("branch: codex/example-change", rendered)
        self.assertEqual(rendered.count("suspend: false"), 2)
        self.assertNotIn("${", rendered)

    def test_timeout_parsing_supports_seconds_minutes_and_composites(self) -> None:
        self.assertEqual(verify.parse_duration("300").raw, "300s")
        self.assertEqual(verify.parse_duration("10m").seconds, 600)
        self.assertEqual(verify.parse_duration("1h30m5s").seconds, 5405)
        with self.assertRaises(argparse.ArgumentTypeError):
            verify.parse_duration("soon")

    def test_run_command_wraps_subprocess_timeout(self) -> None:
        config = self._config()
        runner = FakeRunner(timeout_on="rollout")

        with self.assertRaisesRegex(verify.VerificationError, "timed out"):
            verify.run_command(
                verify.kubectl(config, "-n", config.namespace, "rollout", "status", f"deployment/{config.namespace}"),
                runner=runner,
                timeout=config.timeout,
            )

    def test_acceptance_command_sequence_uses_push_terraform_apply_reconcile_assert_and_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "terraform" / "development").mkdir(parents=True)
            runner = FakeRunner(plan_returncode=2)
            config = self._config(push=True, terraform_apply=True)

            verify.run_acceptance(config, runner=runner, repo_root=root, template_text=TEMPLATE)

        commands = [" ".join(command) for command in runner.commands]
        self.assertIn("git push origin HEAD:refs/heads/codex/example-change", commands[0])
        self.assertTrue(any("terraform -chdir=" in command and " init -input=false -no-color" in command for command in commands))
        self.assertTrue(
            any("terraform -chdir=" in command and " plan -detailed-exitcode -input=false -no-color" in command for command in commands)
        )
        self.assertTrue(any("terraform -chdir=" in command and " apply -input=false -no-color -auto-approve" in command for command in commands))
        self.assertTrue(any("flux --kubeconfig /tmp/kubeconfig reconcile source git branch-example-change" in command for command in commands))
        self.assertTrue(any("rollout status deployment/whoami-example-change" in command for command in commands))
        self.assertTrue(any("delete kustomization.kustomize.toolkit.fluxcd.io/branch-whoami-example-change" in command for command in commands))
        self.assertTrue(any("wait namespace/whoami-example-change --for=delete" in command for command in commands))
        self.assertTrue(any("delete gitrepository.source.toolkit.fluxcd.io/branch-example-change" in command for command in commands))

    def test_apply_uses_rendered_activation_stdin(self) -> None:
        runner = FakeRunner()
        config = self._config()
        rendered = verify.render_activation_template(TEMPLATE, branch=config.branch, slug=config.slug)

        verify.apply_activation(config, rendered, runner=runner)

        command, kwargs = runner.calls[0]
        self.assertEqual(command, ["kubectl", "--kubeconfig", "/tmp/kubeconfig", "apply", "-f", "-"])
        self.assertEqual(kwargs["input"], rendered)

    def test_httproute_assert_requires_accepted_and_resolved_refs_on_one_parent(self) -> None:
        missing_resolved_refs = """{
          "status": {
            "parents": [
              {"conditions": [{"type": "Accepted", "status": "True"}]},
              {"conditions": [{"type": "ResolvedRefs", "status": "True"}]}
            ]
          }
        }"""

        with self.assertRaisesRegex(verify.VerificationError, "Accepted and ResolvedRefs"):
            verify.assert_httproute_ready(missing_resolved_refs, route_name="whoami-example-change")

    def test_cleanup_is_attempted_after_activation_failure_unless_keep_is_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "terraform" / "development").mkdir(parents=True)
            runner = FakeRunner(fail_on_rollout=True)

            with self.assertRaises(verify.VerificationError):
                verify.run_acceptance(self._config(), runner=runner, repo_root=root, template_text=TEMPLATE)

        commands = [" ".join(command) for command in runner.commands]
        self.assertTrue(any("delete kustomization.kustomize.toolkit.fluxcd.io/branch-whoami-example-change" in command for command in commands))
        self.assertTrue(any("delete gitrepository.source.toolkit.fluxcd.io/branch-example-change" in command for command in commands))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "terraform" / "development").mkdir(parents=True)
            runner = FakeRunner(fail_on_rollout=True)

            with self.assertRaises(verify.VerificationError):
                verify.run_acceptance(self._config(keep=True), runner=runner, repo_root=root, template_text=TEMPLATE)

        commands = [" ".join(command) for command in runner.commands]
        self.assertFalse(any("delete kustomization.kustomize.toolkit.fluxcd.io" in command for command in commands))

    def test_readme_and_runbook_examples_reference_real_cli_flags(self) -> None:
        parser = verify.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }
        text = (REPO_ROOT / "tools/development/README.md").read_text(encoding="utf-8")
        text += "\n"
        text += (REPO_ROOT / "docs/runbooks/development-cluster.md").read_text(encoding="utf-8")

        for flag in ("--app", "--branch", "--slug", "--push", "--terraform-apply", "--kubeconfig", "--timeout", "--keep"):
            self.assertIn(flag, text)
            self.assertIn(flag, option_strings)

    def _config(
        self,
        *,
        push: bool = False,
        terraform_apply: bool = False,
        keep: bool = False,
    ) -> verify.AppConfig:
        return verify.AppConfig(
            app="whoami",
            branch="codex/example-change",
            slug="example-change",
            kubeconfig=Path("/tmp/kubeconfig"),
            timeout=verify.parse_duration("2m"),
            push=push,
            terraform_apply=terraform_apply,
            keep=keep,
        )


if __name__ == "__main__":
    unittest.main()
