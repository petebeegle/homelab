# Data Model: Access Broker Delivery Roadmap

This is the target conceptual model. Future persistence details are owned by
S01 and S06.

## Principal

Represents a Discord requester.

| Field | Rule |
| ----- | ---- |
| Discord user ID | Stable unique ownership key |
| Current display name | Mutable presentation metadata |
| Broker ownership metadata | Records which external identity/resources the broker may manage |
| Created/updated timestamps | Audit metadata |

## Access Request

Represents an operator-reviewed request.

| Field | Rule |
| ----- | ---- |
| Request ID | Unique, opaque identifier |
| Principal ID | Required |
| Guild/channel context | Required and validated against intake policy |
| Status | Pending, claimed, provisioning, approved, denied, failed, superseded |
| Reviewer and reason | Required for review transitions |
| Created/claimed/reviewed timestamps | Required |

Only one pending or provisioning request may exist per principal.

## Access Grant

Represents current authorization.

| Field | Rule |
| ----- | ---- |
| Grant ID | Unique |
| Principal ID | Required |
| State | Active, revocation queued, revoking, revoked, expired, revocation failed |
| Authentik identity/provider IDs | Stable external references |
| WireGuard peer ID | Stable external reference |
| Starts/expires/revoked timestamps | Policy and audit metadata |
| Ownership and policy version | Required for safe reconciliation |

Only one active or revoking grant may exist per principal.

## Artifact

Represents temporary sensitive delivery material.

| Field | Rule |
| ----- | ---- |
| Artifact ID and grant ID | Required |
| Type | VPN configuration or activation handoff |
| Token hash | Store hash, never raw bearer token |
| State | Available, consumed, expired, purged |
| Expires/consumed/purged timestamps | Required by transition |
| Encrypted payload reference | Present only while available |

Consumed or expired artifacts transition to purged and retain no private
configuration.

## Delivery

Represents requester notification or retrieval.

| Field | Rule |
| ----- | ---- |
| Delivery ID and principal ID | Required |
| Channel | Requester status response or Discord DM |
| State | Pending, sent, blocked, retryable failure, permanent failure |
| Attempt count and next attempt | Required for retryable delivery |
| Safe error class | Must not contain credentials or payload |

Requester status remains available regardless of DM state.

## Job

Represents durable external reconciliation.

| Field | Rule |
| ----- | ---- |
| Job ID and type | Required |
| Aggregate ID | Request, grant, artifact, or delivery owner |
| State | Queued, leased, running, retryable, succeeded, permanently failed |
| Lease owner/expiry | Required while leased or running |
| Attempt count/next run | Required |
| Idempotency key | Unique for one intended side effect |

Jobs use transactional compare-and-swap transitions.

## Audit Event

Represents append-only safe history.

| Field | Rule |
| ----- | ---- |
| Event ID/type/time | Required |
| Actor and aggregate IDs | Required when applicable |
| From/to state | Required for lifecycle transitions |
| Result and safe reason | Required |
| Correlation/request ID | Required |

Audit events never contain raw tokens, passwords, private keys, full VPN
configurations, or Discord interaction tokens.

## State Transitions

```text
Request:
pending -> claimed -> provisioning -> approved
   |          |             |
   v          v             v
denied      failed       superseded

Grant:
active -> revocation_queued -> revoking -> revoked
   |                              |
   +---- expires_at reached ------+
                                  |
                                  v
                           revocation_failed

Artifact:
available -> consumed -> purged
    |
    +------ expired -> purged

Job:
queued -> leased -> running -> succeeded
                    |  ^
                    v  |
                 retryable
                    |
                    v
             permanently_failed
```
