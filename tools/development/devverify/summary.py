"""What a smoke run checked and how it went, for the GitHub job summary.

GitHub renders the Markdown appended to $GITHUB_STEP_SUMMARY on the run page, so a
result can be read there without opening the log. Outside Actions nothing is written.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Mapping

from .config import AppConfig, SmokeProfile
from .profiles import render_profile_value


def step_summary_path(env: Mapping[str, str] = os.environ) -> Path | None:
    value = env.get("GITHUB_STEP_SUMMARY", "")
    return Path(value) if value else None


def cell(text: str) -> str:
    """One table cell: a single line, pipes escaped, long errors cut."""
    flat = " ".join(str(text).split()).replace("|", "\\|")
    return flat if len(flat) <= 300 else flat[:297] + "..."


class Stages:
    """Records each stage of a run as passed or failed, in order."""

    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        try:
            yield
        except BaseException as exc:
            self.rows.append((name, "failed", str(exc) or type(exc).__name__))
            raise
        self.rows.append((name, "passed", ""))

    @property
    def failed(self) -> bool:
        return any(result == "failed" for _, result, _ in self.rows)

    def table(self, not_reached: tuple[str, ...] = ()) -> str:
        done = {name for name, _, _ in self.rows}
        rows = self.rows + [(name, "not reached", "") for name in not_reached if name not in done]
        lines = ["| Stage | Result | Detail |", "| --- | --- | --- |"]
        lines += [f"| {cell(name)} | {result} | {cell(detail)} |" for name, result, detail in rows]
        return "\n".join(lines)


def append(path: Path | None, markdown: str) -> None:
    if path is None:
        return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(markdown.rstrip("\n") + "\n\n")


def profile_checks(config: AppConfig, profile: SmokeProfile) -> list[str]:
    """The checks the profile asks for, rendered for this branch, in the order they run."""

    def value(template: str, field: str) -> str:
        return render_profile_value(template, config=config, field=field)

    namespace = value(profile.namespace, "namespace")
    checks = [f"Namespace `{namespace}` exists"]
    checks += [f"Kustomization `{value(k, 'kustomization')}` Ready" for k in profile.kustomizations]
    checks += [f"Secret `{value(s, 'secretRef')}` exists" for s in profile.secret_refs]
    checks += [f"HelmRelease `{value(h, 'helmRelease')}` Ready" for h in profile.helm_releases]
    checks.append(f"All pods in `{namespace}` Ready")
    for pvc in profile.pvcs:
        storage = f" on `{pvc.storage_class}`" if pvc.storage_class else ""
        checks.append(f"PVC `{value(pvc.name, 'pvc')}` Bound{storage}")
    checks += [f"Service `{value(s, 'service')}` exists" for s in profile.services]
    checks += [f"HTTPRoute `{value(r, 'httpRoute')}` accepted by its Gateway" for r in profile.http_routes]
    checks += [f"TLSRoute `{value(r, 'tlsRoute')}` accepted by its Gateway" for r in profile.tls_routes]
    for probe in profile.http_probes:
        service = value(probe.service, "httpProbe.service")
        checks.append(f"GET `http://{service}:{probe.port}{probe.path}` returns 2xx with a body matching `{probe.body_regex}`")
    if config.browser and profile.browser is not None:
        checks.append(f"Browser test `{profile.browser.spec}` passes through the Gateway")
    return checks


def verify_report(config: AppConfig, profile: SmokeProfile, stages: Stages, planned: tuple[str, ...]) -> str:
    outcome = "FAILED" if stages.failed else "passed"
    checks = "\n".join(f"- {line}" for line in profile_checks(config, profile))
    return (
        f"### Smoke `{config.app}` from `{config.branch}` (`{config.slug}`): {outcome}\n\n"
        f"{stages.table(planned)}\n\n"
        f"<details><summary>What \"App checks\" covers</summary>\n\n{checks}\n\n</details>"
    )
