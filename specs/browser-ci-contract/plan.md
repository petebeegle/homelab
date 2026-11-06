# Plan

Risk: low (CI and docs only). SDD: low. Use a manually dispatched GitHub-hosted workflow for a *publicly reachable* development route only. It does not assume the internal development DNS is reachable. An isolated runner for private routes is a later infrastructure step, never a privileged runner executing arbitrary PR code. Install pinned Playwright package using the existing package manifest and install Chromium; run Whoami smoke using an explicitly validated slug. Upload JUnit and traces. No cluster changes.

User's 'Continue' authorizes this bounded next step; low-risk human gates combined. Do not merge before CI checks.
