# Evidence: home-assistant-auth-gate

**Branch**: `codex/home-assistant-auth-gate`
**Risk Tier**: high
**Started**: 2026-07-03
**Owner**: implementation-agent-home-assistant-auth-gate

## Spec Kit Initialization

- Command: Not run; repository already has Spec Kit templates and this implementation used the existing SDD artifact templates directly.
- Outcome: Existing templates used.
- Spec Kit version: Not queried because no Spec Kit scaffolding was changed.
- Integration: Existing repository integration.
- Fallback: None.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | No validator output. |
| `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | No validator output. |
| `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"` | PASS | No validator output. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `kubectl kustomize kubernetes/apps/home-assistant > .codex/tmp/home-assistant.render.yaml` | PASS | Rendered base Home Assistant manifests. |
| `kubectl kustomize kubernetes/apps/home-assistant/branch > .codex/tmp/home-assistant-branch.render.yaml` | PASS | Rendered branch overlay manifests. |
| `kubectl kustomize kubernetes/clusters/production/apps > .codex/tmp/production-apps.render.yaml` | PASS | Rendered production apps aggregate. |
| `python3 tools/architecture/render.py --write` | PASS | Refreshed generated architecture. |
| `python3 tools/architecture/render.py --check` | PASS | Generated architecture is current. |
| `python3 -m json.tool .../config/storage/onboarding` plus focused JSON assertions | PASS | Production and branch seeds use storage version `4`, key `onboarding`, and done list `user`, `core_config`, `analytics`, `integration`. |
| Targeted invalid package slug grep | PASS | No invalid hyphenated package slug or file reference in Home Assistant manifests, rendered output, SDD artifacts, or Home Assistant runbook. |
| Home Assistant Deployment extraction with `awk` plus `grep` | PASS | Production and branch renders contain `/config/.storage/onboarding` mounted with subPath `onboarding` from their storage ConfigMaps. |
| Home Assistant HTTPRoute extraction with `awk` plus `grep` | PASS | Base render contains both `gateway/internal` and `gateway/external` parentRefs for `home-assistant/home-assistant`. |
| `git diff --check` | PASS | No whitespace errors. |
| `npm --prefix kubernetes/apps/synthetics/smoke test` before dependency install | FAIL | Playwright binary was not installed in the package directory. |
| `npm --prefix kubernetes/apps/synthetics/smoke ci` | PASS | Installed package dependencies from lockfile; no vulnerabilities reported. |
| `npm --prefix kubernetes/apps/synthetics/smoke test` | FAIL EXPECTED | Six routed services passed; Home Assistant failed because live production still serves onboarding, with the new explicit message to confirm the GitOps onboarding seed is mounted and Authentik OIDC is verified. |

## Development Validation

- Profile: manual branch verifier
- Branch slug: home-assistant-auth-gate
- HEAD: Final local HEAD reported in handoff.
- Report path: None.
- Cleanup: N/A.
- Result or exception: Development branch verifier was previously attempted for commit `1c5683126c9f6aae6f7732c1f8469c6947c1dc02` and failed before cluster activation because required Terraform development variables were unavailable. It was not rerun for the follow-up local commit because exact-HEAD verification would require pushing the new commit, and current workflow requires separate verifier approval before push.

## Documentation Impact

- Updated: `docs/runbooks/home-assistant.md`; `specs/home-assistant-auth-gate/`
- Generated docs: `docs/architecture.md`
- No-docs rationale: N/A.

## Exceptions And Follow-Ups

- Live production Home Assistant still serves first-run onboarding until this branch is reconciled. Synthetic smoke correctly fails and must continue to fail if onboarding appears after the GitOps onboarding seed is mounted.
- Development branch validation remains blocked by unavailable Terraform development variables and by the no-push-before-verifier constraint for the new local HEAD.

## Final State

- Final branch: `codex/home-assistant-auth-gate`
- Final HEAD: Recorded after commit in `.codex/tmp/pr-summary.md` and final handoff.
- Commit: Final local commit reported in handoff
- Verifier approval: not created by implementation owner
