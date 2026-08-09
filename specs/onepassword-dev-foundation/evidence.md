# Evidence: onepassword-dev-foundation

**Branch**: `codex/onepassword-dev-foundation`
**Risk Tier**: high
**Started**: 2026-08-01
**Live acceptance completed**: 2026-08-09

## Spec Kit Initialization

- Command: Spec Kit specify/clarify/plan/checklist/tasks/analyze/implement/converge workflow
- Outcome: Local implementation and live development acceptance complete
- Spec Kit version: `0.12.5.dev0`
- Integration: `codex`
- Fallback: Worktree at `/home/vscode/homelab-worktrees/onepassword-dev-foundation`; `/workspaces/homelab-worktrees/` was not writable.

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent brief | PASS | User supplied the complete seven-phase migration outcome, constraints, rollout, and acceptance plan. |
| Spec approval | PASS | User explicitly requested implementation of the supplied plan; this PR is bounded to its first phase. |
| Clarify | SKIP | No unresolved scope, security, architecture, or acceptance decisions remain for phase 1. |
| Plan approval | PASS | Direct operator/service-account design and development-first rollout were explicitly approved by the user. |
| Checklist | PASS | Requirements and security checklists complete before implementation. |
| Tasks/analyze approval | PASS | Read-only analysis covered 11 requirements and 21 tasks with full coverage and no critical/high gaps; user implementation approval authorizes execution. |
| Converge | PASS | Rechecked all 11 functional requirements against implementation and tests; repository work and live development acceptance are complete for phase 1. |

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | Completed with no findings after spec, plan, tasks, and checklists were created. |
| Requirements/security checklists | PASS | 16/16 requirements checks and 13/13 security checks complete. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| Bootstrap TDD red phase | PASS | Five tests failed only because `install-flux-bootstrap-secrets.sh` did not yet exist; establishes the expected pre-implementation failure. |
| `python3 -m unittest discover -s tools/codex-harness/tests` | PASS | 81 tests passed, including eight bootstrap tests for all provider modes, idempotency, validation, redaction, file mode, and cleanup. |
| `python3 tools/development/tests/test_verify_onepassword_operator.py` | PASS | Six tests passed for readiness, ID resolution, metadata-only rotation, timeout/failure cleanup, cleanup failure, and `--keep`. Sentinel values did not appear in verifier output. |
| `tools/policy/check_onepassword_operator_chart.sh` | PASS | Rendered committed values against official chart `connect` 2.4.1; no Connect image, Connect auth environment, or Secret rendered; direct-auth operator 1.12.0 and resource constraints present. |
| `bash -n terraform/scripts/install-flux-bootstrap-secrets.sh terraform/scripts/flux-install.sh tools/policy/check_onepassword_operator_chart.sh` | PASS | Shell syntax valid. |
| `terraform fmt -check -recursive terraform` | PASS | Terraform sources formatted. |
| `terraform -chdir=terraform/development init -backend=false -input=false -no-color` | PASS | Providers initialized from the lock file. |
| `terraform -chdir=terraform/development validate -no-color` | PASS | Configuration valid; existing Proxmox datastore deprecation warnings remain. |
| Strict development, production, operator, and canary renders | PASS | Both cluster entrypoints and the parameterized canary rendered and passed `flux envsubst --strict`; `var=placeholder` was supplied only for a literal shell-expansion example embedded in an upstream CRD description. |
| `kubeconform -summary -ignore-missing-schemas` over four renders | PASS | Post-rebase: 127 resources found; 48 valid, 0 invalid, 0 errors, 79 skipped because schemas were intentionally unavailable. |
| Production render comparison against `origin/main` | PASS | Byte-identical production cluster render; no production path or `.sops.yaml` change. |
| `python3 tools/architecture/render.py --check` | PASS | Generated architecture is current after adding the development-only operator relationship. |
| `pre-commit run --all-files` | PASS | All YAML, Kubernetes, Terraform, generated-doc, and repository policy hooks passed. Terraform docs added the new non-secret development input to `terraform/development/README.md`. |
| `python3 tools/development/tests/test_verify_branch_deploy.py` | PASS | Post-rebase: all 32 tests passed; the prior baseline Immich discovery mismatch was fixed upstream. |
| Live-discovered branch-base regression | PASS | The first exact-HEAD attempt showed the self-managed root GitRepository resetting to `main` before branch-only child Kustomizations were created. The verifier now applies the exact checkout's development `infra` and `apps` Flux declarations before the second source pin; all 32 branch-verifier tests pass with ordering coverage. |
| `python3 -m unittest tools.development.tests.test_jellyfin_config_migration` | PASS | All 9 upstream Jellyfin migration tests passed after conflict resolution. |

## Rebase Evidence

