# Quickstart: Validate The Access Broker Roadmap

## Prerequisites

- Worktree branch is `codex/access-broker-roadmap`.
- `.specify/feature.json` points to `specs/access-broker-roadmap`.
- `spec.md`, `plan.md`, `tasks.md`, and `evidence.md` exist.

## 1. Validate Spec Kit Context

```bash
.specify/scripts/bash/check-prerequisites.sh \
  --json --require-tasks --include-tasks

python3 tools/codex-harness/validate_sdd_context.py \
  --root "$(pwd)" \
  --branch "$(git branch --show-current)" \
  --require-plan-artifacts
```

Expected: both commands pass and resolve
`specs/access-broker-roadmap`.

## 2. Validate Requirement Coverage

Check that each `FR-###` and buildable `SC-###` in `spec.md` maps to at least one
task and every task maps back to a requirement or story.

Expected: 100 percent functional requirement coverage and no unmapped
implementation task.

## 3. Validate Dependencies

Review the dependency graph in `plan.md`:

- S01 and S02A/S02B are the only foundation gates.
- Every Wave 2 slice depends on S01 or an explicit decision gate.
- S10 depends on provider, persistence, and audit contracts.
- M1 depends on S16.
- M2 depends on S17 through S19.
- M3 depends on S20 through S22B.

Expected: no dependency cycle and no slice scheduled before its contract,
credential, storage, or rollout prerequisite.

## 4. Audit Parallel Write Scopes

For every wave, compare the repository and write-scope columns.

Expected:

- one owner for central application dispatch and startup;
- one owner for request schema migration;
- one owner for each Authentik blueprint registration merge;
- one homelab integration queue owner for access-broker Deployment, ConfigMap,
  and Secret;
- all other `[P]` slices own disjoint packages or new files.

## 5. Validate Milestones

Review each milestone against the user path:

- M0 prevents duplicate and ambiguous prototype behavior.
- M1 proves a non-admin requester completes request, private retrieval, VPN, and
  Authentik login.
- M2 proves expiration, revocation, repeat policy, and secret cleanup.
- M3 proves operations, restore, alerts, registration, and full smoke.

Expected: no milestone relies on readiness or rendering alone.

## 6. Review Deferred Decisions

Ensure DG-001, DG-002, and DG-003 each list:

- owning implementation;
- blocked slices;
- recommended default;
- human approval requirement.

Expected: none blocks S01 or S02A/S02B, and none is silently resolved.

## 7. Final Diff Review

```bash
git diff --check
git status --short
```

Expected: only `.specify/feature.json` and
`specs/access-broker-roadmap/` are changed.
