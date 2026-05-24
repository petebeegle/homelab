from __future__ import annotations

import unittest
import io
import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from unittest import mock
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def jellyfin_oauth_provider_attr_lines() -> list[str]:
    path = REPO_ROOT / "kubernetes/infra/authentik/blueprints/jellyfin-oauth.yaml"
    lines = path.read_text(encoding="utf-8").splitlines()
    provider_start = next(
        index
        for index, line in enumerate(lines)
        if line == "    model: authentik_providers_oauth2.oauth2provider"
        and index > 0
        and lines[index - 2] == "  - identifiers:"
        and lines[index - 1] == "      name: jellyfin"
    )
    attrs_start = next(
        index for index in range(provider_start, len(lines)) if lines[index] == "    attrs:"
    )
    provider_end = next(
        (index for index in range(attrs_start + 1, len(lines)) if lines[index].startswith("  - identifiers:")),
        len(lines),
    )
    return lines[attrs_start + 1 : provider_end]


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


def embedded_script_namespace(path: str) -> dict[str, object]:
    script = embedded_script(path)
    definitions = script.split("\ntry:\n", 1)[0]
    namespace: dict[str, object] = {}
    with mock.patch.dict(
        os.environ,
        {
            "JELLYFIN_OIDC_ENDPOINT": "https://authentik.example.test/application/o/jellyfin/.well-known/openid-configuration",
            "JELLYFIN_PUBLIC_URL": "https://jellyfin.example.test",
            "JELLYFIN_OAUTH_CLIENT_SECRET": "test-secret",
        },
    ):
        exec(compile(definitions, path, "exec"), namespace)
    return namespace


