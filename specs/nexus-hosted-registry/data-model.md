# Registry Configuration Model

| Entity | Identity and fields | Relations and invariants |
| --- | --- | --- |
| Hosted blob store | `docker-hosted`, file path `/nexus-data/docker-hosted` | Existing persistent NAS mount; do not destroy populated data during rollback |
| Hosted repository | `docker-hosted`, online, HTTP 8083, Docker v1 disabled, strict validation, ALLOW writes | References hosted blob store; TLS is outside Nexus |
| Group | Existing `docker-group`, connector 8082 | Members ordered hosted then existing proxy; existing resource identity preserved |
| Publisher role | `docker-hosted-publish` | Exactly hosted browse/read/add/edit; no delete, administration or wildcard actions |
| Publisher user | `docker-publisher`, independent generated password | Only publisher role; secret output sensitive |
| Consumer | Existing `docker`, current group role | No new write privileges or implicit password rotation |
| Private route | `nexus-docker-hosted`, `docker-push.${cluster_domain}` | Internal Gateway HTTPS; preserves registry path, external host and scheme |
| External backend | `nexus-docker-hosted` Service and EndpointSlice | NAS IP from `nfs_server`, TCP 8083; no selector |
| Development fixture | Namespace `nexus-${branch_slug}` | Disposable data and credentials; separate Terraform state and provider URL |
| Smoke artifact | Unique `homelab/registry-smoke-<run>` image, versioned tag and digest | Test owns only these artifacts; admin-only cleanup |

State progression: approved design → validated development configuration → recovered production state/credentials → reviewed production plan → hosted connector + NAS publication → Flux route applied → exact-endpoint smoke verified. Do not skip a stage or infer the next from a status-only probe.

Tag replacement moves the tag to a new manifest; it must not itself delete the previously stored manifest digest. Failed partial rollout retains existing production repositories and stored content.
