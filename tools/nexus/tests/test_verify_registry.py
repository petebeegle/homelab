import base64
import hashlib
import json
import importlib.util
from pathlib import Path
import tempfile
import secrets
import unittest
from urllib.parse import quote

spec = importlib.util.spec_from_file_location('verify_registry', Path(__file__).parents[1] / 'verify_registry.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

class SafetyTests(unittest.TestCase):
    def test_redacts_raw_url_and_basic_encoded_credentials(self):
        password = secrets.token_urlsafe(12)
        password += '/?%'
        creds = {'username': 'writer', 'password': password}
        encoded = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
        text = ' '.join([creds['password'], quote(creds['password'], safe=''), encoded])
        self.assertEqual(verify.redact(text, [creds]), '[REDACTED] [REDACTED] [REDACTED]')

    def test_development_cannot_target_production_or_http(self):
        for url in ['https://docker-push.lab.petebeegle.com', 'http://a.dev.lab.petebeegle.com', 'https://a.dev.lab.petebeegle.com.evil', 'https://u:p@a.dev.lab.petebeegle.com']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                verify.validate_endpoint('development', url)
        verify.validate_endpoint('development', 'https://docker-push-test.dev.lab.petebeegle.com')

    def test_scratch_state_and_provider_must_be_isolated(self):
        root = Path('/repo/.codex/tmp/nexus-hosted-registry')
        verify.validate_dev_state(root / 'fixture', root, 'http://127.0.0.1:18081')
        for path, url in [(Path('/repo/terraform/external/nexus'), 'http://127.0.0.1:18081'), (root / 'fixture', 'http://192.168.30.99:8081')]:
            with self.assertRaises(ValueError): verify.validate_dev_state(path, root, url)

    def test_transport_errors_are_not_authorization_denials(self):
        for code in (401, 403): verify.require_denial(code)
        for code in (None, 0, 200, 404, 500, 502):
            with self.assertRaises(AssertionError): verify.require_denial(code)

    def test_manifest_mismatch_is_failure(self):
        verify.require_digest('sha256:abc', 'sha256:abc')
        with self.assertRaises(AssertionError): verify.require_digest('sha256:abc', 'sha256:def')

    def test_external_locations_allow_relative_but_reject_internal_hosts(self):
        base = 'https://docker-push-test.dev.lab.petebeegle.com'
        for location in ['/v2/token', base + '/v2/uploads/123']:
            self.assertTrue(verify.external_url(base, location).startswith(base))
        for location in ['http://nexus:8083/v2/token', '//evil.test/v2/token', 'https://evil.test', base + ':8443/token', 'https://u:p@docker-push-test.dev.lab.petebeegle.com/token']:
            with self.subTest(location=location), self.assertRaises(ValueError): verify.external_url(base, location)

    def test_credentials_require_private_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'auth.json'; p.write_text('{"username":"a","password":"b"}'); p.chmod(0o644)
            with self.assertRaises(ValueError): verify.read_credentials(p)
            p.chmod(0o600)
            self.assertEqual(verify.read_credentials(p)['username'], 'a')

class ContentTests(unittest.TestCase):
    def test_clean_oci_download_checks_every_blob(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            blobs = root / 'blobs/sha256'; blobs.mkdir(parents=True)
            payload = b'actual downloaded layer'
            layer = hashlib.sha256(payload).hexdigest()
            (blobs / layer).write_bytes(payload)
            config = hashlib.sha256(b'{}').hexdigest()
            (blobs / config).write_bytes(b'{}')
            manifest = json.dumps({'config': {'digest': 'sha256:' + config}, 'layers': [{'digest': 'sha256:' + layer}]}).encode()
            digest = hashlib.sha256(manifest).hexdigest()
            (blobs / digest).write_bytes(manifest)
            (root/'index.json').write_text(json.dumps({'manifests':[{'digest':'sha256:'+digest}]}))
            verify.verify_oci(root, 'sha256:' + digest)
            (blobs / layer).write_bytes(b'corrupt')
            with self.assertRaises(AssertionError): verify.verify_oci(root, 'sha256:' + digest)

    def test_cleanup_refuses_other_repositories_and_names(self):
        own = 'homelab/registry-smoke-123'
        for component in [{'repository':'docker-proxy','name':own}, {'repository':'docker-hosted','name':'someone/important'}, {'repository':'docker-hosted','name':own+'-other'}]:
            with self.assertRaises(ValueError): verify.owned_component(component, {own})
        verify.owned_component({'repository':'docker-hosted','name':own}, {own})

    def test_collision_is_development_only(self):
        self.assertTrue(verify.collision_enabled('development'))
        self.assertFalse(verify.collision_enabled('production'))

if __name__ == '__main__': unittest.main()
