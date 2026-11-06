# Plan

SDD tier: low; workflow risk: low. Smoke strategy: local subprocess tests and GitHub-hosted CI; live development smoke not applicable to this tooling-only increment. Fanout: no conflicting edits.

Add a stdlib-only command runner that executes the existing URL guard unit test and a static Playwright test discovery contract. CI runs the same entrypoint. Add unit tests for exit propagation and missing commands. Do not edit binding safety hooks. Document the migration inventory and separate dev-cluster runner as follow-up.

Human gate exception: the user's explicit 'Send it' authorizes this bounded PR; separate spec/plan/task approvals consolidated. Review and CI remain authoritative.
