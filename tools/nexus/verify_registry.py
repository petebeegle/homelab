#!/usr/bin/env python3
"""Exact-endpoint registry acceptance. Credentials and client state stay private."""
import base64
import json
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit


def redact(text, credentials):
    for credential in credentials:
        password = credential['password']
        variants = [password, quote(password, safe=''), base64.b64encode(f"{credential['username']}:{password}".encode()).decode()]
        for secret in sorted(variants, key=len, reverse=True):
            if secret:
                text = text.replace(secret, '[REDACTED]')
    return text


def validate_endpoint(environment, url):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.port not in (None, 443) or parsed.path not in ('', '/') or parsed.query or parsed.fragment:
        raise ValueError('Registry must be an HTTPS origin without credentials')
    host = parsed.hostname or ''
    if environment == 'development':
        valid = host.endswith('.dev.lab.petebeegle.com')
    elif environment == 'production':
        valid = host in ('docker-push.lab.petebeegle.com', 'docker-registry.petebeegle.com')
    else:
        valid = False
    if not valid:
        raise ValueError('Registry does not belong to the selected environment')


def validate_dev_state(directory, scratch_root, provider_url):
    directory, scratch_root = Path(directory).resolve(), Path(scratch_root).resolve()
    if directory == scratch_root or not directory.is_relative_to(scratch_root):
        raise ValueError('Development state must be in a dedicated scratch subdirectory')
    url = urlsplit(provider_url)
    if url.scheme != 'http' or url.hostname != '127.0.0.1' or not url.port or url.username or url.password or url.path not in ('', '/'):
        raise ValueError('Development provider must use the verified loopback port-forward')


def require_denial(status):
    if status not in (401, 403):
        raise AssertionError(f'Expected authorization denial, got HTTP {status}')


def require_digest(expected, actual):
    if not expected or expected != actual:
        raise AssertionError(f'Digest mismatch: expected {expected}, got {actual}')


def external_url(origin, location):
    result = urljoin(origin + '/', location)
    expected, actual = urlsplit(origin), urlsplit(result)
    if actual.scheme != 'https' or actual.hostname != expected.hostname or actual.port not in (None, 443) or actual.username or actual.password or actual.fragment:
        raise ValueError('Registry advertised a URL outside its external HTTPS origin')
    return result


def read_credentials(path):
    path = Path(path)
    if path.stat().st_mode & 0o077:
        raise ValueError('Credential files must be private (0600)')
    result = json.loads(path.read_text())
    if not all(isinstance(result.get(k), str) and result[k] for k in ('username', 'password')):
        raise ValueError('Credential file needs nonempty username and password')
    return result


def verify_oci(directory, expected):
    """Hash downloaded bytes, including each config/layer; never trust daemon cache."""
    import hashlib
    directory = Path(directory)
    index = json.loads((directory / 'index.json').read_text())
    digest = index['manifests'][0]['digest']
    require_digest(expected, digest)
    def blob(digest):
        algorithm, value = digest.split(':', 1)
        if algorithm != 'sha256' or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('Unsupported content digest')
        content = (directory / 'blobs' / algorithm / value).read_bytes()
        require_digest(digest, 'sha256:' + hashlib.sha256(content).hexdigest())
        return content
    manifest = json.loads(blob(digest))
    for descriptor in [manifest['config'], *manifest['layers']]:
        blob(descriptor['digest'])
    return len(manifest['layers'])


def owned_component(component, names):
    if component.get('repository') != 'docker-hosted' or component.get('name') not in names:
        raise ValueError('Refusing to delete a component outside this smoke run')


def collision_enabled(environment):
    return environment == 'development'


