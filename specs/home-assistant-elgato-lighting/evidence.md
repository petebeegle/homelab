# Evidence: home-assistant-elgato-lighting

**Branch**: `codex/home-assistant-elgato-lighting`
**Risk Tier**: medium
**Started**: 2026-07-04

## Scope Update

- Existing docs-only/tiny SDD artifacts were revised for a medium-risk Home
  Assistant app behavior/config change.
- Implemented Git-owned desk Elgato ambient balance in
  `kubernetes/apps/home-assistant/config/packages/code_first.yaml` and mirrored
  it in `kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml`.
- Updated `docs/runbooks/home-assistant.md` with the Git-owned automation
  location and entities.
- Runtime Home Assistant `.storage`, config entries, credentials, SOPS secrets,
  Kubernetes workload, Gateway, PVC, Service, Flux, and generated architecture
  files were not changed.

## Spec Kit And Workflow Notes

| Command | Result | Notes |
| ------- | ------ | ----- |
| `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` | FAIL | Script could not resolve a feature directory because `.specify/feature.json` is not present. Continued from the explicit implementation path `specs/home-assistant-elgato-lighting/` required by the workflow and user request. |
| `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Runtime implementation marker accepted. |
| `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Runtime implementation plan accepted after scope/risk update. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Owner attestation accepted. |
| `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | SDD artifacts are present and non-empty. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `kubectl kustomize kubernetes/apps/home-assistant > .codex/tmp/home-assistant.render.yaml` | PASS | Production Home Assistant kustomization rendered successfully. |
| `kubectl kustomize kubernetes/apps/home-assistant/branch > .codex/tmp/home-assistant-branch.render.yaml` | PASS | Branch Home Assistant kustomization rendered successfully. |
| `docker run --rm -v "$PWD/.codex/tmp/ha-branch-check:/config" ghcr.io/home-assistant/home-assistant:2026.7.1 python -m homeassistant --script check_config --config /config` | PASS | Offline Home Assistant config check passed against a temporary copy of the branch config. The production package is identical to the branch package; production-only secrets/OIDC custom component were not required for this package sanity check. |
| `diff -u kubernetes/apps/home-assistant/config/packages/code_first.yaml kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml` | PASS | No diff; production/base and branch overlay package behavior match. |
| `rg -n "desk_light_auto_balance|desk_elgato_ambient_balance|office_desk_illuminance|elgato_key_light_air|color_temp_kelvin|brightness_pct|transition: 3" .codex/tmp/home-assistant.render.yaml .codex/tmp/home-assistant-branch.render.yaml` | PASS | Rendered ConfigMaps include the helper, automation, trigger sensor, target lights, documented color-temperature field, brightness percentages, and transition values. |
| `git diff --check` | PASS | No whitespace errors. |
| `git status --short` | PASS | Before evidence refresh, changed files were limited to the Home Assistant runbook, production/base package, branch package, and SDD artifacts. |

## Behavior Review

| Requirement | Result | Notes |
| ----------- | ------ | ----- |
| Trigger on illuminance changes | PASS | Automation uses `triggers: - trigger: state` with `entity_id: sensor.office_desk_illuminance`. |
| Manual enable helper | PASS | Package defines `input_boolean.desk_light_auto_balance`; automation conditions require it to be `on`. |
| Numeric sensor guard | PASS | Automation requires `is_number(trigger.to_state.state)` before converting to `desk_lux`. |
| Bright threshold | PASS | `desk_lux >= 400` turns both Elgato lights off with `transition: 3`. |
| Light fill | PASS | `250-399` lux sets ambient `35%`/`4000K` and camera `18%`/`3800K` with `transition: 3`. |
| Medium fill | PASS | `100-249` lux sets ambient `55%`/`3800K` and camera `28%`/`3600K` with `transition: 3`. |
| Strong fill | PASS | `<100` lux sets ambient `75%`/`3500K` and camera `38%`/`3300K` with `transition: 3`. |

## Development Validation

- Profile: home-assistant branch deploy
- Branch slug: home-assistant-elgato-lighting
- Validated branch/head:
  `codex/home-assistant-elgato-lighting@sha1:da780f3b5a0c3a993cf8062377ef4c5c2a684eda`
- Command:
  `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-elgato-lighting --slug home-assistant-elgato-lighting --kubeconfig ~/.kube/homelab-development.config --timeout 20m`
- Result: PASS
- Report path: Not captured in this evidence update; result details were
  provided by the verifier/operator after the run.
- Secrets preparation:
  `.codex/scripts/prepare_development_smoke_secrets.sh home-assistant-elgato-lighting /workspaces/homelab-ideas/home-assistant-elgato-lighting`
  installed `terraform/development/terraform.tfvars` before smoke.
- Terraform preflight: `init`, `validate`, and `plan` passed. Plan exited with
  detailed-exitcode `2` and showed planned development infra creates, accepted
  by verifier as an acceptable preflight result.
- Flux source: Branch `GitRepository` fetched
  `codex/home-assistant-elgato-lighting@sha1:da780f3b5a0c3a993cf8062377ef4c5c2a684eda`.
- Flux apply: Branch `Kustomization` became Ready.
- Runtime acceptance: Namespace
  `home-assistant-home-assistant-elgato-lighting` became Active; Home Assistant
  branch pod became Ready; Service, PVC, HTTPRoute, and in-cluster HTTP probe
  passed.
- Cleanup: Deleted the branch Kustomization, waited for namespace deletion, and
  deleted the branch GitRepository.
- Note: This evidence-only amend will produce a new local commit SHA after the
  successful smoke. The smoke validated the implementation content at
  `da780f3b5a0c3a993cf8062377ef4c5c2a684eda`; this amend records the result.

## Rebase Refresh

- Rebased onto current `origin/main`:
  `be0b777d96eb0262d8ddc9ff673828ed56d79a5a`
- Rebased branch HEAD before evidence amend:
  `bb0024a23aea3f1b3738230e16c4cd436c101383`
- Rebase conflicts: none; `git rebase origin/main` completed successfully.
- Branch state after rebase: `codex/home-assistant-elgato-lighting` was
  `ahead 2` of `origin/main` and no longer behind.

### Rebase Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `git fetch origin && git rev-parse origin/main && git rebase origin/main` | PASS | Fetched `be0b777d96eb0262d8ddc9ff673828ed56d79a5a`; rebase completed with no conflicts. |
| `kubectl kustomize kubernetes/apps/home-assistant > .codex/tmp/home-assistant.render.yaml` | PASS | Production Home Assistant kustomization rendered successfully after rebase. |
| `kubectl kustomize kubernetes/apps/home-assistant/branch > .codex/tmp/home-assistant-branch.render.yaml` | PASS | Branch Home Assistant kustomization rendered successfully after rebase. |
| `diff -u kubernetes/apps/home-assistant/config/packages/code_first.yaml kubernetes/apps/home-assistant/branch/config/packages/code_first.yaml` | PASS | No diff; production/base and branch overlay package behavior still match. |
| `docker run --rm -v "$PWD/.codex/tmp/ha-branch-check:/config" ghcr.io/home-assistant/home-assistant:2026.7.1 python -m homeassistant --script check_config --config /config` | PASS | Offline Home Assistant config check passed against a temporary copy of the branch config. |
| `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Runtime implementation marker remains valid after rebase. |
| `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Runtime implementation plan remains valid with `base: origin/main`. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | Owner attestation remains valid. |
| `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence --head "$(git rev-parse HEAD)"` | PASS | SDD artifacts and evidence remain valid. |
| `rg -n "desk_light_auto_balance\|desk_elgato_ambient_balance\|office_desk_illuminance\|elgato_key_light_air\|color_temp_kelvin\|brightness_pct\|transition: 3" .codex/tmp/home-assistant.render.yaml .codex/tmp/home-assistant-branch.render.yaml` | PASS | Rendered ConfigMaps still include the helper, automation, trigger sensor, target lights, documented color-temperature field, brightness percentages, and transition values. |
| `git diff --check` | PASS | No whitespace errors after rebase. |
| `git status --short --branch` | PASS | Branch was clean and `ahead 2` of `origin/main` before this evidence update. |

## Documentation Impact

- Updated: `docs/runbooks/home-assistant.md`
- Generated docs: Not required; Kubernetes and Terraform resource shape did not
  change. ConfigMap file content changed only through existing generators.
- No-docs rationale: N/A

## Final State

- Final branch: `codex/home-assistant-elgato-lighting`
- Final HEAD before cleanup amend:
  `1136f169dceac8affd4ec473c61890f04dc713d7`
- Commit: `feat(home-assistant): add desk elgato auto balance`
- Push: Not run by implementation owner during this evidence update.
- Verifier approval: Recorded externally for exact HEAD
  `da780f3b5a0c3a993cf8062377ef4c5c2a684eda` before this evidence-only amend.
