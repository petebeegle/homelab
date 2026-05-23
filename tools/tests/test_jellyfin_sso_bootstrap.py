from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def embedded_script(path: str) -> str:
    lines = (REPO_ROOT / path).read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("  bootstrap-sso.py: |") + 1
    except ValueError:
        raise AssertionError(f"bootstrap-sso.py block not found in {path}")

    body: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith("    "):
            break
        body.append(line[4:] if line.startswith("    ") else "")
    return "\n".join(body)


class JellyfinSsoBootstrapTest(unittest.TestCase):
    def test_production_bootstrap_writes_oid_value_with_plugin_configuration_root(self) -> None:
        script = embedded_script("kubernetes/apps/jellyfin/sso-bootstrap.yaml")

        self.assertIn('PROVIDER_NAME = "authentik"', script)
        self.assertIn('oid_config = ET.Element("PluginConfiguration")', script)
        self.assertNotIn('oid_config = ET.Element("OidConfig")', script)
        self.assertIn("./value/PluginConfiguration/CanonicalLinks", script)

    def test_branch_bootstrap_static_xml_uses_plugin_configuration_value_root(self) -> None:
        script = embedded_script("kubernetes/apps/jellyfin/branch/jellyfin.yaml")

        self.assertIn("<key><string>authentik</string></key>", script)
        self.assertIn("<value>\n        <PluginConfiguration>", script)
        self.assertIn("</PluginConfiguration>\n      </value>", script)
        self.assertNotIn("<OidConfig>", script)
        self.assertNotIn("</OidConfig>", script)


if __name__ == "__main__":
    unittest.main()