# urllib normally follows redirects, which could forward Authorization to another
# origin. Protocol probes deliberately require the original endpoint to answer.
import urllib.request
import urllib.error


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(url, method='GET', credentials=None, token=None, data=None, headers=None):
    headers = dict(headers or {})
    if credentials:
        encoded = base64.b64encode(f"{credentials['username']}:{credentials['password']}".encode()).decode()
        headers['Authorization'] = 'Basic ' + encoded
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        response = urllib.request.build_opener(NoRedirect).open(req, timeout=300)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.status, response.headers, response.read(8 * 1024 * 1024)


def bearer(origin, credentials, name, actions):
    import re
    from urllib.parse import urlencode
    status, headers, _ = request(origin + '/v2/')
    if status != 401:
        raise AssertionError(f'Expected token challenge, got HTTP {status}')
    challenge = headers.get('WWW-Authenticate', '')
    if not challenge.lower().startswith('bearer '):
        raise AssertionError('Expected Bearer authentication challenge')
    params = dict(re.findall(r'(\w+)="([^"]*)"', challenge))
    realm = external_url(origin, params['realm'])
    query = urlencode({'service': params.get('service', ''), 'scope': f'repository:{name}:{actions}'})
    status, _, body = request(realm + ('&' if '?' in realm else '?') + query, credentials=credentials)
    if status != 200:
        return status, None
    result = json.loads(body)
    return status, result.get('token') or result.get('access_token')


def write_auth(directory, origin, credentials):
    directory.mkdir(mode=0o700)
    encoded = base64.b64encode(f"{credentials['username']}:{credentials['password']}".encode()).decode()
    path = directory / 'config.json'
    path.write_text(json.dumps({'auths': {urlsplit(origin).netloc: {'auth': encoded}}}))
    path.chmod(0o600)
    return path


