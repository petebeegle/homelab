# Implementation Plan: Access Broker Delivery Roadmap

**Branch**: `codex/access-broker-roadmap` | **Date**: 2026-07-25 | **Spec**:
`specs/access-broker-roadmap/spec.md`

**Input**: Feature specification from
`specs/access-broker-roadmap/spec.md`

## Summary

Create a portfolio plan for finishing the access broker through small,
dependency-ordered implementations. First establish transactional lifecycle
contracts, stable principal ownership, and narrower integration seams. Then fan
out provider, persistence, intake, requester delivery, identity, and
observability module work. Serialize shared server wiring, database cutover,
Kubernetes configuration, and production rollout. Every future slice gets its
own branch, repository PR, and risk-appropriate smoke evidence. Homelab
desired-state slices additionally use matching Spec Kit artifacts.

## Technical Context

**Risk Tier**: low for this docs-only roadmap; future slices are medium or high
**Workflow Tier**: docs-only
**Primary Areas**: cross-repository roadmap, Discord interactions, Authentik,
wg-easy, persistence, jobs, Kubernetes, Flux, SOPS, Grafana, CI
**Dependencies**: Spec Kit, `petebeegle/homelab-access`,
`petebeegle/homelab`, Discord API, Authentik API and blueprints, wg-easy API,
CloudNativePG, Flux, Gateway API, SOPS, Grafana
**Storage**: current JSON data is on `nfs-csi-storage`; planned transactional
state uses a dedicated PostgreSQL service rather than SQLite on NFS
**Ingress**: preserve existing Cloudflare Tunnel to `gateway/public` contract;
new public Authentik exposure requires a separate approved slice
**Secrets**: rotate exposed Discord credentials and commit replacements only in
SOPS-encrypted manifests
**Smoke Strategy**: none for this docs-only roadmap; every user-facing future
slice declares development or synthetic smoke against the exact path
**Fanout Targets**: provider adapters, persistence, intake validation,
Authentik desired state, observability design, test design, and read-only audits
after the domain foundation contracts land
**Development Validation**: none; no deployable state changes in this planning
slice
**Post-Implementation SDD Conformance**: local workflow and Spec Kit artifact
analysis required

## Human Gates

**Spec Gate**: Approved by the user on 2026-07-25.

**Checklist Status**: Requirements checklist complete; roadmap quality
checklist generated at
`specs/access-broker-roadmap/checklists/roadmap.md`.

**Plan Gate**: Approved by the user on 2026-07-25.

**Task/Analyze Gate**: Approved by the user on 2026-07-25 after the roadmap
analysis completed with no critical consistency findings. Each future slice
repeats its own gates.

## Constitution Check

*GATE: Passed for planning; re-check in every future implementation.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; this roadmap changes no cluster state and
      future slices declare development validation.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered; SQLite on NFS is rejected for concurrent durable
      jobs and a dedicated PostgreSQL path is planned.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Branch is `codex/access-broker-roadmap`; the approved sibling worktree
      fallback is recorded because `/workspaces/homelab-worktrees` is not
      writable.
- [x] Documentation impact identified; the roadmap artifacts are the durable
      documentation.
- [x] PR review/status checks remain the review gate.

## Current Baseline

The deployed prototype can accept `/access request`, authorize an admin
approval, create or reuse an Authentik user, create or reuse a readable wg-easy
peer, defer long Discord approvals, and provide a preview-safe single-use VPN
download. The important remaining baseline defects are:

- the approval link is shown to the approving admin rather than reliably to the
  requester;
- the Authentik user has no usable activation or linked login method;
- request guild and channel values are recorded but not enforced;
- approval jobs are process-local goroutines and are lost on restart;
- the JSON store has process-local locking and retains raw tokens and private
  VPN configuration after use;
- concurrent approvers can trigger duplicate external side effects;
- peer ownership depends partly on mutable display names;
- no provider revocation, access expiration, retry, reissue, audit event,
  delivery state, or cleanup lifecycle exists;
- the deployment uses mutable `:main`, and Secret changes do not guarantee a
  rollout;
- metrics do not expose business or failure outcomes.

## Architecture Strategy

### Foundation Before Fanout

The first application slice establishes:

