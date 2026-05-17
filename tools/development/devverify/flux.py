"""Flux command helpers for development verification."""

from __future__ import annotations

import json

from .config import DEVELOPMENT_BASE_KUSTOMIZATIONS, FLUX_NAMESPACE, AppConfig, Runner, SmokeProfile, VerificationError
from .kube import kubectl, run_command
from .profiles import render_profile_value


def flux(config: AppConfig, *args: str) -> list[str]:
    return ["flux", "--kubeconfig", str(config.kubeconfig), *args]


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
    from .checks import wait_for_active_pods_ready

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
