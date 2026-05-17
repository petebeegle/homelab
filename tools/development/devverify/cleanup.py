"""Cleanup helpers for branch verification resources."""

from __future__ import annotations

from .config import FLUX_NAMESPACE, AppConfig, Runner, SmokeProfile
from .kube import kubectl, run_command
from .profiles import render_profile_value


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
