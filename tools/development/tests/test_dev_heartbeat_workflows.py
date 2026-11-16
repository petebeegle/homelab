from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CLEANUP = REPO_ROOT / ".github" / "workflows" / "dev-cleanup.yml"
HEARTBEAT = REPO_ROOT / ".github" / "workflows" / "dev-heartbeat.yml"


def read(path: Path) -> str:
    assert path.exists(), f"missing: {path.relative_to(REPO_ROOT)}"
    return path.read_text(encoding="utf-8")


def triggers(text: str) -> str:
    return text.split("\njobs:\n", 1)[0]


class DevCleanupWorkflowTest(unittest.TestCase):
    def test_runs_every_30_minutes_and_on_demand_only(self) -> None:
        head = triggers(read(CLEANUP))
        self.assertRegex(head, r"(?m)^    - cron: '\*/30 \* \* \* \*'$")
        self.assertIn("workflow_dispatch:", head)
        for forbidden in ("pull_request", "pull_request_target", "push:"):
            self.assertNotIn(forbidden, head)

    def test_runs_on_the_dev_runner_and_removes_environments_older_than_3_hours(self) -> None:
        text = read(CLEANUP)
        self.assertRegex(text, r"(?m)^    runs-on: homelab-dev$")
        self.assertRegex(text, r"(?m)^    timeout-minutes: \d+$")
        self.assertIn("cleanup_pr_envs.py", text)
        self.assertIn('--older-than 3h', text)
        self.assertRegex(text, r"(?m)^permissions:\n  contents: read$")

    def test_never_overlaps_itself(self) -> None:
        head = triggers(read(CLEANUP))
        self.assertRegex(head, r"(?m)^concurrency:\n  group: dev-cleanup$")

    def test_checkout_does_not_persist_credentials(self) -> None:
        self.assertRegex(read(CLEANUP), r"(?m)^          persist-credentials: false$")


class DevHeartbeatWorkflowTest(unittest.TestCase):
    def test_runs_hourly_and_on_demand_only(self) -> None:
        head = triggers(read(HEARTBEAT))
        self.assertRegex(head, r"(?m)^    - cron: '\d+ \* \* \* \*'$")
        self.assertIn("workflow_dispatch:", head)
        for forbidden in ("pull_request", "pull_request_target", "push:"):
            self.assertNotIn(forbidden, head)

    def test_runs_on_github_hosted_so_it_survives_a_dead_dev_runner(self) -> None:
        text = read(HEARTBEAT)
        self.assertRegex(text, r"(?m)^    runs-on: ubuntu-latest$")
        self.assertNotIn("homelab-dev", text)

    def test_fails_when_dev_cleanup_has_not_succeeded_in_two_hours(self) -> None:
        text = read(HEARTBEAT)
        self.assertRegex(text, r"actions/workflows/dev-cleanup\.yml/runs\?status=success")
        self.assertIn("dev_heartbeat.py", text)
        self.assertIn("--max-age-seconds 7200", text)
        self.assertRegex(text, r"(?m)^permissions:\n  actions: read\n  contents: read$")


if __name__ == "__main__":
    unittest.main()