class JellyfinSsoBootstrapTest(unittest.TestCase):
    def test_authentik_jellyfin_provider_allows_authorization_code_with_refresh_tokens(self) -> None:
        attrs = jellyfin_oauth_provider_attr_lines()
        grant_types_start = attrs.index("      grant_types:")
        grant_types: list[str] = []
        for line in attrs[grant_types_start + 1 :]:
            if not line.startswith("        - "):
                break
            grant_types.append(line.removeprefix("        - "))

        self.assertEqual(grant_types, ["authorization_code", "refresh_token"])

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

    def test_bootstrap_scripts_force_https_scheme_for_gateway_tls_termination(self) -> None:
        production = embedded_script_namespace("kubernetes/apps/jellyfin/sso-bootstrap.yaml")
        oid_config = production["build_oid_config"](None)

        self.assertEqual(oid_config.findtext("SchemeOverride"), "https")

        branch = embedded_script("kubernetes/apps/jellyfin/branch/jellyfin.yaml")
        self.assertIn("<SchemeOverride>https</SchemeOverride>", branch)
        self.assertNotIn("<SchemeOverride />", branch)

    def test_production_bootstrap_skips_complete_plugin_without_removing_it(self) -> None:
        namespace = embedded_script_namespace("kubernetes/apps/jellyfin/sso-bootstrap.yaml")

        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir) / "plugins" / "SSO Authentication_4.0.0.4"
            plugin_dir.mkdir(parents=True)
            for filename in namespace["EXPECTED_PLUGIN_FILES"]:
                (plugin_dir / filename).write_text("present", encoding="utf-8")

            namespace["PLUGIN_DIR"] = plugin_dir
            with (
                mock.patch("builtins.print"),
                mock.patch.object(namespace["shutil"], "rmtree", side_effect=AssertionError("rmtree called")),
                mock.patch.object(namespace["urllib"].request, "urlopen", side_effect=AssertionError("download called")),
            ):
                namespace["install_plugin"]()

            self.assertTrue(plugin_dir.is_dir())

    def test_production_bootstrap_reports_incomplete_plugin_replacement_failure(self) -> None:
        namespace = embedded_script_namespace("kubernetes/apps/jellyfin/sso-bootstrap.yaml")

        archive_buffer = io.BytesIO()
        with zipfile.ZipFile(archive_buffer, "w") as plugin_zip:
            for filename in namespace["EXPECTED_PLUGIN_FILES"]:
                plugin_zip.writestr(filename, "present")
        archive_bytes = archive_buffer.getvalue()

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self):
                return archive_bytes

        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir) / "plugins" / "SSO Authentication_4.0.0.4"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "SSO-Auth.dll").write_text("partial", encoding="utf-8")

            namespace["PLUGIN_DIR"] = plugin_dir
            namespace["PLUGIN_SHA256"] = namespace["hashlib"].sha256(archive_bytes).hexdigest()
            with (
                mock.patch.object(namespace["urllib"].request, "urlopen", return_value=Response()),
                mock.patch.object(namespace["shutil"], "rmtree", side_effect=OSError("busy")),
            ):
                with self.assertRaisesRegex(RuntimeError, "could not be replaced safely; stop Jellyfin and retry"):
                    namespace["install_plugin"]()

    def test_bootstrap_scripts_check_expected_plugin_files_before_reinstalling(self) -> None:
        production = embedded_script("kubernetes/apps/jellyfin/sso-bootstrap.yaml")
        branch = embedded_script("kubernetes/apps/jellyfin/branch/jellyfin.yaml")

        for script in (production, branch):
            self.assertIn("SSO-Auth.dll", script)
            self.assertIn("Duende.IdentityModel.dll", script)
            self.assertIn("Duende.IdentityModel.OidcClient.dll", script)
            self.assertIn("meta.json", script)
            self.assertIn("plugin_install_complete()", script)
            self.assertIn("already installed; skipping install", script)
            self.assertIn(".is_file() for name in", script)
            self.assertIn(".install-", script)
            self.assertIn("could not be replaced safely", script)

        self.assertNotIn("if PLUGIN_DIR.exists():\n                shutil.rmtree(PLUGIN_DIR)", production)
        self.assertNotIn("if plugin_dir.exists():\n                shutil.rmtree(plugin_dir)", branch)

    def test_bootstrap_scripts_force_qsv_encoding_settings(self) -> None:
        for path in (
            "kubernetes/apps/jellyfin/sso-bootstrap.yaml",
            "kubernetes/apps/jellyfin/branch/jellyfin.yaml",
        ):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as temp_dir:
                namespace = embedded_script_namespace(path)
                encoding_config = Path(temp_dir) / "config" / "encoding.xml"
                encoding_config.parent.mkdir(parents=True)
                encoding_config.write_text(
                    """<?xml version='1.0' encoding='utf-8'?>
<EncodingOptions>
  <HardwareAccelerationType>none</HardwareAccelerationType>
  <VaapiDevice>/dev/dri/renderD128</VaapiDevice>
  <EnableHardwareEncoding>false</EnableHardwareEncoding>
  <EnableDecodingColorDepth10Hevc>false</EnableDecodingColorDepth10Hevc>
  <EnableDecodingColorDepth10Vp9>false</EnableDecodingColorDepth10Vp9>
  <PreferSystemNativeHwDecoder>false</PreferSystemNativeHwDecoder>
  <HardwareDecodingCodecs>
    <string>h264</string>
    <string>vc1</string>
  </HardwareDecodingCodecs>
</EncodingOptions>
""",
                    encoding="utf-8",
                )

                namespace["ENCODING_CONFIG"] = encoding_config
                namespace["configure_encoding"]()

                root = ET.parse(encoding_config).getroot()
                self.assertEqual(root.findtext("HardwareAccelerationType"), "qsv")
                self.assertEqual(root.findtext("VaapiDevice"), "/dev/dri/renderD128")
                self.assertEqual(root.findtext("QsvDevice"), "/dev/dri/renderD128")
                self.assertEqual(root.findtext("EnableHardwareEncoding"), "true")
                self.assertEqual(root.findtext("EnableDecodingColorDepth10Hevc"), "true")
                self.assertEqual(root.findtext("EnableDecodingColorDepth10Vp9"), "true")
                self.assertEqual(root.findtext("PreferSystemNativeHwDecoder"), "true")
                self.assertEqual(
                    [item.text for item in root.findall("./HardwareDecodingCodecs/string")],
                    ["h264", "hevc", "mpeg2video", "vc1", "vp8", "vp9"],
                )


if __name__ == "__main__":
    unittest.main()
