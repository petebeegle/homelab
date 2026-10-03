# Repair Renovate Playwright update

SDD tier: medium. Repair PR #376 without expanding its dependency scope.

The user requested review, then said "fix them fan out" after the exact mirror
and browser-image defects and recommended correction were reported. This is
approval to implement that bounded correction and its combined decision gates.

Requirements: both smoke npm dependency sets use Playwright 1.63.0; mirrored
lockfiles remain byte-identical; intentional package.json script differences
remain; the in-cluster browser image matches 1.63.0. Demonstrate the existing
mirror failure before editing, focused checks afterward, and actual development
browser execution. Do not change production or refactor Renovate policy.

Authority: docs/runbooks/spec-driven-development.md,
docs/runbooks/implementation-workflow.md,
docs/decisions/tdd-and-development-smoke-evidence.md and
 docs/runbooks/synthetic-smoke-tests.md.
