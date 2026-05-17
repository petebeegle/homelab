#!/usr/bin/env python3
"""Validate Synology Authentik OAuth redirect policy."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS_LIB = Path(__file__).resolve().parents[2] / "tools" / "lib"
if str(TOOLS_LIB) not in sys.path:
    sys.path.insert(0, str(TOOLS_LIB))

from homelab_tools.reporting import CheckResult


ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT = ROOT / "kubernetes/infra/authentik/blueprints/synology-oauth.yaml"
EXPECTED_REDIRECT = "https://synology.petebeegle.com"
FORBIDDEN_REDIRECTS = {
    "https://synology.petebeegle.com:5001",
    "https://synology.petebeegle.com/#/signin",
    "https://192.168.30.99:5001",
}


def main() -> int:
    text = BLUEPRINT.read_text(encoding="utf-8")
    result = CheckResult()

    redirect_urls = {
        line.split("url:", 1)[1].strip()
        for line in text.splitlines()
        if line.lstrip().startswith("url:")
    }

    if EXPECTED_REDIRECT not in redirect_urls:
        result.add(
            f"{BLUEPRINT.relative_to(ROOT)} must include Synology OAuth redirect "
            f"{EXPECTED_REDIRECT!r}"
        )

    for forbidden in sorted(FORBIDDEN_REDIRECTS):
        if forbidden in redirect_urls:
            result.add(
                f"{BLUEPRINT.relative_to(ROOT)} must not use redirect "
                f"{forbidden!r}"
            )

    if not result.ok:
        result.print(bullet="")
        return result.exit_code()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
