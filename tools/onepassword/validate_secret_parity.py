#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import binascii
import hmac
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from render_production_items import DEFAULT_INVENTORY, load_inventory


NAMESPACE_PATTERN = re.compile(r"^[a-z0-9](?:[-a-z0-9]*[a-z0-9])?$")


def decode_data(secret: dict[str, Any]) -> dict[str, bytes]:
    encoded = secret.get("data") or {}
    if not isinstance(encoded, dict):
        raise ValueError("Secret data is invalid")
    decoded: dict[str, bytes] = {}
    for key, value in encoded.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("Secret data is invalid")
        try:
            decoded[key] = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as error:
            raise ValueError("Secret data contains invalid base64") from error
    return decoded


def compare_pair(
    legacy: dict[str, Any],
    generated: dict[str, Any],
    expected_keys: set[str],
    expected_type: str,
) -> None:
    if legacy.get("type") != expected_type or generated.get("type") != expected_type:
        raise ValueError("Secret type mismatch")
    legacy_data = decode_data(legacy)
    generated_data = decode_data(generated)
    if set(legacy_data) != expected_keys or set(generated_data) != expected_keys:
        raise ValueError(
            "Secret key set mismatch: "
            f"expected {len(expected_keys)}, legacy {len(legacy_data)}, generated {len(generated_data)}"
        )
    mismatches = sum(
        not hmac.compare_digest(legacy_data[key], generated_data[key])
        for key in expected_keys
    )
    if mismatches:
        raise ValueError(f"Secret byte mismatch: {mismatches} value(s) differ")


def run_json(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"command failed without displaying captured output: {command[0]} get")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"command returned invalid JSON: {command[0]} get") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"command returned unexpected JSON: {command[0]} get")
    return value


def is_ready(item: dict[str, Any]) -> bool:
    return any(
        condition.get("type") == "Ready" and condition.get("status") == "True"
        for condition in item.get("status", {}).get("conditions", [])
    )


def parse_namespace_overrides(values: list[str]) -> dict[str, str]:
    overrides: dict[str, str] = {}
    for value in values:
        if value.count("=") != 1:
            raise ValueError("namespace override must be SOURCE=TARGET")
        source, target = value.split("=", 1)
        if (
            not NAMESPACE_PATTERN.fullmatch(source)
            or not NAMESPACE_PATTERN.fullmatch(target)
            or source in overrides
        ):
            raise ValueError("namespace override is invalid or duplicated")
        overrides[source] = target
    return overrides


def validate_live(
    kubeconfig: Path,
    inventory: dict[str, Any],
    namespace_overrides: dict[str, str] | None = None,
) -> None:
    namespace_overrides = namespace_overrides or {}
    passed = 0
    for item in inventory["items"]:
        namespace = namespace_overrides.get(item["namespace"], item["namespace"])
        base = ["kubectl", "--kubeconfig", str(kubeconfig), "-n", namespace, "get"]
        opi = run_json(base + ["onepassworditem", item["generated_name"], "-o", "json"])
        if not is_ready(opi):
            raise ValueError(f"OnePasswordItem is not Ready for {namespace}/{item['generated_name']}")
        legacy = run_json(base + ["secret", item["legacy_name"], "-o", "json"])
        generated = run_json(base + ["secret", item["generated_name"], "-o", "json"])
        compare_pair(legacy, generated, set(item["keys"]), item["type"])
        passed += 1
        print(f"PASS {namespace}/{item['legacy_name']} -> {item['generated_name']}")
    print(f"Secret parity passed: {passed}/{len(inventory['items'])}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare legacy and 1Password-generated Kubernetes Secrets without displaying data")
    parser.add_argument("--kubeconfig", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument(
        "--namespace-override",
        action="append",
        default=[],
        metavar="SOURCE=TARGET",
        help="Map an inventory namespace to its live namespace; repeat as needed",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        inventory = load_inventory(args.inventory)
        overrides = parse_namespace_overrides(args.namespace_override)
        validate_live(args.kubeconfig, inventory, overrides)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Secret parity failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
