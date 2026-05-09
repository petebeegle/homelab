---
status: approved
created: 2026-05-09
source: user-preference
kind: workflow-preference
---

# Commit Hygiene Preference

Use conventional commit messages and split changes into atomic commits.

For multi-area work in this repo:

- Separate documentation, harness/config, tooling, generated artifacts, and runtime environment changes.
- Keep generated artifacts out of commits unless they are intentionally part of the change.
- Verify each atomic slice before pushing when practical.
