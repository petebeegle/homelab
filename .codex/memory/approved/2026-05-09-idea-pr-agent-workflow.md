---
status: approved
created: 2026-05-09
source: user-preference
kind: workflow-preference
---

# Idea PR Agent Workflow

Break work into named ideas before implementation.

Each idea maps to one pull request and may contain multiple conventional commits. A separate implementation agent owns each idea's implementation work.

New idea branches must always branch from `main`.

As implementation agents finish, create separate verifier agents to review the result. The planner coordinates the idea breakdown, delegates implementation and verification, and summarizes status.

Conventional commits are enforced locally and by origin.

Do not push to origin until verifier approval is recorded for the exact `HEAD` commit.
