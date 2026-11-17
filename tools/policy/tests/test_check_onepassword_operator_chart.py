"""The 1Password chart check must follow the committed pins, not hardcode them.

Renovate bumps the HelmRelease chart version; a check that hardcodes the version
fails every such PR (see docs/runbooks/renovate.md).
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "tools" / "policy" / "check_onepassword_operator_chart.sh"
APP = Path("kubernetes/infra/controllers/onepassword-operator/app.yaml")
VALUES = Path("kubernetes/infra/controllers/onepassword-operator/values.yaml")

GOOD_RENDER = """\
kind: Deployment
spec:
  template:
    spec:
      containers:
        - image: 1password/onepassword-operator:{operator}
          env:
            - name: OP_SERVICE_ACCOUNT_TOKEN
            - name: POLLING_INTERVAL
              value: "3600"
          resources:
            limits:
              cpu: 500m
              memory: 256Mi
            requests:
              cpu: 50m
              memory: 64Mi
"""


class OnePasswordOperatorChartCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="onepassword-chart-")
        self.root = Path(self.temp.name) / "repo"
        self.bin = Path(self.temp.name) / "bin"
        self.bin.mkdir()
        for relative in (APP, VALUES):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((REPO_ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")
        self.helm_args = Path(self.temp.name) / "helm-args"
        self.render = Path(self.temp.name) / "render.yaml"
        self._stub("flux", "cat\n")
        self._stub("helm", f'printf "%s\\n" "$@" > "{self.helm_args}"\ncat "{self.render}"\n')

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _stub(self, name: str, body: str) -> None:
        path = self.bin / name
        path.write_text(f"#!/usr/bin/env bash\nset -euo pipefail\n{body}", encoding="utf-8")
        path.chmod(0o755)

    def _set_pins(self, chart: str, operator: str) -> None:
        app = self.root / APP
        text = app.read_text(encoding="utf-8")
        start = text.index("chart: connect")
        version_start = text.index('version: "', start) + len('version: "')
        version_end = text.index('"', version_start)
        app.write_text(text[:version_start] + chart + text[version_end:], encoding="utf-8")
        values = self.root / VALUES
        text = values.read_text(encoding="utf-8")
        version_start = text.index('  version: "') + len('  version: "')
        version_end = text.index('"', version_start)
        values.write_text(text[:version_start] + operator + text[version_end:], encoding="utf-8")

    def _run(self, render: str) -> subprocess.CompletedProcess[str]:
        self.render.write_text(render, encoding="utf-8")
        env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", ONEPASSWORD_CHART_CHECK_ROOT=str(self.root))
        return subprocess.run(["bash", str(SCRIPT)], env=env, capture_output=True, text=True, check=False)

    def test_renders_the_committed_chart_version(self) -> None:
        self._set_pins("9.8.7", "6.5.4")
        result = self._run(GOOD_RENDER.format(operator="6.5.4"))
        self.assertEqual(result.returncode, 0, result.stderr)
        args = self.helm_args.read_text(encoding="utf-8").split("\n")
        self.assertEqual(args[args.index("--version") + 1], "9.8.7")
        self.assertEqual(args[args.index("--repo") + 1], "https://1password.github.io/connect-helm-charts")

    def test_fails_when_rendered_operator_image_is_not_the_values_pin(self) -> None:
        self._set_pins("9.8.7", "6.5.4")
        result = self._run(GOOD_RENDER.format(operator="1.0.0"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pinned operator image", result.stderr)

    def test_fails_when_chart_is_not_connect(self) -> None:
        app = self.root / APP
        app.write_text(app.read_text(encoding="utf-8").replace("chart: connect", "chart: other"), encoding="utf-8")
        result = self._run(GOOD_RENDER.format(operator="1.12.0"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("connect", result.stderr)

    def test_fails_when_connect_workload_renders(self) -> None:
        operator = "1.12.0"
        self._set_pins("2.4.1", operator)
        result = self._run(GOOD_RENDER.format(operator=operator) + "        - image: 1password/connect-api:1.0.0\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Connect workload", result.stderr)


if __name__ == "__main__":
    unittest.main()
