from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "foundry_bluegreen.py"
SPEC = importlib.util.spec_from_file_location("foundry_bluegreen", MODULE_PATH)
foundry_bluegreen = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["foundry_bluegreen"] = foundry_bluegreen
SPEC.loader.exec_module(foundry_bluegreen)


class FakeRunner:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str | None]] = []

    def run(self, args, *, input_text=None):
        self.calls.append((list(args), input_text))
        return foundry_bluegreen.CommandResult(args=args)


class FakeResolver:
    def __init__(self, addresses: list[str]) -> None:
        self.addresses = addresses
        self.hostnames: list[str] = []

    def __call__(self, hostname: str) -> list[str]:
        self.hostnames.append(hostname)
        return self.addresses


class FoundryBlueGreenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.write_minimal_repo()

    def write(self, path: str, text: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def write_minimal_repo(self) -> None:
        self.write("tools/foundry_bluegreen.py", "tool version\n")
        self.write("kubernetes/infra/controllers/nfs-csi/app.yaml", "nfs\n")
        self.write("kubernetes/apps/foundry-bluegreen-fixture/kustomization.yaml", "fixture\n")
        self.write("kubernetes/clusters/development/apps/foundry-bluegreen-fixture.yaml", "fixture flux\n")
        self.write(
            "kubernetes/apps/foundryvtt/deployment.yaml",
            """---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: foundryvtt
spec:
  replicas: 1
""",
        )
        self.write(
            "kubernetes/apps/foundryvtt/service.yaml",
            """---
apiVersion: v1
kind: Service
metadata:
  name: foundryvtt
spec:
  selector:
    app: foundryvtt
    foundryvtt.petebeegle.com/color: blue
""",
        )
        self.write(
            "kubernetes/apps/foundryvtt/kustomization.yaml",
            """---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
  - pvc.yaml
""",
        )
        self.write("kubernetes/apps/foundryvtt/pvc.yaml", "blue pvc\n")

    def args(self, command: str, **kwargs) -> Namespace:
        values = {
            "root": self.root,
            "evidence": Path(".codex/tmp/foundry-bluegreen-dev-rehearse.json"),
            "command": command,
        }
        values.update(kwargs)
        return Namespace(**values)

    def write_current_evidence(self) -> None:
        foundry_bluegreen.write_json(
            self.root / ".codex/tmp/foundry-bluegreen-dev-rehearse.json",
            {
                "status": "succeeded",
                "config_version": foundry_bluegreen.config_version(self.root),
                "completed_at": "2026-05-16T00:00:00Z",
            },
        )

    def quiet(self, func, *args):
        with redirect_stdout(io.StringIO()):
            return func(*args)

    def test_prepare_requires_current_dev_rehearsal(self) -> None:
        with self.assertRaisesRegex(foundry_bluegreen.FoundryBlueGreenError, "dev-rehearse"):
            foundry_bluegreen.command_prepare(
                self.args("prepare", image="felddy/foundryvtt:14.361")
            )

    def test_prepare_pauses_blue_and_adds_green_desired_state(self) -> None:
        self.write_current_evidence()

        self.quiet(
            foundry_bluegreen.command_prepare,
            self.args("prepare", image="felddy/foundryvtt:14.362")
        )

        deployment = (self.root / "kubernetes/apps/foundryvtt/deployment.yaml").read_text()
        service = (self.root / "kubernetes/apps/foundryvtt/service.yaml").read_text()
        kustomization = (self.root / "kubernetes/apps/foundryvtt/kustomization.yaml").read_text()
        green = (self.root / "kubernetes/apps/foundryvtt/deployment-green.yaml").read_text()
        route = (self.root / "kubernetes/apps/foundryvtt/httproute-green-preview.yaml").read_text()
        self.assertIn("replicas: 0", deployment)
        self.assertIn("foundryvtt.petebeegle.com/color: blue", service)
        self.assertIn("felddy/foundryvtt:14.362", green)
        self.assertIn("name: internal", route)
        self.assertIn("foundry-green.${cluster_domain}", route)
        self.assertIn("- snapshot-blue.yaml", kustomization)
        self.assertIn("- deployment-green.yaml", kustomization)

    def test_promote_moves_stable_service_to_green_and_keeps_blue_zero(self) -> None:
        self.write_current_evidence()
        self.quiet(
            foundry_bluegreen.command_prepare,
            self.args("prepare", image="felddy/foundryvtt:14.362")
        )

        self.quiet(foundry_bluegreen.command_promote, self.args("promote"))

        deployment = (self.root / "kubernetes/apps/foundryvtt/deployment.yaml").read_text()
        service = (self.root / "kubernetes/apps/foundryvtt/service.yaml").read_text()
        self.assertIn("replicas: 0", deployment)
        self.assertIn("foundryvtt.petebeegle.com/color: green", service)

    def test_rollback_restores_blue_and_scales_green_down(self) -> None:
        self.write_current_evidence()
        self.quiet(
            foundry_bluegreen.command_prepare,
            self.args("prepare", image="felddy/foundryvtt:14.362")
        )
        self.quiet(foundry_bluegreen.command_promote, self.args("promote"))

        self.quiet(foundry_bluegreen.command_rollback, self.args("rollback"))

        deployment = (self.root / "kubernetes/apps/foundryvtt/deployment.yaml").read_text()
        green = (self.root / "kubernetes/apps/foundryvtt/deployment-green.yaml").read_text()
        service = (self.root / "kubernetes/apps/foundryvtt/service.yaml").read_text()
        self.assertIn("replicas: 1", deployment)
        self.assertIn("replicas: 0", green)
        self.assertIn("foundryvtt.petebeegle.com/color: blue", service)

    def test_dev_rehearse_uses_fixture_and_writes_current_evidence(self) -> None:
        runner = FakeRunner()
        resolver = FakeResolver([foundry_bluegreen.DEVELOPMENT_GATEWAY_INTERNAL_IP])

        self.quiet(
            foundry_bluegreen.command_dev_rehearse,
            self.args("dev-rehearse", kubeconfig=str(foundry_bluegreen.DEV_KUBECONFIG)),
            runner,
            resolver,
        )

        self.assertEqual([foundry_bluegreen.DEVELOPMENT_PREVIEW_HOSTNAME], resolver.hostnames)
        commands = [" ".join(call[0]) for call in runner.calls]
        self.assertIn("kubectl kustomize " + str(self.root / foundry_bluegreen.FIXTURE_DIR), commands)
        self.assertTrue(any("apply -k" in command for command in commands))
        self.assertTrue(any("deployment/foundry-fixture-blue --replicas=0" in command for command in commands))
        self.assertTrue(any("volumesnapshot/foundry-fixture-blue-rehearsal" in command for command in commands))
        evidence = foundry_bluegreen.read_evidence(
            self.root, Path(".codex/tmp/foundry-bluegreen-dev-rehearse.json")
        )
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence["status"], "succeeded")
        self.assertEqual(evidence["config_version"], foundry_bluegreen.config_version(self.root))

    def test_dev_rehearse_rejects_non_development_kubeconfig_before_kubectl(self) -> None:
        runner = FakeRunner()
        resolver = FakeResolver([foundry_bluegreen.DEVELOPMENT_GATEWAY_INTERNAL_IP])

        with self.assertRaisesRegex(foundry_bluegreen.FoundryBlueGreenError, "development kubeconfig"):
            foundry_bluegreen.command_dev_rehearse(
                self.args("dev-rehearse", kubeconfig="~/.kube/homelab-production.config"),
                runner,
                resolver,
            )

        self.assertEqual([], resolver.hostnames)
        self.assertEqual([], runner.calls)
        self.assertIsNone(
            foundry_bluegreen.read_evidence(
                self.root, Path(".codex/tmp/foundry-bluegreen-dev-rehearse.json")
            )
        )

    def test_development_preview_dns_preflight_accepts_development_gateway(self) -> None:
        resolver = FakeResolver([foundry_bluegreen.DEVELOPMENT_GATEWAY_INTERNAL_IP])

        foundry_bluegreen.require_development_preview_dns(resolver)

        self.assertEqual([foundry_bluegreen.DEVELOPMENT_PREVIEW_HOSTNAME], resolver.hostnames)

    def test_development_preview_dns_preflight_rejects_production_gateway(self) -> None:
        resolver = FakeResolver([foundry_bluegreen.PRODUCTION_GATEWAY_INTERNAL_IP])

        with self.assertRaisesRegex(
            foundry_bluegreen.FoundryBlueGreenError,
            "production Gateway 192\\.168\\.30\\.241",
        ):
            foundry_bluegreen.require_development_preview_dns(resolver)

    def test_development_preview_dns_preflight_rejects_no_a_records(self) -> None:
        resolver = FakeResolver([])

        with self.assertRaisesRegex(foundry_bluegreen.FoundryBlueGreenError, "has no A records"):
            foundry_bluegreen.require_development_preview_dns(resolver)

    def test_dev_rehearse_rejects_dns_mismatch_before_kubectl_or_evidence(self) -> None:
        runner = FakeRunner()
        resolver = FakeResolver(["192.168.30.250"])

        with self.assertRaisesRegex(foundry_bluegreen.FoundryBlueGreenError, "unexpected A record"):
            foundry_bluegreen.command_dev_rehearse(
                self.args("dev-rehearse", kubeconfig=str(foundry_bluegreen.DEV_KUBECONFIG)),
                runner,
                resolver,
            )

        self.assertEqual([], runner.calls)
        self.assertIsNone(
            foundry_bluegreen.read_evidence(
                self.root, Path(".codex/tmp/foundry-bluegreen-dev-rehearse.json")
            )
        )


if __name__ == "__main__":
    unittest.main()