- stable Discord user ID as the principal key;
- one active grant per principal;
- explicit request, job, grant, artifact, delivery, and audit states;
- atomic approval claim semantics;
- provider, repository, delivery, and job interfaces;
- command handlers split away from the central HTTP server.

This foundation is intentionally small. It need not migrate persistence or add
new user behavior, but it prevents every later lane from independently changing
the same JSON record and `server.go`.

### Parallel Work Rules

- Parallel lanes must own disjoint packages or repositories.
- `internal/server/server.go`, request schema migration, application startup,
  Kubernetes `deployment.yaml`, `configmap.yaml`, and encrypted
  `secret.yaml` each have one integration owner per wave.
- Provider lanes may build against foundation interfaces before persistence and
  command integration finish.
- Homelab desired-state PRs may be prepared concurrently when their files are
  disjoint, but merge and Flux rollout are serialized.
- App releases are not deployed concurrently until immutable image references
  and deterministic rollout triggers are in place.
- All helper or agent results consolidate into the owning slice's
  `evidence.md`.

## Decision Gates

| Gate | Decision | Blocks | Recommended default |
| ---- | -------- | ------ | ------------------- |
| DG-001 | Authentik activation model: Discord-linked identity or temporary password setup | S11, S12, M1 | Spike Discord linking first; use password setup if duplicate-free linking cannot be proved |
| DG-002 | Default access lifetime | S17, S19, M2 | Seven days with explicit renewal |
| DG-003 | Initial Authentik access bundle | S05, S12, M1 | Dedicated `Homelab Access` group with application bindings added explicitly |
| DG-004 | Blocked-DM behavior | S13 | Requester `/access status` remains authoritative; DM is best-effort |

DG-001 through DG-003 require human approval in their owning implementation.
DG-004 is a roadmap assumption and can be overridden at that slice's spec gate.

## Delivery Waves

### Wave 0 - Planning And Decisions

No implementation work begins until this roadmap's spec, plan, and task/analysis
gates are approved. DG-001 through DG-003 may be researched in parallel, but
their selections are recorded only by the affected implementation.

### Wave 1 - Foundations

| ID | Implementation | Repository | Scope | Depends on | Parallel boundary | Risk | Completion signal |
| -- | -------------- | ---------- | ----- | ---------- | ----------------- | ---- | ----------------- |
| S01 | `access-broker-domain-foundation` | `homelab-access` | Lifecycle entities, atomic approval claim, one-active-grant rule, stable principal key, interfaces, command package seams | Roadmap approval | Critical path; sole owner of request schema and `server.go` decomposition | medium | Race tests prove one approval claim and one active grant |
| S02A | `access-broker-immutable-images` | `homelab-access` | Publish commit-addressed images with OCI source/revision metadata and retain `main` only as a discovery alias | Roadmap approval | May run beside S01; owns CI image publishing only | medium | Merged commit has immutable tag and digest with matching revision metadata |
| S02B | `access-broker-release-hygiene` | `homelab` | Pin reviewed image digest, automate digest update PRs, add deterministic config/Secret rollout, and rotate exposed credentials | S02A | May prepare beside S01; sole owner of deployment, update policy, and encrypted Secret | high | Old credentials rejected, desired digest applied, Secret/config change rolls pod |

S01 is the application fanout gate. S02A/S02B are the safe-deployment gate and
must pass before multiple app slices are rolled out.

### Wave 2 - Module Fanout

All lanes branch from merged S01 contracts. Module tests land before shared
command or worker integration.

