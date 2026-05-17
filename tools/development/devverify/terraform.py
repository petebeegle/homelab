"""Terraform and Git helpers for branch deployment verification."""

from __future__ import annotations

from pathlib import Path

from .config import AppConfig, REPO_ROOT, Runner
from .kube import run_command


def push_branch(config: AppConfig, *, runner: Runner, repo_root: Path = REPO_ROOT) -> None:
    run_command(
        ["git", "push", "origin", f"HEAD:refs/heads/{config.branch}"],
        runner=runner,
        cwd=repo_root,
        timeout=config.timeout,
    )


def run_terraform(config: AppConfig, *, runner: Runner, repo_root: Path = REPO_ROOT) -> None:
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
