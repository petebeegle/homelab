#!/usr/bin/env python3
"""Verify an app-scoped branch deployment on the development cluster."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR = Path(__file__).resolve().parent / "smoke-profiles"
DEFAULT_KUBECONFIG = Path("~/.kube/homelab-development.config").expanduser()
DEFAULT_TIMEOUT = "10m"
FLUX_NAMESPACE = "flux-system"
DEVELOPMENT_BASE_KUSTOMIZATIONS = (
    "crds",
    "cert-manager",
    "nfs-csi",
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
    helm_releases: tuple[str, ...]
    services: tuple[str, ...]
    http_routes: tuple[str, ...]
    pvcs: tuple[PvcCheck, ...]
    http_probes: tuple[HttpProbe, ...]


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


def render_activation_template(template_text: str, *, branch: str, slug: str) -> str:
    validate_branch(branch)
    validate_slug(slug)

    rendered = template_text.replace("${branch_name}", branch).replace("${branch_slug}", slug)
    rendered = re.sub(r"(^\s*suspend:\s*)true(\s*)$", r"\1false\2", rendered, flags=re.MULTILINE)
    if "${" in rendered:
        raise VerificationError("rendered activation still contains an unsubstituted placeholder")
    if rendered.count("suspend: false") < 2:
        raise VerificationError("rendered activation did not unsuspend both Flux resources")
    return rendered


def load_smoke_profiles(profile_dir: Path = PROFILE_DIR) -> dict[str, SmokeProfile]:
    profiles: dict[str, SmokeProfile] = {}
    if not profile_dir.is_dir():
        raise VerificationError(f"smoke profile directory not found: {profile_dir}")

    for path in sorted(profile_dir.glob("*.json")):
        profile = load_smoke_profile_file(path)
        if profile.app in profiles:
            raise VerificationError(f"duplicate smoke profile for app {profile.app!r}")
        profiles[profile.app] = profile
    if not profiles:
        raise VerificationError(f"no smoke profiles found in {profile_dir}")
    return profiles


def load_smoke_profile_file(path: Path) -> SmokeProfile:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise VerificationError(f"smoke profile {path} is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise VerificationError(f"smoke profile {path} must be a JSON object")

    checks = _mapping(raw.get("checks", {}), f"{path}:checks")
    app = _required_string(raw, "app", path)
    profile = SmokeProfile(
        app=app,
        git_repository=raw.get("gitRepository") if isinstance(raw.get("gitRepository"), str) else "branch-${branch_slug}",
        activation_template=_required_string(raw, "activationTemplate", path),
        namespace=_required_string(raw, "namespace", path),
        helm_releases=tuple(_string_list(checks.get("helmReleases", []), f"{path}:checks.helmReleases")),
        services=tuple(_string_list(checks.get("services", []), f"{path}:checks.services")),
        http_routes=tuple(_string_list(checks.get("httpRoutes", []), f"{path}:checks.httpRoutes")),
        pvcs=tuple(_pvc_checks(checks.get("pvcs", []), path)),
        http_probes=tuple(_http_probes(checks.get("httpProbes", []), path)),
    )
    return profile


def load_smoke_profile(app: str, profile_dir: Path = PROFILE_DIR) -> SmokeProfile:
    profiles = load_smoke_profiles(profile_dir)
    try:
        return profiles[app]
    except KeyError as exc:
        raise VerificationError(f"unsupported app {app!r}; supported apps: {', '.join(sorted(profiles))}") from exc


def supported_apps(profile_dir: Path = PROFILE_DIR) -> frozenset[str]:
    try:
        return frozenset(load_smoke_profiles(profile_dir))
    except VerificationError:
        return frozenset()


def _required_string(raw: Mapping[str, object], key: str, path: Path) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"smoke profile {path} field {key!r} must be a non-empty string")
    return value


def _mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise VerificationError(f"{field} must be an object")
    return value


def _string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{field} must be a list of non-empty strings")
    return list(value)


def _pvc_checks(value: object, path: Path) -> list[PvcCheck]:
    if not isinstance(value, list):
        raise VerificationError(f"{path}:checks.pvcs must be a list")
    checks: list[PvcCheck] = []
    for index, item in enumerate(value):
        field = f"{path}:checks.pvcs[{index}]"
        raw = _mapping(item, field)
        checks.append(
            PvcCheck(
                name=_required_string(raw, "name", path),
                storage_class=raw.get("storageClass") if isinstance(raw.get("storageClass"), str) else None,
            )
        )
    return checks


def _http_probes(value: object, path: Path) -> list[HttpProbe]:
    if not isinstance(value, list):
        raise VerificationError(f"{path}:checks.httpProbes must be a list")
    probes: list[HttpProbe] = []
    for index, item in enumerate(value):
        field = f"{path}:checks.httpProbes[{index}]"
        raw = _mapping(item, field)
        port = raw.get("port")
        if not isinstance(port, int) or port <= 0:
            raise VerificationError(f"{field}.port must be a positive integer")
        probes.append(
            HttpProbe(
                service=_required_string(raw, "service", path),
                port=port,
                path=_required_string(raw, "path", path),
                body_regex=_required_string(raw, "bodyRegex", path),
            )
        )
    return probes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify an app branch environment on the homelab development cluster."
    )
    parser.add_argument("--app", required=True, type=validate_app, choices=sorted(supported_apps()))
    parser.add_argument("--branch", required=True, type=validate_branch)
    parser.add_argument("--slug", required=True, type=validate_slug)
    parser.add_argument("--push", action="store_true", help="Push current HEAD to origin as --branch before activation.")
    parser.add_argument("--terraform-apply", action="store_true", help="Run terraform apply after a successful plan.")
    parser.add_argument(
        "--include-cluster-base",
        action="store_true",
        help="Temporarily reconcile the development base from --branch before branch app verification.",
    )
    parser.add_argument("--kubeconfig", type=Path, default=DEFAULT_KUBECONFIG)
    parser.add_argument("--timeout", type=parse_duration, default=parse_duration(DEFAULT_TIMEOUT))
    parser.add_argument("--keep", action="store_true", help="Keep branch Flux resources for debugging.")
    return parser


def run_acceptance(
    config: AppConfig,
    *,
    runner: Runner = subprocess.run,
    repo_root: Path = REPO_ROOT,
    template_text: str | None = None,
) -> None:
    activated = False
    failure: BaseException | None = None
    profile = load_smoke_profile(config.app)

    try:
        if config.push:
            push_branch(config, runner=runner, repo_root=repo_root)

        run_terraform(config, runner=runner, repo_root=repo_root)

        if config.include_cluster_base:
            verify_cluster_base(config, runner=runner)

        rendered = render_activation_template(
            template_text
            if template_text is not None
            else (repo_root / profile.activation_template).read_text(encoding="utf-8"),
            branch=config.branch,
            slug=config.slug,
        )
        apply_activation(config, rendered, runner=runner)
        activated = True

        reconcile_flux(config, profile, runner=runner)
        assert_smoke_profile(config, profile, runner=runner)
    except BaseException as exc:
        failure = exc
    finally:
        if activated and not config.keep:
            try:
                cleanup_branch_environment(config, profile, runner=runner)
            except BaseException as cleanup_exc:
                if failure is None:
                    failure = cleanup_exc
                else:
                    print(f"cleanup failed after primary error: {cleanup_exc}", file=sys.stderr)

    if failure is not None:
        raise failure


def push_branch(config: AppConfig, *, runner: Runner, repo_root: Path) -> None:
    run_command(
        ["git", "push", "origin", f"HEAD:refs/heads/{config.branch}"],
        runner=runner,
        cwd=repo_root,
        timeout=config.timeout,
    )


def run_terraform(config: AppConfig, *, runner: Runner, repo_root: Path) -> None:
    terraform_dir = "terraform/development"
    terraform = "terraform"
    run_command(
        [terraform, f"-chdir={terraform_dir}", "init", "-input=false", "-no-color"],
        runner=runner,
        cwd=repo_root,
        timeout=config.timeout,
    )
    run_command(
        [terraform, f"-chdir={terraform_dir}", "validate", "-no-color"],
        runner=runner,
        cwd=repo_root,
        timeout=config.timeout,
    )
    run_command(
        [terraform, f"-chdir={terraform_dir}", "plan", "-detailed-exitcode", "-input=false", "-no-color"],
        runner=runner,
        cwd=repo_root,
        timeout=config.timeout,
        success_codes=(0, 2),
    )
    if config.terraform_apply:
        run_command(
            [terraform, f"-chdir={terraform_dir}", "apply", "-input=false", "-no-color", "-auto-approve"],
            runner=runner,
            cwd=repo_root,
            timeout=config.timeout,
        )


def apply_activation(config: AppConfig, rendered: str, *, runner: Runner) -> None:
    run_command(
        kubectl(config, "apply", "-f", "-"),
        runner=runner,
        timeout=config.timeout,
        input_text=rendered,
    )


def reconcile_flux(config: AppConfig, profile: SmokeProfile, *, runner: Runner) -> None:
    git_repository = render_profile_value(profile.git_repository, config=config, field="gitRepository")
    run_command(
        flux(config, "reconcile", "source", "git", git_repository, "--namespace", FLUX_NAMESPACE, "--timeout", config.timeout.raw),
        runner=runner,
        timeout=config.timeout,
    )
    run_command(
        kubectl(
            config,
            "-n",
            FLUX_NAMESPACE,
            "wait",
            f"gitrepository.source.toolkit.fluxcd.io/{git_repository}",
            "--for=condition=Ready",
            f"--timeout={config.timeout.raw}",
        ),
        runner=runner,
        timeout=config.timeout,
    )
    run_command(
        flux(
            config,
            "reconcile",
            "kustomization",
            config.kustomization,
            "--namespace",
            FLUX_NAMESPACE,
            "--with-source",
            "--timeout",
            config.timeout.raw,
        ),
        runner=runner,
        timeout=config.timeout,
    )
    run_command(
        kubectl(
            config,
            "-n",
            FLUX_NAMESPACE,
            "wait",
            f"kustomization.kustomize.toolkit.fluxcd.io/{config.kustomization}",
            "--for=condition=Ready",
            f"--timeout={config.timeout.raw}",
        ),
        runner=runner,
        timeout=config.timeout,
    )


def verify_cluster_base(config: AppConfig, *, runner: Runner) -> None:
    failure: BaseException | None = None
    try:
        pin_flux_system_source(config, branch=config.branch, runner=runner)
        reconcile_flux_system_source(config, runner=runner)
        reconcile_flux_kustomization(config, "flux-system", runner=runner)

        pin_flux_system_source(config, branch=config.branch, runner=runner)
        reconcile_flux_system_source(config, runner=runner)
        for kustomization in DEVELOPMENT_BASE_KUSTOMIZATIONS:
            reconcile_flux_kustomization(config, kustomization, runner=runner)

        wait_for_active_pods_ready(
            config,
            runner=runner,
            namespace=None,
            require_non_terminated=False,
            context="development cluster",
        )
    except BaseException as exc:
        failure = exc
    finally:
        try:
            restore_flux_system_source(config, runner=runner)
        except BaseException as restore_exc:
            if failure is None:
                failure = restore_exc
            else:
                failure = VerificationError(f"{failure}; additionally failed to restore flux-system GitRepository: {restore_exc}")

    if failure is not None:
        raise failure


def pin_flux_system_source(config: AppConfig, *, branch: str, runner: Runner) -> None:
    patch = json.dumps({"spec": {"ref": {"branch": branch}}})
    run_command(
        kubectl(
            config,
            "-n",
            FLUX_NAMESPACE,
            "patch",
            "gitrepository.source.toolkit.fluxcd.io/flux-system",
            "--type=merge",
            "-p",
            patch,
        ),
        runner=runner,
        timeout=config.timeout,
    )


def reconcile_flux_system_source(config: AppConfig, *, runner: Runner) -> None:
    run_command(
        flux(
            config,
            "reconcile",
            "source",
            "git",
            "flux-system",
            "--namespace",
            FLUX_NAMESPACE,
            "--timeout",
            config.timeout.raw,
        ),
        runner=runner,
        timeout=config.timeout,
    )
    run_command(
        kubectl(
            config,
            "-n",
            FLUX_NAMESPACE,
            "wait",
            "gitrepository.source.toolkit.fluxcd.io/flux-system",
            "--for=condition=Ready",
            f"--timeout={config.timeout.raw}",
        ),
        runner=runner,
        timeout=config.timeout,
    )


def restore_flux_system_source(config: AppConfig, *, runner: Runner) -> None:
    pin_flux_system_source(config, branch="main", runner=runner)
    reconcile_flux_system_source(config, runner=runner)
    reconcile_flux_kustomization(config, "flux-system", runner=runner)


def reconcile_flux_kustomization(config: AppConfig, name: str, *, runner: Runner) -> None:
    run_command(
        flux(
            config,
            "reconcile",
            "kustomization",
            name,
            "--namespace",
            FLUX_NAMESPACE,
            "--with-source",
            "--timeout",
            config.timeout.raw,
        ),
        runner=runner,
        timeout=config.timeout,
    )
    run_command(
        kubectl(
            config,
            "-n",
            FLUX_NAMESPACE,
            "wait",
            f"kustomization.kustomize.toolkit.fluxcd.io/{name}",
            "--for=condition=Ready",
            f"--timeout={config.timeout.raw}",
        ),
        runner=runner,
        timeout=config.timeout,
    )


def assert_smoke_profile(config: AppConfig, profile: SmokeProfile, *, runner: Runner) -> None:
    name = render_profile_value(profile.namespace, config=config, field="namespace")
    run_command(kubectl(config, "get", "namespace", name), runner=runner, timeout=config.timeout)
    for helm_release in profile.helm_releases:
        resource_name = render_profile_value(helm_release, config=config, field="helmRelease")
        run_command(
            kubectl(
                config,
                "-n",
                name,
                "wait",
                f"helmrelease.helm.toolkit.fluxcd.io/{resource_name}",
                "--for=condition=Ready",
                f"--timeout={config.timeout.raw}",
            ),
            runner=runner,
            timeout=config.timeout,
        )
    wait_for_active_pods_ready(
        config,
        runner=runner,
        namespace=name,
        require_non_terminated=True,
        context=f"namespace {name}",
    )
    for pvc in profile.pvcs:
        resource_name = render_profile_value(pvc.name, config=config, field="pvc")
        assert_pvc_ready(config, namespace=name, pvc_name=resource_name, storage_class=pvc.storage_class, runner=runner)
    for service in profile.services:
        resource_name = render_profile_value(service, config=config, field="service")
        run_command(kubectl(config, "-n", name, "get", "service", resource_name), runner=runner, timeout=config.timeout)
    for http_route in profile.http_routes:
        resource_name = render_profile_value(http_route, config=config, field="httpRoute")
        route = run_command(
            kubectl(config, "-n", name, "get", "httproute", resource_name, "-o", "json"),
            runner=runner,
            timeout=config.timeout,
            capture_output=True,
        )
        assert_httproute_ready(str(getattr(route, "stdout", "")), route_name=resource_name)
    for index, probe in enumerate(profile.http_probes):
        run_command(
            build_http_probe_command(config, namespace=name, probe=probe, probe_index=index, total_probes=len(profile.http_probes)),
            runner=runner,
            timeout=config.timeout,
        )


def assert_whoami(config: AppConfig, *, runner: Runner) -> None:
    assert_smoke_profile(config, load_smoke_profile("whoami"), runner=runner)


def render_profile_value(value: str, *, config: AppConfig, field: str) -> str:
    rendered = (
        value.replace("${branch_slug}", config.slug)
        .replace("${branch_name}", config.branch)
        .replace("${app}", config.app)
    )
    if "${" in rendered:
        raise VerificationError(f"profile field {field} has an unsubstituted placeholder: {value}")
    return rendered


def assert_pvc_ready(
    config: AppConfig,
    *,
    namespace: str,
    pvc_name: str,
    storage_class: str | None,
    runner: Runner,
) -> None:
    pvc = run_command(
        kubectl(config, "-n", namespace, "get", "pvc", pvc_name, "-o", "json"),
        runner=runner,
        timeout=config.timeout,
        capture_output=True,
    )
    assert_pvc_bound(str(getattr(pvc, "stdout", "")), pvc_name=pvc_name, storage_class=storage_class)


def assert_pvc_bound(pvc_json: str, *, pvc_name: str, storage_class: str | None) -> None:
    try:
        pvc = json.loads(pvc_json)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"PVC {pvc_name} did not return valid JSON: {exc}") from exc

    phase = pvc.get("status", {}).get("phase")
    if phase != "Bound":
        raise VerificationError(f"PVC {pvc_name} is not Bound; observed phase {phase!r}")
    if storage_class is not None and pvc.get("spec", {}).get("storageClassName") != storage_class:
        observed = pvc.get("spec", {}).get("storageClassName")
        raise VerificationError(f"PVC {pvc_name} storageClassName is {observed!r}, expected {storage_class!r}")


def build_http_probe_command(
    config: AppConfig,
    *,
    namespace: str,
    probe: HttpProbe,
    probe_index: int,
    total_probes: int,
) -> list[str]:
    service = render_profile_value(probe.service, config=config, field="httpProbe.service")
    pod_name = f"probe-{config.slug}" if total_probes == 1 else f"p{probe_index}-{config.slug}"
    url = f"http://{service}.{namespace}.svc.cluster.local:{probe.port}{probe.path}"
    script = (
        "for attempt in $(seq 1 60); do "
        f"if body=$(curl -fsS --max-time 20 {shlex.quote(url)}); then "
        f"printf '%s' \"$body\" | grep -E {shlex.quote(probe.body_regex)} >/dev/null && exit 0; "
        "fi; "
        "sleep 5; "
        "done; "
        "exit 1"
    )
    return kubectl(
        config,
        "-n",
        namespace,
        "run",
        pod_name,
        "--image=curlimages/curl:8.16.0",
        "--restart=Never",
        "--rm=true",
        "--overrides",
        probe_pod_overrides(pod_name),
        "-i",
        "--quiet",
        "--command",
        "--",
        "sh",
        "-ec",
        script,
    )


def probe_pod_overrides(pod_name: str) -> str:
    return json.dumps(
        {
            "spec": {
                "securityContext": {
                    "runAsNonRoot": True,
                    "seccompProfile": {"type": "RuntimeDefault"},
                },
                "containers": [
                    {
                        "name": pod_name,
                        "securityContext": {
                            "allowPrivilegeEscalation": False,
                            "capabilities": {"drop": ["ALL"]},
                            "runAsNonRoot": True,
                        },
                    }
                ],
            }
        },
        separators=(",", ":"),
    )


def wait_for_active_pods_ready(
    config: AppConfig,
    *,
    runner: Runner,
    namespace: str | None,
    require_non_terminated: bool,
    context: str,
) -> None:
    if namespace is None:
        pod_list = run_command(
            kubectl(config, "get", "pods", "--all-namespaces", "-o", "json"),
            runner=runner,
            timeout=config.timeout,
            capture_output=True,
        )
    else:
        pod_list = run_command(
            kubectl(config, "-n", namespace, "get", "pods", "-o", "json"),
            runner=runner,
            timeout=config.timeout,
            capture_output=True,
        )

    pods = parse_pods(str(getattr(pod_list, "stdout", "")), context=context)
    non_terminated = [pod for pod in pods if not is_pod_deleting(pod) and pod_phase(pod) not in {"Succeeded", "Failed"}]
    if require_non_terminated and not non_terminated:
        raise VerificationError(f"{context} has no non-terminated pods")

    for pod in pods:
        if is_pod_deleting(pod) or pod_phase(pod) == "Succeeded":
            continue
        name = pod_name(pod)
        pod_namespace = pod_namespace_name(pod, default=namespace)
        if pod_namespace is None:
            raise VerificationError(f"{context} pod {name} did not include a namespace")
        run_command(
            kubectl(config, "-n", pod_namespace, "wait", f"pod/{name}", "--for=condition=Ready", f"--timeout={config.timeout.raw}"),
            runner=runner,
            timeout=config.timeout,
        )


def parse_pods(pods_json: str, *, context: str) -> list[dict[str, object]]:
    try:
        pod_list = json.loads(pods_json)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"{context} pods did not return valid JSON: {exc}") from exc

    items = pod_list.get("items")
    if not isinstance(items, list):
        raise VerificationError(f"{context} pods JSON did not contain an items list")
    return [pod for pod in items if isinstance(pod, dict)]


def is_pod_deleting(pod: dict[str, object]) -> bool:
    metadata = pod.get("metadata", {})
    return isinstance(metadata, dict) and bool(metadata.get("deletionTimestamp"))


def pod_phase(pod: dict[str, object]) -> str:
    status = pod.get("status", {})
    if not isinstance(status, dict):
        return ""
    phase = status.get("phase")
    return str(phase) if phase is not None else ""


def pod_name(pod: dict[str, object]) -> str:
    metadata = pod.get("metadata", {})
    if not isinstance(metadata, dict):
        raise VerificationError("pod did not include metadata")
    name = metadata.get("name")
    if not name:
        raise VerificationError("pod did not include metadata.name")
    return str(name)


def pod_namespace_name(pod: dict[str, object], *, default: str | None) -> str | None:
    metadata = pod.get("metadata", {})
    if not isinstance(metadata, dict):
        return default
    namespace = metadata.get("namespace")
    return str(namespace) if namespace else default


def assert_httproute_ready(route_json: str, *, route_name: str) -> None:
    try:
        route = json.loads(route_json)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"HTTPRoute {route_name} did not return valid JSON: {exc}") from exc

    parents = route.get("status", {}).get("parents", [])
    for parent in parents:
        conditions = parent.get("conditions", [])
        if all(
            any(condition.get("type") == condition_type and condition.get("status") == "True" for condition in conditions)
            for condition_type in ("Accepted", "ResolvedRefs")
        ):
            return
    raise VerificationError(f"HTTPRoute {route_name} has no parent with Accepted and ResolvedRefs conditions")


def cleanup_branch_environment(config: AppConfig, profile: SmokeProfile, *, runner: Runner) -> None:
    git_repository = render_profile_value(profile.git_repository, config=config, field="gitRepository")
    run_command(
        kubectl(
            config,
            "-n",
            FLUX_NAMESPACE,
            "delete",
            f"kustomization.kustomize.toolkit.fluxcd.io/{config.kustomization}",
            "--ignore-not-found=true",
            "--wait=true",
            f"--timeout={config.timeout.raw}",
        ),
        runner=runner,
        timeout=config.timeout,
    )
    run_command(
        kubectl(config, "wait", f"namespace/{config.namespace}", "--for=delete", f"--timeout={config.timeout.raw}"),
        runner=runner,
        timeout=config.timeout,
    )
    run_command(
        kubectl(
            config,
            "-n",
            FLUX_NAMESPACE,
            "delete",
            f"gitrepository.source.toolkit.fluxcd.io/{git_repository}",
            "--ignore-not-found=true",
            "--wait=true",
            f"--timeout={config.timeout.raw}",
        ),
        runner=runner,
        timeout=config.timeout,
    )


def kubectl(config: AppConfig, *args: str) -> list[str]:
    return ["kubectl", "--kubeconfig", str(config.kubeconfig), *args]


def flux(config: AppConfig, *args: str) -> list[str]:
    return ["flux", "--kubeconfig", str(config.kubeconfig), *args]


def run_command(
    args: Sequence[str],
    *,
    runner: Runner,
    timeout: Duration,
    cwd: Path | None = None,
    input_text: str | None = None,
    capture_output: bool = False,
    success_codes: tuple[int, ...] = (0,),
) -> subprocess.CompletedProcess[str] | SimpleNamespace:
    if not getattr(runner, "quiet", False):
        print("+ " + shlex.join(str(arg) for arg in args))
    try:
        result = runner(
            [str(arg) for arg in args],
            cwd=str(cwd) if cwd is not None else None,
            input=input_text,
            text=True,
            capture_output=capture_output,
            timeout=timeout.seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise VerificationError(f"command timed out after {timeout.raw}: {shlex.join(str(arg) for arg in args)}") from exc

    returncode = int(getattr(result, "returncode", 0))
    if returncode not in success_codes:
        raise VerificationError(
            f"command failed with exit code {returncode}: {shlex.join(str(arg) for arg in args)}"
        )
    return result


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = config_from_args(args)
    try:
        run_acceptance(config)
    except VerificationError as exc:
        print(f"verification failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
