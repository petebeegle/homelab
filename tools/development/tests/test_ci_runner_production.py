"""The CI runner in production (#522 A0). It tests the development cluster from outside it, holds
nothing that can change production, and can only reach DNS, GitHub, npm, and development's API
server and internal gateway."""
from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
APP = REPO_ROOT / "kubernetes" / "apps" / "ci-runner"
PROD = REPO_ROOT / "kubernetes" / "clusters" / "production"
PROD_VAULT = "ydtsmbjna24k5of6ga23boczuu"  # "cluster production"
DEV_API = "192.168.30.170/32"
DEV_GATEWAY = "192.168.30.225/32"


def read(path: Path) -> str:
    assert path.exists(), f"missing: {path.relative_to(REPO_ROOT)}"
    return path.read_text(encoding="utf-8")


class ProductionActivationTest(unittest.TestCase):
    def test_production_runs_the_shared_arc_controller(self) -> None:
        self.assertRegex(read(PROD / "infra" / "kustomization.yaml"), r"(?m)^  - arc\.yaml$")
        arc = read(PROD / "infra" / "arc.yaml")
        self.assertIn("path: ./kubernetes/infra/controllers/arc", arc)

    def test_production_activates_the_runner_after_arc_and_the_operator(self) -> None:
        self.assertRegex(read(PROD / "apps" / "kustomization.yaml"), r"(?m)^  - ci-runner\.yaml$")
        flux = read(PROD / "apps" / "ci-runner.yaml")
        self.assertIn("path: ./kubernetes/apps/ci-runner", flux)
        self.assertRegex(flux, r"(?s)dependsOn:.*- name: arc")
        self.assertRegex(flux, r"(?s)dependsOn:.*- name: onepassword-operator")


class RunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.release = read(APP / "app.yaml")

    def test_one_ephemeral_runner_at_a_time(self) -> None:
        self.assertRegex(self.release, r"(?m)^    minRunners: 0$")
        self.assertRegex(self.release, r"(?m)^    maxRunners: 1$")

    def test_runner_pod_has_no_production_credentials(self) -> None:
        self.assertRegex(self.release, r"(?m)^        automountServiceAccountToken: false$")
        self.assertNotIn("serviceAccountName:", self.release)
        for path in APP.glob("*.yaml"):
            self.assertNotRegex(read(path), r"(?m)^kind: (Cluster)?Role(Binding)?$", f"{path.name} grants RBAC")

    def test_reaches_development_with_the_mounted_dev_runner_kubeconfig(self) -> None:
        self.assertRegex(
            self.release,
            r"(?m)^              - name: DEV_CLUSTER_KUBECONFIG\n                value: /var/run/dev-cluster/kubeconfig$",
        )
        self.assertRegex(self.release, r"(?m)^                mountPath: /var/run/dev-cluster$")
        self.assertRegex(self.release, r"(?m)^              secretName: dev-runner-kubeconfig$")
        # The Secret volume is root-owned with mode 0440: the runner user (uid 1002) reads it only
        # through its group, so the pod's fsGroup must be the runner's group.
        uid = re.search(r"(?m)^          runAsUser: (\d+)$", self.release).group(1)
        self.assertRegex(self.release, rf"(?m)^          fsGroup: {uid}$")
        self.assertRegex(self.release, r"(?m)^              defaultMode: 0440$")

    def test_uses_the_runner_image_this_repo_builds(self) -> None:
        self.assertRegex(self.release, r"(?m)^\s+image: ghcr\.io/petebeegle/homelab-dev-runner\S*$")
        self.assertIn("homelab-dev-runner", read(REPO_ROOT / ".github" / "workflows" / "runner-image.yml"))

    def test_credentials_come_from_the_cluster_production_vault(self) -> None:
        items = read(APP / "onepassword-items.yaml")
        self.assertIn(f'itemPath: "vaults/{PROD_VAULT}/items/github_arc"', items)
        self.assertIn(f'itemPath: "vaults/{PROD_VAULT}/items/dev-runner-kubeconfig"', items)
        secret = re.search(r"(?m)^    githubConfigSecret: (\S+)$", self.release).group(1)
        self.assertRegex(items, rf"(?m)^  name: {re.escape(secret)}$")
        self.assertRegex(items, r"(?m)^  name: dev-runner-kubeconfig$")


