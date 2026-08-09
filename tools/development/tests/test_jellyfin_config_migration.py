from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MIGRATION_SCRIPT = REPO_ROOT / "kubernetes" / "apps" / "jellyfin" / "migrate-config.sh"
JELLYFIN_MANIFESTS = REPO_ROOT / "kubernetes" / "apps" / "jellyfin"
FLUX_KUSTOMIZATION = (
    REPO_ROOT / "kubernetes" / "clusters" / "production" / "apps" / "jellyfin.yaml"
)
PLUGIN_FILES = (
    "SSO-Auth.dll",
    "Duende.IdentityModel.dll",
    "Duende.IdentityModel.OidcClient.dll",
    "meta.json",
)


def write_file(path: Path, content: bytes | str = b"state") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        path.write_text(content, encoding="utf-8")
    else:
        path.write_bytes(content)


def create_config(root: Path) -> None:
    write_file(root / "config" / "system.xml", "<ServerConfiguration />")
    write_file(root / "config" / "branding.xml", "<BrandingOptions />")
    write_file(
        root / "plugins" / "configurations" / "SSO-Auth.xml",
        "<PluginConfiguration><OidConfigs /></PluginConfiguration>",
    )
    plugin_dir = root / "plugins" / "SSO Authentication_4.0.0.4"
    for plugin_file in PLUGIN_FILES:
        write_file(plugin_dir / plugin_file, f"plugin:{plugin_file}")
    write_file(root / "data" / "jellyfin.db", b"sqlite-state")
    write_file(root / "data" / "authentication.db", b"authentication-state")
    write_file(root / ".hidden-state", b"hidden")


def extract_migration_script(manifests: str) -> str:
    for document in manifests.split("\n---\n"):
        if (
            "\nkind: ConfigMap\n" not in document
            or "name: jellyfin-config-migration\n" not in document
            or "  migrate.sh: |\n" not in document
        ):
            continue

        lines = document.splitlines(keepends=True)
        start = lines.index("  migrate.sh: |\n") + 1
        script_lines: list[str] = []
        for line in lines[start:]:
            if line.strip() and not line.startswith("    "):
                break
            script_lines.append(line[4:] if line.startswith("    ") else line)
        return "".join(script_lines)

    raise AssertionError("rendered jellyfin-config-migration ConfigMap was not found")


class JellyfinConfigMigrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime_script_dir = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.runtime_script_dir.cleanup)

        local_kustomization = Path(cls.runtime_script_dir.name) / "jellyfin.yaml"
        local_kustomization.write_text(
            FLUX_KUSTOMIZATION.read_text(encoding="utf-8").replace(
                "  postBuild:\n",
                "  postBuild:\n"
                "    substitute:\n"
                '      cluster_domain: "lab.petebeegle.com"\n'
                '      nfs_server: "192.0.2.10"\n',
            ),
            encoding="utf-8",
        )

        rendered = subprocess.run(
            [
                "flux",
                "build",
                "kustomization",
                "app-jellyfin",
                "--path",
                str(JELLYFIN_MANIFESTS),
                "--kustomization-file",
                str(local_kustomization),
                "--dry-run",
                "--strict-substitute",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if rendered.returncode != 0:
            raise AssertionError(rendered.stderr)

        cls.rendered_manifests = rendered.stdout
        cls.runtime_script = Path(cls.runtime_script_dir.name) / "migrate.sh"
        cls.runtime_script.write_text(
            extract_migration_script(rendered.stdout), encoding="utf-8"
        )

    def test_flux_preserves_migration_script(self) -> None:
        self.assertEqual(
            self.runtime_script.read_bytes(),
            MIGRATION_SCRIPT.read_bytes(),
        )

    def test_flux_still_substitutes_neighboring_application_values(self) -> None:
        self.assertNotIn("${cluster_domain}", self.rendered_manifests)
        self.assertNotIn("${nfs_server}", self.rendered_manifests)
        self.assertIn("https://jellyfin.lab.petebeegle.com", self.rendered_manifests)
        self.assertIn("server: 192.0.2.10", self.rendered_manifests)

    def run_migration(self, source: Path, target: Path) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update({"SOURCE_ROOT": str(source), "TARGET_ROOT": str(target)})
        return subprocess.run(
            ["/bin/sh", str(self.runtime_script)],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def test_copies_and_validates_complete_authentication_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            target = root / "target"
            create_config(source)
            target.mkdir()
            write_file(target / "partial", b"untrusted")

            result = self.run_migration(source, target)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((target / "partial").exists())
            self.assertTrue((target / ".homelab-config-migration-v1").is_file())
            self.assertEqual(
                (target / "plugins" / "configurations" / "SSO-Auth.xml").read_bytes(),
                (source / "plugins" / "configurations" / "SSO-Auth.xml").read_bytes(),
            )
            self.assertEqual(
                (target / "data" / "authentication.db").read_bytes(),
                (source / "data" / "authentication.db").read_bytes(),
            )
            self.assertEqual((target / ".hidden-state").read_bytes(), b"hidden")

    def test_completed_migration_does_not_require_source_contents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            target = root / "target"
            create_config(source)
            target.mkdir()

            first = self.run_migration(source, target)
            self.assertEqual(first.returncode, 0, first.stderr)

            for path in sorted(source.rglob("*"), reverse=True):
                if path.is_file() or path.is_symlink():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            source.rmdir()

            second = self.run_migration(source, target)

            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("already completed", second.stdout)

    def test_completed_migration_fails_closed_when_authentication_state_is_lost(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            target = root / "target"
            create_config(source)
            target.mkdir()

            first = self.run_migration(source, target)
            self.assertEqual(first.returncode, 0, first.stderr)
            (target / "plugins" / "configurations" / "SSO-Auth.xml").unlink()

            second = self.run_migration(source, target)

            self.assertNotEqual(second.returncode, 0)
            self.assertIn("SSO-Auth.xml", second.stderr)

    def test_fails_closed_when_sso_configuration_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            target = root / "target"
            create_config(source)
            (source / "plugins" / "configurations" / "SSO-Auth.xml").unlink()
            target.mkdir()

            result = self.run_migration(source, target)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SSO-Auth.xml", result.stderr)
            self.assertFalse((target / ".homelab-config-migration-v1").exists())


if __name__ == "__main__":
    unittest.main()
