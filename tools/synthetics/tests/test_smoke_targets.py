from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SPEC = REPO_ROOT / "kubernetes" / "apps" / "synthetics" / "smoke" / "routes.spec.js"
VALHEIM = REPO_ROOT / "kubernetes" / "apps" / "valheim" / "app.yaml"
SYNTHETICS = REPO_ROOT / "kubernetes" / "clusters" / "production" / "apps" / "synthetics.yaml"


class ValheimProbeTest(unittest.TestCase):
    def test_the_valheim_probe_targets_the_address_players_use(self) -> None:
        # Valheim is UDP only and has no DNS name of its own (valheim.<domain> is the gateway's
        # wildcard), so the probe names the LoadBalancer IP. Keep it in step with the HelmRelease.
        lb_ip = re.search(r"(?m)^\s+loadBalancerIP: (\S+)$", VALHEIM.read_text(encoding="utf-8"))
        self.assertIsNotNone(lb_ip)
        probe = re.search(r'const valheimAddress = "([^"]+)";', SPEC.read_text(encoding="utf-8"))
        self.assertIsNotNone(probe, "routes.spec.js has no valheimAddress")
        self.assertEqual(probe.group(1), lb_ip.group(1))

    def test_the_valheim_probe_expects_the_configured_server_name(self) -> None:
        name = re.search(r"(?m)^\s+serverName: (\S+)$", VALHEIM.read_text(encoding="utf-8"))
        self.assertIsNotNone(name)
        probe = re.search(r'const valheimServerName = "([^"]+)";', SPEC.read_text(encoding="utf-8"))
        self.assertIsNotNone(probe, "routes.spec.js has no valheimServerName")
        self.assertEqual(probe.group(1), name.group(1))

    def test_the_smoke_job_waits_for_valheim(self) -> None:
        self.assertRegex(SYNTHETICS.read_text(encoding="utf-8"), r"(?m)^    - name: app-valheim$")


if __name__ == "__main__":
    unittest.main()