class CutoverTest(unittest.TestCase):
    """After cutover (#522 A0 step 4) production's runner is the only homelab-dev runner."""

    def test_production_registers_the_name_the_workflows_use(self) -> None:
        name = re.search(r"(?m)^    runnerScaleSetName: (\S+)$", read(APP / "app.yaml")).group(1)
        self.assertEqual(name, "homelab-dev")
        workflows = sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))
        self_hosted = {
            label
            for path in workflows
            for label in re.findall(r"(?m)^    runs-on: (\S+)$", read(path))
            if not label.startswith(("ubuntu-", "windows-", "macos-"))
        }
        self.assertEqual(self_hosted, {name})

    def test_development_no_longer_runs_a_runner(self) -> None:
        dev = REPO_ROOT / "kubernetes" / "apps" / "dev-runner"
        for path in dev.glob("*.yaml"):
            text = read(path)
            self.assertNotRegex(text, r"(?m)^kind: (HelmRelease|OnePasswordItem)$", f"{path.name} still runs a runner")
        # What stays in development: the account the production runner acts as.
        kustomization = read(dev / "kustomization.yaml")
        for kept in ("namespace.yaml", "rbac.yaml", "token.yaml"):
            self.assertIn(f"- {kept}", kustomization)


    def test_development_does_not_run_the_runner_controller(self) -> None:
        dev = REPO_ROOT / "kubernetes" / "clusters" / "development"
        self.assertNotRegex(read(dev / "infra" / "kustomization.yaml"), r"(?m)^  - arc\.yaml$")
        self.assertFalse((dev / "infra" / "arc.yaml").exists())
        self.assertNotRegex(read(dev / "apps" / "dev-runner.yaml"), r"(?m)^    - name: (arc|onepassword-operator)$")


class EgressPolicyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = read(APP / "network-policy.yaml")

    def test_denies_by_default_in_both_directions_with_no_ingress(self) -> None:
        self.assertRegex(self.policy, r"(?m)^kind: CiliumNetworkPolicy$")
        self.assertRegex(self.policy, r"(?m)^  endpointSelector: \{\}$")
        self.assertRegex(self.policy, r"(?m)^  enableDefaultDeny:\n    egress: true\n    ingress: true$")
        self.assertNotRegex(self.policy, r"(?m)^  ingress:")

    def test_only_development_addresses_are_reachable_by_ip(self) -> None:
        cidrs = set(re.findall(r"(?m)^\s+- (\d+\.\d+\.\d+\.\d+/\d+)$", self.policy))
        self.assertEqual(cidrs, {DEV_API, DEV_GATEWAY})
        self.assertNotRegex(self.policy, r"(?m)^\s+-?\s*toEntities:|0\.0\.0\.0/0")

    def test_dns_goes_through_the_proxy_so_fqdn_rules_apply(self) -> None:
        self.assertRegex(self.policy, r"k8s-app: kube-dns")
        self.assertRegex(self.policy, r'(?s)rules:\n\s+dns:\n\s+- matchPattern: "\*"')

    def test_names_only_github_and_npm(self) -> None:
        names = re.findall(r'(?m)^\s+- match(?:Name|Pattern): "?([^"\s]+)"?$', self.policy)
        names = [n for n in names if n != "*"]
        allowed_suffixes = ("github.com", "githubusercontent.com", "blob.core.windows.net", "npmjs.org")
        self.assertTrue(names)
        for name in names:
            self.assertTrue(name.endswith(allowed_suffixes), f"unexpected FQDN {name}")


if __name__ == "__main__":
    unittest.main()
