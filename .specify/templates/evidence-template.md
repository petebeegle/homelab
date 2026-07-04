# Evidence: [IMPLEMENTATION]

**Branch**: `codex/[IMPLEMENTATION]`
**Risk Tier**: [tiny|low|medium|high]
**Started**: [DATE]

## Spec Kit Initialization

- Command:
- Outcome:
- Spec Kit version:
- Integration:
- Fallback:

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent brief | [PASS/FAIL/SKIP] | [human-provided outcome, constraints, acceptance] |
| Spec approval | [PASS/FAIL/PENDING] | [approver/context] |
| Clarify | [PASS/SKIP] | [summary or skipped-gate rationale] |
| Plan approval | [PASS/FAIL/PENDING] | [approver/context] |
| Checklist | [PASS/SKIP] | [checklist path/summary or skipped-gate rationale] |
| Tasks/analyze approval | [PASS/FAIL/PENDING] | [analyze result or skipped-analyze rationale] |
| Converge | [PASS/SKIP] | [converge result or skipped-converge rationale] |

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | [PASS/FAIL/SKIP] | [notes] |

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `[command]` | [PASS/FAIL/SKIP] | [notes] |

## Automated Smoke And Live Verification

| Target | Method | Result | Notes |
| ------ | ------ | ------ | ----- |
| [exact URL, smoke profile, or Job] | [development profile, synthetic Job, Gateway curl, Playwright, etc.] | [PASS/FAIL/SKIP] | [SHA, status, or exception] |

## Deployment State

- Source fetched SHA:
- Target applied SHA:
- Live resource spec checked:
- Gateway/listener/DNS/certificate checked:
- Exact user-facing URL result:

## Development Validation

- Profile: [whoami|manual|none]
- Branch slug:
- HEAD:
- Report path:
- Cleanup:
- Result or exception:

## Documentation Impact

- Updated:
- Generated docs:
- No-docs rationale:

## SDD Conformance

- Local sources checked:
- Upstream Spec Kit sources checked:
- Human-gated Spec Kit alignment:
- Artifact updates after implementation:

## Exceptions And Follow-Ups

- [Exception or `None`]

## Final State

- Final branch:
- Final HEAD:
- Commit:
