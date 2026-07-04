"""Configuration models and argument validation for development verification."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Callable


REPO_ROOT = Path(__file__).resolve().parents[3]
PROFILE_DIR = Path(__file__).resolve().parents[1] / "smoke-profiles"
DEFAULT_KUBECONFIG = Path("~/.kube/homelab-development.config").expanduser()
DEFAULT_TIMEOUT = "10m"
FLUX_NAMESPACE = "flux-system"
DEVELOPMENT_BASE_KUSTOMIZATIONS = (
    "crds",
    "cert-manager",
    "local-path-provisioner",
    "nfs-csi",
    "cloudnative-pg",
    "cilium",
    "certs",
    "gateway",
    "app-whoami",
)

BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9._/-]+$")
SLUG_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,54}[a-z0-9])?$")
DURATION_PATTERN = re.compile(r"^(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?$")


@dataclass(frozen=True)
class Duration:
    raw: str
    seconds: int


@dataclass(frozen=True)
class AppConfig:
    app: str
    branch: str
    slug: str
    kubeconfig: Path
    timeout: Duration
    push: bool
    terraform_apply: bool
    include_cluster_base: bool
    keep: bool

    @property
    def git_repository(self) -> str:
        return f"branch-{self.slug}"

    @property
    def kustomization(self) -> str:
        return f"branch-{self.app}-{self.slug}"

    @property
    def namespace(self) -> str:
        return f"{self.app}-{self.slug}"


class VerificationError(RuntimeError):
    """Raised when validation or a live verification step fails."""


Runner = Callable[..., subprocess.CompletedProcess[str] | SimpleNamespace]


@dataclass(frozen=True)
class PvcCheck:
    name: str
    storage_class: str | None = None


@dataclass(frozen=True)
class HttpProbe:
    service: str
    port: int
    path: str
    body_regex: str


@dataclass(frozen=True)
class SmokeProfile:
    app: str
    git_repository: str
    activation_template: str
    namespace: str
    kustomizations: tuple[str, ...]
    helm_releases: tuple[str, ...]
    services: tuple[str, ...]
    http_routes: tuple[str, ...]
    tls_routes: tuple[str, ...]
    secret_refs: tuple[str, ...]
    pvcs: tuple[PvcCheck, ...]
    http_probes: tuple[HttpProbe, ...]
    route_urls: tuple[str, ...]


def parse_duration(value: str) -> Duration:
    if not value:
        raise argparse.ArgumentTypeError("duration must not be empty")
    if value.isdigit():
        seconds = int(value)
        if seconds <= 0:
            raise argparse.ArgumentTypeError("duration must be greater than zero")
        return Duration(raw=f"{seconds}s", seconds=seconds)

    match = DURATION_PATTERN.fullmatch(value)
    if not match:
        raise argparse.ArgumentTypeError("duration must look like 300s, 10m, 1h, or 1h30m")

    seconds = (
        int(match.group("hours") or 0) * 3600
        + int(match.group("minutes") or 0) * 60
        + int(match.group("seconds") or 0)
    )
    if seconds <= 0:
        raise argparse.ArgumentTypeError("duration must be greater than zero")
    return Duration(raw=value, seconds=seconds)


def validate_app(app: str) -> str:
    from .profiles import supported_apps

    apps = supported_apps()
    if app not in apps:
        raise argparse.ArgumentTypeError(f"unsupported app {app!r}; supported apps: {', '.join(sorted(apps))}")
    return app


def validate_branch(branch: str) -> str:
    if not branch or branch.startswith("/") or branch.endswith("/") or "//" in branch:
        raise argparse.ArgumentTypeError("branch must be a non-empty Git branch name")
    if branch.startswith("-"):
        raise argparse.ArgumentTypeError("branch must not start with '-'")
    if ".." in branch or branch.endswith(".") or "@{" in branch:
        raise argparse.ArgumentTypeError("branch must be valid for git check-ref-format --branch")
    if not BRANCH_PATTERN.fullmatch(branch):
        raise argparse.ArgumentTypeError("branch may contain only letters, numbers, '.', '_', '-', and '/'")
    if any(part.startswith(".") or part.endswith(".lock") for part in branch.split("/")):
        raise argparse.ArgumentTypeError("branch contains an invalid path component")
    return branch


def validate_slug(slug: str) -> str:
    if not SLUG_PATTERN.fullmatch(slug):
        raise argparse.ArgumentTypeError(
            "slug must be a deterministic DNS-safe label: lowercase letters, numbers, hyphens, "
            "start and end with alphanumeric characters, and be at most 56 characters"
        )
    return slug


def config_from_args(args: argparse.Namespace) -> AppConfig:
    return AppConfig(
        app=args.app,
        branch=args.branch,
        slug=args.slug,
        kubeconfig=args.kubeconfig.expanduser(),
        timeout=args.timeout,
        push=args.push,
        terraform_apply=args.terraform_apply,
        include_cluster_base=args.include_cluster_base,
        keep=args.keep,
    )
