from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "dev-smoke.yml"

SAME_REPO = "github.event.pull_request.head.repo.full_name == github.repository"


def read() -> str:
    assert WORKFLOW.exists(), f"missing: {WORKFLOW.relative_to(REPO_ROOT)}"
    return WORKFLOW.read_text(encoding="utf-8")


def jobs(text: str) -> dict[str, str]:
    body = text.split("\njobs:\n", 1)[1]
    parts = re.split(r"(?m)^  ([\w-]+):\s*$", body)
    return dict(zip(parts[1::2], parts[2::2]))


def job_if(block: str) -> str:
    match = re.search(r"(?m)^    if: (.+)$", block)
    return match.group(1) if match else ""


def indented_blocks(text: str, header: str, indent: int) -> list[str]:
    """Bodies of every `<header>` key at `indent` spaces (a `with:` map or a `run: |` script)."""
    pad = " " * indent
    pattern = rf"(?m)^{pad}{re.escape(header)}\n((?:{pad}  .*\n|\n)+)"
    return re.findall(pattern, text + "\n")


class DevSmokeWorkflowTest(unittest.TestCase):
    def test_trigger_is_pull_request_target_without_path_filters(self) -> None:
        text = read()
        self.assertRegex(text, r"(?m)^  pull_request_target:")
        self.assertNotRegex(text, r"(?m)^  pull_request:")
        self.assertNotRegex(text, r"(?m)^\s+paths(-ignore)?:")

    def test_every_job_requires_same_repo(self) -> None:
        all_jobs = jobs(read())
        self.assertEqual({"classify", "smoke", "dev-smoke"}, set(all_jobs))
        for name, block in all_jobs.items():
            self.assertIn(SAME_REPO, job_if(block), f"job {name} must require a same-repo PR")
        aggregator = job_if(all_jobs["dev-smoke"])
        self.assertTrue(aggregator.startswith("always() && "), aggregator)
        self.assertIn(SAME_REPO, aggregator)

    def test_concurrency_group_is_per_pr_and_cancels(self) -> None:
        text = read().split("\njobs:\n", 1)[0]
        self.assertRegex(text, r"(?m)^concurrency:")
        self.assertRegex(text, r"(?m)^  group: .*github\.event\.pull_request\.number")
        self.assertRegex(text, r"(?m)^  cancel-in-progress: true$")

    def test_checkouts_use_main_only(self) -> None:
        text = read()
        withs = indented_blocks(text, "with:", 8)
        checkout_withs = [w for w in withs if "persist-credentials" in w or "ref:" in w]
        self.assertGreaterEqual(len(checkout_withs), 2, "classify and smoke both check out")
        for block in checkout_withs:
            self.assertRegex(block, r"(?m)^\s+ref: main$")
            self.assertRegex(block, r"(?m)^\s+persist-credentials: false$")
        for block in withs:
            self.assertNotIn("github.event.pull_request.head", block)

    def test_head_ref_is_passed_via_env(self) -> None:
        text = read()
        for script in indented_blocks(text, "run: |", 8):
            self.assertNotIn("${{ github.event.", script, "untrusted event data must reach scripts through env")
        smoke = jobs(text)["smoke"]
        self.assertRegex(smoke, r"(?m)^\s+HEAD_REF: \$\{\{ github\.event\.pull_request\.head\.ref \}\}$")
        self.assertIn('--branch "$HEAD_REF"', smoke)

    def test_smoke_job_runs_on_the_dev_runner_with_a_timeout(self) -> None:
        smoke = jobs(read())["smoke"]
        self.assertRegex(smoke, r"(?m)^    runs-on: homelab-dev$")
        self.assertRegex(smoke, r"(?m)^    timeout-minutes: 20$")
        self.assertRegex(smoke, r"(?m)^    needs: classify$")
        self.assertIn("needs.classify.outputs.tested == 'true'", job_if(smoke))

    def test_smoke_uses_ci_mode_and_browser_only_when_classified(self) -> None:
        smoke = jobs(read())["smoke"]
        self.assertIn("--ci", smoke)
        self.assertIn("verify_branch_deploy.py", smoke)
        self.assertIn("cleanup_pr_envs.py", smoke)
        self.assertIn('--slug "pr-${PR_NUMBER}"', smoke)
        browser_lines = [line for line in smoke.splitlines() if "--browser" in line]
        self.assertTrue(browser_lines)
        self.assertRegex(smoke, r'if \[ "\$BROWSER" = true \]')

    def test_results_are_uploaded_even_on_failure_and_env_is_cleaned(self) -> None:
        smoke = jobs(read())["smoke"]
        steps = re.split(r"\n      - ", smoke)
        uploads = [s for s in steps if "upload-artifact" in s]
        self.assertTrue(uploads)
        for step in uploads:
            self.assertIn("if: always()", step)
        cleanups = [s for s in steps if "cleanup_pr_envs.py" in s and "if: always()" in s]
        self.assertTrue(cleanups, "a final always() cleanup step must remove the PR environment")

    def test_aggregator_is_the_dev_smoke_check_and_explains_untested_prs(self) -> None:
        block = jobs(read())["dev-smoke"]
        self.assertRegex(block, r"(?m)^    name: dev-smoke$")
        self.assertRegex(block, r"(?m)^    needs: \[classify, smoke\]$")
        self.assertIn("not smoke-tested: ", block)
        self.assertIn("GITHUB_STEP_SUMMARY", block)
        self.assertIn("needs.smoke.result", block)
        self.assertIn("needs.classify.result", block)

    def test_smoke_job_also_sweeps_stale_environments_without_failing_the_smoke(self) -> None:
        smoke = jobs(read())["smoke"]
        steps = re.split(r"\n      - ", smoke)
        sweeps = [s for s in steps if "--older-than 3h" in s]
        self.assertEqual(1, len(sweeps), "one step removes other PRs' stale environments")
        sweep = sweeps[0]
        self.assertIn("cleanup_pr_envs.py", sweep)
        self.assertNotIn("--slug", sweep, "the sweep is age-based, never a named PR")
        self.assertIn("::warning::", sweep, "a failed sweep is a warning, not a smoke failure")
        self.assertRegex(sweep, r"(?m)^\s+if ! python3 tools/development/cleanup_pr_envs\.py")
        self.assertIn("if: ${{ !cancelled() }}", sweep)
        own = [i for i, s in enumerate(steps) if "Remove this PR's environment" in s]
        self.assertEqual(1, len(own))
        self.assertGreater(steps.index(sweep), own[0], "sweep after the PR's own environment is removed")


if __name__ == "__main__":
    unittest.main()
