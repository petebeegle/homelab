# Planned Validation And Operator Guide

These commands describe the approved-design validation path; source changes and endpoint provisioning are not complete yet. Execute only after the plan and task/analysis gates.

## Preparation

1. Stage ignored Nexus/development provider inputs and needed kubeconfigs using the main checkout's `.codex/scripts/stage_implementation_secrets.sh`; install into matching paths with `install_implementation_secrets.sh`. Keep state and client auth files private under `.codex/tmp/`.
2. Confirm the development API server is `https://192.168.30.170:6443`, and check the LAN branch hostname resolves to `192.168.30.225` with trusted TLS after deployment.
3. Run Terraform validation, Compose validation, rendered-manifest checks, relevant Python tests and generated architecture checks from `plan.md`.

## Development deployment

After required artifacts permit pushing the branch:

```sh
python3 tools/development/verify_branch_deploy.py \
  --app nexus --branch codex/nexus-hosted-registry \
  --slug nexus-hosted-registry \
  --kubeconfig "$HOME/.kube/homelab-development.config" \
  --timeout 20m --keep
```

The branch must exist on origin. Do not pass `--terraform-apply`. The verifier still plans development infrastructure; supply its ignored inputs. Bootstrap the fixture's generated admin password securely, then use a separate scratch Terraform directory/state and the development API port-forward to configure the same repository resources. Reconfirm the provider URL before apply.

Run the full [registry acceptance matrix](contracts/registry.md) with development-only publisher/consumer credentials. Record the tested branch revision, actual Gateway parent/conditions, URL, digests, negative permissions and cleanup. Delete the branch Flux Kustomization, wait for namespace deletion, then delete its GitRepository; do not delete production data or credentials.

## Production rollout prerequisites

Recover authoritative Nexus state and verify the current consumer password before planning against production. The saved workspace consumer credentials currently fail; do not overwrite the live account to bypass this prerequisite. An explicitly approved coordinated reset requires an amended plan.

Once baseline and feature plans are reviewed and development smoke passes: apply hosted resources, publish NAS 8083 while preserving the deployed image/data mount, and let Flux reconcile the new route. Confirm the existing group remains healthy after the NAS container recreation. Run the full matrix on the production URLs before handing off.

## Image publishing after rollout

Retrieve the publisher password directly into Docker's stdin using a private client configuration directory:

```sh
terraform -chdir=terraform/external/nexus output -raw nexus_docker_publisher_password |
  docker login docker-push.lab.petebeegle.com \
    --username docker-publisher --password-stdin

docker tag YOUR_LOCAL_IMAGE docker-push.lab.petebeegle.com/homelab/YOUR_IMAGE:YOUR_TAG
docker push docker-push.lab.petebeegle.com/homelab/YOUR_IMAGE:YOUR_TAG
```

Use the existing pull-only identity to consume `docker-registry.petebeegle.com/homelab/YOUR_IMAGE:YOUR_TAG`. Deployment consumers can pin the verified digest. Never put the password in a command argument or commit Docker's auth file.
