# Implementation Plan: home-assistant-hue-v2

**Branch**: `codex/home-assistant-hue-v2` | **Date**: 2026-07-03 | **Spec**:
`specs/home-assistant-hue-v2/spec.md`

**Input**: Feature specification from `specs/home-assistant-hue-v2/spec.md`

## Summary

Update durable docs and SDD artifacts to make the Philips Hue V2 boundary explicit: Home Assistant owns the bridge pairing config-flow and stores it on the PVC, while the repository owns later packages and automations only after real Hue entity IDs are available.

## Technical Context

**Risk Tier**: tiny
**Workflow Tier**: docs-only
**Primary Areas**: Home Assistant operator docs, SDD artifacts
**Dependencies**: Spec Kit templates already present in the repository; local git and Python harness validators
**Storage**: Existing `home-assistant-config` PVC remains the runtime location for Home Assistant config-flow state
**Ingress**: N/A; no Gateway API or route changes
**Secrets**: No SOPS or plaintext secret changes; Hue credentials and tokens are explicitly excluded from Git
**Development Validation**: none; docs-only guidance change, and Hue pairing requires a physical bridge plus Home Assistant UI access

## Constitution Check

*GATE: Must pass before tracked edits and be re-checked before commit.*

- [x] GitOps source of truth preserved; no durable live-cluster-only state.
- [x] No production-first mutation; development validation plan or exception is recorded for covered changes.
- [x] Gateway API invariant preserved; no new Kubernetes `Ingress` resources.
- [x] SOPS invariant preserved; no plaintext secret manifests staged.
- [x] NFS default considered for PVC-backed workloads.
- [x] Talos boundary preserved; no SSH-based node operations introduced.
- [x] Sibling clone ownership files validated before tracked edits.
- [x] Documentation impact identified; docs updated or no-docs rationale recorded.
- [x] Separate verifier approval required before PR creation.

## Project Structure

### SDD Artifacts

```text
specs/home-assistant-hue-v2/
├── spec.md
├── plan.md
├── tasks.md
└── evidence.md
```

### Source Or Documentation Changes

```text
docs/runbooks/home-assistant.md
specs/home-assistant-hue-v2/
```

## Tiered TDD And Validation Plan

**TDD expectation**: No failing code test is required for docs-only/tiny work. Validation is local review, harness validation, whitespace checking, and targeted checks that no Hue runtime state or credentials were added.

**Local checks**:

- `python3 tools/codex-harness/validate_active_implementation.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_implementation_plan.py --plan .codex/tmp/implementation-plan.yaml --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_workflow_attestations.py --kind owner --attestation .codex/tmp/implementation-owner-attestation.yaml --marker .codex/tmp/active-implementation --plan .codex/tmp/implementation-plan.yaml --root "$(pwd)" --branch "$(git branch --show-current)"`
- `python3 tools/codex-harness/validate_sdd_context.py --marker .codex/tmp/active-implementation --root "$(pwd)" --branch "$(git branch --show-current)" --require-plan-artifacts`
- `git diff --check`
- `git diff --name-only`
- `git diff -- docs/runbooks/home-assistant.md specs/home-assistant-hue-v2 | rg -n '(^|/|\\.)storage|config_entries|access_token|refresh_token|client_secret|bridge credential|Hue token|hue_token|hue\\.yaml'`

**Development smoke**: none; this implementation changes only docs and SDD artifacts. Hue V2 pairing requires runtime UI access to Home Assistant and a physical Hue bridge, so no development cluster validation can prove it.

**Evidence destination**: `specs/home-assistant-hue-v2/evidence.md` and
`.codex/tmp/pr-summary.md`.

## Documentation Impact

Update `docs/runbooks/home-assistant.md` with Hue V2 pairing, runtime state, inventory, and later Git-owned automation guidance. Generated `docs/architecture.md` is not affected because no Kubernetes or Terraform source changes are made.

## Implementation Steps

1. Create SDD artifacts under `specs/home-assistant-hue-v2/`.
2. Update `docs/runbooks/home-assistant.md` with Hue V2 declarative boundary and inventory guidance.
3. Run owner workflow and SDD validators.
4. Run local docs checks and targeted grep/diff checks for excluded Hue runtime state or credentials.
5. Record evidence, write `.codex/tmp/pr-summary.md`, commit with a conventional commit, and stop before verifier approval or PR creation.

## Risks

| Risk | Mitigation |
| ---- | ---------- |
| Operators expect Hue to be declared fully in Git before pairing | State that Home Assistant UI pairing is required runtime config-flow state on the PVC |
| Hue credentials or tokens are committed accidentally | Exclude `.storage`, config entries, credentials, tokens, and fake integration config in docs and validate with targeted diff/grep checks |
| Placeholder package implies automations are ready | Do not add `hue.yaml`; document that packages follow after entity IDs exist |

## Complexity Tracking

> Fill only when the constitution check has a violation that must be justified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A | N/A | N/A |
