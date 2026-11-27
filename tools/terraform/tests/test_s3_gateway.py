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

    def test_credentials_are_placeholders_that_terraform_replaces(self) -> None:
        text = compose()
        self.assertIn("ROOT_ACCESS_KEY: set-by-terraform", text)
        self.assertIn("ROOT_SECRET_KEY: set-by-terraform", text)
        self.assertNotIn("${", text, "the file is yamldecoded, not templated")

    def test_renovate_tracks_the_image(self) -> None:
        # Renovate's docker-compose manager matches (docker-)compose*.yaml basenames only.
        self.assertRegex(COMPOSE.name, r"^(?:docker-)?compose[^/]*\.ya?ml$")


class SynologyRootTest(unittest.TestCase):
    def test_the_gateway_is_a_container_project_built_from_the_compose_file(self) -> None:
        text = (SYNOLOGY_ROOT / "s3.tf").read_text(encoding="utf-8")
        self.assertIn('resource "synology_container_project" "s3"', text)
        self.assertIn('share_path = "/docker/s3"', text)
        self.assertRegex(text, r'yamldecode\(file\("\$\{path\.module\}/\.\./\.\./\.\./scripts/synology/s3/docker-compose\.yaml"\)\)')
        self.assertRegex(text, r"(?m)^  services = \{$")

    def test_the_project_never_sets_raw_content(self) -> None:
        # Provider 0.6.11 plans `content` from the `services` attribute and rejects any literal
        # content ("planned value services: {} does not match config value"), so the project is
        # described only through `services`.
        project = (SYNOLOGY_ROOT / "s3.tf").read_text(encoding="utf-8").split('resource "synology_container_project" "s3"', 1)[1]
        self.assertNotRegex(project.split("\n}\n", 1)[0], r"(?m)^  content\s*=")

    def test_keys_reach_the_gateway_through_an_env_file_never_the_project(self) -> None:
        # The provider computes the project's `content` without a sensitive mark, so anything in
        # `services` is printed by every plan (#486). Compose reads ${...} from .env in the project
        # folder; that file's content comes from config and stays sensitive.
        text = (SYNOLOGY_ROOT / "s3.tf").read_text(encoding="utf-8")
        project = text.split('resource "synology_container_project" "s3"', 1)[1].split("\n}\n", 1)[0]
        self.assertNotIn("random_password", project)
        self.assertIn('ROOT_ACCESS_KEY = "$${ROOT_ACCESS_KEY}"', project)
        self.assertIn('ROOT_SECRET_KEY = "$${ROOT_SECRET_KEY}"', project)
        env_file = text.split('resource "synology_filestation_file" "s3_env"', 1)[1].split("\n}\n", 1)[0]
        self.assertIn('path      = "/docker/s3/.env"', env_file)
        self.assertIn("random_password.s3_access_key.result", env_file)
        self.assertIn("random_password.s3_secret_key.result", env_file)

    def test_no_resource_calls_a_non_idempotent_synology_create_api(self) -> None:
        # synology_api with method "create" runs the call again on every replace, and its state
        # had already drifted from the live reverse proxy (#486). Reverse proxies are set by hand.
        for path in SYNOLOGY_ROOT.glob("*.tf"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r'(?s)resource "synology_api".*?method\s*=\s*"create"', path.name)


if __name__ == "__main__":
    unittest.main()
