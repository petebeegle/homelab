# Evidence: onepassword-prod-foundation

**Branch**: `codex/onepassword-prod-foundation`
**Base**: `origin/main` at merged phase-1 revision `7ca874e3ca15a4174d793408da7bc182bdcf2c37`
**Status**: Implementation in progress

## Prior Gate

- Development operator sync/rotation: PASS in `specs/onepassword-dev-foundation/evidence.md`.
- Observed development Secret resourceVersion: `51596478 -> 51597279`.
- Observed development pod UID: `810fa831-46a4-43f8-8a5a-f892865f0eef -> 7979058d-b10d-4928-afa4-9850e2eb09d8`.
- Merged phase-1 revision applied by development Flux: `main@sha1:7ca874e3ca15a4174d793408da7bc182bdcf2c37`.

## Local Validation

| Check | Result | Evidence |
| --- | --- | --- |
| Focused production policy tests | PASS | Two tests cover complete repository policy and rejection of Secret-bearing item metrics. |
| Existing canary tests | PASS | Six metadata-only readiness, rotation, failure, timeout, and cleanup tests. |
| Codex harness | PASS | 81 tests. |
| Terraform production init/validate | PASS | Configuration valid; only pre-existing Proxmox provider deprecation warnings. |
| Terraform docs | PASS | Pinned terraform-docs 0.23.0 refreshed the production input table; unrelated generated files remained byte-identical. |
| Development and production entrypoint renders | PASS | `kubectl kustomize` completed for both roots. |
| kubeconform 0.7.0 | PASS | 121 resources, 44 validated, 77 missing-schema skips, zero invalid/errors. |
| Direct-auth chart policy | PASS | Official chart 2.4.1 rendered operator 1.12.0 with zero Connect or token-valued Secret resources. |
| Architecture generator | PASS | Generated output and subsequent `--check` agree. |
| Pre-commit | PASS | All YAML, Kubernetes, Terraform, docs, architecture, and repository policy hooks passed. |
| Bootstrap shell syntax | PASS | Both bootstrap scripts and chart assertion parse successfully. |
| SOPS coexistence diff | PASS | Current/base counts remain 17 Flux SOPS decryption blocks and 16 encrypted Secret manifests; no SOPS, decryption, or consumer reference line changed. |

The phase adds only the production operator activation plus monitoring configuration under Kubernetes. No existing application manifest changes.

## Live Production Validation

### Bootstrap trust roots

PASS on 2026-08-09 using the production kubeconfig and authenticated user `op` session:

- `flux-system/sops-age` remained present with its original creation timestamp `2026-03-21T03:49:13Z`.
- `onepassword-system` was created and reports `Active`.
- `onepassword-system/onepassword-service-account-token` was created as an `Opaque` Secret at `2026-08-09T23:08:46Z`.
- The helper reported provider `dual`; no token or Age-key value was printed or inspected.
- Production operator resources were not reconciled before the Git change, so existing workloads remained on SOPS.

Pending merge/exact-main Flux reconciliation and production-vault canary.

## Secret Safety

No Secret value will be recorded here. Evidence is limited to identifiers, revisions, readiness conditions, resource versions, pod UIDs, and cleanup state.
