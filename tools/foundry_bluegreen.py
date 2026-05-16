#!/usr/bin/env python3
"""Safe, dev-gated blue/green workflow for Foundry VTT upgrades."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path("kubernetes/apps/foundryvtt")
FIXTURE_DIR = Path("kubernetes/apps/foundry-bluegreen-fixture")
EVIDENCE_PATH = Path(".codex/tmp/foundry-bluegreen-dev-rehearse.json")
DEV_KUBECONFIG = Path.home() / ".kube/homelab-development.config"
PRODUCTION_COMMANDS = {"prepare", "promote", "rollback", "retire"}
CONFIG_VERSION_GLOBS = [
    "tools/foundry_bluegreen.py",
    "kubernetes/infra/controllers/nfs-csi/*.yaml",
    "kubernetes/apps/foundry-bluegreen-fixture/*.yaml",
    "kubernetes/clusters/development/apps/foundry-bluegreen-fixture.yaml",
]


class FoundryBlueGreenError(RuntimeError):
    """Raised when a workflow precondition fails."""


@dataclass
class CommandResult:
    args: Sequence[str]
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0


class CommandRunner:
    def run(self, args: Sequence[str], *, input_text: str | None = None) -> CommandResult:
        completed = subprocess.run(
            list(args),
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            rendered = " ".join(args)
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise FoundryBlueGreenError(f"command failed: {rendered}\n{detail}")
        return CommandResult(args=args, stdout=completed.stdout, stderr=completed.stderr, returncode=0)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def config_version(root: Path) -> str:
    digest = hashlib.sha256()
    for pattern in CONFIG_VERSION_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                digest.update(rel(root, path).encode())
                digest.update(b"\0")
                digest.update(path.read_bytes())
                digest.update(b"\0")
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_evidence(root: Path, evidence_path: Path) -> dict[str, object] | None:
    path = root / evidence_path
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def require_current_dev_rehearsal(root: Path, evidence_path: Path) -> dict[str, object]:
    expected = config_version(root)
    evidence = read_evidence(root, evidence_path)
    if not evidence:
        raise FoundryBlueGreenError(
            "production command blocked: run `tools/foundry_bluegreen.py dev-rehearse` first"
        )
    if evidence.get("status") != "succeeded":
        raise FoundryBlueGreenError("production command blocked: last dev-rehearse did not succeed")
    if evidence.get("config_version") != expected:
        raise FoundryBlueGreenError(
            "production command blocked: dev-rehearse evidence is stale for this tool/config version"
        )
    return evidence


def resolved_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def require_development_kubeconfig(kubeconfig: str | Path) -> Path:
    actual = resolved_path(kubeconfig)
    expected = resolved_path(DEV_KUBECONFIG)
    if actual != expected:
        raise FoundryBlueGreenError(
            f"dev-rehearse requires development kubeconfig {expected}; got {actual}"
        )
    return actual


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_first_replicas(path: Path, replicas: int) -> None:
    text = read(path)
    next_text, count = re.subn(r"(?m)^  replicas: \d+\s*$", f"  replicas: {replicas}", text, count=1)
    if count != 1:
        raise FoundryBlueGreenError(f"could not update replicas in {path}")
    write(path, next_text)


def set_service_color(path: Path, color: str) -> None:
    text = read(path)
    next_text, count = re.subn(
        r"(?m)^    foundryvtt\.petebeegle\.com/color: (blue|green)\s*$",
        f"    foundryvtt.petebeegle.com/color: {color}",
        text,
        count=1,
    )
    if count != 1:
        raise FoundryBlueGreenError(f"could not update active service color in {path}")
    write(path, next_text)


def service_color(path: Path) -> str:
    match = re.search(r"(?m)^    foundryvtt\.petebeegle\.com/color: (blue|green)\s*$", read(path))
    if not match:
        raise FoundryBlueGreenError(f"could not determine active service color in {path}")
    return match.group(1)


def ensure_kustomization_resource(path: Path, resource: str) -> None:
    text = read(path)
    line = f"  - {resource}"
    if line in text.splitlines():
        return
    if "resources:\n" not in text:
        raise FoundryBlueGreenError(f"{path} has no resources block")
    text = text.rstrip() + f"\n{line}\n"
    write(path, text)


def remove_kustomization_resource(path: Path, resource: str) -> None:
    lines = [line for line in read(path).splitlines() if line.strip() != f"- {resource}"]
    write(path, "\n".join(lines).rstrip() + "\n")


def remove_file_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def validate_image(image: str) -> str:
    if not re.fullmatch(r"felddy/foundryvtt:[A-Za-z0-9._-]+", image):
        raise FoundryBlueGreenError("prepare requires --image in the form felddy/foundryvtt:<tag>")
    return image


def green_deployment(image: str) -> str:
    return f"""---
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: foundryvtt
  name: foundryvtt-green
  labels:
    app: foundryvtt
    foundryvtt.petebeegle.com/color: green
spec:
  replicas: 1
  selector:
    matchLabels:
      app: foundryvtt
      foundryvtt.petebeegle.com/color: green
  template:
    metadata:
      labels:
        app: foundryvtt
        foundryvtt.petebeegle.com/color: green
    spec:
      securityContext:
        runAsUser: 421
        runAsGroup: 421
        fsGroup: 421
      containers:
        - name: foundryvtt
          image: {image}
          imagePullPolicy: IfNotPresent
          env:
            - name: FOUNDRY_ADMIN_KEY
              valueFrom:
                secretKeyRef:
                  name: foundryvtt-secret
                  key: FOUNDRY_ADMIN_KEY
            - name: FOUNDRY_USERNAME
              valueFrom:
                secretKeyRef:
                  name: foundryvtt-secret
                  key: FOUNDRY_USERNAME
            - name: FOUNDRY_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: foundryvtt-secret
                  key: FOUNDRY_PASSWORD
            - name: FOUNDRY_LICENSE_KEY
              valueFrom:
                secretKeyRef:
                  name: foundryvtt-secret
                  key: FOUNDRY_LICENSE_KEY
          ports:
            - name: web
              containerPort: 30000
          volumeMounts:
            - name: foundryvtt-data-persistent-storage
              mountPath: /data
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "4Gi"
              cpu: "1"
      volumes:
        - name: foundryvtt-data-persistent-storage
          persistentVolumeClaim:
            claimName: foundryvtt-data-green-pvc
"""


def green_pvc() -> str:
    return """---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: foundryvtt-data-green-pvc
  namespace: foundryvtt
  labels:
    app: foundryvtt
    foundryvtt.petebeegle.com/color: green
spec:
  storageClassName: nfs-csi-storage
  accessModes:
    - ReadWriteOnce
  dataSource:
    apiGroup: snapshot.storage.k8s.io
    kind: VolumeSnapshot
    name: foundryvtt-blue-pre-upgrade
  resources:
    requests:
      storage: 40G
"""


def blue_snapshot() -> str:
    return """---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: foundryvtt-blue-pre-upgrade
  namespace: foundryvtt
  labels:
    app: foundryvtt
    foundryvtt.petebeegle.com/color: blue
spec:
  volumeSnapshotClassName: nfs-csi-snapshot
  source:
    persistentVolumeClaimName: foundryvtt-data-pvc
"""


def green_preview_service() -> str:
    return """---
apiVersion: v1
kind: Service
metadata:
  name: foundryvtt-green
  labels:
    name: foundryvtt-green
    foundryvtt.petebeegle.com/color: green
  namespace: foundryvtt
spec:
  selector:
    app: foundryvtt
    foundryvtt.petebeegle.com/color: green
  ports:
    - name: web
      port: 80
      targetPort: 30000
"""


def green_preview_route() -> str:
    return """---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: foundryvtt-green-preview
  namespace: foundryvtt
spec:
  parentRefs:
    - name: internal
      namespace: gateway
      sectionName: https-gateway
  hostnames:
    - foundry-green.${cluster_domain}
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: foundryvtt-green
          port: 80
          weight: 1
"""


def write_green_resources(root: Path, image: str) -> None:
    app = root / APP_DIR
    resources = {
        "snapshot-blue.yaml": blue_snapshot(),
        "pvc-green.yaml": green_pvc(),
        "deployment-green.yaml": green_deployment(image),
        "service-green-preview.yaml": green_preview_service(),
        "httproute-green-preview.yaml": green_preview_route(),
    }
    for name, text in resources.items():
        write(app / name, text)
        ensure_kustomization_resource(app / "kustomization.yaml", name)


def ensure_green_prepared(root: Path) -> None:
    required = ["deployment-green.yaml", "pvc-green.yaml", "service-green-preview.yaml", "httproute-green-preview.yaml"]
    missing = [name for name in required if not (root / APP_DIR / name).exists()]
    if missing:
        raise FoundryBlueGreenError(f"green is not prepared; missing {', '.join(missing)}")


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--evidence", type=Path, default=EVIDENCE_PATH, help="dev rehearsal evidence path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="show active color and dev gate status")

    dev = subparsers.add_parser("dev-rehearse", help="exercise the safe development fixture")
    dev.add_argument("--kubeconfig", default=str(DEV_KUBECONFIG), help="development kubeconfig")

    prepare = subparsers.add_parser("prepare", help="prepare green Foundry desired state")
    prepare.add_argument("--image", required=True, help="Foundry image, for example felddy/foundryvtt:14.361")

    subparsers.add_parser("promote", help="move stable production service to green desired state")
    subparsers.add_parser("rollback", help="move stable production service back to blue desired state")
    subparsers.add_parser("retire", help="remove inactive desired state after the outcome is accepted")
    return parser


def dispatch(args: argparse.Namespace, runner: CommandRunner | None = None) -> int:
    runner = runner or CommandRunner()
    if args.command == "status":
        return command_status(args)
    if args.command == "dev-rehearse":
        return command_dev_rehearse(args, runner)
    if args.command == "prepare":
        return command_prepare(args)
    if args.command == "promote":
        return command_promote(args)
    if args.command == "rollback":
        return command_rollback(args)
    if args.command == "retire":
        return command_retire(args)
    raise FoundryBlueGreenError(f"unknown command: {args.command}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    args.root = args.root.resolve()
    try:
        return dispatch(args)
    except FoundryBlueGreenError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
