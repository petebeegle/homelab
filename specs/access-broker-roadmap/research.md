# Research: Access Broker Delivery Roadmap

## Decision: Establish Domain Contracts Before Feature Fanout

**Rationale**: Requester delivery, activation, revocation, retry, cleanup, and
expiration all need to change the current combined request record and central
server handler. A small foundation slice defining lifecycle entities, atomic
claims, stable ownership, interfaces, and handler seams turns later work into
disjoint modules.

**Alternatives considered**:

- Build each feature directly on the JSON store: rejected because every lane
  would independently migrate the same state and command dispatch.
- Perform a full rewrite first: rejected because it delays user value and
  increases migration risk.

## Decision: Use Stable Discord User ID As Principal Ownership

**Rationale**: Display names change and are not unique. Human-readable peer
names remain metadata, while provider IDs and the Discord user ID establish
ownership.

**Alternatives considered**:

- Name-based identity: rejected because rename can create duplicate peers.
- Authentik username alone: rejected because requester authorization begins in
  Discord and must survive Authentik activation changes.

## Decision: One Active Grant Per Principal

**Rationale**: A normal repeat request should not silently create another
long-lived VPN peer. Retry reconciles the same grant; reissue explicitly rotates
the peer; renewal extends policy; revoke ends the grant.

**Alternatives considered**:

- Unlimited peers per requester: rejected because ownership and revocation
  become ambiguous.
- Always rotate on `/access request`: rejected because accidental repeats would
  invalidate working access.

## Decision: Requester Status Is Authoritative Delivery

**Rationale**: The requester can always invoke an ephemeral command in the
approved Discord context. Direct messages can be blocked and require a rotated
bot token. `/access status` therefore owns private retrieval and reissue;
requester DM is a best-effort convenience.

**Alternatives considered**:

- Admin forwards the link: rejected because it exposes credentials to the wrong
  actor and is operationally fragile.
- DM-only delivery: rejected because Discord privacy settings can block it.
- Public unauthenticated status portal: rejected until a separate authenticated
  portal requirement exists.

## Decision: PostgreSQL Is The Durable Coordination Store

**Rationale**: Durable jobs require transactions, leases, uniqueness, restart
recovery, and future multi-replica safety. The current JSON lock is
process-local. SQLite on the existing NFS path has undesirable locking and
failure behavior for this workload.

**Alternatives considered**:

- Keep JSON permanently: rejected because external side effects cannot be
  atomically claimed or recovered.
- SQLite on NFS: rejected as a long-term concurrent coordination store.
- Kubernetes Jobs only: rejected because provider reconciliation and delivery
  still need durable application state.

## Decision: Separate Desired State From External Side Effects

**Rationale**: Jobs persist desired transitions and reconcile Authentik,
wg-easy, and Discord idempotently. A crash after an external API call can then
resume from recorded provider IDs without repeating ownership changes.

**Alternatives considered**:

- Continue detached goroutines: rejected because pod restart loses work.
- Distributed transaction across external APIs: unavailable and unnecessary;
  reconciliation is the appropriate model.

## Decision: Revoke Entitlement, Preserve Identity

**Rationale**: Revocation removes or disables the VPN peer and removes the
broker-owned Authentik access entitlement. It must not delete unrelated identity
data. Deactivation is allowed only when ownership metadata proves the identity
was created solely by the broker and policy explicitly requires it.

**Alternatives considered**:

- Delete the Authentik user: rejected because the user may own unrelated
  sessions, factors, or application data.
- Leave identity entitlement active: rejected because VPN revocation alone does
  not end application authorization.

## Decision: Purge Secrets, Retain Audit Metadata

**Rationale**: Raw bearer tokens and WireGuard private configurations are not
audit records. Store hashed token identifiers, purge private material on
consume/expiry, and retain actor, request, grant, provider IDs, timestamps,
result, and reason.

**Alternatives considered**:

- Retain configuration for easy re-download: rejected because it extends
  private-key exposure indefinitely.
- Delete the entire request: rejected because operators need lifecycle and
  security audit history.

## Decision: Immutable Releases Precede Concurrent Rollout

**Rationale**: A mutable `:main` tag makes parallel app changes impossible to
attribute and currently requires manual pod deletion. Pinning an immutable
release identity with source/revision metadata in `homelab-access`, then pinning
its reviewed digest and adding deterministic config/Secret rollout in `homelab`,
makes later waves reviewable and reversible without crossing repository PR
boundaries.

**Alternatives considered**:

- Continue manual pod deletion: rejected because it is not desired state and
  cannot prove which source revision runs.
- Use timestamp-only rollout annotations with mutable image: rejected because
  source-to-image provenance remains ambiguous.

## Deferred Decisions

- **DG-001**: Discord-linked Authentik identity versus temporary password setup.
- **DG-002**: Default grant lifetime and renewal policy.
- **DG-003**: Initial Authentik application/group bundle.

These decisions alter their owning implementations but do not alter the roadmap
critical path.
