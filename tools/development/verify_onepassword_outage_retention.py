#!/usr/bin/env python3
"""Prove a 1Password outage retains an existing Secret and ready consumer."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol


DNS_LABEL = re.compile(r"^[a-z0-9](?:[-a-z0-9]*[a-z0-9])?$")
NETWORK_POLICY_SETTLE_SECONDS = 5.0


class VerificationError(RuntimeError):
    """Raised when outage-retention acceptance cannot be proved."""


class Runner(Protocol):
    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]: ...


@dataclass(frozen=True)
class Config:
    slug: str
    kubeconfig: Path
    namespace: str
    item: str
    secret: str
    timeout_seconds: int

    @property
    def resource_name(self) -> str:
        return f"onepassword-outage-{self.slug}"


@dataclass(frozen=True)
class SecretSnapshot:
    uid: str
    resource_version: str
    data_digest: str


def _run(
    runner: Runner,
    args: list[str],
    *,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        result = runner(
            args,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as error:
        raise VerificationError(f"unable to run required command: {args[0]}") from error
    if result.returncode != 0:
        raise VerificationError(
            f"command failed without displaying captured output: {args[0]} {args[1]}"
        )
    return result


def _json(result: subprocess.CompletedProcess[str], description: str) -> dict[str, object]:
    try:
        value = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError) as error:
        raise VerificationError(f"{description} returned invalid JSON") from error
    if not isinstance(value, dict):
        raise VerificationError(f"{description} returned an unexpected JSON shape")
    return value


def _kubectl(config: Config, *args: str) -> list[str]:
    return ["kubectl", "--kubeconfig", str(config.kubeconfig), *args]


def _item_ready(item: dict[str, object]) -> bool:
    status = item.get("status")
    if not isinstance(status, dict):
        return False
    conditions = status.get("conditions")
    return isinstance(conditions, list) and any(
        isinstance(condition, dict)
        and condition.get("type") == "Ready"
        and condition.get("status") == "True"
        for condition in conditions
    )


def _get_item(config: Config, runner: Runner) -> dict[str, object]:
    return _json(
        _run(
            runner,
            _kubectl(
                config,
                "-n",
                config.namespace,
                "get",
                "onepassworditem",
                config.item,
                "-o",
                "json",
            ),
        ),
        "OnePasswordItem",
    )


def _wait_item(
    config: Config,
    runner: Runner,
    expected_ready: bool,
    sleep: Callable[[float], None],
    monotonic: Callable[[], float],
) -> None:
    deadline = monotonic() + config.timeout_seconds
    while monotonic() < deadline:
        if _item_ready(_get_item(config, runner)) is expected_ready:
            return
        sleep(3)
    state = "Ready=True" if expected_ready else "Ready=False"
    raise VerificationError(f"timed out waiting for OnePasswordItem {state}")


def _secret_snapshot(config: Config, runner: Runner) -> SecretSnapshot:
    secret = _json(
        _run(
            runner,
            _kubectl(
                config,
                "-n",
                config.namespace,
                "get",
                "secret",
                config.secret,
                "-o",
                "json",
            ),
        ),
        "Secret",
    )
    metadata = secret.get("metadata")
    data = secret.get("data")
    if not isinstance(metadata, dict) or not isinstance(data, dict) or not data:
        raise VerificationError("Secret metadata or data is invalid")
    uid = metadata.get("uid")
    resource_version = metadata.get("resourceVersion")
    if not isinstance(uid, str) or not uid or not isinstance(resource_version, str):
        raise VerificationError("Secret identity metadata is invalid")
    digest = hashlib.sha256()
    for key in sorted(data):
        value = data[key]
        if not isinstance(key, str) or not isinstance(value, str):
            raise VerificationError("Secret data is invalid")
        try:
            decoded = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as error:
            raise VerificationError("Secret data is invalid") from error
        digest.update(len(key).to_bytes(4, "big"))
        digest.update(key.encode())
        digest.update(len(decoded).to_bytes(8, "big"))
        digest.update(decoded)
    return SecretSnapshot(uid, resource_version, digest.hexdigest())


def _pod_uid(config: Config, runner: Runner) -> str:
    pods = _json(
        _run(
            runner,
            _kubectl(
                config,
                "-n",
                config.namespace,
                "get",
                "pod",
                "-l",
                f"app.kubernetes.io/name={config.resource_name}",
                "-o",
                "json",
            ),
        ),
        "consumer Pod",
    )
    items = pods.get("items")
    if not isinstance(items, list) or len(items) != 1 or not isinstance(items[0], dict):
        raise VerificationError("expected exactly one outage consumer Pod")
    pod = items[0]
    metadata = pod.get("metadata")
    status = pod.get("status")
    conditions = status.get("conditions") if isinstance(status, dict) else None
    uid = metadata.get("uid") if isinstance(metadata, dict) else None
    ready = isinstance(conditions, list) and any(
        isinstance(condition, dict)
        and condition.get("type") == "Ready"
        and condition.get("status") == "True"
        for condition in conditions
    )
    if not isinstance(uid, str) or not uid or not ready:
        raise VerificationError("outage consumer Pod is not Ready")
    return uid


def _consumer_manifest(config: Config) -> str:
    return f"""---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {config.resource_name}
  namespace: {config.namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: {config.resource_name}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {config.resource_name}
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: hold
          image: alpine:3.24
          command: ["/bin/sh", "-c", "sleep 3600"]
          volumeMounts:
            - name: generated-secret
              mountPath: /run/onepassword
              readOnly: true
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop: ["ALL"]
            readOnlyRootFilesystem: true
          resources:
            requests:
              cpu: 5m
              memory: 8Mi
            limits:
              cpu: 50m
              memory: 32Mi
      volumes:
        - name: generated-secret
          secret:
            secretName: {config.secret}
"""


def _policy_manifest(config: Config) -> str:
    return f"""---
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: {config.resource_name}
  namespace: onepassword-system
spec:
  endpointSelector:
    matchLabels:
      name: onepassword-connect
  egress:
    - toEntities:
        - kube-apiserver
"""


def _annotate(config: Config, runner: Runner, token: str) -> None:
    _run(
        runner,
        _kubectl(
            config,
            "-n",
            config.namespace,
            "annotate",
            f"onepassworditem/{config.item}",
            f"homelab.petebeegle.com/refresh-request={token}",
            "--overwrite",
        ),
    )


def _restart_operator(config: Config, runner: Runner) -> None:
    _run(
        runner,
        _kubectl(
            config,
            "-n",
            "onepassword-system",
            "delete",
            "pod",
            "-l",
            "name=onepassword-connect",
            "--wait=true",
            f"--timeout={config.timeout_seconds}s",
        ),
    )


def _operator_ready(config: Config, runner: Runner) -> tuple[bool, bool]:
    pods = _json(
        _run(
            runner,
            _kubectl(
                config,
                "-n",
                "onepassword-system",
                "get",
                "pod",
                "-l",
                "name=onepassword-connect",
                "-o",
                "json",
            ),
        ),
        "1Password operator Pods",
    )
    items = pods.get("items")
    if not isinstance(items, list) or not items:
        return False, False
    ready = any(
        isinstance(pod, dict)
        and any(
            isinstance(condition, dict)
            and condition.get("type") == "Ready"
            and condition.get("status") == "True"
            for condition in (
                pod.get("status", {}).get("conditions", [])
                if isinstance(pod.get("status"), dict)
                else []
            )
        )
        for pod in items
    )
    return True, ready


def _wait_operator(
    config: Config,
    runner: Runner,
    expected_ready: bool,
    sleep: Callable[[float], None],
    monotonic: Callable[[], float],
) -> None:
    deadline = monotonic() + config.timeout_seconds
    while monotonic() < deadline:
        present, ready = _operator_ready(config, runner)
        if present and ready is expected_ready:
            return
        sleep(3)
    state = "Ready" if expected_ready else "present and NotReady"
    raise VerificationError(f"timed out waiting for 1Password operator to be {state}")


def verify(
    config: Config,
    *,
    runner: Runner = subprocess.run,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    refresh_token: Callable[[], str] = lambda: str(time.time_ns()),
) -> None:
    names = [config.slug, config.namespace, config.item, config.secret, config.resource_name]
    if any(len(name) > 63 or not DNS_LABEL.fullmatch(name) for name in names):
        raise VerificationError("slug and Kubernetes resource names must be safe DNS labels")
    if config.timeout_seconds <= 0:
        raise VerificationError("timeout must be positive")

    consumer_started = False
    policy_started = False
    failure_triggered = False
    try:
        _wait_item(config, runner, True, sleep, monotonic)
        consumer_started = True
        _run(runner, _kubectl(config, "apply", "-f", "-"), input_text=_consumer_manifest(config))
        _run(
            runner,
            _kubectl(
                config,
                "-n",
                config.namespace,
                "rollout",
                "status",
                f"deployment/{config.resource_name}",
                f"--timeout={config.timeout_seconds}s",
            ),
        )
        initial_secret = _secret_snapshot(config, runner)
        initial_pod_uid = _pod_uid(config, runner)

        policy_started = True
        _run(
            runner,
            _kubectl(config, "apply", "-f", "-"),
            input_text=_policy_manifest(config),
        )
        # Give Cilium time to program the selected operator endpoint before
        # forcing a vault read.
        sleep(NETWORK_POLICY_SETTLE_SECONDS)
        failure_triggered = True
        _annotate(config, runner, refresh_token())
        _restart_operator(config, runner)
        _wait_operator(config, runner, False, sleep, monotonic)
        print("1Password operator unavailable while vault egress was blocked")

        retained_secret = _secret_snapshot(config, runner)
        retained_pod_uid = _pod_uid(config, runner)
        if (
            retained_secret.uid != initial_secret.uid
            or retained_secret.data_digest != initial_secret.data_digest
        ):
            raise VerificationError("generated Secret changed during outage")
        if retained_pod_uid != initial_pod_uid:
            raise VerificationError("consumer Pod restarted during outage")
        print("1Password outage retained generated Secret and ready consumer")
    finally:
        if policy_started:
            _run(
                runner,
                _kubectl(
                    config,
                    "-n",
                    "onepassword-system",
                    "delete",
                    "ciliumnetworkpolicy",
                    config.resource_name,
                    "--ignore-not-found=true",
                ),
            )
        if failure_triggered:
            _annotate(config, runner, refresh_token())
            _wait_operator(config, runner, True, sleep, monotonic)
            _wait_item(config, runner, True, sleep, monotonic)
            print("OnePasswordItem recovered after operator egress restoration")
        if consumer_started:
            _run(
                runner,
                _kubectl(
                    config,
                    "-n",
                    config.namespace,
                    "delete",
                    "deployment",
                    config.resource_name,
                    "--ignore-not-found=true",
                    "--wait=true",
                    f"--timeout={config.timeout_seconds}s",
                ),
            )
            print(f"Outage consumer removed: {config.namespace}/{config.resource_name}")


def _duration(value: str) -> int:
    match = re.fullmatch(r"([1-9][0-9]*)([smh]?)", value)
    if not match:
        raise argparse.ArgumentTypeError(
            "timeout must be a positive integer with optional s, m, or h"
        )
    return int(match.group(1)) * {"": 1, "s": 1, "m": 60, "h": 3600}[match.group(2)]


def _parse_args() -> Config:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--kubeconfig", type=Path, required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--item", required=True)
    parser.add_argument("--secret", required=True)
    parser.add_argument("--timeout", type=_duration, default=600, dest="timeout_seconds")
    return Config(**vars(parser.parse_args()))


def main() -> int:
    try:
        verify(_parse_args())
    except VerificationError as error:
        print(f"1Password outage-retention verification failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
