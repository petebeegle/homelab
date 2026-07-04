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
- Spec -> Plan -> Tasks -> Implement alignment:
- Artifact updates after implementation:

## Exceptions And Follow-Ups

- [Exception or `None`]

## Final State

- Final branch:
- Final HEAD:
- Commit:
