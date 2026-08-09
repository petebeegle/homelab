# Evidence: onepassword-dev-foundation

**Branch**: `codex/onepassword-dev-foundation`
**Risk Tier**: high
**Started**: 2026-08-01

## Spec Kit Initialization

- Command: Spec Kit specify/clarify/plan/checklist/tasks/analyze/implement/converge workflow
- Outcome: Local implementation complete; live development acceptance blocked on external 1Password prerequisites
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
| Converge | PASS | Rechecked all 11 functional requirements against implementation and tests; no unbuilt repository work remains in phase 1. Live acceptance remains explicitly gated. |

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
| `python3 -m unittest tools.development.tests.test_jellyfin_config_migration` | PASS | All 9 upstream Jellyfin migration tests passed after conflict resolution. |

## Rebase Evidence

- Rebased onto `origin/main` at `0d5e55a60696d4f49c0202dcfe74d1967235e1dd`.
- Resolved `.github/workflows/ci.yml` by preserving upstream Helm v5, Jellyfin repository, Flux CLI, and Jellyfin migration checks while retaining `tools/policy/check_onepassword_operator_chart.sh`.
- Resolved `.specify/feature.json` to `specs/onepassword-dev-foundation` for the active branch.
- Post-rebase implementation commit: `4702a9b6b7b6ed6a501c74e2dad1d6282453aef0`.
- Force-with-lease push and GitHub Actions verification: Pending.

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| Development 1Password operator and canary | Dedicated canary verifier plus development base reconciliation | BLOCKED | Development kubeconfig exists and the API is reachable, but `op whoami` is unauthenticated, ignored development tfvars are absent in this worktree, and the development vault, read-only service account, bootstrap token item, and disposable Login canary item cannot be confirmed or created here. No branch reconcile was attempted without its trust root. |

## Deployment State

- Source fetched SHA: Not available; live reconcile not attempted without the 1Password trust root
- Target applied SHA: Not available
- Live resource spec checked: Not available; local Helm/Kustomize renders passed
- Gateway/listener/DNS/certificate checked: Not applicable to this foundation
- Exact user-facing URL result: Not applicable; canary has no route

## Development Validation

- Profile: none
- Branch slug: onepassword-dev-foundation
- HEAD: Not applicable; branch was not activated
- Report path: This evidence file
- Cleanup: No canary or branch resources were created
- Result or exception: External credential prerequisite unavailable. Phase 2 MUST NOT start until `verify_branch_deploy.py --app whoami --include-cluster-base` and the live canary both pass on a pushed phase-1 commit.

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
- The ignored development tfvars and authenticated 1Password administration session must be staged/provided before live validation; no token value is requested in Git, Terraform, command arguments, or evidence.
- Branch push: PASS; `codex/onepassword-dev-foundation` exists on `origin`.
- Draft PR creation: PASS; [PR #381](https://github.com/petebeegle/homelab/pull/381) targets `main` and remains gated on live development acceptance.

## Final State

- Final branch: `codex/onepassword-dev-foundation`
- Final HEAD: Deferred to the implementation-owner handoff after the evidence/PR-status commit.
- Implementation commit: `4702a9b6b7b6ed6a501c74e2dad1d6282453aef0` (`feat: add 1password development foundation`, rebased)
