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
from typing import Any, Callable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR = REPO_ROOT / "tools" / "development" / "smoke-profiles"
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


@dataclass(frozen=True)
class SmokeProfile:
    app: str
    activation_template: str
    git_repository: str
    namespace: str
    require_active_pods: bool
    services: tuple[str, ...]
    httproutes: tuple[str, ...]
    configmaps: tuple[dict[str, Any], ...]
    cronjobs: tuple[dict[str, Any], ...]
    javascript_validity_jobs: tuple[dict[str, Any], ...]
    max_slug_length: int | None


class VerificationError(RuntimeError):
    """Raised when validation or a live verification step fails."""


Runner = Callable[..., subprocess.CompletedProcess[str] | SimpleNamespace]


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


def supported_apps(profile_dir: Path = PROFILE_DIR) -> set[str]:
    return {path.stem for path in profile_dir.glob("*.json")}


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


def load_profile(app: str, *, repo_root: Path = REPO_ROOT) -> SmokeProfile:
    path = repo_root / "tools" / "development" / "smoke-profiles" / f"{app}.json"
    if not path.exists() and repo_root != REPO_ROOT:
        path = REPO_ROOT / "tools" / "development" / "smoke-profiles" / f"{app}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VerificationError(f"smoke profile {app!r} not found at {path}") from exc
    except json.JSONDecodeError as exc:
        raise VerificationError(f"smoke profile {app!r} is not valid JSON: {exc}") from exc

    if data.get("app") != app:
        raise VerificationError(f"smoke profile {path} app does not match {app!r}")
    return SmokeProfile(
        app=app,
        activation_template=require_string(data, "activation_template", path),
        git_repository=str(data.get("git_repository", "branch-${branch_slug}")),
        namespace=require_string(data, "namespace", path),
        require_active_pods=bool(data.get("require_active_pods", False)),
        services=tuple(require_string_list(data.get("services", []), f"{path}: services")),
        httproutes=tuple(require_string_list(data.get("httproutes", []), f"{path}: httproutes")),
        configmaps=tuple(require_dict_list(data.get("configmaps", []), f"{path}: configmaps")),
        cronjobs=tuple(require_dict_list(data.get("cronjobs", []), f"{path}: cronjobs")),
        javascript_validity_jobs=tuple(
            require_dict_list(data.get("javascript_validity_jobs", []), f"{path}: javascript_validity_jobs")
        ),
        max_slug_length=optional_positive_int(data.get("max_slug_length"), f"{path}: max_slug_length"),
    )


def require_string(data: dict[str, Any], key: str, path: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"smoke profile {path} requires non-empty string key {key!r}")
    return value


