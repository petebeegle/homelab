"""Jobs on the homelab-dev runner get their development-cluster kubeconfig from one shared
action. In the development cluster it is built from the runner pod's ServiceAccount; once the
runner runs in production (#522 A0) it comes from a mounted file named by DEV_CLUSTER_KUBECONFIG."""
from __future__ import annotations

import os
import re
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ACTION = REPO_ROOT / ".github" / "actions" / "dev-kubeconfig" / "action.yml"
WORKFLOWS = [REPO_ROOT / ".github" / "workflows" / name for name in ("dev-smoke.yml", "dev-cleanup.yml")]
DEV_RUNNER = REPO_ROOT / "kubernetes" / "apps" / "dev-runner"


def action_script() -> str:
    text = ACTION.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^      run: \|\n(.*?)(?=^\S|\Z)", text)
    assert match, "dev-kubeconfig action has no run script"
    return textwrap.dedent(match.group(1))


class DevKubeconfigActionTest(unittest.TestCase):
    def run_action(self, env: dict[str, str]) -> tuple[Path, Path, list[str]]:
        tmp = Path(tempfile.mkdtemp())
        runner_temp = tmp / "runner-temp"
        runner_temp.mkdir()
        github_env = tmp / "github-env"
        github_env.write_text("", encoding="utf-8")
        bin_dir = tmp / "bin"
        bin_dir.mkdir()
        calls = tmp / "kubectl-calls"
        fake = bin_dir / "kubectl"
        fake.write_text(f'#!/bin/sh\necho "$*" >> "{calls}"\n', encoding="utf-8")
        fake.chmod(0o755)
        sa = tmp / "sa"
        sa.mkdir()
        (sa / "token").write_text("sa-token", encoding="utf-8")
        (sa / "ca.crt").write_text("ca", encoding="utf-8")
        script = action_script().replace("/var/run/secrets/kubernetes.io/serviceaccount", str(sa))
        full_env = {
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "RUNNER_TEMP": str(runner_temp),
            "GITHUB_ENV": str(github_env),
            **env,
        }
        subprocess.run(["bash", "-c", script], env=full_env, check=True, capture_output=True, text=True)
        logged = calls.read_text(encoding="utf-8").splitlines() if calls.exists() else []
        return runner_temp / "kubeconfig", github_env, logged

    def test_uses_the_mounted_kubeconfig_when_present(self) -> None:
        mounted = Path(tempfile.mkdtemp()) / "kubeconfig"
        mounted.write_text("apiVersion: v1\nkind: Config\n", encoding="utf-8")
        kubeconfig, github_env, kubectl_calls = self.run_action({"DEV_CLUSTER_KUBECONFIG": str(mounted)})
        self.assertEqual(kubeconfig.read_text(encoding="utf-8"), "apiVersion: v1\nkind: Config\n")
        self.assertEqual(stat.S_IMODE(kubeconfig.stat().st_mode), 0o600)
        self.assertIn(f"KUBECONFIG={kubeconfig}", github_env.read_text(encoding="utf-8"))
        self.assertEqual(kubectl_calls, [], "must not fall back to the pod ServiceAccount")

    def test_builds_from_the_pod_service_account_otherwise(self) -> None:
        kubeconfig, github_env, kubectl_calls = self.run_action({})
        self.assertTrue(any("set-cluster dev --server=https://kubernetes.default.svc" in c for c in kubectl_calls))
        self.assertTrue(any("set-credentials runner --token=sa-token" in c for c in kubectl_calls))
        self.assertIn(f"KUBECONFIG={kubeconfig}", github_env.read_text(encoding="utf-8"))

    def test_fails_when_the_named_kubeconfig_is_missing(self) -> None:
        # A production runner whose mount is broken must not silently use its own (RBAC-less) account.
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_action({"DEV_CLUSTER_KUBECONFIG": "/nonexistent/kubeconfig"})

    def test_every_dev_runner_workflow_uses_the_action(self) -> None:
        for workflow in WORKFLOWS:
            text = workflow.read_text(encoding="utf-8")
            self.assertIn("uses: ./.github/actions/dev-kubeconfig", text, workflow.name)
            self.assertNotIn("set-credentials runner", text, f"{workflow.name} still builds its own kubeconfig")


class DevRunnerTokenTest(unittest.TestCase):
    def test_a_long_lived_token_exists_for_the_dev_runner_account(self) -> None:
        token = (DEV_RUNNER / "token.yaml").read_text(encoding="utf-8")
        self.assertRegex(token, r"(?m)^type: kubernetes\.io/service-account-token$")
        self.assertRegex(token, r"(?m)^    kubernetes\.io/service-account\.name: dev-runner$")
        self.assertRegex(token, r"(?m)^  namespace: dev-runner$")
        self.assertNotRegex(token, r"(?m)^(data|stringData):", "Kubernetes fills the token; the repo holds none")
        self.assertIn("- token.yaml", (DEV_RUNNER / "kustomization.yaml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
