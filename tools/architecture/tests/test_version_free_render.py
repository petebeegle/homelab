"""The generated architecture doc must not carry dependency versions.

Renovate bumps versions in manifests but cannot regenerate docs/architecture.md, so
any version string in the doc turns every such bump into a failing pre-commit check.
"""
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ARCHITECTURE_ROOT = REPO_ROOT / "tools" / "architecture"
if str(ARCHITECTURE_ROOT) not in sys.path:
    sys.path.insert(0, str(ARCHITECTURE_ROOT))

import render
from architecture.kubernetes import kustomize_resources


class VersionFreeRenderTest(unittest.TestCase):
    def kustomization(self, *resources: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "kustomization.yaml"
            body = "".join(f"  - {item}\n" for item in resources)
            path.write_text(f"apiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n{body}", encoding="utf-8")
            return kustomize_resources(path)

    def test_remote_ref_query_is_replaced(self) -> None:
        self.assertEqual(
            self.kustomization(
                "https://github.com/kubernetes-csi/external-snapshotter//client/config/crd?ref=v8.6.0",
                "github.com/rancher/local-path-provisioner/deploy?ref=v0.0.37",
            ),
            [
                "https://github.com/kubernetes-csi/external-snapshotter//client/config/crd?ref=<ref>",
                "github.com/rancher/local-path-provisioner/deploy?ref=<ref>",
            ],
        )

    def test_raw_githubusercontent_ref_segment_is_replaced(self) -> None:
        self.assertEqual(
            self.kustomization(
                "https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v1.5.1/config/crd/standard/x.yaml"
            ),
            ["https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/<ref>/config/crd/standard/x.yaml"],
        )

    def test_local_resources_are_unchanged(self) -> None:
        self.assertEqual(self.kustomization("app.yaml", "../base", "grafana"), ["app.yaml", "../base", "grafana"])

    def test_rendered_document_has_no_pinned_refs(self) -> None:
        document = render.render()
        self.assertIsNone(re.search(r"[?&]ref=(?!<ref>)", document))
        self.assertIsNone(re.search(r"raw\.githubusercontent\.com/[^/]+/[^/]+/(?!<ref>/)", document))


if __name__ == "__main__":
    unittest.main()
