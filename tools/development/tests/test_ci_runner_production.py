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

    def test_uses_the_same_runner_image_as_development(self) -> None:
        image = re.compile(r"(?m)^\s+image: (ghcr\.io/petebeegle/homelab-dev-runner\S*)$")
        dev = image.search(read(REPO_ROOT / "kubernetes" / "apps" / "dev-runner" / "app.yaml"))
        prod = image.search(self.release)
        self.assertIsNotNone(prod)
        self.assertEqual(prod.group(1), dev.group(1))

    def test_credentials_come_from_the_cluster_production_vault(self) -> None:
        items = read(APP / "onepassword-items.yaml")
        self.assertIn(f'itemPath: "vaults/{PROD_VAULT}/items/github_arc"', items)
        self.assertIn(f'itemPath: "vaults/{PROD_VAULT}/items/dev-runner-kubeconfig"', items)
        secret = re.search(r"(?m)^    githubConfigSecret: (\S+)$", self.release).group(1)
        self.assertRegex(items, rf"(?m)^  name: {re.escape(secret)}$")
        self.assertRegex(items, r"(?m)^  name: dev-runner-kubeconfig$")


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
