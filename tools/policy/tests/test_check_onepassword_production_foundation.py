from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools/policy/check_onepassword_production_foundation.py"


class OnePasswordProductionFoundationPolicyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("onepassword_prod_policy", MODULE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load production foundation policy checker")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_repository_satisfies_production_foundation_policy(self) -> None:
        self.assertEqual([], self.module.check_repository(REPO_ROOT))

    def test_operator_alert_targets_live_helm_deployment_name(self) -> None:
        alerts = (
            REPO_ROOT
            / "kubernetes/infra/monitoring/grafana/alerting/alert-rules-onepassword.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn('deployment="onepassword-connect-operator"', alerts)
        self.assertNotIn('deployment="onepassword-operator"', alerts)

    def test_checker_rejects_secret_data_in_item_metric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metrics = root / "kubernetes/infra/monitoring/kube-state-metrics/config/metrics.yaml"
            metrics.parent.mkdir(parents=True)
            metrics.write_text(
                "      resources:\n"
                "        - groupVersionKind:\n"
                "            group: onepassword.com\n"
                "            version: v1\n"
                "            kind: OnePasswordItem\n"
                "          metrics:\n"
                "            - name: item_info\n"
                "              value: [status, secret, password]\n",
                encoding="utf-8",
            )
            errors = self.module.check_item_metric_safety(root)
        self.assertTrue(any("Secret data" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