| ID | Implementation | Repository | Scope | Depends on | Parallel boundary | Risk | Completion signal |
| -- | -------------- | ---------- | ----- | ---------- | ----------------- | ---- | ----------------- |
| S03 | `access-broker-intake-guard` | `homelab-access` | Allowed guild/request/review channel validation before store mutation | S01 | Owns config parsing, intake policy package, focused handler files | medium | Commands outside allowed contexts create no request |
| S04 | `access-broker-provider-lifecycle` | `homelab-access` | Idempotent Authentik entitlement/deactivation and wg-easy lookup/revoke/rotate by recorded stable ID | S01 | Owns `internal/authentik/` and `internal/wgeasy/` | high | Retry and concurrent tests produce one external resource; revoke is reconcilable |
| S05 | `access-broker-authentik-entitlement` | `homelab` | Git-owned `Homelab Access` group and initial policy scaffolding | DG-003 | Owns a new blueprint and blueprint registration | high | Blueprint reconciles and test user gains only declared entitlement |
| S06 | `access-broker-postgres-repository` | `homelab-access` | Transactional repository, schema, JSON importer, uniqueness constraints | S01 | Owns new persistence package and migration fixtures | high | Repeated import is idempotent; concurrent claims preserve invariants |
| S07 | `access-broker-requester-delivery` | `homelab-access` | Requester-owned `/access status`, on-demand artifact issuance, delivery state, safe reissue semantics | S01 | Owns delivery package and new command handlers; no provider changes | medium | Requester retrieves privately without admin forwarding; other users cannot |
| S08 | `access-broker-audit-metrics` | `homelab-access` | Append-only audit contract and request/job/grant/delivery metrics | S01 | Owns new audit/metrics packages; server wiring deferred | medium | Tests prove identifiers are logged while secrets and configs are absent |

S03 through S08 are safe parallel lanes after a write-scope review. S03, S07,
and S08 may add new handler files but do not independently rewrite central
dispatch.

### Wave 3 - Durable Runtime And Desired State

Application integration and homelab integration each serialize through one
owner.

| ID | Implementation | Repository | Scope | Depends on | Parallel boundary | Risk | Completion signal |
| -- | -------------- | ---------- | ----- | ---------- | ----------------- | ---- | ----------------- |
| S09 | `access-broker-postgres-deployment` | `homelab` | Dedicated PostgreSQL desired state, encrypted credentials, backup and migration job contract | S06, S02B | Homelab integration queue owner | high | Development migration, backup, repeated import, and rollback rehearsal pass |
| S10 | `access-broker-durable-jobs` | `homelab-access` | Leased jobs, retry/backoff, startup recovery, graceful shutdown, provider reconciliation | S04, S06, S08 | App integration owner for startup and central wiring | high | Crash after each external side effect resumes without duplication |
| S11 | `access-broker-authentik-activation-app` | `homelab-access` | Activation adapter and private requester delivery contract for selected DG-001 model | S06, S07, S10, DG-001 | Owns activation package | high | Requester activates exactly the pre-approved identity |
| S12 | `access-broker-authentik-activation-gitops` | `homelab` | Recovery flow or Discord source, group bindings, routes and secrets required by DG-001/DG-003 | S05, S11, DG-001, DG-003 | Follows S09 in homelab integration queue | high | Development user completes activation and reaches only authorized apps |

### Wave 4 - Minimum Viable Multi-User Service

| ID | Implementation | Repository | Scope | Depends on | Parallel boundary | Risk | Completion signal |
| -- | -------------- | ---------- | ----- | ---------- | ----------------- | ---- | ----------------- |
| S13 | `access-broker-discord-delivery` | `homelab-access` | Optional requester DM notification, blocked-DM classification, idempotent retry; `/access status` remains fallback | S07, S10, S02B, DG-004 | Owns Discord outbound client and DM handler | medium | Blocked DM does not reprovision or lose access; retry succeeds |
| S14 | `access-broker-command-lifecycle` | `homelab-access` | `/access list`, `status`, `retry`, `reissue`, and `revoke` with requester/admin authorization | S04, S07, S10 | Sole command integration owner | high | Commands are idempotent and enforce actor boundaries |
| S15 | `access-broker-intake-deployment` | `homelab` | SOPS/config rollout for allowed contexts and final command contract | S03, S14, S02B | Homelab integration queue owner | high | `#test` succeeds; other guilds/channels/DMs are rejected |
| S16 | `access-broker-mvp-smoke` | `homelab` | Automated or tightly scripted requester E2E and recovery runbook | S09-S15 | Read-only smoke fanout after deployment | high | Request to private retrieval to VPN to Authentik login passes for non-admin requester |

M1 is reached when S16 passes. The service may then be offered to a small
allowlisted user set.

### Wave 5 - Managed Lifecycle

