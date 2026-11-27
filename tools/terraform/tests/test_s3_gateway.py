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

    def test_credentials_are_template_placeholders_not_values(self) -> None:
        text = compose()
        self.assertIn("ROOT_ACCESS_KEY: ${access_key}", text)
        self.assertIn("ROOT_SECRET_KEY: ${secret_key}", text)

    def test_renovate_tracks_the_image(self) -> None:
        # Renovate's docker-compose manager matches (docker-)compose*.yaml basenames only.
        self.assertRegex(COMPOSE.name, r"^(?:docker-)?compose[^/]*\.ya?ml$")


class SynologyRootTest(unittest.TestCase):
    def test_the_gateway_is_a_container_project_rendered_from_the_compose_file(self) -> None:
        text = (SYNOLOGY_ROOT / "s3.tf").read_text(encoding="utf-8")
        self.assertIn('resource "synology_container_project" "s3"', text)
        self.assertIn('share_path = "/docker/s3"', text)
        self.assertIn("scripts/synology/s3/docker-compose.yaml", text)

    def test_no_resource_calls_a_non_idempotent_synology_create_api(self) -> None:
        # synology_api with method "create" runs the call again on every replace, and its state
        # had already drifted from the live reverse proxy (#486). Reverse proxies are set by hand.
        for path in SYNOLOGY_ROOT.glob("*.tf"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r'(?s)resource "synology_api".*?method\s*=\s*"create"', path.name)


if __name__ == "__main__":
    unittest.main()
