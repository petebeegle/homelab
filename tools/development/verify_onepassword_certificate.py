#!/usr/bin/env python3
"""Issue and remove a disposable staging certificate without reading its Secret."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


DNS_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,38}[a-z0-9])?$")
DNS_NAME = re.compile(r"^[a-z0-9](?:[-a-z0-9.]*[a-z0-9])?$")


class VerificationError(RuntimeError):
    """Raised when certificate acceptance cannot be proved."""


class Runner(Protocol):
    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]: ...


@dataclass(frozen=True)
class Config:
    slug: str
    kubeconfig: Path
    domain: str
    timeout_seconds: int

    @property
    def namespace(self) -> str:
        return f"onepassword-certificate-{self.slug}"

    @property
    def dns_name(self) -> str:
        return f"onepassword-{self.slug}.{self.domain}"


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


def _kubectl(config: Config, *args: str) -> list[str]:
    return ["kubectl", "--kubeconfig", str(config.kubeconfig), *args]


def _manifest(config: Config) -> str:
    return f"""---
apiVersion: v1
kind: Namespace
metadata:
  name: {config.namespace}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: onepassword-cutover
  namespace: {config.namespace}
spec:
  secretName: onepassword-cutover-tls
  issuerRef:
    kind: ClusterIssuer
    name: cloudflare-staging
  dnsNames:
    - {config.dns_name}
"""


def verify(config: Config, *, runner: Runner = subprocess.run) -> None:
    if not DNS_LABEL.fullmatch(config.slug):
        raise VerificationError("slug must be a lowercase DNS label of at most 40 characters")
    if not DNS_NAME.fullmatch(config.domain) or "." not in config.domain:
        raise VerificationError("domain must be a lowercase DNS name")
    if config.timeout_seconds <= 0:
        raise VerificationError("timeout must be positive")

    mutation_started = False
    try:
        mutation_started = True
        _run(runner, _kubectl(config, "apply", "-f", "-"), input_text=_manifest(config))
        _run(
            runner,
            _kubectl(
                config,
                "-n",
                config.namespace,
                "wait",
                "certificate/onepassword-cutover",
                "--for=condition=Ready=True",
                f"--timeout={config.timeout_seconds}s",
            ),
        )
        print(f"Disposable staging Certificate Ready: {config.namespace}/onepassword-cutover")
    finally:
        if mutation_started:
            _run(
                runner,
                _kubectl(
                    config,
                    "delete",
                    "namespace",
                    config.namespace,
                    "--ignore-not-found=true",
                    "--wait=true",
                    f"--timeout={config.timeout_seconds}s",
                ),
            )
            print(f"Disposable certificate namespace removed: {config.namespace}")


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
    parser.add_argument("--domain", default="dev.lab.petebeegle.com")
    parser.add_argument("--timeout", type=_duration, default=600, dest="timeout_seconds")
    return Config(**vars(parser.parse_args()))


def main() -> int:
    try:
        verify(_parse_args())
    except VerificationError as error:
        print(f"Disposable certificate verification failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
