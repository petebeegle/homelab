# Dev browser smoke command — plan

SDD tier: low. Workflow risk: low for repository code and docs; the live verification mutates only temporary, self-cleaning development-cluster objects.
Smoke strategy: unit tests with the existing FakeRunner (41 pass) plus a full live run of the real CLI against development, including the Terraform step.
Fanout: runner-infrastructure discovery ran as a parallel read-only agent (results feed specs/dev-runner-infrastructure, not this change).
Exceptions: Terraform needed the git-ignored tfvars (staged per AGENTS.md without printing contents) and `TF_VAR_talos_version` because `origin/main` gives that variable no default; state is local and was not staged, so the plan's contents are not a drift signal. The branch-protection ruleset was applied through the API (a repository setting, not a tracked file); a copy is committed for reference.
Human gate: the user approved all three items ("make them required with a break glass option", "yeah its a good start").