class Acceptance:
    def __init__(self, args):
        import uuid
        self.args = args
        self.credentials = [read_credentials(p) for p in (args.publisher_credentials_file, args.consumer_credentials_file, args.admin_credentials_file)]
        self.publisher, self.consumer, self.admin = self.credentials
        self.root = Path(args.work_dir).resolve()
        # A preexisting work directory could contain reused client/image state.
        self.root.mkdir(mode=0o700, parents=True, exist_ok=False)
        self.name = 'homelab/registry-smoke-' + uuid.uuid4().hex[:16]
        self.names = {self.name}
        self.report = {'environment': args.environment, 'image': self.name, 'checks': [], 'cleanup': 'pending'}
        self.auths = []
        self.local_images = []
        self.hosted_auth = write_auth(self.root / 'publisher', args.hosted_url, self.publisher)
        self.group_auth = write_auth(self.root / 'consumer', args.group_url, self.consumer)
        self.auths.extend([self.hosted_auth, self.group_auth])

    def check(self, name, **details):
        self.report['checks'].append({'name': name, 'passed': True, **details})
        print(name + ': passed', flush=True)

    def command(self, args, timeout=600):
        import subprocess
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        if result.returncode:
            # Client output can include tokens. Keep it out of durable reports.
            raise RuntimeError(f'{args[0]} {args[1]} failed (exit {result.returncode}); inspect endpoint health')
        return result.stdout.strip()

    def push(self, reference):
        self.command(['docker', '--config', str(self.hosted_auth.parent), 'push', reference])

    def digest(self, origin, name, tag, credential):
        status, token = bearer(origin, credential, name, 'pull')
        if status != 200 or not token:
            raise AssertionError(f'Token request failed: HTTP {status}')
        accept = 'application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json'
        status, headers, body = request(f'{origin}/v2/{name}/manifests/{tag}', token=token, headers={'Accept': accept})
        if status != 200:
            raise AssertionError(f'Manifest read failed: HTTP {status}')
        import hashlib
        digest = 'sha256:' + hashlib.sha256(body).hexdigest()
        require_digest(digest, headers.get('Docker-Content-Digest'))
        return digest

    def pull(self, origin, name, tag, digest, label, auth):
        destination = self.root / label
        if destination.exists():
            raise ValueError('Clean pull destination already exists')
        self.command(['skopeo', 'copy', '--preserve-digests', '--authfile', str(auth), f'docker://{urlsplit(origin).netloc}/{name}@{digest}', f'oci:{destination}:smoke'])
        layers = verify_oci(destination, digest)
        self.check(label, digest=digest, layers=layers)

    def components(self):
        from urllib.parse import urlencode
        items, continuation = [], None
        while True:
            query = {'repository': 'docker-hosted'}
            if continuation:
                query['continuationToken'] = continuation
            status, _, body = request(self.args.admin_url + '/service/rest/v1/components?' + urlencode(query), credentials=self.admin)
            if status != 200:
                raise AssertionError(f'Admin component listing failed: HTTP {status}')
            page = json.loads(body)
            items.extend(c for c in page['items'] if c.get('name') in self.names)
            continuation = page.get('continuationToken')
            if not continuation:
                return items

    def run(self):
        import os
        import hashlib
        args = self.args
        context = self.root / 'build'; context.mkdir()
        (context / 'large').write_bytes(os.urandom(12 * 1024 * 1024))
        (context / 'version').write_text('version-one')
        (context / 'Dockerfile').write_text('FROM scratch\nCOPY large /large\nCOPY version /version\n')
        reference = urlsplit(args.hosted_url).netloc + '/' + self.name + ':current'
        self.local_images.append(reference)
        self.command(['docker', 'build', '--provenance=false', '-t', reference, str(context)])
        self.push(reference)
        old = self.digest(args.hosted_url, self.name, 'current', self.publisher)
        self.check('multi-layer push over HTTPS', digest=old, large_layer_bytes=12 * 1024 * 1024)
        self.pull(args.hosted_url, self.name, 'current', old, 'clean-hosted-pull', self.hosted_auth)
        status, token = bearer(args.hosted_url, self.publisher, self.name, 'pull,push')
        if status != 200 or not token:
            raise AssertionError('Publisher token missing')
        status, headers, _ = request(f'{args.hosted_url}/v2/{self.name}/blobs/uploads/', method='POST', token=token, data=b'')
        if status != 202:
            raise AssertionError(f'Upload initiation failed: HTTP {status}')
        location = external_url(args.hosted_url, headers['Location'])
        # Complete our protocol probe as an empty blob instead of abandoning it.
        location += ('&' if '?' in location else '?') + 'digest=sha256:' + hashlib.sha256(b'').hexdigest()
        status, headers, _ = request(location, method='PUT', token=token, data=b'', headers={'Content-Type':'application/octet-stream'})
        if status != 201:
            raise AssertionError(f'Upload completion failed: HTTP {status}')
        external_url(args.hosted_url, headers['Location'])
        self.check('external HTTPS realm and upload locations')
        for label, credential in [('anonymous', None), ('invalid', {'username':'invalid-smoke', 'password':'invalid-smoke'}), ('consumer', self.consumer)]:
            status, denied_token = bearer(args.hosted_url, credential, self.name, 'pull,push')
            if status == 200:
                status, _, _ = request(f'{args.hosted_url}/v2/{self.name}/blobs/uploads/', method='POST', token=denied_token, data=b'')
            require_denial(status)
            self.check(label + ' push denied', status=status)
        status, _, _ = request(args.admin_url + '/service/rest/v1/repositories', credentials=self.publisher)
        require_denial(status)
        self.check('publisher administration denied', status=status)
        components = self.components()
        if not components:
            raise AssertionError('Could not find test-owned component for deletion denial')
        component = components[0]; owned_component(component, self.names)
        status, _, _ = request(args.admin_url + '/service/rest/v1/components/' + quote(component['id'], safe=''), method='DELETE', credentials=self.publisher)
        require_denial(status)
        require_digest(old, self.digest(args.hosted_url, self.name, 'current', self.publisher))
        self.check('publisher deletion denied and image retained', status=status)
        (context / 'version').write_text('version-two')
        self.command(['docker', 'build', '--provenance=false', '-t', reference, str(context)])
        self.push(reference)
        new = self.digest(args.hosted_url, self.name, 'current', self.publisher)
        if old == new:
            raise AssertionError('Replacing the tag did not change the manifest')
        self.pull(args.hosted_url, self.name, 'current', new, 'replacement-tag-pull', self.hosted_auth)
        self.pull(args.hosted_url, self.name, old, old, 'old-digest-retained', self.hosted_auth)
        require_digest(new, self.digest(args.group_url, self.name, 'current', self.consumer))
        self.pull(args.group_url, self.name, 'current', new, 'consumer-group-pull', self.group_auth)
        upstream = self.digest(args.group_url, 'library/busybox', '1.37.0', self.consumer)
        # Upstream may be a multiarch index; skopeo selects one platform and
        # validates its manifest/layers, recorded separately from the index.
        target = self.root / 'upstream'
        self.command(['skopeo', 'copy', '--authfile', str(self.group_auth), f'docker://{urlsplit(args.group_url).netloc}/library/busybox:1.37.0', f'oci:{target}:smoke'])
        selected = json.loads((target / 'index.json').read_text())['manifests'][0]['digest']
        verify_oci(target, selected)
        self.check('upstream Docker Hub regression', index_digest=upstream, selected_digest=selected)
        if collision_enabled(args.environment):
            # The fixture is disposable; production never shadows upstream names.
            self.names.add('library/busybox')
            collision = urlsplit(args.hosted_url).netloc + '/library/busybox:1.37.0'
            self.local_images.append(collision)
            self.command(['docker', 'tag', reference, collision]); self.push(collision)
            require_digest(new, self.digest(args.group_url, 'library/busybox', '1.37.0', self.consumer))
            self.pull(args.group_url, 'library/busybox', '1.37.0', new, 'hosted-first-collision', self.group_auth)

    def cleanup(self):
        import shutil
        try:
            for component in self.components():
                owned_component(component, self.names)
                status, _, _ = request(self.args.admin_url + '/service/rest/v1/components/' + quote(component['id'], safe=''), method='DELETE', credentials=self.admin)
                if status not in (204, 404):
                    raise AssertionError(f'Owned smoke cleanup failed: HTTP {status}')
            self.report['cleanup'] = 'owned components removed'
        finally:
            for auth in self.auths:
                shutil.rmtree(auth.parent)
            if self.local_images:
                self.command(['docker', 'image', 'rm', *self.local_images])


