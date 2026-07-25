# Contract: Roadmap Slice

Every future slice must declare the following fields before its spec gate:

| Field | Required content |
| ----- | ---------------- |
| ID | Stable roadmap ID such as `S01` |
| Implementation | Unique slug used by branch and Spec Kit directory |
| Outcome | One independently valuable behavior or operational capability |
| Repository | `homelab-access` or `homelab`; cross-repo work is split into dependent slices |
| Risk tier | Local workflow tier with rationale |
| Prerequisites | Slice and decision gates that must be complete |
| Dependents | Downstream slices or milestone |
| Write scope | Exact packages, manifests, docs, or new files owned |
| Conflict exclusions | Shared files the slice must not edit concurrently |
| Local tests | Exact focused and broad commands |
| Development validation | Profile, synthetic job, manual exact path, or documented exception |
| Production smoke | Exact Discord, Authentik, VPN, download, metrics, or rollout path |
| Rollback/recovery | Safe reversal or reconciliation behavior |
| Evidence | Required SHAs, image digest, Flux state, external state, and cleanup |
| PR boundary | Exactly one repository PR; dependent repository changes get another slice; homelab slices include matching Spec Kit artifacts |

## Parallel Eligibility

A slice may carry `[P]` only when:

1. all prerequisites are merged;
2. its write scope does not overlap another active slice's owned scope;
3. shared contracts are already merged;
4. it does not deploy a mutable image shared with another active release;
5. its tests and evidence can be collected independently.

Read-only analysis, test design, smoke execution, and evidence audits may fan
out even when tracked integration is serialized.

## Completion Contract

A slice is complete only when:

1. homelab slices record spec, plan, checklist, tasks, analyze, and
   implementation gates; app-only slices record equivalent scope, decisions,
   tests, and smoke evidence in their PR;
2. local checks pass;
3. required development validation passes or has an approved unavailable-
   infrastructure exception;
4. PR checks pass and merge SHA is recorded;
5. deployed slices record Flux fetched/applied revision and live image identity;
6. the exact user or operator path passes;
7. temporary validation resources are cleaned up;
8. no credentials or private configurations appear in Git, logs, evidence, or
   PR text.
