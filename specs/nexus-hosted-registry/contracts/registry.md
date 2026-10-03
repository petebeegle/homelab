# Docker Registry Interface Contract

## Endpoints and identities

- Production hosted: `https://docker-push.lab.petebeegle.com`.
- Existing production group: `https://docker-registry.petebeegle.com`.
- Development hosted: `https://docker-push-nexus-hosted-registry.dev.lab.petebeegle.com`.
- Development group: `https://docker-group-nexus-hosted-registry.dev.lab.petebeegle.com`.
- Published image reference: `<host>/homelab/<image>:<tag>` or `<host>/homelab/<image>@sha256:<digest>`, without a URL scheme or repository-directory prefix.
- `docker-publisher`: hosted read/write only, no administrative/delete capabilities.
- Existing consumer: group pulls only; hosted write must be denied.

All client requests use trusted HTTPS. Authentication challenges and upload Location headers must resolve to the same externally reachable HTTPS endpoint, including relative locations resolved against that endpoint. Basic or Bearer challenges are handled by the standard client; never log credentials or tokens.

## Acceptance matrix

| Operation | Expected result |
| --- | --- |
| Unauthenticated hosted `/v2/` | Valid TLS and authentication challenge, not a readiness/push success claim |
| Publisher login and multi-layer push | Success, including one layer over 10 MiB |
| Clean-client hosted pull | Same manifest digest and retrievable layers |
| Consumer group pull of hosted image | Same manifest digest as hosted URL |
| Consumer group pull of known upstream image | Success, preserving the cache workflow |
| Publisher replaces its smoke tag | Tag resolves to new digest; old digest remains retrievable |
| Anonymous/invalid-credential/consumer hosted push | Authentication/authorization denial; network failure is not a passing denial |
| Publisher deletion of owned smoke component | Denied; component remains retrievable |
| Publisher access to administrative user listing | Denied; role configuration additionally proves no management privileges |

The smoke utility accepts hosted/group URLs plus protected credential-file paths, and produces a redacted JSON report with checks, HTTP outcomes, tested client network, tags, and digests. Passwords do not appear in command arguments, reports or exception text. Separate auth/storage directories ensure a clean pull does not reuse the locally built image.

Failures return nonzero and identify DNS, TLS, authentication, authorization, upload, digest, or cleanup layer. Only test-owned images are eligible for cleanup; persistent user images and Nexus repositories are never smoke-cleanup targets.