def require_string_list(value: Any, context: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{context} must be a list of non-empty strings")
    return value


def require_dict_list(value: Any, context: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise VerificationError(f"{context} must be a list of objects")
    return value


def optional_positive_int(value: Any, context: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or value <= 0:
        raise VerificationError(f"{context} must be a positive integer")
    return value


def render_value(value: str, config: AppConfig) -> str:
    return (
        value.replace("${branch_name}", config.branch)
        .replace("${branch_slug}", config.slug)
        .replace("${app}", config.app)
        .replace("${namespace}", config.namespace)
    )


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
    profile: SmokeProfile | None = None

    try:
        profile = load_profile(config.app, repo_root=repo_root)
        validate_profile_slug(profile, config)
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

        reconcile_flux(config, profile=profile, runner=runner)
        assert_profile(config, profile, runner=runner)
    except BaseException as exc:
        failure = exc
    finally:
        if activated and not config.keep:
            try:
                cleanup_branch_environment(config, profile=profile, runner=runner)
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


def reconcile_flux(config: AppConfig, *, profile: SmokeProfile | None = None, runner: Runner) -> None:
    git_repository = profile_git_repository(config, profile)
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


def assert_profile(config: AppConfig, profile: SmokeProfile, *, runner: Runner) -> None:
    validate_profile_slug(profile, config)
    namespace = render_value(profile.namespace, config)
    run_command(kubectl(config, "get", "namespace", namespace), runner=runner, timeout=config.timeout)
    if profile.require_active_pods:
        wait_for_active_pods_ready(
            config,
            runner=runner,
            namespace=namespace,
            require_non_terminated=True,
            context=f"namespace {namespace}",
        )
    for service in profile.services:
        run_command(kubectl(config, "-n", namespace, "get", "service", render_value(service, config)), runner=runner, timeout=config.timeout)
    for route in profile.httproutes:
        route_name = render_value(route, config)
        route_result = run_command(
            kubectl(config, "-n", namespace, "get", "httproute", route_name, "-o", "json"),
            runner=runner,
            timeout=config.timeout,
            capture_output=True,
        )
        assert_httproute_ready(str(getattr(route_result, "stdout", "")), route_name=route_name)
    for configmap in profile.configmaps:
        assert_configmap(config, namespace, configmap, runner=runner)
    for cronjob in profile.cronjobs:
        assert_cronjob(config, namespace, cronjob, runner=runner)
    for job in profile.javascript_validity_jobs:
        run_javascript_validity_job(config, namespace, job, runner=runner)


def assert_whoami(config: AppConfig, *, runner: Runner) -> None:
    assert_profile(config, whoami_profile(), runner=runner)


def whoami_profile() -> SmokeProfile:
    return SmokeProfile(
        app="whoami",
        activation_template="kubernetes/clusters/development/branches/whoami-template.yaml",
        git_repository="branch-${branch_slug}",
        namespace="whoami-${branch_slug}",
        require_active_pods=True,
        services=("whoami-${branch_slug}",),
        httproutes=("whoami-${branch_slug}",),
        configmaps=(),
        cronjobs=(),
        javascript_validity_jobs=(),
        max_slug_length=56,
    )


def validate_profile_slug(profile: SmokeProfile, config: AppConfig) -> None:
    if profile.max_slug_length is not None and len(config.slug) > profile.max_slug_length:
        raise VerificationError(
            f"slug {config.slug!r} is too long for {profile.app}; maximum length is {profile.max_slug_length}"
        )


def assert_configmap(config: AppConfig, namespace: str, check: dict[str, Any], *, runner: Runner) -> None:
    name = render_value(require_check_string(check, "name", "ConfigMap check"), config)
    result = get_json_resource(config, namespace, "configmap", name, runner=runner)
    data = result.get("data")
    if not isinstance(data, dict):
        raise VerificationError(f"ConfigMap {namespace}/{name} has no data")
    for key in require_string_list(check.get("required_keys", []), f"ConfigMap {namespace}/{name} required_keys"):
        if key not in data:
            raise VerificationError(f"ConfigMap {namespace}/{name} missing required key {key!r}")


def assert_cronjob(config: AppConfig, namespace: str, check: dict[str, Any], *, runner: Runner) -> None:
    name = render_value(require_check_string(check, "name", "CronJob check"), config)
    cronjob = get_json_resource(config, namespace, "cronjob", name, runner=runner)
    if check.get("suspend") is not None and cronjob.get("spec", {}).get("suspend") is not bool(check["suspend"]):
        raise VerificationError(f"CronJob {namespace}/{name} suspend did not equal {bool(check['suspend'])}")

    pod_spec = cronjob.get("spec", {}).get("jobTemplate", {}).get("spec", {}).get("template", {}).get("spec", {})
    if not isinstance(pod_spec, dict):
        raise VerificationError(f"CronJob {namespace}/{name} has no pod template spec")
    containers = pod_spec.get("containers")
    if not isinstance(containers, list) or not containers:
        raise VerificationError(f"CronJob {namespace}/{name} has no containers")
    container = containers[0]
    if not isinstance(container, dict):
        raise VerificationError(f"CronJob {namespace}/{name} first container is not an object")

    for volume_name, configmap_name in check.get("configmap_volumes", {}).items():
        assert_configmap_volume(pod_spec, volume_name, render_value(str(configmap_name), config), cronjob_name=f"{namespace}/{name}")
    for env_name, env_value in check.get("env", {}).items():
        assert_container_env(container, str(env_name), render_value(str(env_value), config), cronjob_name=f"{namespace}/{name}")


def assert_configmap_volume(pod_spec: dict[str, Any], volume_name: str, configmap_name: str, *, cronjob_name: str) -> None:
    volumes = pod_spec.get("volumes")
    if not isinstance(volumes, list):
        raise VerificationError(f"CronJob {cronjob_name} has no volumes")
    for volume in volumes:
        if isinstance(volume, dict) and volume.get("name") == volume_name:
            actual = volume.get("configMap", {}).get("name")
            if actual == configmap_name:
                return
            raise VerificationError(f"CronJob {cronjob_name} volume {volume_name!r} references {actual!r}, not {configmap_name!r}")
    raise VerificationError(f"CronJob {cronjob_name} missing volume {volume_name!r}")


def assert_container_env(container: dict[str, Any], name: str, value: str, *, cronjob_name: str) -> None:
    env = container.get("env")
    if not isinstance(env, list):
        raise VerificationError(f"CronJob {cronjob_name} container has no env list")
    for item in env:
        if isinstance(item, dict) and item.get("name") == name:
            if item.get("value") == value:
                return
            raise VerificationError(f"CronJob {cronjob_name} env {name!r} is {item.get('value')!r}, not {value!r}")
    raise VerificationError(f"CronJob {cronjob_name} missing env {name!r}")


def run_javascript_validity_job(config: AppConfig, namespace: str, check: dict[str, Any], *, runner: Runner) -> None:
    cronjob_name = render_value(require_check_string(check, "cronjob", "JavaScript validity job"), config)
    job_name = render_value(require_check_string(check, "name", "JavaScript validity job"), config)
    command = require_check_string(check, "command", "JavaScript validity job")
    cronjob = get_json_resource(config, namespace, "cronjob", cronjob_name, runner=runner)
    job = job_from_cronjob(cronjob, namespace=namespace, job_name=job_name, command=command)
    failure: BaseException | None = None

    try:
        run_command(
            kubectl(config, "apply", "-f", "-"),
            runner=runner,
            timeout=config.timeout,
            input_text=json.dumps(job),
        )
        run_command(
            kubectl(config, "-n", namespace, "wait", f"job/{job_name}", "--for=condition=Complete", f"--timeout={config.timeout.raw}"),
            runner=runner,
            timeout=config.timeout,
        )
    except BaseException as exc:
        failure = exc
        logs = run_command(
            kubectl(config, "-n", namespace, "logs", f"job/{job_name}", "--all-containers=true", "--tail=200"),
            runner=runner,
            timeout=config.timeout,
            capture_output=True,
            success_codes=(0, 1),
        )
        output = str(getattr(logs, "stdout", "")).strip()
        raise VerificationError(f"JavaScript validity Job {namespace}/{job_name} failed: {output or failure}") from exc
    finally:
        try:
            run_command(
                kubectl(
                    config,
                    "-n",
                    namespace,
                    "delete",
                    f"job/{job_name}",
                    "--ignore-not-found=true",
                    "--wait=true",
                    f"--timeout={config.timeout.raw}",
                ),
                runner=runner,
                timeout=config.timeout,
            )
        except BaseException as cleanup_exc:
            if failure is None:
                raise cleanup_exc
            print(f"JavaScript validity Job cleanup failed after primary error: {cleanup_exc}", file=sys.stderr)


def job_from_cronjob(cronjob: dict[str, Any], *, namespace: str, job_name: str, command: str) -> dict[str, Any]:
    job_spec = cronjob.get("spec", {}).get("jobTemplate", {}).get("spec")
    if not isinstance(job_spec, dict):
        raise VerificationError("CronJob has no job template spec")
    spec = json.loads(json.dumps(job_spec))
    pod_spec = spec.get("template", {}).get("spec", {})
    containers = pod_spec.get("containers")
    if not isinstance(containers, list) or not containers or not isinstance(containers[0], dict):
        raise VerificationError("CronJob job template has no first container")
    env = containers[0].setdefault("env", [])
    if not isinstance(env, list):
        raise VerificationError("CronJob first container env is not a list")
    env[:] = [item for item in env if not (isinstance(item, dict) and item.get("name") == "SMOKE_PLAYWRIGHT_COMMAND")]
    env.append({"name": "SMOKE_PLAYWRIGHT_COMMAND", "value": command})
    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": job_name,
            "namespace": namespace,
            "labels": {
                "app.kubernetes.io/name": "synthetic-smoke",
                "app.kubernetes.io/component": "javascript-validity",
            },
        },
        "spec": spec,
    }


def require_check_string(check: dict[str, Any], key: str, context: str) -> str:
    value = check.get(key)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{context} requires non-empty string key {key!r}")
    return value


def get_json_resource(config: AppConfig, namespace: str, kind: str, name: str, *, runner: Runner) -> dict[str, Any]:
    result = run_command(
        kubectl(config, "-n", namespace, "get", kind, name, "-o", "json"),
        runner=runner,
        timeout=config.timeout,
        capture_output=True,
    )
    try:
        resource = json.loads(str(getattr(result, "stdout", "")))
    except json.JSONDecodeError as exc:
        raise VerificationError(f"{kind} {namespace}/{name} did not return valid JSON: {exc}") from exc
    if not isinstance(resource, dict):
        raise VerificationError(f"{kind} {namespace}/{name} did not return a JSON object")
    return resource


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


def parse_pods(pods_json: str, *, context: str) -> list[dict[str, Any]]:
    try:
        pod_list = json.loads(pods_json)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"{context} pods did not return valid JSON: {exc}") from exc

    items = pod_list.get("items")
    if not isinstance(items, list):
        raise VerificationError(f"{context} pods JSON did not contain an items list")
    return [pod for pod in items if isinstance(pod, dict)]


def is_pod_deleting(pod: dict[str, Any]) -> bool:
    metadata = pod.get("metadata", {})
    return isinstance(metadata, dict) and bool(metadata.get("deletionTimestamp"))


def pod_phase(pod: dict[str, Any]) -> str:
    status = pod.get("status", {})
    if not isinstance(status, dict):
        return ""
    phase = status.get("phase")
    return str(phase) if phase is not None else ""


def pod_name(pod: dict[str, Any]) -> str:
    metadata = pod.get("metadata", {})
    if not isinstance(metadata, dict):
        raise VerificationError("pod did not include metadata")
    name = metadata.get("name")
    if not name:
        raise VerificationError("pod did not include metadata.name")
    return str(name)


def pod_namespace_name(pod: dict[str, Any], *, default: str | None) -> str | None:
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


def profile_git_repository(config: AppConfig, profile: SmokeProfile | None) -> str:
    if profile is None:
        return config.git_repository
    return render_value(profile.git_repository, config)


def cleanup_branch_environment(config: AppConfig, *, profile: SmokeProfile | None = None, runner: Runner) -> None:
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
            f"gitrepository.source.toolkit.fluxcd.io/{profile_git_repository(config, profile)}",
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
