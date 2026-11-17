"""The `Flux render` check (#522 part B): every Flux Kustomization and HelmRelease that
production runs is built and templated on each PR, without a cluster."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"
SETUP_FLUX = REPO_ROOT / ".github" / "actions" / "setup-flux" / "action.yml"
REQUIREMENTS = REPO_ROOT / "tools" / "ci" / "flux-local" / "requirements.txt"
RULESET = REPO_ROOT / ".github" / "rulesets" / "main-required-checks.json"


def job(text: str, name: str) -> str:
    match = re.search(rf"(?ms)^  {re.escape(name)}:\n(.*?)(?=^  \S|\Z)", text)
    assert match, f"ci.yml has no job {name!r}"
    return match.group(1)


class FluxRenderCheckTest(unittest.TestCase):
    def test_ci_has_a_flux_render_job_that_templates_production_with_helm(self) -> None:
        body = job(CI.read_text(encoding="utf-8"), "flux-render")
        self.assertRegex(body, r"(?m)^    name: Flux render$")
        self.assertIn("flux-local test --enable-helm --all-namespaces --path kubernetes/clusters/production", body)

    def test_tools_are_pinned_so_renovate_can_bump_them(self) -> None:
        body = job(CI.read_text(encoding="utf-8"), "flux-render")
        self.assertIn(f"pip install --requirement {REQUIREMENTS.relative_to(REPO_ROOT)}", body)
        self.assertRegex(REQUIREMENTS.read_text(encoding="utf-8"), r"(?m)^flux-local==\d+\.\d+\.\d+$")
        self.assertRegex(body, r'KUSTOMIZE_VERSION: "\d+\.\d+\.\d+"')
        self.assertIn("sha256sum -c", body, "kustomize download must be checksum-verified")
        self.assertIn("uses: ./.github/actions/setup-flux", body)

    def test_flux_cli_install_is_shared_not_copied(self) -> None:
        ci = CI.read_text(encoding="utf-8")
        self.assertIn("sha256sum -c", SETUP_FLUX.read_text(encoding="utf-8"))
        self.assertEqual(ci.count("uses: ./.github/actions/setup-flux"), 2, "Kubernetes and Flux render jobs")
        self.assertNotIn("flux2/releases/download", ci)

    def test_flux_render_is_recorded_as_a_required_check(self) -> None:
        ruleset = json.loads(RULESET.read_text(encoding="utf-8"))
        checks = ruleset["rules"][0]["parameters"]["required_status_checks"]
        self.assertIn({"context": "Flux render", "integration_id": 15368}, checks)

    def test_remote_kustomize_resources_name_their_scheme(self) -> None:
        # `flux build` (used by flux-local) treats a schemeless "github.com/..." resource as a local path.
        offenders = []
        for path in sorted((REPO_ROOT / "kubernetes").rglob("kustomization.yaml")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if re.match(r"^\s*-\s*(github\.com|gitlab\.com|bitbucket\.org)/", line):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}: {line.strip()}")
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
