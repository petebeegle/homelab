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

## Rebase

- Command: `git fetch origin && git rebase origin/main`
- Result: PASS after conflict resolution.
- New base: `origin/main` at
  `ad0d5454dfdb44b1bdd1d54ad5ad89985aaf2c04`.
- Rebased implementation commit before evidence refresh:
  `c35bb9cfce7be3fba2f20804691a7446c26884f0`.
- Conflicts resolved:
  - `docs/runbooks/home-assistant.md`: kept upstream UI-managed desk Elgato
    wording and added the PVC-writable `/config/automations.yaml` guidance.
  - `specs/home-assistant-ui-automation/{spec.md,plan.md,tasks.md,evidence.md}`:
    kept the expanded automations-writability implementation scope and refreshed
    evidence after validation.
- Publish note: The first post-rebase smoke attempt failed at the verifier's
  plain `git push` because the remote branch still pointed at the pre-rebase
  SHA. The branch was updated with
  `git push --force-with-lease origin HEAD:refs/heads/codex/home-assistant-ui-automation`,
  then the same smoke command with `--push` was rerun successfully.

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
| Rendered automations mount/content check | PASS | Rendered base and branch output have no `automations.yaml` ConfigMap data key and no `/config/automations.yaml` volumeMount; both include init seeding with `[ -f /config/automations.yaml ] || printf '[]\n' > /config/automations.yaml`. |
| Source automations mount/content check | PASS | Base and branch kustomizations no longer reference `automations.yaml=config/automations.yaml`; deployments no longer mount `/config/automations.yaml`; both init containers seed missing automation YAML; both `configuration.yaml` files keep `automation: !include automations.yaml`; tracked base/branch `config/automations.yaml` files are removed. |
| Offline Home Assistant config validation | SKIP | No local `hass` or `home-assistant` CLI was available, and PyYAML is not installed. Kustomize render plus targeted manifest/content checks were used as substitutes. |
| `python3 tools/architecture/render.py --check` | PASS | Generated architecture documentation remains current after Kubernetes manifest edits. |
| `git diff --check` | PASS | No whitespace errors. |
| `git status --short` | PASS | Expected tracked changes only before amend. |

## Development Validation

- Profile: home-assistant
- Branch slug: home-assistant-ui-automation
- Command:
  `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-ui-automation --slug home-assistant-ui-automation --kubeconfig ~/.kube/homelab-development.config --timeout 20m --push`
- Result: PASS.
- Pushed branch revision fetched by Flux:
  `codex/home-assistant-ui-automation@sha1:c35bb9cfce7be3fba2f20804691a7446c26884f0`.
- Remote branch check:
  `git ls-remote origin refs/heads/codex/home-assistant-ui-automation`
  returned `c35bb9cfce7be3fba2f20804691a7446c26884f0`.
- Runtime checks:
  - Terraform development `init`, `validate`, and `plan -detailed-exitcode`
    completed; plan reported expected unapplied development-cluster resources
    and provider deprecation warnings.
  - Branch `GitRepository`
    `branch-home-assistant-home-assistant-ui-automation` was created and became
    Ready.
  - Branch `Kustomization`
    `branch-home-assistant-home-assistant-ui-automation` applied revision
    `codex/home-assistant-ui-automation@sha1:c35bb9cfce7be3fba2f20804691a7446c26884f0`
    and became Ready.
  - Namespace `home-assistant-home-assistant-ui-automation` became Active.
  - Pod `home-assistant-home-assistant-ui-automation-85fb78586c-vg8wb` became
    Ready.
  - PVC `home-assistant-config-home-assistant-ui-automation` was checked by the
    Home Assistant smoke profile.
  - Service `home-assistant-home-assistant-ui-automation` existed with
    ClusterIP `10.108.51.254`.
  - HTTPRoute `home-assistant-home-assistant-ui-automation` was checked by the
    Home Assistant smoke profile.
  - In-cluster curl probe against the Home Assistant service shell succeeded.
- Report path: N/A; verifier emitted command output only.
- Cleanup: PASS. Deleted branch Kustomization, waited for namespace
  `home-assistant-home-assistant-ui-automation` deletion, and deleted branch
  GitRepository.
- Note: The smoke command intentionally used `--push`, so the branch was pushed
  for Flux to fetch the committed manifest fix before this evidence-only
  amendment.

## Documentation Impact

- Updated: `docs/runbooks/home-assistant.md`
- Generated docs: Not updated; Kubernetes and Terraform topology did not
  require regenerated output; `python3 tools/architecture/render.py --check`
  passed.
- No-docs rationale: N/A

## Exceptions And Follow-Ups

- None.

## Final State

- Final branch: `codex/home-assistant-ui-automation`
- Final local commit: Amended after smoke evidence update; exact SHA is reported
  in handoff to avoid stale exact-commit evidence inside the commit.
- Pushed smoke-tested branch revision:
  `c35bb9cfce7be3fba2f20804691a7446c26884f0`.
