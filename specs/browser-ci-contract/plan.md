# Plan

Risk: low (CI and docs only). SDD: low. Use a manually dispatched workflow targeting a dedicated ephemeral self-hosted development-network runner, with internal DNS and Gateway trust. Runner provisioning is a separate infrastructure task; no claim that a runner is already registered. An isolated runner for private routes is a later infrastructure step, never a privileged runner executing arbitrary PR code. Install pinned Playwright package using the existing package manifest and install Chromium; run Whoami smoke using an explicitly validated slug. Upload JUnit and traces. No cluster changes.

User's 'Continue' authorizes this bounded next step; low-risk human gates combined. Do not merge before CI checks.