- Rebased onto `origin/main` at `0d5e55a60696d4f49c0202dcfe74d1967235e1dd`.
- Resolved `.github/workflows/ci.yml` by preserving upstream Helm v5, Jellyfin repository, Flux CLI, and Jellyfin migration checks while retaining `tools/policy/check_onepassword_operator_chart.sh`.
- Resolved `.specify/feature.json` to `specs/onepassword-dev-foundation` for the active branch.
- Post-rebase implementation commit: `4702a9b6b7b6ed6a501c74e2dad1d6282453aef0`.
- Force-with-lease push: PASS at `0ad40d41903a96d6360fb80ee2a3fa2ae854324c`.
- GitHub Actions on the rebased source: PASS; Pre-commit, Python, Terraform, Kubernetes, Secrets, Agnix, and GitGuardian completed successfully.

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| Development bootstrap trust roots | Metadata-only Kubernetes inspection | PASS | `flux-system/sops-age` remained unchanged and `onepassword-system/onepassword-service-account-token` was created through an authenticated `op read` using `op://cluster bootstrap/onepassword-development-operator/credential`; no value was printed or recorded. |
| First exact-HEAD branch-base attempt | `verify_branch_deploy.py --app whoami --include-cluster-base` | FAIL, FIXED | Flux fetched `codex/onepassword-dev-foundation@sha1:96b9c47faf589621f9428740062c21e670eb615e`, but the root reconciled its self-managed source back to `main` before creating `onepassword-operator`. Cleanup restored `main`; no branch app resources were activated. T027 adds the regression fix and coverage before retry. |
| Second exact-HEAD branch-base attempt | Same verifier at `50dd2ad07373968130ead12c7d4d0a689cb3abf4` | FAIL, FIXED | The exact branch declarations created `onepassword-operator`, but the active self-managing root reacted to the source update and pruned it from `main`. Cleanup restored `main`. The verifier now suspends only the root during ordered child validation and always restores the source and resumes the root. |
| Corrected exact-HEAD development base and whoami smoke | `verify_branch_deploy.py --app whoami --include-cluster-base` | PASS | Flux fetched and applied `codex/onepassword-dev-foundation@sha1:9f69d60ac7c558acb1c9615c18a670e624e2c392`; ordered base Kustomizations, all active cluster pods, the temporary whoami Deployment, Service, and accepted HTTPRoute passed. The branch environment was removed automatically. |
| Initial 1Password canary sync | `verify_onepassword_operator.py --skip-rotation --keep` | PASS | `OnePasswordItem Ready=True`; generated Secret resource version `51596478`; consuming pod UID `810fa831-46a4-43f8-8a5a-f892865f0eef` was Ready. A prior status-update conflict was transient and the retained diagnostic rerun completed in 22 seconds. |
| 1Password rotation and automatic restart | Full canary verifier | PASS | Secret resource version changed `51596478 -> 51597279`; consuming pod UID changed `810fa831-46a4-43f8-8a5a-f892865f0eef -> 7979058d-b10d-4928-afa4-9850e2eb09d8`. No Secret value was requested or printed. |
| Canary cleanup and Flux restoration | Verifier cleanup plus metadata-only cluster inspection | PASS | Canary namespace was removed. Canonical `flux-system` source was restored to `main@sha1:0d5e55a60696d4f49c0202dcfe74d1967235e1dd`, root reconciliation resumed and reported Ready. The temporary branch-only Kustomization was deleted with `deletionPolicy: Orphan`; the bootstrap token, HelmRelease, and validated Operator Deployment remain intact for adoption after merge. |

## Deployment State

- Source fetched SHA: `9f69d60ac7c558acb1c9615c18a670e624e2c392`
- Target applied SHA: `9f69d60ac7c558acb1c9615c18a670e624e2c392`
- Live resource spec checked: chart `2.4.1`, operator image `1password/onepassword-operator:1.12.0`, HelmRelease Ready, Deployment `1/1`, and no Connect workload
- Gateway/listener/DNS/certificate checked: Not applicable to this foundation
- Exact user-facing URL result: Not applicable; canary has no route

## Development Validation

- Profile: `whoami` with development cluster base
- Branch slug: onepassword-dev-foundation
- HEAD: `9f69d60ac7c558acb1c9615c18a670e624e2c392`
- Report path: This evidence file
- Cleanup: Branch whoami resources and canary namespace removed; canonical Flux source restored to `main` and root reconciliation resumed
- Result or exception: PASS. Initial sync, rotation, automatic Deployment restart, and cleanup were proven without exposing values. Phase 1's live gate is satisfied.

## Documentation Impact

- Updated: development-cluster runbook, development tools README, generated Terraform development README, CI chart-render gate, SDD quickstart/contracts
- Generated docs: `docs/architecture.md` regenerated and checked
- No-docs rationale: Not applicable

## SDD Conformance

- Local sources checked: `AGENTS.md`, Spec Kit and implementation workflow runbooks, constitution, secret/TDD ADRs
- Upstream Spec Kit sources checked: Local initialized Spec Kit `0.12.5.dev0` skills and templates
- Human-gated Spec Kit alignment: User approval applies to this first bounded phase; live development evidence gates phase 2
- Artifact updates after implementation: Tasks and evidence converged after local implementation; no new repository tasks appended

## Exceptions And Follow-Ups

- Production phases remain intentionally unstarted until this phase has live development sync/rotation evidence.
- The operator-unavailable and `OnePasswordItem`-unready ten-minute alerts remain assigned to `onepassword-prod-foundation`, as declared out of scope in this phase's approved specification because development does not reconcile the monitoring stack.
- The development vault is `cluster development`; the read-only operator token is stored as the immutable `credential` field at the non-secret reference `op://cluster bootstrap/onepassword-development-operator/credential`.
- Branch push: PASS; `codex/onepassword-dev-foundation` exists on `origin`.
- Draft PR creation: PASS; [PR #381](https://github.com/petebeegle/homelab/pull/381) targets `main` and remains gated on live development acceptance.

## Final State

- Final branch: `codex/onepassword-dev-foundation`
- Final tested implementation HEAD: `9f69d60ac7c558acb1c9615c18a670e624e2c392`; the subsequent evidence-only commit records these results.
- Implementation commit: `4702a9b6b7b6ed6a501c74e2dad1d6282453aef0` (`feat: add 1password development foundation`, rebased)
