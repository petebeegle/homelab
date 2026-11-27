from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE = REPO_ROOT / "scripts" / "synology" / "s3" / "docker-compose.yaml"
SYNOLOGY_ROOT = REPO_ROOT / "terraform" / "external" / "synology"


def compose() -> str:
    assert COMPOSE.exists(), f"missing: {COMPOSE.relative_to(REPO_ROOT)}"
    return COMPOSE.read_text(encoding="utf-8")


def s3_tf() -> str:
    return (SYNOLOGY_ROOT / "s3.tf").read_text(encoding="utf-8")


def block(text: str, header: str) -> str:
    assert header in text, f"missing: {header}"
    return text.split(header, 1)[1].split("\n}\n", 1)[0]


class S3GatewayComposeTest(unittest.TestCase):
    def test_the_image_is_pinned_by_version_and_digest(self) -> None:
        self.assertRegex(compose(), r"(?m)^\s+image: versity/versitygw:v\d+\.\d+\.\d+@sha256:[0-9a-f]{64}$")

    def test_plain_http_listens_on_the_nas_loopback_only(self) -> None:
        # TLS comes from the Synology reverse proxy for s3.petebeegle.com; the gateway itself
        # must not answer plain HTTP on the LAN.
        ports = re.findall(r'(?m)^\s+- "([^"]+)"$', compose().split("ports:", 1)[1].split("volumes:", 1)[0])
        self.assertEqual(ports, ["127.0.0.1:7070:7070"])

    def test_objects_are_versioned_on_the_docker_share(self) -> None:
        text = compose()
        self.assertIn("--versioning-dir", text)
        self.assertIn("/volume2/docker/s3/data:/data", text)
        self.assertIn("/volume2/docker/s3/versions:/versions", text)

    def test_keys_come_from_the_env_file_in_the_project_folder(self) -> None:
        # Compose fills ${...} from /volume2/docker/s3/.env, which Terraform writes.
        text = compose()
        self.assertIn("ROOT_ACCESS_KEY: ${ROOT_ACCESS_KEY}", text)
        self.assertIn("ROOT_SECRET_KEY: ${ROOT_SECRET_KEY}", text)

    def test_renovate_tracks_the_image(self) -> None:
        # Renovate's docker-compose manager matches (docker-)compose*.yaml basenames only.
        self.assertRegex(COMPOSE.name, r"^(?:docker-)?compose[^/]*\.ya?ml$")


class SynologyRootTest(unittest.TestCase):
    def test_terraform_writes_the_keys_to_the_project_env_file(self) -> None:
        env_file = block(s3_tf(), 'resource "synology_filestation_file" "s3_env" {')
        self.assertIn('path      = "/docker/s3/.env"', env_file)
        self.assertIn("ROOT_ACCESS_KEY=${random_password.s3_access_key.result}", env_file)
        self.assertIn("ROOT_SECRET_KEY=${random_password.s3_secret_key.result}", env_file)

    def test_the_container_project_is_not_managed_by_terraform(self) -> None:
        # Provider 0.6.11's synology_container_project fails both ways (#486): create starts the
        # project, then cannot decode the plain-text build log and drops it from state; update
        # cannot record `services` (it returns the prior state when content is unchanged). The
        # project is applied by hand from the compose file, like Nexus.
        text = s3_tf()
        self.assertNotIn('resource "synology_container_project"', text)
        removed = block(text, "removed {")
        self.assertIn("from = synology_container_project.s3", removed)
        self.assertRegex(removed, r"(?s)lifecycle\s*\{\s*destroy\s*=\s*false\s*\}")

    def test_no_resource_calls_a_non_idempotent_synology_create_api(self) -> None:
        # synology_api with method "create" runs the call again on every replace, and its state
        # had already drifted from the live reverse proxy (#486). Reverse proxies are set by hand.
        for path in SYNOLOGY_ROOT.glob("*.tf"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r'(?s)resource "synology_api".*?method\s*=\s*"create"', path.name)


if __name__ == "__main__":
    unittest.main()
