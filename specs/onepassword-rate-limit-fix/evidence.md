# Evidence: 1Password Rate-Limit Fix

**Branch**: `codex/onepassword-rate-limit-fix`
**Risk Tier**: high
**Started**: 2026-08-11

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent brief | PASS | User requested the active 1Password alerts be fixed. |
| Spec approval | PASS | Expedited incident correction under the direct request. |
| Clarify | SKIP | Live status and quota metadata made the cause unambiguous. |
| Plan approval | PASS | Narrow quota-safe correction reported during execution. |
| Checklist | PASS | `checklists/requirements.md`. |
| Tasks/analyze approval | PASS | Manual cross-artifact review found no conflicts. |
| Converge | PASS | The development manual-refresh refinement is reflected consistently across artifacts, implementation, tests, and runbook. |

## Incident Evidence

- Both operator Deployments were available at one replica.
- All 17 production `OnePasswordItem` resources transitioned to `Ready=False` near `2026-08-11T03:08Z` with retrieval failures.
- The production bootstrap Secret retained its original creation timestamp; only metadata and decoded byte length were inspected.
- A token-authenticated metadata-only query reported token reads `0/1000` used but account reads/writes `1000/1000` used, with about 18.6 hours until reset. No token or item value was displayed.
- At 300 seconds, 17 items require about 4,896 baseline reads/day. Production at 3600 seconds requires about 408 reads/day; development at 31536000 seconds is effectively manual-only.
- Upstream operator 1.12.0 constructs `time.NewTicker` directly from `POLLING_INTERVAL`; zero is not a valid disable value. Updating a `OnePasswordItem` is watched by its controller and provides an explicit refresh trigger.
- On 2026-08-14, before this branch had a PR or merge, both live Deployments still rendered the main-branch value `300`. Production again reached the account-wide `1000/1000` limit, with all 17 items `Ready=False` and a latest transition near `05:32Z`. Development had zero items. This recurrence confirms the five-minute main-branch interval as the active cause; it is not a failure of the undeployed cluster-specific intervals.

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `validate_sdd_context.py --require-plan-artifacts` | PASS | Matching high-risk branch artifacts found. |
| `python3 -m unittest discover -s tools/codex-harness/tests` | PASS | 81 tests. |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| Focused policy and verifier tests | PASS | 12 tests; initial missing-checker test failed before implementation as expected. |
| Full policy tests | PASS | 11 tests. |
| Direct-auth chart render | PASS | Operator 1.12.0, production interval 3600, no Connect workload or token Secret. |
| Production foundation policy | PASS | Cluster-specific interval contract accepted. |
| Flux operator builds | PASS | Development rendered `31536000`; production rendered `3600`. Quoting prevents Helm scientific notation and operator integer-parse fallback. |
| Strict cluster entrypoint renders | PASS | Production 7350 lines and development 6790 lines; literal CRD example variable supplied as `var=placeholder`. |
| Kubeconform 0.7.0 | PASS | 122 resources; 44 valid, 0 invalid/errors, 78 missing-schema skips. |
| Python compile and Bash syntax | PASS | Changed verifier, policy checker, and chart script. |
| Architecture check | PASS | Generated architecture remains current. |

## Development Validation

- Profile: shared development base/operator
- Branch slug: onepassword-rate-limit-fix
- HEAD: `87d8cc6916bc9e443c7edb0080becb60b83c758e`
- Cleanup: Branch whoami resources were removed; the base source returned to `main@sha1:0986a461d21e02d4adc973729648bae98c1d56eb` and Ready.
- Result: PASS. Development fetched and applied the exact branch revision for CRDs, the operator, and dependent base resources. ReplicaSet `onepassword-connect-operator-86545f4ff8` rendered `POLLING_INTERVAL=31536000`, and its pod reached Ready. The exact-branch whoami workload, Service, and HTTPRoute reconciled and its pod reached Ready.
- Explicit refresh: Unit coverage proves the verifier issues a unique annotation update after item rotation. Live item refresh was skipped because the provider account quota is exhausted; it cannot succeed before reset and would add avoidable requests.

## Documentation Impact

- Updated: `docs/runbooks/onepassword-operator.md`
- Generated docs: architecture check passed; no topology change.

## Exceptions And Follow-Ups

- Preferred worktree location was not writable; the established `/home/vscode/homelab-worktrees/` fallback is used.
- Provider quota must reset before production items return Ready; no repository change can clear that external lockout early.
- The 2026-08-14 recurrence query reported about 1.6 hours until the next provider reset. Post-merge verification must wait for available quota and confirm all 17 items recover.
- The first development smoke attempt stopped before Flux mutation because the isolated worktree lacked ignored `terraform.tfvars`. The repository no-output staging helper installed the existing ignored file; the rerun passed. The file remains ignored and uncommitted.

## Final State

- Final branch: `codex/onepassword-rate-limit-fix`
- Final HEAD: pending evidence commit
- Commit: `87d8cc6916bc9e443c7edb0080becb60b83c758e` plus final evidence follow-up
