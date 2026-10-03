# Research: Nexus Hosted Registry

## Provider and protocol

- **Decision**: Use a hosted HTTP connector behind Gateway TLS, with explicit publisher privileges. Nexus provider 2.8.0 supports `http_port`, strict validation, and `write_policy=ALLOW`; its subdomain connector is PRO-only. [Pinned provider schema](https://raw.githubusercontent.com/datadrivers/terraform-provider-nexus/v2.8.0/docs/resources/repository_docker_hosted.md).
- **Rationale**: The current instance rejects group pushes, while a direct hosted connector fits Community edition and avoids changing the pull-cache endpoint.
- **Alternatives**: PRO group publication is out of scope; repository path rewrites add client/proxy complexity; direct Synology TLS for the new endpoint would add another certificate lifecycle instead of using the required Gateway model.
- **Decision**: Preserve external Host and forwarded HTTPS metadata and test realm/Location responses. [Sonatype reverse proxy requirements](https://help.sonatype.com/en/run-behind-a-reverse-proxy.html) and [Docker connector guidance](https://support.sonatype.com/hc/en-us/articles/115013153887-Docker-Repository-Configuration-and-Client-Connection).

## Existing state and credentials

- **Observation**: Nexus state and initialized-backend metadata are absent locally. Live user `docker` is active with `docker-group-view`; its role has only the existing group's wildcard repository privileges. Existing realms are `NexusAuthenticatingRealm` and `DockerToken`.
- **Observation**: Credentials found in production tfvars and saved Talos machine configuration returned HTTP 401. No secrets were printed or changed. A user question requests the authoritative secret location or an explicitly coordinated reset.
- **Decision**: Require recovery before production apply. Random-password import can trigger replacement if generation settings differ, so a successful import is not sufficient evidence of safe adoption. [Random provider 3.9.0 import limitations](https://raw.githubusercontent.com/hashicorp/terraform-provider-random/v3.9.0/docs/resources/password.md).
- **Alternative rejected**: Applying the root without state or allowing a fresh random password would recreate resources or invalidate consumer credentials.

## Development topology

- **Decision**: Disposable branch-scoped Nexus with `emptyDir`, matching production version, isolated Terraform state, two HTTPS routes, and a separate registry smoke harness.
- **Rationale**: Development is available: node `192.168.30.170` is Ready; internal Gateway `192.168.30.225` is Programmed. The node reports roughly 22 GiB allocatable memory. A second permanent Nexus is unnecessary.
- **Research lane**: `registry_dev_research` inspected verifier code, branch templates, runbook, and cleanup behavior read-only. Profile naming must match `nexus-${branch_slug}` and `branch-nexus-${branch_slug}`. The verifier always plans development Terraform, so stage its tfvars even when no infrastructure apply is intended.
- **Limitation**: Built-in HTTP probes use plain Service HTTP and reject a normal `/v2/` 401; they cannot prove TLS, auth, upload or pull. The branch fixture cannot prove NAS port publication; final production smoke must.
- **Alternative rejected**: `nfs-csi-storage` is Retain; a disposable PVC would leave PV/NAS cleanup obligations. Ephemeral data is appropriate for this fixture and not a change to production persistence.

## Network and runtime

- **Observation**: `docker-push.lab.petebeegle.com` resolves to `192.168.30.241`. `docker-push-nexus-hosted-registry.dev.lab.petebeegle.com` resolves to `192.168.30.225` from the workspace.
- **Observation**: NAS TCP 8083 currently refuses connections; confirm no configured-but-stopped port owner before assignment.
- **Decision**: Reuse the external selectorless Service/EndpointSlice pattern and LAN HTTPS listener. Leave the existing Synology group route and certificate untouched.
- **Runtime precaution**: Compose currently names an unpinned `sonatype/nexus3` image. Capture the deployed image ID/digest and avoid pulling `latest` during connector publication; no Nexus upgrade is authorized.

## Remaining prerequisite

The technical design is defined. Production rollout remains blocked on consumer credential/state recovery or explicit approval to amend scope for a coordinated reset. This is not a justification for skipping development validation or silently rotating credentials.
