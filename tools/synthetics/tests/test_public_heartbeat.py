from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "synthetics"))

import public_heartbeat as heartbeat  # noqa: E402

TUNNEL = REPO_ROOT / "kubernetes" / "apps" / "cloudflare-tunnels" / "deployment.yaml"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "public-heartbeat.yml"

FOUNDRY = heartbeat.Target(host="foundry.example.com", path="/", status=200, body_regex="Foundry Virtual Tabletop")


def tunnel_hostnames() -> set[str]:
    return set(re.findall(r"(?m)^\s+- hostname: (\S+)$", TUNNEL.read_text(encoding="utf-8")))


class TargetsTest(unittest.TestCase):
    def test_every_public_hostname_is_checked_from_outside(self) -> None:
        # A host added to the tunnel without a target here would go unwatched from outside.
        hosts = tunnel_hostnames()
        self.assertTrue(hosts, "no hostnames parsed from the cloudflared config")
        self.assertEqual({t.host for t in heartbeat.load_targets()}, hosts)

    def test_targets_expect_an_answer_from_the_app_not_from_cloudflare(self) -> None:
        for target in heartbeat.load_targets():
            # 5xx is how Cloudflare reports a dead tunnel or origin (502, 530), so it never means up.
            self.assertLess(target.status, 500, target.host)
            self.assertTrue(target.body_regex, f"{target.host}: a status alone could come from Cloudflare")


class CheckTest(unittest.TestCase):
    def test_a_matching_answer_passes(self) -> None:
        self.assertEqual(heartbeat.check([FOUNDRY], fetch=lambda url: (200, "<title>Foundry Virtual Tabletop</title>")), [])

    def test_a_cloudflare_error_fails_and_names_the_host(self) -> None:
        failures = heartbeat.check([FOUNDRY], fetch=lambda url: (530, "error code: 1033"), delay=0)
        self.assertEqual(len(failures), 1)
        self.assertIn("https://foundry.example.com/", failures[0])
        self.assertIn("530", failures[0])

    def test_the_wrong_body_fails(self) -> None:
        failures = heartbeat.check([FOUNDRY], fetch=lambda url: (200, "404 page not found"), delay=0)
        self.assertEqual(len(failures), 1)
        self.assertIn("Foundry Virtual Tabletop", failures[0])

    def test_an_unreachable_host_fails_instead_of_raising(self) -> None:
        def unreachable(url: str) -> tuple[int, str]:
            raise OSError("Name or service not known")

        failures = heartbeat.check([FOUNDRY], fetch=unreachable, delay=0)
        self.assertEqual(len(failures), 1)
        self.assertIn("Name or service not known", failures[0])

    def test_an_expected_client_error_passes(self) -> None:
        # onboard's routed paths answer 400 without an OAuth code; that 400 is the app's.
        target = heartbeat.Target(host="onboard.example.com", path="/oauth/callback", status=400, body_regex="oauth")
        self.assertEqual(heartbeat.check([target], fetch=lambda url: (400, '{"error":"missing discord oauth code"}')), [])

    def test_a_blip_is_retried_before_it_fails(self) -> None:
        answers = iter([(502, "bad gateway"), (200, "Foundry Virtual Tabletop")])
        self.assertEqual(heartbeat.check([FOUNDRY], fetch=lambda url: next(answers), attempts=2, delay=0), [])


class WorkflowTest(unittest.TestCase):
    def test_runs_on_a_schedule_on_a_github_hosted_runner(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        head = text.split("\njobs:\n", 1)[0]
        self.assertRegex(head, r"(?m)^    - cron: '")
        self.assertIn("workflow_dispatch:", head)
        for forbidden in ("pull_request", "push:"):
            self.assertNotIn(forbidden, head)
        # Outside the homelab, so it still runs when production is down.
        self.assertRegex(text, r"(?m)^    runs-on: ubuntu-latest$")
        self.assertRegex(text, r"(?m)^permissions:\n  contents: read$")
        self.assertIn("python3 tools/synthetics/public_heartbeat.py", text)


if __name__ == "__main__":
    unittest.main()
