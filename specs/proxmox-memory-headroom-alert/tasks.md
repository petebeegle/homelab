---
description: "Homelab SDD task list for proxmox-memory-headroom-alert"
---

# Tasks: proxmox-memory-headroom-alert

**Input**: `specs/proxmox-memory-headroom-alert/spec.md` and
`specs/proxmox-memory-headroom-alert/plan.md`
**Risk Tier**: medium
**Prerequisites**: Valid workflow marker, implementation plan, owner attestation,
and delegation token under `.codex/tmp/`

## Format: `[ID] [P?] [Req] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on another task.
- **[Req]**: Requirement or user story trace, such as `FR-001` or `US1`.
- Include exact file paths in each task.

## Phase 1: Workflow Setup

- [x] T001 [FR-OWN] Create or refresh the sibling clone on
      `codex/proxmox-memory-headroom-alert`.
- [x] T002 [FR-OWN] Create `.codex/tmp/active-implementation`,
      `.codex/tmp/implementation-plan.yaml`,
      `.codex/tmp/implementation-owner-attestation.yaml`, and matching
      delegation token evidence.
- [x] T003 [FR-OWN] Run the three owner workflow validators and record outcomes
      in `specs/proxmox-memory-headroom-alert/evidence.md`.

## Phase 2: Spec And Plan

- [x] T004 [FR-SPEC] Write
      `specs/proxmox-memory-headroom-alert/spec.md`.
- [x] T005 [FR-PLAN] Write
      `specs/proxmox-memory-headroom-alert/plan.md`, including tiered TDD and
      development validation expectations.
- [x] T006 [FR-DOCS] Confirm documentation impact and generated architecture
      expectations.

## Phase 3: Implementation

- [x] T007 [FR-IMPL] Edit only existing UID `proxmox-host-memory-high` in
      `kubernetes/infra/monitoring/grafana/alerting/alert-rules-proxmox.yaml`.
- [x] T008 [FR-IMPL] Re-check constitution gates after implementation edits.

## Phase 4: Verification

- [x] T009 [FR-TEST] Run `pre-commit run yamllint --files kubernetes/infra/monitoring/grafana/alerting/alert-rules-proxmox.yaml`.
- [x] T010 [FR-TEST] Run `pre-commit run k8svalidate --files kubernetes/infra/monitoring/grafana/alerting/alert-rules-proxmox.yaml`.
- [x] T011 [FR-TEST] Run `kubectl kustomize kubernetes/infra/monitoring/grafana/alerting >/tmp/proxmox-alerting-render.yaml`.
- [x] T012 [FR-SMOKE] Run read-only production Mimir checks for the exact pve01
      free-GiB query and aggregate alert query.
- [x] T013 [FR-WORKFLOW] Run required workflow validators including SDD context
      with evidence and current HEAD.
- [x] T014 [FR-EVIDENCE] Record command outcomes, smoke exception, observed
      query values, documentation impact, and final `HEAD` in
      `specs/proxmox-memory-headroom-alert/evidence.md`.

## Phase 5: Commit And Handoff

- [x] T015 [FR-PR] Write `.codex/tmp/pr-summary.md` from the plan and final
      evidence.
- [x] T016 [FR-PR] Commit with a conventional commit message.
- [x] T017 [FR-PR] Report exact `HEAD` and do not create verifier approval, push,
      or PR.
