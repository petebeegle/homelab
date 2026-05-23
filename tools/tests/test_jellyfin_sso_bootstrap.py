from __future__ import annotations

import unittest
import io
import os
import tempfile
import zipfile
from unittest import mock
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


if __name__ == "__main__":
    unittest.main()
