# Evidence: Jellyfin SOPS Decryption Fix

## Discovery

- Live decoded `jellyfin/jellyfin-secrets.JELLYFIN_OAUTH_CLIENT_SECRET` begins with a SOPS `ENC[` envelope.
- Production `flux-system/app-jellyfin` lacks `spec.decryption` in Git.
- Status-only local SOPS comparison proved the committed Jellyfin and Authentik plaintext bytes match.

## Human Gates

- Intent/spec/plan/task scope approved by the user on 2026-08-10 after the separate prerequisite PR, exact configuration change, and no-output acceptance were stated.
- Clarification produced no critical questions; scope and failure behavior are explicit.
- Requirements checklist passes 8/8.

## Validation

- Pre-change structural assertion: expected failure confirmed because `app-jellyfin` had no `spec.decryption`.
- Spec Kit analyze: 6/6 functional requirements and 4/4 success criteria mapped to tasks; zero ambiguity, duplication, inconsistency, or constitution findings.
- Spec Kit agent-context update was not run because this repository does not include `.specify/scripts/bash/update-agent-context.sh`; no agent guidance change is required by the feature.
- Production and development root renders: PASS.
- Rendered `flux-system/app-jellyfin`: exactly one `spec.decryption`, `provider: sops`, `secretRef.name: sops-age`.
- Committed OAuth plaintext equality/non-envelope comparison: PASS with status-only output.
- Diff-scope assertion: no Secret, consumer, workload, Authentik blueprint, or development path changed.
- Architecture generator: regenerated and check PASS; only Jellyfin's decryption column changes from `no` to `sops`.
- Direct-auth 1Password chart and production-foundation policies: PASS.
- Codex harness: 81 tests PASS.
- Full pre-commit: PASS, including YAML, Kubernetes validation, generated architecture, and repository policies.
- `git diff --check`: PASS.
- Local kubeconform: unavailable in the devcontainer; CI installs pinned 0.7.0. Local `k8svalidate` passed.
- Spec Kit converge: clean; all local buildable requirements are satisfied and no convergence tasks were appended. Post-merge acceptance remains intentionally pending.

## Development Validation Exception

The edited Flux Kustomization exists only under `kubernetes/clusters/production`. Development Jellyfin is exercised through a branch profile with a placeholder OAuth value, so a development smoke would neither reconcile this resource nor test SOPS decryption. Copying the production credential into development was rejected because it violates environment isolation. Substitute evidence is the pre/post structural assertion, both cluster renders, status-only committed-value equality, broad local policy/tests, and mandatory exact-revision production acceptance after merge.

## Post-Merge Acceptance

Pending merge.

## PR State

- Branch: `codex/jellyfin-sops-decryption-fix`
- Commit subject: `fix: enable Jellyfin SOPS decryption`
- Draft PR: #390
- Local worktree clean after publication.
