# Evidence: home-assistant-ui-automation

**Branch**: `codex/home-assistant-ui-automation`
**Risk Tier**: medium
**Started**: 2026-07-04

## Spec Kit Initialization

- Command: Manual artifact creation from `.specify/templates/` after reading
  repository SDD runbooks.
- Outcome: Created `spec.md`, `plan.md`, `tasks.md`, and this `evidence.md`.
- Spec Kit version: Not re-initialized for this implementation; existing repo
  templates used.
- Integration: Existing repository Spec Kit integration.
- Fallback: N/A.
- Note: `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks
  --include-tasks` exited `0` but inferred
  `specs/pretty-discord-alert-triage-cards` instead of this branch's feature
  directory, so implementation validation used the explicit SDD context
  validator below.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_active_implementation.py --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | `.codex/tmp/active-implementation` matched branch, owner, and clone path. |
| `python3 tools/codex-harness/validate_implementation_plan.py --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | `.codex/tmp/implementation-plan.yaml` matched the active marker. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Owner attestation and delegation token evidence validated. No verifier approval was created. |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence` | PASS | Durable SDD artifacts are present and non-empty. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `kubectl kustomize kubernetes/apps/home-assistant` | PASS | Rendered successfully. |
| `kubectl kustomize kubernetes/apps/home-assistant/branch` | PASS | Rendered successfully. |
| `diff -u kubernetes/apps/home-assistant/config/packages/code_first.yaml kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml` | PASS | No differences; base and branch packages match. |
| `rg 'desk_elgato_ambient_balance|desk_light_auto_balance' kubernetes/apps/home-assistant` | PASS | Exit `1` with no matches, confirming removed identifiers are absent from Git-owned Home Assistant config. |
| `git diff --check` | PASS | No whitespace errors. |
| `git status --short` | PASS | Expected tracked changes only before commit: runbook, two package files, and `specs/home-assistant-ui-automation/`. |

## Development Validation

- Profile: home-assistant
- Branch slug: home-assistant-ui-automation
- Command:
  `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-ui-automation --slug home-assistant-ui-automation --kubeconfig ~/.kube/homelab-development.config --timeout 20m --push`
- Result: PASS.
- Pushed branch revision fetched by Flux:
  `codex/home-assistant-ui-automation@sha1:7fa197b2cecc92eaeace14d5b89c54ef1a9b2429`.
- Remote branch check:
  `git ls-remote origin refs/heads/codex/home-assistant-ui-automation`
  returned `7fa197b2cecc92eaeace14d5b89c54ef1a9b2429`.
- Runtime checks:
  - Terraform development `init`, `validate`, and `plan -detailed-exitcode`
    completed; plan reported expected unapplied development-cluster resources
    and provider deprecation warnings.
  - Branch `GitRepository`
    `branch-home-assistant-home-assistant-ui-automation` was created and became
    Ready.
  - Branch `Kustomization`
    `branch-home-assistant-home-assistant-ui-automation` applied revision
    `codex/home-assistant-ui-automation@sha1:7fa197b2cecc92eaeace14d5b89c54ef1a9b2429`
    and became Ready.
  - Namespace `home-assistant-home-assistant-ui-automation` became Active.
  - Pod `home-assistant-home-assistant-ui-automation-56954495fc-88758` became
    Ready.
  - PVC `home-assistant-config-home-assistant-ui-automation` was checked by the
    Home Assistant smoke profile.
  - Service `home-assistant-home-assistant-ui-automation` existed with
    ClusterIP `10.98.86.152`.
  - HTTPRoute `home-assistant-home-assistant-ui-automation` was checked by the
    Home Assistant smoke profile.
  - In-cluster curl probe against the Home Assistant service shell succeeded.
- Report path: N/A; verifier emitted command output only.
- Cleanup: PASS. Deleted branch Kustomization, waited for namespace
  `home-assistant-home-assistant-ui-automation` deletion, and deleted branch
  GitRepository.
- Note: The smoke command intentionally used `--push`, so the branch was pushed
  for Flux to fetch before this evidence-only amendment.

## Documentation Impact

- Updated: `docs/runbooks/home-assistant.md`
- Generated docs: Not updated; Kubernetes and Terraform topology did not
  change, and `docs/architecture.md` is unaffected.
- No-docs rationale: N/A

## Exceptions And Follow-Ups

- None.

## Final State

- Final branch: `codex/home-assistant-ui-automation`
- Final local commit: Amended after smoke evidence update; exact SHA is reported
  in handoff to avoid stale exact-commit evidence inside the commit.
- Pushed smoke-tested branch revision:
  `7fa197b2cecc92eaeace14d5b89c54ef1a9b2429`.
