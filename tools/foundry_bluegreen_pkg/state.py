"""Small desired-state text mutations used by the Foundry workflow."""

from __future__ import annotations

import re
from pathlib import Path

from .errors import FoundryBlueGreenError


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_first_replicas(path: Path, replicas: int) -> None:
    text = read(path)
    next_text, count = re.subn(r"(?m)^  replicas: \d+\s*$", f"  replicas: {replicas}", text, count=1)
    if count != 1:
        raise FoundryBlueGreenError(f"could not update replicas in {path}")
    write(path, next_text)


def set_service_color(path: Path, color: str) -> None:
    text = read(path)
    next_text, count = re.subn(
        r"(?m)^    foundryvtt\.petebeegle\.com/color: (blue|green)\s*$",
        f"    foundryvtt.petebeegle.com/color: {color}",
        text,
        count=1,
    )
    if count != 1:
        raise FoundryBlueGreenError(f"could not update active service color in {path}")
    write(path, next_text)


def service_color(path: Path) -> str:
    match = re.search(r"(?m)^    foundryvtt\.petebeegle\.com/color: (blue|green)\s*$", read(path))
    if not match:
        raise FoundryBlueGreenError(f"could not determine active service color in {path}")
    return match.group(1)


def ensure_kustomization_resource(path: Path, resource: str) -> None:
    text = read(path)
    line = f"  - {resource}"
    if line in text.splitlines():
        return
    if "resources:\n" not in text:
        raise FoundryBlueGreenError(f"{path} has no resources block")
    text = text.rstrip() + f"\n{line}\n"
    write(path, text)


def remove_kustomization_resource(path: Path, resource: str) -> None:
    lines = [line for line in read(path).splitlines() if line.strip() != f"- {resource}"]
    write(path, "\n".join(lines).rstrip() + "\n")


def remove_file_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()
