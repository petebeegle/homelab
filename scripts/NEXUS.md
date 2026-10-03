# Nexus Docker registry

Nexus runs in Synology Container Manager project `nexus`, using
`/volume2/Nexus/compose.yaml` and persistent data at `/volume2/Nexus/nexus-data`.
Terraform configuration lives in `terraform/external/nexus/`.

| Endpoint | Repository | Credentials | Purpose |
| --- | --- | --- | --- |
| `docker-push.lab.petebeegle.com` | `docker-hosted`, connector 8083 | `docker-publisher` | Publish and read local images |
| `docker-registry.petebeegle.com` | `docker-group`, connector 8082 | existing `docker` consumer | Pull hosted images and Docker Hub cache |

The hosted endpoint requires LAN connectivity. Its certificate and renewal belong
to the Kubernetes internal Gateway and cert-manager wildcard certificate. The
existing group endpoint retains its Synology reverse proxy/certificate renewal.
Group pushes require Nexus PRO; Community publishers must use the hosted endpoint.

**Rollout status:** the configuration is proposed on `codex/nexus-hosted-registry`.
Check `specs/nexus-hosted-registry/evidence.md` before assuming production is live.
The existing consumer credential and Terraform state have been recovered privately.
Production still requires the reviewed feature plan and development acceptance.
Do not run a fresh apply against existing Nexus.

## Credentials and publishing

The publisher has only hosted browse/read/add/edit privileges. It cannot administer
Nexus or delete components. The existing consumer role/password are preserved.
Tags may be replaced intentionally; pin deployment references by digest when needed.

After the reviewed production apply, retrieve the publisher password directly into
an isolated Docker config. Never paste it into commands, logs, PRs or manifests:

```bash
umask 077
mkdir -p .codex/tmp/nexus-publish
export DOCKER_CONFIG="$PWD/.codex/tmp/nexus-publish"
terraform -chdir=terraform/external/nexus output -raw nexus_docker_publisher_password |
  docker login docker-push.lab.petebeegle.com --username docker-publisher --password-stdin
docker tag my-app:latest docker-push.lab.petebeegle.com/homelab/my-app:latest
docker push docker-push.lab.petebeegle.com/homelab/my-app:latest
docker logout docker-push.lab.petebeegle.com
unset DOCKER_CONFIG
```

Consumers continue using their existing credentials with
`docker-registry.petebeegle.com/homelab/my-app:latest`. Hosted is the first group
member, followed by the Docker Hub proxy. Use a private namespace such as `homelab/`
to avoid unintentionally shadowing upstream names.

## Recover state before production changes

1. Recover the authoritative state backup and a verified working `docker` password
   from the approved secret store. Stage ignored inputs using the repository's
   implementation-secret scripts before worktree commands. Keep state, plans and
   credentials private; they contain passwords even when outputs are sensitive.
2. If recovery requires import, back up live configuration first. Import the
   existing blob store, proxy, group, role, user and security realms using the
   pinned provider's documented IDs (`active` for realms). Import the random
   password only after verifying the existing credential. Import defaults can
   propose password replacement when length/special settings differ: inspect them.
3. The consumer password lifecycle ignore prevents writes after import; the
   random-password alphabet ignore preserves imported generation metadata.
   Coordinated consumer rotation requires deliberately revisiting that safeguard.
   Produce a baseline plan that preserves every existing resource and password.
   Do not hand-edit state, accept replacements or reset the consumer to get past
   recovery. A reset needs an explicit amendment and coordinated consumer updates.
4. Review a saved feature plan. Expected changes are the hosted blob/repository,
   publisher password/role/user, outputs and hosted-first group membership only.
   Any existing-password change, replacement, deletion or unexplained drift blocks
   rollout. Do not publish unredacted plan JSON.

## Ordered production rollout

Development acceptance and normal PR review/status gates must pass first. Then:

1. Inspect the effective Container Manager project, ports, UID/GID, data mount and
   running image ID. Confirm 8083 is unallocated, including stopped containers.
   The running 3.87.1-01 image was identified as config digest
   `sha256:3bf69e5aab61f11153f33791078b38d4dad29fb830b759287cc51f6ef9964617`.
2. Back up the effective Compose configuration privately. Apply the reviewed Nexus
   Terraform saved plan. Existing UI/group connectors must remain available.