def main():
    import argparse
    import os
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment', required=True, choices=['development', 'production'])
    for flag in ['hosted-url', 'group-url', 'publisher-credentials-file', 'consumer-credentials-file', 'admin-credentials-file', 'admin-url', 'work-dir', 'report']:
        parser.add_argument('--' + flag, required=True)
    args = parser.parse_args()
    os.umask(0o077)
    for url in [args.hosted_url, args.group_url]:
        validate_endpoint(args.environment, url)
    # Administrative probes/cleanup use an explicitly verified local tunnel.
    admin = urlsplit(args.admin_url)
    if admin.scheme != 'http' or admin.hostname != '127.0.0.1' or not admin.port or admin.username or admin.password or admin.path not in ('', '/'):
        parser.error('--admin-url must be a verified loopback API tunnel')
    smoke = Acceptance(args)
    try:
        smoke.run()
        smoke.report['passed'] = True
    except Exception as error:
        smoke.report['passed'] = False
        smoke.report['error'] = redact(str(error), smoke.credentials)
    finally:
        try:
            smoke.cleanup()
        except Exception as error:
            smoke.report['passed'] = False
            smoke.report['cleanup'] = 'failed: ' + redact(str(error), smoke.credentials)
        Path(args.report).write_text(json.dumps(smoke.report, indent=2) + '\n')
    print('Registry acceptance ' + ('passed' if smoke.report['passed'] else 'FAILED; see redacted report'))
    return 0 if smoke.report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
