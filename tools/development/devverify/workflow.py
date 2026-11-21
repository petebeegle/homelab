"""Ordered acceptance workflow for development branch verification."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from .browser import preflight_browser, run_browser_smoke
from .checks import assert_smoke_profile
from .cleanup import cleanup_branch_environment
from .config import REPO_ROOT, AppConfig, Runner, VerificationError, validate_branch, validate_slug
from .flux import assert_dev_base_ready, reconcile_flux, verify_cluster_base
from .kube import apply_activation
from .profiles import load_smoke_profile
from .summary import Stages, append, verify_report
from .terraform import push_branch, run_terraform


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


def run_acceptance(
    config: AppConfig,
    *,
    runner: Runner = subprocess.run,
    repo_root: Path = REPO_ROOT,
    template_text: str | None = None,
    step_summary: Path | None = None,
) -> None:
    activated = False
    failure: BaseException | None = None
    profile = load_smoke_profile(config.app)
    stages = Stages()
    planned = tuple(
        name
        for name, wanted in (
            ("Browser preflight", config.browser),
            ("Development base healthy", config.ci),
            ("Push branch", config.push),
            ("Terraform", not config.ci),
            ("Cluster base from branch", config.include_cluster_base),
            ("Activate branch environment", True),
            ("Flux reconciled", True),
            ("App checks", True),
            ("Browser check", config.browser),
            ("Cleanup", not config.keep),
        )
        if wanted
    )

    try:
        if config.browser:
            with stages.stage("Browser preflight"):
                preflight_browser(config, profile, repo_root=repo_root)

        if config.ci:
            with stages.stage("Development base healthy"):
                assert_dev_base_ready(config, runner=runner)

        if config.push:
            with stages.stage("Push branch"):
                push_branch(config, runner=runner, repo_root=repo_root)

        if not config.ci:
            with stages.stage("Terraform"):
                run_terraform(config, runner=runner, repo_root=repo_root)

        if config.include_cluster_base:
            with stages.stage("Cluster base from branch"):
                verify_cluster_base(config, runner=runner, repo_root=repo_root)

        with stages.stage("Activate branch environment"):
            rendered = render_activation_template(
                template_text
                if template_text is not None
                else (repo_root / profile.activation_template).read_text(encoding="utf-8"),
                branch=config.branch,
                slug=config.slug,
            )
            apply_activation(config, rendered, runner=runner)
            activated = True

        with stages.stage("Flux reconciled"):
            reconcile_flux(config, profile, runner=runner)
        with stages.stage("App checks"):
            assert_smoke_profile(config, profile, runner=runner)

        if config.browser:
            with stages.stage("Browser check"):
                run_browser_smoke(config, profile, runner=runner, repo_root=repo_root)
    except BaseException as exc:
        failure = exc
    finally:
        if activated and not config.keep:
            try:
                with stages.stage("Cleanup"):
                    cleanup_branch_environment(config, profile, runner=runner)
            except BaseException as cleanup_exc:
                if failure is None:
                    failure = cleanup_exc
                else:
                    print(f"cleanup failed after primary error: {cleanup_exc}", file=sys.stderr)
        try:
            append(step_summary, verify_report(config, profile, stages, planned))
        except OSError as exc:
            print(f"could not write the job summary: {exc}", file=sys.stderr)

    if failure is not None:
        raise failure
