#!/usr/bin/env python3
"""Validate deterministic local workflow role attestations."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from validate_active_implementation import GENERIC_OWNER_AGENTS, parse_marker
from validate_implementation_plan import parse_plan


OWNER_REQUIRED_FIELDS = (
    "implementation",
    "branch",
    "base",
    "role",
    "agent_id",
    "clone_path",
    "created_at",
    "delegation_token",
    "delegation_token_path",
)
VERIFIER_REQUIRED_FIELDS = OWNER_REQUIRED_FIELDS + ("approved_head",)
DELEGATION_TOKEN_REQUIRED_FIELDS = (
    "delegation_token",
    "implementation",
    "role",
    "agent_id",
    "created_at",
)
GENERIC_IDENTITIES = GENERIC_OWNER_AGENTS
DELEGATION_TOKEN_ROOT = Path(".codex/tmp/delegation-tokens")


@dataclass(frozen=True)
class AttestationValidationResult:
    attestation: Mapping[str, str]
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_attestation(attestation_path: Path) -> dict[str, str]:
    """Parse the scalar-only YAML subset used by workflow attestations."""
    attestation: dict[str, str] = {}
    for lineno, raw_line in enumerate(attestation_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if raw_line.startswith(" "):
            raise ValueError(f"{attestation_path}:{lineno}: unsupported indentation")
        if ":" not in raw_line:
            raise ValueError(f"{attestation_path}:{lineno}: expected key: value")

        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = _strip_quotes(raw_value.strip())
        if not key:
            raise ValueError(f"{attestation_path}:{lineno}: key must not be empty")
        if key in attestation:
            raise ValueError(f"{attestation_path}:{lineno}: duplicate field {key}")
        attestation[key] = value
    return attestation


def validate_owner_attestation(
    attestation: Mapping[str, str],
    *,
    marker: Mapping[str, str],
    plan: Mapping[str, object] | None = None,
    delegation_token: Mapping[str, str] | None = None,
    current_root: Path | str | None = None,
    current_branch: str | None = None,
) -> AttestationValidationResult:
    errors: list[str] = []

    _require_fields(attestation, OWNER_REQUIRED_FIELDS, errors)
    _validate_common_identity(attestation, expected_role="implementation-agent", errors=errors)
    _validate_common_matches(
        attestation,
        marker=marker,
        fields=("implementation", "branch", "base", "clone_path"),
        errors=errors,
    )

    agent_id = attestation.get("agent_id", "")
    owner_agent = marker.get("owner_agent", "")
    if agent_id != owner_agent:
        errors.append(
            f"Field 'agent_id' must match active implementation marker owner_agent '{owner_agent}', got '{agent_id}'."
        )

    if marker.get("owner_role", "") and attestation.get("role", "") != marker.get("owner_role", ""):
        errors.append(
            "Field 'role' must match active implementation marker owner_role "
            f"'{marker.get('owner_role', '')}', got '{attestation.get('role', '')}'."
        )

    if plan is not None:
        for field in ("implementation", "branch", "base", "clone_path"):
            plan_value = _string(plan.get(field))
            attestation_value = attestation.get(field, "")
            if attestation_value != plan_value:
                errors.append(
                    f"Field '{field}' must match implementation plan value '{plan_value}', got '{attestation_value}'."
                )
        if agent_id != _string(plan.get("owner_agent")):
            errors.append(
                "Field 'agent_id' must match implementation plan owner_agent "
                f"'{_string(plan.get('owner_agent'))}', got '{agent_id}'."
            )

    _validate_current_context(attestation, current_root=current_root, current_branch=current_branch, errors=errors)
    _validate_delegation_token(
        attestation,
        delegation_token=delegation_token,
        expected_role="implementation-agent",
        errors=errors,
    )
    return AttestationValidationResult(attestation=attestation, errors=tuple(errors))


def validate_verifier_attestation(
    attestation: Mapping[str, str],
    *,
    marker: Mapping[str, str],
    owner_attestation: Mapping[str, str],
    owner_delegation_token: Mapping[str, str] | None = None,
    verifier_delegation_token: Mapping[str, str] | None = None,
    current_head: str,
    current_root: Path | str | None = None,
    current_branch: str | None = None,
) -> AttestationValidationResult:
    errors: list[str] = []

    owner_result = validate_owner_attestation(
        owner_attestation,
        marker=marker,
        delegation_token=owner_delegation_token,
        current_root=current_root,
        current_branch=current_branch,
    )
    errors.extend(f"Owner attestation: {error}" for error in owner_result.errors)

    _require_fields(attestation, VERIFIER_REQUIRED_FIELDS, errors)
    _validate_common_identity(attestation, expected_role="verifier-agent", errors=errors)
    _validate_common_matches(
        attestation,
        marker=marker,
        fields=("implementation", "branch", "base", "clone_path"),
        errors=errors,
    )

    verifier_agent = attestation.get("agent_id", "")
    owner_agent = owner_attestation.get("agent_id", "")
    if verifier_agent and owner_agent and verifier_agent == owner_agent:
        errors.append("Field 'agent_id' must differ from implementation owner agent_id.")

    approved_head = attestation.get("approved_head", "")
    if approved_head != current_head:
        errors.append(f"Field 'approved_head' must match current HEAD '{current_head}', got '{approved_head}'.")

    _validate_current_context(attestation, current_root=current_root, current_branch=current_branch, errors=errors)
    _validate_delegation_token(
        attestation,
        delegation_token=verifier_delegation_token,
        expected_role="verifier-agent",
        errors=errors,
    )

    owner_token = owner_attestation.get("delegation_token", "")
    verifier_token = attestation.get("delegation_token", "")
    if owner_token and verifier_token and owner_token == verifier_token:
        errors.append("Field 'delegation_token' must differ from implementation owner delegation_token.")

    owner_token_path = owner_attestation.get("delegation_token_path", "")
    verifier_token_path = attestation.get("delegation_token_path", "")
    if owner_token_path and verifier_token_path and owner_token_path == verifier_token_path:
        errors.append("Field 'delegation_token_path' must differ from implementation owner delegation_token_path.")

    return AttestationValidationResult(attestation=attestation, errors=tuple(errors))


def discover_git_root(cwd: Path) -> Path | None:
    return _git_output(["git", "rev-parse", "--show-toplevel"], cwd=cwd, as_path=True)


def discover_git_branch(cwd: Path) -> str | None:
    return _git_output(["git", "branch", "--show-current"], cwd=cwd)


def discover_git_head(cwd: Path) -> str | None:
    return _git_output(["git", "rev-parse", "HEAD"], cwd=cwd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate local workflow role attestations.")
    parser.add_argument("--kind", choices=("owner", "verifier"), required=True)
    parser.add_argument("--attestation", help="Path to the attestation file.")
    parser.add_argument("--marker", default=".codex/tmp/active-implementation")
    parser.add_argument("--plan", default=".codex/tmp/implementation-plan.yaml")
    parser.add_argument("--owner-attestation", default=".codex/tmp/implementation-owner-attestation.yaml")
    parser.add_argument("--root", help="Current repository root. Defaults to git rev-parse --show-toplevel.")
    parser.add_argument("--branch", help="Current branch. Defaults to git branch --show-current.")
    parser.add_argument("--head", help="Current HEAD SHA. Defaults to git rev-parse HEAD.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    marker_path = _path(args.marker)
    if not marker_path.is_file():
        print(f"Active implementation marker not found: {marker_path}", file=sys.stderr)
        return 1

    try:
        marker = parse_marker(marker_path)
    except (OSError, ValueError) as exc:
        print(f"Active implementation marker is invalid: {exc}", file=sys.stderr)
        return 1

    attestation_path = _path(
        args.attestation
        or (
            ".codex/tmp/implementation-owner-attestation.yaml"
            if args.kind == "owner"
            else ".codex/tmp/verifier-attestation.yaml"
        )
    )
    if not attestation_path.is_file():
        print(f"Workflow {args.kind} attestation not found: {attestation_path}", file=sys.stderr)
        return 1

    try:
        attestation = parse_attestation(attestation_path)
    except (OSError, ValueError) as exc:
        print(f"Workflow {args.kind} attestation is invalid: {exc}", file=sys.stderr)
        return 1

    current_root = Path(args.root) if args.root is not None else discover_git_root(Path.cwd())
    current_branch = args.branch if args.branch is not None else discover_git_branch(Path.cwd())

    if args.kind == "owner":
        plan_path = _path(args.plan)
        if not plan_path.is_file():
            print(f"Implementation plan not found: {plan_path}", file=sys.stderr)
            return 1
        try:
            plan = parse_plan(plan_path)
        except (OSError, ValueError) as exc:
            print(f"Implementation plan is invalid: {exc}", file=sys.stderr)
            return 1
        delegation_token = _load_delegation_token(attestation, current_root=current_root)
        result = validate_owner_attestation(
            attestation,
            marker=marker,
            plan=plan,
            delegation_token=delegation_token,
            current_root=current_root,
            current_branch=current_branch,
        )
    else:
        owner_path = _path(args.owner_attestation)
        if not owner_path.is_file():
            print(f"Workflow owner attestation not found: {owner_path}", file=sys.stderr)
            return 1
        try:
            owner_attestation = parse_attestation(owner_path)
        except (OSError, ValueError) as exc:
            print(f"Workflow owner attestation is invalid: {exc}", file=sys.stderr)
            return 1
        current_head = args.head if args.head is not None else discover_git_head(Path.cwd())
        if not current_head:
            print("Unable to determine current HEAD.", file=sys.stderr)
            return 1
        owner_delegation_token = _load_delegation_token(owner_attestation, current_root=current_root)
        verifier_delegation_token = _load_delegation_token(attestation, current_root=current_root)
        result = validate_verifier_attestation(
            attestation,
            marker=marker,
            owner_attestation=owner_attestation,
            owner_delegation_token=owner_delegation_token,
            verifier_delegation_token=verifier_delegation_token,
            current_head=current_head,
            current_root=current_root,
            current_branch=current_branch,
        )

    if result.ok:
        return 0

    print(f"Workflow {args.kind} attestation is invalid:", file=sys.stderr)
    for error in result.errors:
        print(f"  - {error}", file=sys.stderr)
    return 1


def _require_fields(attestation: Mapping[str, str], fields: Sequence[str], errors: list[str]) -> None:
    for field in fields:
        if field not in attestation:
            errors.append(f"Missing required field '{field}'.")


def _validate_common_identity(
    attestation: Mapping[str, str], *, expected_role: str, errors: list[str]
) -> None:
    role = attestation.get("role", "")
    agent_id = attestation.get("agent_id", "")
    if role != expected_role:
        errors.append(f"Field 'role' must be '{expected_role}', got '{role}'.")

    normalized_agent = agent_id.strip().lower()
    if not agent_id.strip():
        errors.append("Field 'agent_id' must identify the workflow agent.")
    elif normalized_agent in GENERIC_IDENTITIES:
        errors.append(
            "Field 'agent_id' must not be a generic workflow identity "
            f"({', '.join(sorted(GENERIC_IDENTITIES))})."
        )

    if not attestation.get("created_at", "").strip():
        errors.append("Field 'created_at' must not be empty.")

    expected_prefix = f"{expected_role}-"
    if agent_id.strip() and not agent_id.startswith(expected_prefix):
        errors.append(f"Field 'agent_id' must start with '{expected_prefix}', got '{agent_id}'.")


def _validate_common_matches(
    attestation: Mapping[str, str],
    *,
    marker: Mapping[str, str],
    fields: Sequence[str],
    errors: list[str],
) -> None:
    for field in fields:
        attestation_value = attestation.get(field, "")
        marker_value = marker.get(field, "")
        if attestation_value != marker_value:
            errors.append(
                f"Field '{field}' must match active implementation marker value '{marker_value}', got '{attestation_value}'."
            )


def _validate_current_context(
    attestation: Mapping[str, str],
    *,
    current_root: Path | str | None,
    current_branch: str | None,
    errors: list[str],
) -> None:
    if current_branch is not None and attestation.get("branch", "") != current_branch:
        errors.append(f"Field 'branch' must match current branch '{current_branch}'.")
    if current_root is not None and attestation.get("clone_path", ""):
        root = Path(current_root)
        if root.resolve() != Path(attestation["clone_path"]).resolve():
            errors.append(
                "Field 'clone_path' must match current repository root "
                f"'{root}', got '{attestation['clone_path']}'."
            )


def _validate_delegation_token(
    attestation: Mapping[str, str],
    *,
    delegation_token: Mapping[str, str] | None,
    expected_role: str,
    errors: list[str],
) -> None:
    if delegation_token is None:
        token_path = attestation.get("delegation_token_path", "")
        if token_path:
            errors.append(f"Delegation token file not found or invalid: {token_path}.")
        else:
            errors.append("Delegation token evidence is required.")
        return

    for field in DELEGATION_TOKEN_REQUIRED_FIELDS:
        if field not in delegation_token:
            errors.append(f"Delegation token: missing required field '{field}'.")

    for field in ("delegation_token", "implementation", "role", "agent_id"):
        token_value = delegation_token.get(field, "")
        attestation_value = attestation.get(field, "")
        if token_value != attestation_value:
            errors.append(
                f"Delegation token field '{field}' must match attestation value "
                f"'{attestation_value}', got '{token_value}'."
            )

    role = delegation_token.get("role", "")
    if role and role != expected_role:
        errors.append(f"Delegation token field 'role' must be '{expected_role}', got '{role}'.")

    if not delegation_token.get("created_at", "").strip():
        errors.append("Delegation token field 'created_at' must not be empty.")


def _git_output(command: Sequence[str], *, cwd: Path, as_path: bool = False):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    if not value:
        return None
    return Path(value) if as_path else value


def _path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def _load_delegation_token(
    attestation: Mapping[str, str],
    *,
    current_root: Path | str | None,
) -> Mapping[str, str] | None:
    token_path_value = attestation.get("delegation_token_path", "")
    if not token_path_value:
        return None

    token_path = Path(token_path_value)
    if token_path.is_absolute():
        return None

    root = Path(current_root) if current_root is not None else Path.cwd()
    token_root = (root / DELEGATION_TOKEN_ROOT).resolve(strict=False)
    full_path = (root / token_path).resolve(strict=False)
    try:
        full_path.relative_to(token_root)
    except ValueError:
        return None

    if not full_path.is_file():
        return None

    try:
        return parse_attestation(full_path)
    except (OSError, ValueError):
        return None


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
