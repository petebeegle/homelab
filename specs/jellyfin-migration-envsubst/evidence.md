# Evidence: Jellyfin Migration Envsubst

**Branch**: `codex/jellyfin-migration-envsubst`
**Risk Tier**: medium
**Started**: 2026-08-08

## Human Gates

| Gate | Result | Notes |
| ---- | ------ | ----- |
| Intent brief | PASS | Verify merged migration, iterate on blockers, and clean up only after success. |
| Spec approval | PASS | User explicitly authorized verification and needed iteration. |
| Clarify | SKIP | Three independent read-only lanes reproduced the exact Flux failure. |
| Plan approval | PASS | Repair is constrained to the diagnosed substitution boundary. |
| Checklist | PASS | `checklists/requirements.md`: 15/15 complete. |
| Tasks/analyze approval | PASS | Six requirements have task coverage; no inconsistency or ambiguity remained. |
| Converge | PASS | No remaining buildable gap across six requirements, five success criteria, four acceptance scenarios, and the scoped plan decisions. |

## Workflow Validation

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts` | PASS | Branch and required SDD artifacts are coherent. |

## Baseline Production State

- PR #380 merged at `2026-08-08T23:11:49Z` as
  `999c28e46b73ae59be1359dacbf762abfa2d859d`.
- `GitRepository/flux-system` fetched that SHA at `2026-08-08T23:12:14Z`.
- `Kustomization/app-jellyfin` reported `Ready=False`, `BuildFailed` at
  `2026-08-08T23:14:51Z`; last applied remained
  `ee26fe2c927523dbec6a6f2ccf9d874389a19af5`.
- Error: `ConfigMap/jellyfin-config-migration: envsubst error: variable
  substitution failed: bad substitution`.
- Live Jellyfin remained on the old `RollingUpdate` deployment and
  `jellyfin-config-v2` NFS PVC; the local PVC and migration ConfigMap were not
  created, so the migration did not start.
- The old pod remained Ready and continued serving the web and SSO-start paths.

## Local Checks

| Command | Result | Notes |
| ------- | ------ | ----- |
| `python3 -m unittest tools.development.tests.test_jellyfin_config_migration` at merge baseline | FAIL (expected) | Strict Flux substitution rejected the first unprotected runtime shell variable, `target_root`; production non-strict substitution reached the nested expression and reported `bad substitution`. |
| `python3 -m unittest tools.development.tests.test_jellyfin_config_migration` after repair | PASS | Six tests passed against the strict local Flux build output; script bytes, normal substitutions, copy, retry, and fail-closed behavior passed. |
| `python3 tools/architecture/render.py --check` | PASS | Generated architecture remains current; the resource annotation does not change topology. |
| `git diff --check` | PASS | No whitespace errors. |
| `pre-commit run --all-files` | PASS | All repository hooks passed. |
| Download Flux `2.9.3`, validate release checksum, and inspect archive | PASS | The exact CI download URLs, checksum entry, and `flux` archive member are valid. |

## Automated Smoke And Live Verification

Pending repaired merge. Baseline anonymous probes returned Jellyfin web/public
info/branding successfully and produced the expected Authentik authorization
redirect. They prove pre-migration availability, not migration success or
authenticated role/session behavior.

## Development Validation

The exact local render/substitution integration replaces a routed development
smoke because the development environment lacks the workload's pinned GPU
resource. The user explicitly accepted that limitation and directed us not to
change the pinning or VM infrastructure now.

## Documentation Impact

No canonical docs or generated architecture change is expected because storage,
authentication, ingress, and migration semantics are unchanged.

## Exceptions And Follow-Ups

- Do not remove migration or rollback assets until the repaired production
  rollout passes every acceptance layer.
- Anonymous SSO smoke cannot prove user/admin authorization, role mapping,
  native login, or session continuity.
