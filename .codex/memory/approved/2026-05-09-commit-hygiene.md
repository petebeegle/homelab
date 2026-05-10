---
status: approved
created: 2026-05-09
last_verified: 2026-05-10
review_after: 2026-08-08
source: user-preference
kind: workflow-preference
scope:
  - git
  - implementation-workflow
authority: advisory
supersedes: []
superseded_by:
---

# Commit Hygiene Preference

Use conventional commit messages and split changes into atomic commits.

For multi-area work in this repo:

- Separate documentation, harness/config, tooling, generated artifacts, and runtime environment changes.
- Keep generated artifacts out of commits unless they are intentionally part of the change.
- Verify each atomic slice before pushing when practical.
