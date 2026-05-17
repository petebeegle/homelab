"""Command handlers for the Foundry blue/green workflow."""

from __future__ import annotations

import argparse

from .config import APP_DIR, FIXTURE_DIR
from .evidence import (
    config_version,
    read_evidence,
    require_current_dev_rehearsal,
    require_development_kubeconfig,
    utc_now,
    write_json,
)
from .manifests import ensure_green_prepared, validate_image, write_green_resources
from .process import CommandRunner
from .state import (
    remove_file_if_exists,
    remove_kustomization_resource,
    replace_first_replicas,
    service_color,
    set_service_color,
)


def command_status(args: argparse.Namespace) -> int:
    root = args.root
    evidence = read_evidence(root, args.evidence)
    active = service_color(root / APP_DIR / "service.yaml")
    current_version = config_version(root)
    print(f"Foundry active production service color: {active}")
    print(f"Current tool/config version: {current_version}")
    if evidence:
        state = "current" if evidence.get("config_version") == current_version else "stale"
        print(f"Last dev-rehearse: {evidence.get('status')} ({state}) at {evidence.get('completed_at')}")
    else:
        print("Last dev-rehearse: none")
    return 0


def command_dev_rehearse(args: argparse.Namespace, runner: CommandRunner) -> int:
    root = args.root
    kubeconfig = require_development_kubeconfig(args.kubeconfig)
    fixture = root / FIXTURE_DIR
    namespace = "foundry-bluegreen-fixture"
    runner.run(["kubectl", "kustomize", str(fixture)])
    kubectl = ["kubectl", "--kubeconfig", str(kubeconfig)]
    runner.run([*kubectl, "apply", "-f", str(root / "kubernetes/infra/controllers/nfs-csi/app.yaml")])
    runner.run([*kubectl, "apply", "-f", str(root / "kubernetes/infra/controllers/nfs-csi/volumesnapshotclass.yaml")])
    runner.run([*kubectl, "-n", "kube-system", "wait", "helmrelease/csi-driver-nfs", "--for=condition=Ready", "--timeout=300s"])
    runner.run([*kubectl, "apply", "-k", str(fixture)])
    for deployment in ["foundry-fixture-blue", "foundry-fixture-green"]:
        runner.run([*kubectl, "-n", namespace, "rollout", "status", f"deployment/{deployment}", "--timeout=120s"])
    runner.run([*kubectl, "-n", namespace, "scale", "deployment/foundry-fixture-blue", "--replicas=0"])
    snapshot = """---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: foundry-fixture-blue-rehearsal
  namespace: foundry-bluegreen-fixture
spec:
  volumeSnapshotClassName: nfs-csi-snapshot
  source:
    persistentVolumeClaimName: foundry-fixture-blue
"""
    runner.run([*kubectl, "apply", "-f", "-"], input_text=snapshot)
    runner.run(
        [
            *kubectl,
            "-n",
            namespace,
            "wait",
            "volumesnapshot/foundry-fixture-blue-rehearsal",
            "--for=jsonpath={.status.readyToUse}=true",
            "--timeout=120s",
        ]
    )
    runner.run([*kubectl, "-n", namespace, "scale", "deployment/foundry-fixture-blue", "--replicas=1"])
    runner.run([*kubectl, "-n", namespace, "rollout", "status", "deployment/foundry-fixture-blue", "--timeout=120s"])
    write_json(
        root / args.evidence,
        {
            "command": "dev-rehearse",
            "status": "succeeded",
            "cluster": "development",
            "fixture": FIXTURE_DIR.as_posix(),
            "kubeconfig": str(kubeconfig),
            "config_version": config_version(root),
            "completed_at": utc_now(),
        },
    )
    print("dev-rehearse succeeded; production commands are now unblocked for this tool/config version")
    return 0


def command_prepare(args: argparse.Namespace) -> int:
    root = args.root
    require_current_dev_rehearsal(root, args.evidence)
    image = validate_image(args.image)
    replace_first_replicas(root / APP_DIR / "deployment.yaml", 0)
    write_green_resources(root, image)
    print("prepared green desired state and paused blue for snapshot consistency")
    print("commit these changes, open a PR, merge it, and wait for Flux before promoting")
    return 0


def command_promote(args: argparse.Namespace) -> int:
    root = args.root
    require_current_dev_rehearsal(root, args.evidence)
    ensure_green_prepared(root)
    replace_first_replicas(root / APP_DIR / "deployment.yaml", 0)
    replace_first_replicas(root / APP_DIR / "deployment-green.yaml", 1)
    set_service_color(root / APP_DIR / "service.yaml", "green")
    print("promoted stable Service/foundryvtt to green desired state; blue remains scaled to zero")
    print("commit these changes, open a PR, merge it, and wait for Flux")
    return 0


def command_rollback(args: argparse.Namespace) -> int:
    root = args.root
    require_current_dev_rehearsal(root, args.evidence)
    ensure_green_prepared(root)
    set_service_color(root / APP_DIR / "service.yaml", "blue")
    replace_first_replicas(root / APP_DIR / "deployment.yaml", 1)
    replace_first_replicas(root / APP_DIR / "deployment-green.yaml", 0)
    print("rolled stable Service/foundryvtt back to blue desired state")
    print("commit these changes, open a PR, merge it, and wait for Flux")
    return 0


def command_retire(args: argparse.Namespace) -> int:
    root = args.root
    require_current_dev_rehearsal(root, args.evidence)
    app = root / APP_DIR
    active = service_color(app / "service.yaml")
    if active == "green":
        retired = ["deployment.yaml", "pvc.yaml", "snapshot-blue.yaml"]
    else:
        retired = [
            "deployment-green.yaml",
            "pvc-green.yaml",
            "service-green-preview.yaml",
            "httproute-green-preview.yaml",
            "snapshot-blue.yaml",
        ]
    for name in retired:
        remove_kustomization_resource(app / "kustomization.yaml", name)
        remove_file_if_exists(app / name)
    print(f"retired inactive {'blue' if active == 'green' else 'green'} desired state")
    print("commit these changes, open a PR, merge it, and wait for Flux")
    return 0