| ID | Implementation | Repository | Scope | Depends on | Parallel boundary | Risk | Completion signal |
| -- | -------------- | ---------- | ----- | ---------- | ----------------- | ---- | ----------------- |
| S17 | `access-broker-grant-expiration` | `homelab-access` | Access lifetime, renewal, expiration scheduler, revocation reconciliation | S10, S14, DG-002 | Owns lifecycle policy and scheduled jobs | high | Expired grant removes VPN and entitlement without deleting unrelated identity |
| S18 | `access-broker-artifact-cleanup` | `homelab-access` | Hashed bearer tokens, private-config purge, retention and cleanup jobs | S06, S10 | Owns artifact persistence and cleanup jobs | high | Consumed/expired secrets are physically absent; audit metadata remains |
| S19 | `access-broker-repeat-request-policy` | `homelab-access` | Explicit reuse, renewal, rotation, revoked-user, and renamed-user behavior | S14, S17 | Owns request policy handlers | medium | One active grant and stable Discord ownership hold through all repeat flows |

S17 and S18 can run concurrently after job contracts stabilize. S19 integrates
their policies.

### Wave 6 - Production Operations

| ID | Implementation | Repository | Scope | Depends on | Parallel boundary | Risk | Completion signal |
| -- | -------------- | ---------- | ----- | ---------- | ----------------- | ---- | ----------------- |
| S20 | `access-broker-observability` | `homelab` | Grafana dashboard, alerts, audit queries, runbooks | S08, S17, S18 | Owns monitoring files | medium | Synthetic failures trigger actionable alerts without secret leakage |
| S21 | `access-broker-command-registration` | `homelab-access` | Versioned command manifest and idempotent guild/global registration tooling | S14 | Owns registration tooling and contract fixtures | medium | Fresh test guild reaches expected command schema automatically |
| S22A | `access-broker-readiness-app` | `homelab-access` | Load/concurrency tests, crash-recovery tests, and immutable release evidence | S16-S19, S21 | Owns application readiness tests and release evidence | high | Application readiness suite passes against an immutable release |
| S22B | `access-broker-production-readiness` | `homelab` | Restore and revocation drills, readiness release deployment, full E2E, final operator docs | S20, S22A | Owns GitOps deployment and final evidence packet | high | All M2/M3 criteria pass and every unverified layer is explicit |

## Milestones

### M0 - Stabilized Prototype

Requires S01-S04 and S02A/S02B deployment hygiene. Concurrent approval cannot create
duplicate resources, intake boundaries are testable, providers have stable
ownership, and releases are deterministic.

### M1 - Minimum Viable Multi-User Service

Requires S05-S16. A non-admin requester can request only in an allowed context,
receive access privately, activate the approved Authentik identity, connect the
VPN, reach only authorized applications, retry delivery safely, and survive a
broker restart.

### M2 - Managed Access Service

Requires S17-S19. Access expires and revokes predictably, repeat requests have
an explicit policy, and sensitive artifacts are removed on use or expiry.

### M3 - Production Ready

Requires S20-S22B. Operators have dashboards, alerts, audit queries, automated
command registration, backup/restore evidence, security drills, and exact-path
end-to-end validation.

## Dependency Graph

```text
Roadmap approval
├── S01 domain foundation ──────────────────────────────────────────────┐
│   ├── S03 intake guard ──────────────────────────────── S15 deploy ──┤
│   ├── S04 provider lifecycle ──┐                                    │
│   ├── S06 PostgreSQL repo ─────┼─ S10 durable jobs ── S14 commands ─┤
│   ├── S07 requester delivery ──┤       │              │             │
│   └── S08 audit/metrics ───────┘       ├─ S11 activation app        │
│                                        └─ S13 Discord delivery       │
├── S02A immutable images ── S02B release hygiene ──────┬──────────────┤
├── DG-003 ── S05 entitlement blueprint                │              │
└── DG-001 ────────────────── S12 activation GitOps ◄───┘              │
                                                                       │
S09 PostgreSQL deployment ◄── S02B + S06 ──────────────────────────────┤
S09-S15 ── S16 MVP smoke ──┬─ DG-002 + S17 expiration ──┐             │
                           ├─ S18 artifact cleanup ───────┼─ S19 policy│
                           └──────────────────────────────┘             │
S08 + S17 + S18 ── S20 observability                                  │
S14 ── S21 registration                                                │
S16-S19 + S21 ─────────────────────────────── S22A app readiness
S20 + S22A ───────────────────────────────── S22B production readiness ─┘
```

## Project Structure

### SDD Artifacts

