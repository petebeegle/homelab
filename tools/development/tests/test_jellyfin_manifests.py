from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
JELLYFIN_MANIFESTS = REPO_ROOT / "kubernetes" / "apps" / "jellyfin"
JELLYFIN_VALUES = JELLYFIN_MANIFESTS / "base" / "values.yaml"
FLUX_KUSTOMIZATION = (
    REPO_ROOT / "kubernetes" / "clusters" / "production" / "apps" / "jellyfin.yaml"
)

class JellyfinManifestsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime_script_dir = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.runtime_script_dir.cleanup)

        local_kustomization = Path(cls.runtime_script_dir.name) / "jellyfin.yaml"
        local_kustomization.write_text(
            FLUX_KUSTOMIZATION.read_text(encoding="utf-8").replace(
                "  postBuild:\n",
                "  postBuild:\n"
                "    substitute:\n"
                '      cluster_domain: "lab.petebeegle.com"\n'
                '      nfs_server: "192.0.2.10"\n',
            ),
            encoding="utf-8",
        )

        rendered = subprocess.run(
            [
                "flux",
                "build",
                "kustomization",
                "app-jellyfin",
                "--path",
                str(JELLYFIN_MANIFESTS),
                "--kustomization-file",
                str(local_kustomization),
                "--dry-run",
                "--strict-substitute",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if rendered.returncode != 0:
            raise AssertionError(rendered.stderr)

        helm_rendered = subprocess.run(
            [
                "helm",
                "template",
                "jellyfin",
                "jellyfin/jellyfin",
                "--version",
                "3.2.0",
                "--values",
                str(JELLYFIN_VALUES),
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if helm_rendered.returncode != 0:
            raise AssertionError(helm_rendered.stderr)

        cls.rendered_manifests = rendered.stdout
        cls.helm_manifests = helm_rendered.stdout

    def test_flux_still_substitutes_neighboring_application_values(self) -> None:
        self.assertNotIn("${cluster_domain}", self.rendered_manifests)
        self.assertNotIn("${nfs_server}", self.rendered_manifests)
        self.assertIn("https://jellyfin.lab.petebeegle.com", self.rendered_manifests)
        self.assertIn("server: 192.0.2.10", self.rendered_manifests)

    def test_helm_actions_use_client_side_apply_without_force(self) -> None:
        self.assertEqual(
            self.rendered_manifests.count("serverSideApply: disabled"),
            2,
        )
        self.assertNotIn("force: true", self.rendered_manifests)

    def test_recreate_strategy_explicitly_clears_rolling_update(self) -> None:
        self.assertIn(
            "  strategy:\n    rollingUpdate: null\n    type: Recreate\n",
            self.helm_manifests,
        )

    def test_config_lives_only_on_the_local_volume(self) -> None:
        # docs/decisions.md (storage): the one-time NFS-to-local migration is finished and its leftovers are gone.
        self.assertIn("claimName: jellyfin-config-local-v1", self.helm_manifests)
        self.assertIn("name: install-sso-auth", self.helm_manifests)
        self.assertIn("gpu.intel.com/i915: 1", self.helm_manifests)
        for leftover in ("migrate-config", "jellyfin-config-v2", "jellyfin-config-migration", "config-source"):
            self.assertNotIn(leftover, self.helm_manifests)
            self.assertNotIn(leftover, self.rendered_manifests)
        self.assertFalse((JELLYFIN_MANIFESTS / "migrate-config.sh").exists())


if __name__ == "__main__":
    unittest.main()
