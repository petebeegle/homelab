"""Development rehearsal evidence and safety gates."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import CONFIG_VERSION_GLOBS, DEV_KUBECONFIG
from .errors import FoundryBlueGreenError


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def config_version(root: Path) -> str:
    digest = hashlib.sha256()
    for pattern in CONFIG_VERSION_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                digest.update(rel(root, path).encode())
                digest.update(b"\0")
                digest.update(path.read_bytes())
                digest.update(b"\0")
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_evidence(root: Path, evidence_path: Path) -> dict[str, object] | None:
    path = root / evidence_path
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def require_current_dev_rehearsal(root: Path, evidence_path: Path) -> dict[str, object]:
    expected = config_version(root)
    evidence = read_evidence(root, evidence_path)
    if not evidence:
        raise FoundryBlueGreenError(
            "production command blocked: run `tools/foundry_bluegreen.py dev-rehearse` first"
        )
    if evidence.get("status") != "succeeded":
        raise FoundryBlueGreenError("production command blocked: last dev-rehearse did not succeed")
    if evidence.get("config_version") != expected:
        raise FoundryBlueGreenError(
            "production command blocked: dev-rehearse evidence is stale for this tool/config version"
        )
    return evidence


def resolved_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def require_development_kubeconfig(kubeconfig: str | Path) -> Path:
    actual = resolved_path(kubeconfig)
    expected = resolved_path(DEV_KUBECONFIG)
    if actual != expected:
        raise FoundryBlueGreenError(
            f"dev-rehearse requires development kubeconfig {expected}; got {actual}"
        )
    return actual