```text
specs/access-broker-roadmap/
├── checklists/
│   ├── requirements.md
│   └── roadmap.md
├── contracts/
│   └── roadmap-slice.md
├── data-model.md
├── evidence.md
├── plan.md
├── quickstart.md
├── research.md
├── spec.md
└── tasks.md
```

### Expected Future Source Areas

```text
/home/vscode/homelab-access/
├── cmd/homelab-access/
├── internal/access/
├── internal/artifacts/
├── internal/audit/
├── internal/authentik/
├── internal/discord/
├── internal/jobs/
├── internal/metrics/
├── internal/persistence/
├── internal/server/
└── internal/wgeasy/

kubernetes/apps/access-broker/
kubernetes/infra/authentik/blueprints/
kubernetes/infra/monitoring/grafana/
docs/runbooks/
specs/<future-implementation>/
```

## Tiered TDD And Validation Plan

**TDD expectation**: This roadmap changes documentation only. Future app slices
use contract-first tests and `go test -race ./...`; persistence and lifecycle
slices include concurrency, crash-recovery, migration, and partial-failure
fixtures before integration.

**Local checks**:

- `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`
- `python3 tools/codex-harness/validate_sdd_context.py --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`
- `git diff --check`
- Task format, requirement traceability, dependency-cycle, and parallel
  write-scope audits described in `quickstart.md`

**Development smoke**: None for this roadmap. Every medium/high future slice
must use the access-broker development path, a one-off synthetic job, or record
an unavailable-infrastructure exception with substitute checks.

**Completion evidence**: Future deployments record app image digest, homelab
merge SHA, Flux fetched and applied SHA, live image ID, exact Discord command
result, exact download/activation path, provider state, and cleanup.

**Fanout plan**: Read-only research was divided across delivery/identity,
lifecycle/persistence, and operations/deployment lanes. Future module work fans
out only after S01. Shared dispatch, startup, schema cutover, homelab app
manifests, encrypted Secret, and rollout remain serialized.

**Evidence destination**:
`specs/access-broker-roadmap/evidence.md` for this roadmap; each future slice
uses its own matching evidence file.

## Documentation Impact

This implementation adds only durable roadmap artifacts under
`specs/access-broker-roadmap/`. No generated architecture change is expected.
Future S16, S20, and S22B slices own operator runbook updates.

## Implementation Steps

1. Approve this roadmap's spec, plan, checklist, and task/analysis gates.
2. Resolve or schedule DG-001 through DG-003.
3. Deliver S01 and S02A/S02B as the two foundation gates.
4. Fan out Wave 2 modules against merged S01 contracts.
5. Serialize runtime and desired-state integration through Waves 3 and 4.
6. Pass M1 smoke before onboarding non-admin users.
7. Add managed lifecycle in Wave 5.
8. Complete production operations and drills in Wave 6.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Nominal parallelism creates conflicting state models | Merge S01 contracts first and assign one owner to schema and central dispatch |
| External side effects duplicate during retries | Persist desired state, use atomic claims, stable provider IDs, and idempotent reconciliation |
| SQLite behaves poorly on NFS or blocks multi-replica jobs | Use dedicated PostgreSQL with transactional leases and uniqueness constraints |
| Requester cannot receive Discord DMs | Make requester `/access status` authoritative and DM best-effort |
| Authentik activation creates a duplicate identity | Gate on DG-001 spike and require exact pre-approved identity smoke |
| Revocation deletes unrelated user data | Remove broker entitlement and VPN peer; deactivate only identities proven broker-owned |
| Sensitive VPN material remains after use | Hash tokens and purge private configuration on consume/expiry |
| Parallel app releases deploy the wrong mutable image | Land S02 immutable image and deterministic rollout before concurrent release rollout |
| Development cannot reproduce Discord or public routing | Use strongest available synthetic path and document unverified layers explicitly |
| Roadmap becomes a perpetual mega-branch | Every slice creates its own implementation branch and PR; homelab slices also create matching Spec Kit artifacts and evidence |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| Approved sibling worktree fallback | `/workspaces/homelab-worktrees` is not writable in this environment | Editing `main` would violate the branch-scoped workflow |
| Dedicated PostgreSQL planned instead of current file store | Durable jobs, leases, partial uniqueness, crash recovery, and future replicas need transactions | JSON has process-local locking; SQLite on NFS is an unsafe long-term coordination store |
