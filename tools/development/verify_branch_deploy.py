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
from typing import Callable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KUBECONFIG = Path("~/.kube/homelab-development.config").expanduser()
DEFAULT_TIMEOUT = "10m"
FLUX_NAMESPACE = "flux-system"
SUPPORTED_APPS = {"whoami"}
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
    if app not in SUPPORTED_APPS:
        raise argparse.ArgumentTypeError(f"unsupported app {app!r}; supported apps: {', '.join(sorted(SUPPORTED_APPS))}")
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify a whoami branch environment on the homelab development cluster."
    )
    parser.add_argument("--app", required=True, type=validate_app, choices=sorted(SUPPORTED_APPS))
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

    try:
        if config.push:
            push_branch(config, runner=runner, repo_root=repo_root)

        run_terraform(config, runner=runner, repo_root=repo_root)

        if config.include_cluster_base:
            verify_cluster_base(config, runner=runner)

        rendered = render_activation_template(
            template_text
            if template_text is not None
            else (repo_root / "kubernetes/clusters/development/branches/whoami-template.yaml").read_text(encoding="utf-8"),
            branch=config.branch,
            slug=config.slug,
        )
        apply_activation(config, rendered, runner=runner)
        activated = True

        reconcile_flux(config, runner=runner)
        assert_whoami(config, runner=runner)
    except BaseException as exc:
        failure = exc
    finally:
        if activated and not config.keep:
            try:
                cleanup_branch_environment(config, runner=runner)
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


def reconcile_flux(config: AppConfig, *, runner: Runner) -> None:
    run_command(
        flux(config, "reconcile", "source", "git", config.git_repository, "--namespace", FLUX_NAMESPACE, "--timeout", config.timeout.raw),
        runner=runner,
        timeout=config.timeout,
    )
    run_command(
        kubectl(
            config,
            "-n",
            FLUX_NAMESPACE,
            "wait",
            f"gitrepository.source.toolkit.fluxcd.io/{config.git_repository}",
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


def assert_whoami(config: AppConfig, *, runner: Runner) -> None:
    name = config.namespace
    run_command(kubectl(config, "get", "namespace", name), runner=runner, timeout=config.timeout)
    wait_for_active_pods_ready(
        config,
        runner=runner,
        namespace=name,
        require_non_terminated=True,
        context=f"namespace {name}",
    )
    run_command(kubectl(config, "-n", name, "get", "service", name), runner=runner, timeout=config.timeout)
    route = run_command(
        kubectl(config, "-n", name, "get", "httproute", name, "-o", "json"),
        runner=runner,
        timeout=config.timeout,
        capture_output=True,
    )
    assert_httproute_ready(str(getattr(route, "stdout", "")), route_name=name)


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


def cleanup_branch_environment(config: AppConfig, *, runner: Runner) -> None:
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
            f"gitrepository.source.toolkit.fluxcd.io/{config.git_repository}",
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