3. Install the reviewed Compose port addition using the existing project path.
   Recreate with the existing local image, no pull or upgrade. Preserve the data
   mount and UID/GID. A brief cache interruption is expected. Never use `down -v`.
4. Confirm UI 8081, group 8082 and hosted 8083 health and existing repository data.
   Let production Flux reconcile the merged `external` app route. Check the expected
   `gateway/internal` parent, current generation and Accepted/ResolvedRefs status.
5. Run the exact production HTTPS acceptance below. A `/v2/` 401 challenge alone is
   not proof that uploads, permissions or group pulls work.
6. Check a follow-up Terraform plan for unexpected drift and record cleanup.

If rollout fails, retain populated hosted storage. Roll back routing/port exposure
and group membership as appropriate, preserving the original group endpoint.
Disable the publisher if necessary; do not destroy the hosted repository/blob store
or remove the NAS data directory as a rollback shortcut.

## Development and exact-endpoint acceptance

The disposable fixture uses `emptyDir`, the production Nexus image digest and
separate credentials/state. It does not mount NAS storage. Verify the kubeconfig
server is `https://192.168.30.170:6443` before activation:

```bash
python3 tools/development/verify_branch_deploy.py \
  --app nexus --branch codex/nexus-hosted-registry --slug nexus-hosted-registry \
  --kubeconfig "$DEV_KUBECONFIG" --timeout 20m --keep
```

Never pass `--terraform-apply` for this fixture. Bootstrap its generated admin
password privately, rotate only the disposable admin and port-forward Service
`nexus-api` to `127.0.0.1:18081`. Copy the Nexus root `.tf` sources to a fresh private
scratch subdirectory, with a development-only provider URL and state. Call
`validate_dev_state` from the smoke module before every fixture apply; also verify
kube API, namespace, pod identity and tunnel. Never copy production Nexus state or
credentials into that fixture directory.

The smoke requires Docker and native Skopeo. Credentials are separate JSON files
with `username` and `password`, mode 0600. `--work-dir` must not already exist;
`--report` contains redacted evidence. The admin URL is a verified loopback tunnel
for permission tests and cleanup, not an externally exposed UI route.

```bash
python3 tools/nexus/verify_registry.py \
  --environment development \
  --hosted-url https://docker-push-nexus-hosted-registry.dev.lab.petebeegle.com \
  --group-url https://docker-group-nexus-hosted-registry.dev.lab.petebeegle.com \
  --admin-url http://127.0.0.1:18081 \
  --publisher-credentials-file "$PRIVATE_DIR/publisher.json" \
  --consumer-credentials-file "$PRIVATE_DIR/consumer.json" \
  --admin-credentials-file "$PRIVATE_DIR/admin.json" \
  --work-dir "$PRIVATE_DIR/run-1" --report "$PRIVATE_DIR/report.json"
```

Production uses `--environment production`, the two production URLs in the table,
a separate verified loopback tunnel to NAS port 8081, and recovered production
credentials. The smoke pushes a unique multi-layer image with a 12 MiB random
layer, independently downloads and hashes every OCI blob, replaces a tag, retrieves
the old digest, checks consumer group pulls and upstream pulls, and tests denied
writes/admin/deletion. Only development performs the upstream-name collision test.
Cleanup deletes only components created by this smoke; no repository/storage removal.

After development acceptance delete only `branch-nexus-nexus-hosted-registry`
Kustomization in `flux-system`, wait for namespace `nexus-nexus-hosted-registry`
deletion, then delete the matching GitRepository. Remove private fixture credentials,
client auth and state after evidence is saved. Namespace deletion removes fixture data.

## Diagnosing failures

- DNS failure: verify LAN DNS and expected Gateway address before TLS or Nexus.
- TLS failure: inspect the internal Gateway wildcard certificate for the new push
  endpoint; Synology owns the existing group endpoint certificate.
- Gateway 502/503: inspect Service/EndpointSlice, NAS 8083 publication and connector.
- `/v2/` 401 with a Bearer challenge is expected without credentials. Realm and upload
  Location URLs must retain the external HTTPS hostname, never NAS HTTP addresses.
- Push rejected with the PRO message: the client is using a group repository.
- HTTP 401/403: check which identity and exact repository privileges were used.
  Timeouts, connection failures and 5xx responses are not authorization denials.
- Hosted push succeeds but group pull differs: verify hosted-first membership,
  requested image name/tag and returned content digest.
