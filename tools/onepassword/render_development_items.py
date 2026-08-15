#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from render_production_items import load_inventory, render_item, resolve


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY = SCRIPT_DIR / "development_items.json"
EXPECTED_OUTPUTS = {
    ("cert-manager", "cloudflare-api-token"): Path(
        "kubernetes/infra/controllers/cert-manager-development/onepassword-item.yaml"
    ),
    ("immich", "immich-postgres-user"): Path(
        "kubernetes/apps/immich/branch/onepassword-items/postgres-user.yaml"
    ),
    ("immich", "immich-secrets"): Path(
        "kubernetes/apps/immich/branch/onepassword-items/configuration.yaml"
    ),
}


def load_development_inventory(path: Path) -> dict[str, Any]:
    inventory = load_inventory(path)
    if inventory.get("expected_count") != 3:
        raise ValueError("development inventory must declare expected_count 3")
    observed: dict[tuple[str, str], Path] = {}
    for item in inventory["items"]:
        output = item.get("output_path")
        if not isinstance(output, str):
            raise ValueError("development item output path is invalid")
        output_path = Path(output)
        if output_path.is_absolute() or ".." in output_path.parts:
            raise ValueError("development item output path is invalid")
        observed[(item["namespace"], item["legacy_name"])] = output_path
    if observed != EXPECTED_OUTPUTS:
        raise ValueError("development item output paths do not match the allowlist")
    return inventory


def write_development_manifests(
    root: Path,
    vault_id: str,
    resolved: list[tuple[dict[str, Any], str]],
) -> None:
    for item, item_id in resolved:
        identity = (item["namespace"], item["legacy_name"])
        output_path = Path(item.get("output_path", ""))
        if EXPECTED_OUTPUTS.get(identity) != output_path:
            raise ValueError("development item output path is not allowed")
        destination = root / output_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_item(item, vault_id, item_id), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve development 1Password item IDs and render ID-only resources"
    )
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--vault", default="cluster development")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        inventory = load_development_inventory(args.inventory)
        vault_id, resolved = resolve(inventory, args.vault)
        if not args.check_only:
            write_development_manifests(args.root, vault_id, resolved)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Development 1Password item resolution failed: {error}", file=sys.stderr)
        return 1
    action = "validated" if args.check_only else "rendered"
    print(f"Development 1Password items {action}: {len(resolved)} ID-only resources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
