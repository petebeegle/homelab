# Tasks: Repair Renovate storage documentation

Spec, plan, and task gates are approved by the user's instruction to fix the
previously reviewed failure. Risk: low; workflow: docs-only.

- [x] T001 [FR-002] Confirm isolated branch, scope, and approved lightweight plan.
- [x] T002 [FR-001] Reproduce architecture staleness, then regenerate
  `docs/architecture.md` using `tools/architecture/render.py --write`.
- [x] T003 [FR-003] Validate generated output, relevant pre-commit hooks, SDD
  context, and whitespace; reconcile requirements in `evidence.md`.
- [x] T004 [FR-002] Prepare only owned files for the local conventional commit;
  parent owns subsequent push and PR review.

This lane is parallel to other PR repairs; its own generation and validation
steps are sequential. No independent internal task warrants a [P] marker.
