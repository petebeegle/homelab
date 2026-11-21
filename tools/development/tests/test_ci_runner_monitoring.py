"""Production watches the CI runner and the development cluster (#522 A0): alerts on the runner
controller and listener, and a probe of development that alerts when it stops succeeding."""
from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ALERTING = REPO_ROOT / "kubernetes" / "infra" / "monitoring" / "grafana" / "alerting"
RULES = ALERTING / "alert-rules-ci-runner.yaml"
APP = REPO_ROOT / "kubernetes" / "apps" / "ci-runner"
PROBE = APP / "dev-probe.yaml"


def read(path: Path) -> str:
    assert path.exists(), f"missing: {path.relative_to(REPO_ROOT)}"
    return path.read_text(encoding="utf-8")


def rule(text: str, uid: str) -> str:
    match = re.search(rf"(?ms)^    - uid: {re.escape(uid)}\n(.*?)(?=^    - uid: |\Z)", text)
    assert match, f"no alert rule {uid}"
    return match.group(1)


class RunnerAlertsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rules = read(RULES)

    def test_rule_group_is_provisioned(self) -> None:
        self.assertRegex(read(ALERTING / "kustomization.yaml"), r"(?m)^  - alert-rules-ci-runner\.yaml$")
        self.assertRegex(self.rules, r"(?m)^kind: GrafanaAlertRuleGroup$")

    def test_alerts_when_the_runner_controller_is_unavailable(self) -> None:
        body = rule(self.rules, "ci-runner-controller-unavailable")
        self.assertIn('exported_namespace="arc-systems",deployment="arc-gha-rs-controller"', body)
        self.assertIn("absent(", body)
        self.assertRegex(body, r"(?m)^      noDataState: Alerting$")

    def test_alerts_when_the_homelab_dev_listener_is_not_running(self) -> None:
        body = rule(self.rules, "ci-runner-listener-down")
        self.assertIn('pod=~"homelab-dev-.*-listener"', body)
        self.assertIn('phase="Running"', body)
        self.assertIn("or vector(0)", body)

    def test_alerts_when_no_development_probe_succeeded_recently(self) -> None:
        body = rule(self.rules, "development-cluster-unhealthy")
        self.assertIn('{namespace="ci-runner", app="dev-probe"} |= "DEV_PROBE" | logfmt | status="ok"', body)
        self.assertRegex(body, r"(?m)^      noDataState: Alerting$", "no successful probe lines must alert")
        self.assertRegex(body, r"datasourceUid: loki")

    def test_every_rule_points_at_the_runbook(self) -> None:
        for uid in ("ci-runner-controller-unavailable", "ci-runner-listener-down", "development-cluster-unhealthy"):
            self.assertIn("docs/runbooks/ci-runner.md", rule(self.rules, uid))


class DevProbeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.probe = read(PROBE)

    def test_runs_in_the_fenced_namespace_every_ten_minutes(self) -> None:
        self.assertRegex(read(APP / "kustomization.yaml"), r"(?m)^  - dev-probe\.yaml$")
        self.assertRegex(self.probe, r"(?m)^  namespace: ci-runner$")
        self.assertRegex(self.probe, r'(?m)^  schedule: "\*/10 \* \* \* \*"$')
        self.assertRegex(self.probe, r"(?m)^  concurrencyPolicy: Forbid$")
        self.assertRegex(self.probe, r"(?m)^            app: dev-probe$")

    def test_has_no_production_credentials_and_uses_the_dev_runner_kubeconfig(self) -> None:
        self.assertRegex(self.probe, r"(?m)^          automountServiceAccountToken: false$")
        self.assertRegex(self.probe, r"(?m)^                secretName: dev-runner-kubeconfig$")
        self.assertRegex(self.probe, r"(?m)^            fsGroup: 1002$")

    def test_checks_api_flux_and_a_route_and_logs_one_summary_line(self) -> None:
        self.assertIn("get --raw /readyz", self.probe)
        self.assertIn("kustomizations.kustomize.toolkit.fluxcd.io", self.probe)
        self.assertIn("https://whoami.dev.lab.petebeegle.com/", self.probe)
        self.assertIn("DEV_PROBE status=", self.probe)

    def test_uses_the_runner_image(self) -> None:
        image = re.compile(r"(?m)^\s+image: (\S+)$")
        self.assertEqual(image.search(self.probe).group(1), image.search(read(APP / "app.yaml")).group(1))


if __name__ == "__main__":
    unittest.main()
