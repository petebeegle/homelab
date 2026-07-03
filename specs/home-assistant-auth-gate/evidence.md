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
| Targeted invalid package slug grep | PASS | No invalid hyphenated package slug or file reference in Home Assistant manifests, rendered output, SDD artifacts, or Home Assistant runbook. |
| Home Assistant HTTPRoute extraction with `awk` plus `grep` | PASS | Base and production aggregate renders both have `gateway/internal` and no `gateway/external` parentRef for `home-assistant/home-assistant`. |
| `git diff --check` | PASS | No whitespace errors. |
| `npm --prefix kubernetes/apps/synthetics/smoke test` before dependency install | FAIL | Playwright binary was not installed in the package directory. |
| `npm --prefix kubernetes/apps/synthetics/smoke ci` | PASS | Installed package dependencies from lockfile; no vulnerabilities reported. |
| `npm --prefix kubernetes/apps/synthetics/smoke test` | FAIL EXPECTED | Six routed services passed; Home Assistant failed because live production still serves onboarding, with the new explicit onboarding/AuthentiK message. |

## Development Validation

- Profile: manual branch verifier
- Branch slug: home-assistant-auth-gate
- HEAD: Pending committed HEAD for verifier push.
- Report path: None yet.
- Cleanup: Pending verifier run.
- Result or exception: Pending post-commit run of `python3 tools/development/verify_branch_deploy.py --app home-assistant --branch codex/home-assistant-auth-gate --slug home-assistant-auth-gate --push --include-cluster-base`.

## Documentation Impact

- Updated: `docs/runbooks/home-assistant.md`; `specs/home-assistant-auth-gate/`
- Generated docs: `docs/architecture.md`
- No-docs rationale: N/A.

## Exceptions And Follow-Ups

- Live production Home Assistant still serves first-run onboarding. Synthetic smoke correctly fails and must continue to fail until onboarding and Authentik OIDC are completed and verified.
- Development branch verifier must run against a committed branch HEAD because it pushes the branch before activation; result is recorded in `.codex/tmp/pr-summary.md` and final handoff.

## Final State

- Final branch: `codex/home-assistant-auth-gate`
- Final HEAD: Recorded after commit in `.codex/tmp/pr-summary.md` and final handoff.
- Commit: Pending
- Verifier approval: not created by implementation owner
