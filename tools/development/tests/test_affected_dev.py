"""affected_dev: which development Flux Kustomizations a PR changes, judged by rendered output."""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import affected_dev  # noqa: E402


def need_kubectl() -> None:
    if shutil.which("kubectl") is None:
        if os.environ.get("GITHUB_ACTIONS"):
            raise AssertionError("kubectl is required in CI")
        raise unittest.SkipTest("kubectl not installed")


FLUX_KS = """\
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: {name}
  namespace: flux-system
spec:
  interval: 2m
  path: ./{path}
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
"""

CONFIGMAP = """\
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}
  namespace: default
data:
  value: "{value}"
"""


def write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text), encoding="utf-8")


def kustomization(*resources: str) -> str:
    return "apiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n" + "".join(
        f"  - {r}\n" for r in resources
    )


def make_tree(root: Path) -> None:
    """A development cluster with two infra Kustomizations; `app` reuses a shared base."""
    cluster = "kubernetes/clusters/development"
    write(root, f"{cluster}/kustomization.yaml", kustomization("flux-system", "cluster-vars.yaml", "infra"))
    write(root, f"{cluster}/flux-system/kustomization.yaml", kustomization("gotk-components.yaml"))
    write(root, f"{cluster}/flux-system/gotk-components.yaml", CONFIGMAP.format(name="gotk", value="v1"))
    write(root, f"{cluster}/cluster-vars.yaml", CONFIGMAP.format(name="cluster-vars", value="dev"))
    write(root, f"{cluster}/infra/kustomization.yaml", kustomization("cilium.yaml", "app.yaml"))
    write(root, f"{cluster}/infra/cilium.yaml", FLUX_KS.format(name="cilium", path="kubernetes/infra/cilium"))
    write(root, f"{cluster}/infra/app.yaml", FLUX_KS.format(name="app", path="kubernetes/apps/app/development"))
    write(root, "kubernetes/infra/cilium/kustomization.yaml", kustomization("cm.yaml"))
    write(root, "kubernetes/infra/cilium/cm.yaml", CONFIGMAP.format(name="cilium", value="1.0"))
    write(root, "kubernetes/apps/app/base/kustomization.yaml", kustomization("cm.yaml"))
    write(root, "kubernetes/apps/app/base/cm.yaml", CONFIGMAP.format(name="app", value="1"))
    write(root, "kubernetes/apps/app/development/kustomization.yaml", kustomization("../base"))
    write(root, "kubernetes/infra/prod-only/kustomization.yaml", kustomization("cm.yaml"))
    write(root, "kubernetes/infra/prod-only/cm.yaml", CONFIGMAP.format(name="prod-only", value="1"))


class AffectedDevTest(unittest.TestCase):
    def setUp(self) -> None:
        need_kubectl()
        tmp = Path(tempfile.mkdtemp())
        self.base, self.head = tmp / "base", tmp / "head"
        make_tree(self.base)
        make_tree(self.head)

    def result(self, changed: list[str]) -> affected_dev.Result:
        return affected_dev.affected(self.base, self.head, changed)

    def test_nothing_rendered_differently_affects_nothing(self) -> None:
        write(self.head, "kubernetes/infra/prod-only/cm.yaml", CONFIGMAP.format(name="prod-only", value="2"))
        result = self.result(["kubernetes/infra/prod-only/cm.yaml"])
        self.assertEqual(result.affected, [])
        self.assertIsNone(result.blocked)

    def test_a_change_in_a_kustomization_path_affects_it(self) -> None:
        write(self.head, "kubernetes/infra/cilium/cm.yaml", CONFIGMAP.format(name="cilium", value="1.1"))
        self.assertEqual(self.result(["kubernetes/infra/cilium/cm.yaml"]).affected, ["cilium"])

    def test_a_change_reached_through_a_shared_base_is_found(self) -> None:
        write(self.head, "kubernetes/apps/app/base/cm.yaml", CONFIGMAP.format(name="app", value="2"))
        self.assertEqual(self.result(["kubernetes/apps/app/base/cm.yaml"]).affected, ["app"])

    def test_a_change_to_the_flux_kustomization_spec_affects_it(self) -> None:
        write(
            self.head,
            "kubernetes/clusters/development/infra/cilium.yaml",
            FLUX_KS.format(name="cilium", path="kubernetes/infra/cilium").replace("2m", "5m"),
        )
        self.assertEqual(self.result(["kubernetes/clusters/development/infra/cilium.yaml"]).affected, ["cilium"])

    def test_a_kustomization_only_the_pr_adds_is_affected(self) -> None:
        write(self.head, "kubernetes/clusters/development/infra/kustomization.yaml", kustomization("cilium.yaml", "app.yaml", "new.yaml"))
        write(self.head, "kubernetes/clusters/development/infra/new.yaml", FLUX_KS.format(name="new", path="kubernetes/infra/prod-only"))
        self.assertEqual(self.result(["kubernetes/clusters/development/infra/new.yaml"]).affected, ["new"])

    def test_flux_itself_and_cluster_vars_are_refused(self) -> None:
        for path in (
            "kubernetes/clusters/development/flux-system/gotk-components.yaml",
            "kubernetes/clusters/development/cluster-vars.yaml",
        ):
            result = self.result([path])
            self.assertIsNotNone(result.blocked, path)
            self.assertIn(path, result.blocked)


if __name__ == "__main__":
    unittest.main()
