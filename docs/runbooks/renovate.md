---
status: current
scope:
  - renovate
  - dependency-management
created: 2026-05-16
last_verified: 2026-11-17
---

# Renovate

Renovate runs in the `renovate` namespace and reads repository policy from
`renovate.json`.

## Flux Updates

Flux component updates found in
`kubernetes/clusters/**/flux-system/gotk-components.yaml` are grouped into a
single `fluxcd` pull request. Generated `gotk-*.yaml` files are ignored by
yamllint at the top-level `.yamllint.yaml` ignore scope; Kubernetes render and
schema validation still run against the cluster kustomizations.

## Terraform Docs

Terraform dependency updates run
`./tools/renovate/update-terraform-docs.sh` as a Renovate post-upgrade task. The
script refreshes Terraform READMEs containing `<!-- BEGIN_TF_DOCS -->` with
pinned `terraform-docs` v0.23.0, matching CI and pre-commit expectations.

The self-hosted Renovate app allows only this exact command for Terraform docs
regeneration. The script uses an existing `terraform-docs` only when it is
v0.23.0; otherwise it downloads the pinned linux-amd64 release into a temporary
directory and removes it before exiting.

## Keeping Renovate PRs green

Renovate edits version strings and, for some managers, lock files. It does not
run repo tooling (apart from the Terraform docs task above), so anything that
must change alongside a version has to be something Renovate already updates.
`tools/renovate/tests/test_renovate_config.py` enforces the rules below.

- **Terraform lock files.** Renovate updates a `.terraform.lock.hcl` only for a
  provider declared in a `.tf` file in the lock file's directory or below it.
  Providers declared only in `terraform/modules/*` got their constraint bumped
  while the root lock files stayed behind, and `terraform init` failed. Each
  root (`terraform/production`, `terraform/development`) therefore redeclares
  every provider its modules use, at the same exact version. When a module gains
  a provider, add it to each root that uses the module and run
  `terraform init -upgrade` there.
- **Playwright.** The runner image (`tools/ci/runner-image/Dockerfile`), the
  synthetics CronJob image and every `@playwright/test` pin (`tests/browser`,
  `tests/smoke`, `kubernetes/apps/synthetics/smoke`) are one `playwright`
  group, so they move in one PR. `ignorePaths` is set to `**/node_modules/**`
  because the `config:recommended` default ignores `**/tests/**`, which hid
  `tests/browser` and `tests/smoke` and left the synthetic smoke lock-file
  mirror out of step.
- **Generated docs.** `docs/architecture.md` replaces pinned refs in remote
  kustomize resources with `<ref>`, so a version bump does not make it stale.
  Keep version strings out of generated output.
- **Policy checks.** Checks read versions from the committed manifests instead of
  hardcoding them (for example `tools/policy/check_onepassword_operator_chart.sh`
  renders whatever chart version the HelmRelease pins).

An existing Renovate PR picks up a fix on `main` only when it is rebased: tick
its rebase checkbox, or let the next run recreate it.

## Run It By Hand

Renovate runs as a CronJob in the `renovate` namespace. To trigger a run now:

```sh
kubectl create job --from=cronjob.batch/renovate renovate-manual-run -n renovate
```

Delete the job afterwards. For a local dry run with a token:

```sh
docker run --rm \
  -e LOG_LEVEL="debug" \
  -e RENOVATE_CONFIG="$(cat renovate.json)" \
  renovate/renovate:<version> \
  --token "$TOKEN" --dry-run="true" petebeegle/homelab
```
