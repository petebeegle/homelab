#!/usr/bin/env python3
"""Verify 1Password Operator sync and rotation without reading Secret values."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Callable, Protocol


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "kubernetes/apps/onepassword-canary/smoke/manifests.yaml"
SLUG_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,38}[a-z0-9])?$")


class VerificationError(RuntimeError):
    """Raised when a verification command or acceptance condition fails."""


class Runner(Protocol):
    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]: ...


@dataclass(frozen=True)
class Config:
    vault: str
    item: str
    slug: str
    kubeconfig: Path
    timeout_seconds: int
    keep: bool
    skip_rotation: bool

    @property
    def namespace(self) -> str:
        return f"onepassword-canary-{self.slug}"


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
        raise VerificationError(f"command failed without displaying captured output: {args[0]} {args[1]}")
    return result


def _json(result: subprocess.CompletedProcess[str], description: str) -> dict[str, object]:
    try:
        value = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError) as error:
        raise VerificationError(f"{description} returned invalid JSON") from error
    if not isinstance(value, dict):
        raise VerificationError(f"{description} returned an unexpected JSON shape")
    return value


def _resolve_ids(config: Config, runner: Runner) -> tuple[str, str]:
    vault = _json(
        _run(runner, ["op", "vault", "get", config.vault, "--format=json"]),
        "op vault get",
    )
    vault_id = vault.get("id")
    if not isinstance(vault_id, str) or not vault_id:
        raise VerificationError("1Password vault response did not contain an ID")

    item = _json(
        _run(
            runner,
            ["op", "item", "get", config.item, "--vault", vault_id, "--format=json"],
        ),
        "op item get",
    )
    item_id = item.get("id")
    if not isinstance(item_id, str) or not item_id:
        raise VerificationError("1Password item response did not contain an ID")
    fields = item.get("fields")
    if not isinstance(fields, list) or not any(
        isinstance(field, dict)
        and field.get("id") == "password"
        and isinstance(field.get("value"), str)
        and bool(field.get("value"))
        for field in fields
    ):
        raise VerificationError("canary Login item must contain a non-empty built-in password field")
    return vault_id, item_id


def _kubectl(config: Config, *args: str) -> list[str]:
    return ["kubectl", "--kubeconfig", str(config.kubeconfig), *args]


def _metadata(config: Config, runner: Runner) -> tuple[str, str]:
    secret_version = _run(
        runner,
        _kubectl(
            config,
            "-n",
            config.namespace,
            "get",
            "secret",
            "onepassword-canary",
            "-o",
            "jsonpath={.metadata.resourceVersion}",
        ),
    ).stdout.strip()
    pod_uid = _run(
        runner,
        _kubectl(
            config,
            "-n",
            config.namespace,
            "get",
            "pod",
            "-l",
            "app.kubernetes.io/name=onepassword-canary",
            "-o",
            "jsonpath={.items[0].metadata.uid}",
        ),
    ).stdout.strip()
    if not secret_version or not pod_uid:
        raise VerificationError("canary metadata was empty")
    return secret_version, pod_uid


def _wait_for_change(
    config: Config,
    runner: Runner,
    sleep: Callable[[float], None],
    initial_secret_version: str,
    initial_pod_uid: str,
    monotonic: Callable[[], float],
) -> tuple[str, str]:
    deadline = monotonic() + config.timeout_seconds
    secret_version = initial_secret_version
    pod_uid = initial_pod_uid
    while monotonic() < deadline:
        secret_version, pod_uid = _metadata(config, runner)
        if secret_version != initial_secret_version and pod_uid != initial_pod_uid:
            return secret_version, pod_uid
        sleep(5)
    raise VerificationError("timed out waiting for Secret refresh and Deployment restart")


def verify(
    config: Config,
    *,
    runner: Runner = subprocess.run,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> None:
    if not SLUG_PATTERN.fullmatch(config.slug):
        raise VerificationError("slug must be a lowercase DNS label of at most 40 characters")
    if config.timeout_seconds <= 0:
        raise VerificationError("timeout must be positive")
    if not MANIFEST_PATH.is_file():
        raise VerificationError(f"missing canary manifest: {MANIFEST_PATH}")

    vault_id, item_id = _resolve_ids(config, runner)
    manifest = Template(MANIFEST_PATH.read_text(encoding="utf-8")).substitute(
        branch_slug=config.slug,
        onepassword_vault_id=vault_id,
        onepassword_item_id=item_id,
    )
    created = False
    try:
        _run(
            runner,
            _kubectl(
                config,
                "-n",
                "flux-system",
                "wait",
                "kustomization/onepassword-operator",
                "--for=condition=Ready=True",
                f"--timeout={config.timeout_seconds}s",
            ),
        )
        _run(
            runner,
            _kubectl(
                config,
                "-n",
                "onepassword-system",
                "wait",
                "helmrelease/onepassword-operator",
                "--for=condition=Ready=True",
                f"--timeout={config.timeout_seconds}s",
            ),
        )
        _run(runner, _kubectl(config, "apply", "-f", "-"), input_text=manifest)
        created = True
        _run(
            runner,
            _kubectl(
                config,
                "-n",
                config.namespace,
                "wait",
                "onepassworditem/onepassword-canary",
                "--for=condition=Ready=True",
                f"--timeout={config.timeout_seconds}s",
            ),
        )
        _run(
            runner,
            _kubectl(
                config,
                "-n",
                config.namespace,
                "rollout",
                "status",
                "deployment/onepassword-canary",
                f"--timeout={config.timeout_seconds}s",
            ),
        )
        initial_secret_version, initial_pod_uid = _metadata(config, runner)

        if config.skip_rotation:
            print(f"Secret resourceVersion: {initial_secret_version}")
            print(f"Pod UID: {initial_pod_uid}")
            return

        _run(
            runner,
            [
                "op",
                "item",
                "edit",
                item_id,
                "--vault",
                vault_id,
                "--generate-password=letters,digits,40",
            ],
        )
        new_secret_version, new_pod_uid = _wait_for_change(
            config,
            runner,
            sleep,
            initial_secret_version,
            initial_pod_uid,
            monotonic,
        )
        print(f"Secret resourceVersion: {initial_secret_version} -> {new_secret_version}")
        print(f"Pod UID: {initial_pod_uid} -> {new_pod_uid}")
    finally:
        if created and config.keep:
            print(f"Canary retained in namespace: {config.namespace}")
        elif created:
            _run(
                runner,
                _kubectl(
                    config,
                    "delete",
                    "namespace",
                    config.namespace,
                    "--wait=true",
                    f"--timeout={config.timeout_seconds}s",
                ),
            )
            print(f"Canary namespace removed: {config.namespace}")


def _duration(value: str) -> int:
    match = re.fullmatch(r"([1-9][0-9]*)([smh]?)", value)
    if not match:
        raise argparse.ArgumentTypeError("timeout must be a positive integer with optional s, m, or h")
    amount = int(match.group(1))
    multiplier = {"": 1, "s": 1, "m": 60, "h": 3600}[match.group(2)]
    return amount * multiplier


def _parse_args() -> Config:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="Development vault name or ID")
    parser.add_argument("--item", required=True, help="Disposable canary item name or ID")
    parser.add_argument("--slug", required=True, help="Unique lowercase DNS-safe test slug")
    parser.add_argument(
        "--kubeconfig",
        type=Path,
        default=Path.home() / ".kube/homelab-development.config",
    )
    parser.add_argument("--timeout", type=_duration, default=900, dest="timeout_seconds")
    parser.add_argument("--keep", action="store_true", help="Retain the canary namespace")
    parser.add_argument(
        "--skip-rotation",
        action="store_true",
        help="Verify initial sync only; do not edit the item",
    )
    args = parser.parse_args()
    return Config(**vars(args))


def main() -> int:
    try:
        verify(_parse_args())
    except VerificationError as error:
        print(f"1Password operator verification failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
