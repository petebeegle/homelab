"""Importable Foundry blue/green workflow package."""

from __future__ import annotations

from .cli import build_parser, dispatch, main
from .config import (
    APP_DIR,
    CONFIG_VERSION_GLOBS,
    DESCRIPTION,
    DEV_KUBECONFIG,
    EVIDENCE_PATH,
    FIXTURE_DIR,
    PRODUCTION_COMMANDS,
    ROOT,
)
from .errors import FoundryBlueGreenError
from .evidence import (
    config_version,
    read_evidence,
    rel,
    require_current_dev_rehearsal,
    require_development_kubeconfig,
    resolved_path,
    utc_now,
    write_json,
)
from .manifests import (
    blue_snapshot,
    ensure_green_prepared,
    green_deployment,
    green_preview_route,
    green_preview_service,
    green_pvc,
    validate_image,
    write_green_resources,
)
from .process import CommandResult, CommandRunner
from .state import (
    ensure_kustomization_resource,
    read,
    remove_file_if_exists,
    remove_kustomization_resource,
    replace_first_replicas,
    service_color,
    set_service_color,
    write,
)
from .workflow import (
    command_dev_rehearse,
    command_prepare,
    command_promote,
    command_retire,
    command_rollback,
    command_status,
)


__all__ = [
    "APP_DIR",
    "CONFIG_VERSION_GLOBS",
    "DESCRIPTION",
    "DEV_KUBECONFIG",
    "EVIDENCE_PATH",
    "FIXTURE_DIR",
    "PRODUCTION_COMMANDS",
    "ROOT",
    "CommandResult",
    "CommandRunner",
    "FoundryBlueGreenError",
    "blue_snapshot",
    "build_parser",
    "command_dev_rehearse",
    "command_prepare",
    "command_promote",
    "command_retire",
    "command_rollback",
    "command_status",
    "config_version",
    "dispatch",
    "ensure_green_prepared",
    "ensure_kustomization_resource",
    "green_deployment",
    "green_preview_route",
    "green_preview_service",
    "green_pvc",
    "main",
    "read",
    "read_evidence",
    "rel",
    "remove_file_if_exists",
    "remove_kustomization_resource",
    "replace_first_replicas",
    "require_current_dev_rehearsal",
    "require_development_kubeconfig",
    "resolved_path",
    "service_color",
    "set_service_color",
    "utc_now",
    "validate_image",
    "write",
    "write_green_resources",
    "write_json",
]
