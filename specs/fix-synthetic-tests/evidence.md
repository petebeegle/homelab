# Evidence: fix-synthetic-tests

**Branch**: `codex/fix-synthetic-tests`
**Risk Tier**: low
**Started**: 2026-07-17

## Spec Kit Initialization

- Command: manual lightweight artifact bootstrap from repo templates
- Outcome: PASS
- Spec Kit version: not checked; no Spec Kit scaffolding changes
- Integration: existing repository templates
- Fallback: preferred `/workspaces/homelab-worktrees/fix-synthetic-tests` worktree path was unavailable due to permission denied, so `/tmp/homelab-worktrees/fix-synthetic-tests` is used

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent brief | PASS | User requested: "fix the synthetic tests"; follow-up clarified the root route is intentionally absent. |
| Spec approval | PASS | User request authorizes focused test fix. |
| Clarify | PASS | Follow-up correction resolved route intent. |
| Plan approval | PASS | User asked to fix the test instead. |
| Checklist | SKIP | Focused low-risk repair; no separate checklist needed. |
| Tasks/analyze approval | SKIP | Analyze skipped for lightweight work with direct tests. |
| Converge | SKIP | Artifacts updated after user correction; no remaining drift. |

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts --require-evidence --head "$(git rev-parse HEAD)"` | PASS | Required spec, plan, tasks, and evidence artifacts present; no stale recorded HEAD. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `npm test -- --reporter=list` from `tests/smoke/` | FAIL | Baseline after `npm ci`: root Homepage test failed with DNS `ERR_NAME_NOT_RESOLVED`; all eight subdomain route tests passed. |
| `curl -kfsSIL --max-time 10 https://homepage.lab.petebeegle.com/` | PASS | Confirmed Homepage is healthy on the intended subdomain route. |
| `python3 tools/architecture/render.py --write && python3 tools/architecture/render.py --check` | PASS | Generated architecture returned to subdomain-only Homepage route state. |
| `kubectl kustomize kubernetes/apps/homepage` | PASS | Rendered Homepage route remains `homepage.${cluster_domain}` only. |
| `kubectl kustomize kubernetes/apps/homepage/development` | PASS | Development render remains `homepage.${cluster_domain}` only. |
| `python3 tools/policy/check_synthetic_smoke_mirroring.py` | PASS | Mirrored route specs and lockfiles synchronized. |
| `python3 -m unittest tools.policy.tests.test_check_synthetic_smoke_mirroring` | PASS | 5 tests passed. |
| `node --test kubernetes/apps/synthetics/smoke/*.test.js` | PASS | 5 Node helper/reporter tests passed. |
| `npm test -- --reporter=list` from `tests/smoke/` | PASS | 9 Playwright route tests passed after retargeting Homepage to `homepage.${cluster_domain}`. |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| Local smoke suite | Playwright | PASS | 9 passed against live routes from this environment. |
| Homepage subdomain | curl | PASS | `https://homepage.lab.petebeegle.com/` returns 200. |

## Deployment State

- Source fetched SHA: N/A; final change is test/docs only
- Target applied SHA: N/A
- Live resource spec checked: rendered Homepage route remains subdomain-only
- Gateway/listener/DNS/certificate checked: no desired-state Gateway change
- Exact user-facing URL result: `https://homepage.lab.petebeegle.com/` returns 200

## Development Validation

- Profile: none
- Branch slug: N/A
- HEAD: branch commit created after validation
- Report path: N/A
- Cleanup: N/A
- Result or exception: no development validation required for final test/docs-only scope; local Playwright smoke validates the intended live route.

## Documentation Impact

- Updated: `docs/runbooks/synthetic-smoke-tests.md`, `kubernetes/apps/homepage/README.md`
- Generated docs: `docs/architecture.md` checked; no net generated architecture route change remains after correction
- No-docs rationale: N/A

## SDD Conformance

- Local sources checked: `AGENTS.md`, `docs/runbooks/spec-driven-development.md`, `docs/runbooks/implementation-workflow.md`
- Upstream Spec Kit sources checked: N/A; no workflow/template changes
- Human-gated Spec Kit alignment: lightweight gate compression recorded; follow-up clarification captured
- Artifact updates after implementation: spec, plan, tasks, and evidence updated after user clarified root route is intentionally absent

## Exceptions And Follow-Ups

- `/workspaces/homelab-worktrees` was not writable; fallback worktree under `/tmp/homelab-worktrees` used.
- Standalone `kustomize` is not installed; `kubectl kustomize` was used as the renderer.

## Final State

- Final branch: codex/fix-synthetic-tests
- Final HEAD: branch commit created after validation
- Commit: pending amended commit
