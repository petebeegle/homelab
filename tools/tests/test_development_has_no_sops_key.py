"""Development holds no SOPS key.

Every SOPS file in the repo is encrypted to one age key, so a cluster holding it
can read every production secret. Development reads its secrets from its own
1Password vault instead: nothing it applies may need SOPS decryption, and its
bootstrap must not install the key.
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEVELOPMENT = REPO_ROOT / "kubernetes/clusters/development"


def documents(text: str) -> list[str]:
    return [d for d in re.split(r"(?m)^---\s*$", text) if d.strip()]


def flux_kustomization_paths() -> dict[str, str]:
    """name -> spec.path of every Flux Kustomization development defines."""
    paths: dict[str, str] = {}
    for file in sorted(DEVELOPMENT.rglob("*.yaml")):
        if file.name == "gotk-components.yaml":
            continue
        for doc in documents(file.read_text(encoding="utf-8")):
            if re.search(r"(?m)^apiVersion: kustomize\.toolkit\.fluxcd\.io/", doc) and re.search(r"(?m)^kind: Kustomization$", doc):
                name = re.search(r"(?m)^  name: (\S+)", doc).group(1)
                paths[name] = re.search(r"(?m)^  path: (\S+)", doc).group(1)
    return paths


class DevelopmentHasNoSopsKeyTest(unittest.TestCase):
    def test_no_development_kustomization_decrypts(self) -> None:
        offenders = [
            str(file.relative_to(REPO_ROOT))
            for file in DEVELOPMENT.rglob("*.yaml")
            if file.name != "gotk-components.yaml"
            and re.search(r"(?m)^\s*decryption:|sops-age", file.read_text(encoding="utf-8"))
        ]
        self.assertEqual(offenders, [], "development must not decrypt SOPS")

    def test_nothing_development_applies_is_sops_encrypted(self) -> None:
        paths = flux_kustomization_paths()
        self.assertIn("cert-manager", paths)
        encrypted: list[str] = []
        for name, path in sorted(paths.items()):
            result = subprocess.run(
                ["kubectl", "kustomize", path], cwd=REPO_ROOT, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, f"kubectl kustomize {path} ({name}) failed: {result.stderr}")
            for doc in documents(result.stdout):
                if re.search(r"(?m)^sops:", doc):
                    kind = re.search(r"(?m)^kind: (\S+)", doc).group(1)
                    object_name = re.search(r"(?m)^  name: (\S+)", doc).group(1)
                    encrypted.append(f"{name}: {kind}/{object_name}")
        self.assertEqual(encrypted, [], "development would apply SOPS-encrypted objects it cannot (and must not) decrypt")

    def test_bootstrap_installs_only_the_1password_token(self) -> None:
        main = (REPO_ROOT / "terraform/development/main.tf").read_text(encoding="utf-8")
        self.assertRegex(main, r'FLUX_BOOTSTRAP_SECRET_PROVIDER\s*=\s*"onepassword"')


if __name__ == "__main__":
    unittest.main()
