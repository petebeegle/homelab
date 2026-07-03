"""Smoke profile loading and template value helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from .config import AppConfig, HttpProbe, PROFILE_DIR, PvcCheck, SmokeProfile, VerificationError


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
        kustomizations=tuple(_string_list(checks.get("kustomizations", []), f"{path}:checks.kustomizations")),
        helm_releases=tuple(_string_list(checks.get("helmReleases", []), f"{path}:checks.helmReleases")),
        services=tuple(_string_list(checks.get("services", []), f"{path}:checks.services")),
        http_routes=tuple(_string_list(checks.get("httpRoutes", []), f"{path}:checks.httpRoutes")),
        tls_routes=tuple(_string_list(checks.get("tlsRoutes", []), f"{path}:checks.tlsRoutes")),
        secret_refs=tuple(_string_list(checks.get("secretRefs", []), f"{path}:checks.secretRefs")),
        pvcs=tuple(_pvc_checks(checks.get("pvcs", []), path)),
        http_probes=tuple(_http_probes(checks.get("httpProbes", []), path)),
        route_urls=tuple(_string_list(raw.get("routeUrls", []), f"{path}:routeUrls")),
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


def render_profile_value(value: str, *, config: AppConfig, field: str) -> str:
    rendered = (
        value.replace("${branch_slug}", config.slug)
        .replace("${branch_name}", config.branch)
        .replace("${app}", config.app)
    )
    if "${" in rendered:
        raise VerificationError(f"profile field {field} has an unsubstituted placeholder: {value}")
    return rendered


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
