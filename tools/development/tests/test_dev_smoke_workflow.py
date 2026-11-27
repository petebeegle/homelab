from __future__ import annotations

import os
import re
import subprocess
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
        self.assertEqual({"classify", "smoke", "base", "dev-smoke"}, set(all_jobs))
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

    def test_checkouts_use_main_except_one_data_only_pr_checkout(self) -> None:
        text = read()
        withs = indented_blocks(text, "with:", 8)
        checkout_withs = [w for w in withs if "persist-credentials" in w or "ref:" in w]
        self.assertGreaterEqual(len(checkout_withs), 2, "classify and smoke both check out")
        for block in checkout_withs:
            self.assertRegex(block, r"(?m)^\s+persist-credentials: false$")
            if "refs/pull/" in block:
                # The PR merged onto main (GitHub's test merge), checked out only as data into pr/.
                self.assertRegex(block, r"(?m)^\s+ref: refs/pull/\$\{\{ github\.event\.pull_request\.number \}\}/merge$")
                self.assertRegex(block, r"(?m)^\s+path: pr$")
                self.assertRegex(block, r"(?m)^\s+fetch-depth: 2$", "HEAD^1 must exist to check the merge")
            else:
                self.assertRegex(block, r"(?m)^\s+ref: main$")

    def test_the_pr_checkout_is_only_rendered_never_executed(self) -> None:
        for script in indented_blocks(read(), "run: |", 8) + re.findall(r"(?m)^        run: (.+)$", read()):
            if re.search(r"(?<![\w/-])pr/|--head(?:-dir)? pr\b", script):
                self.assertRegex(script, r"affected_dev\.py|base_smoke\.py", script)
            self.assertNotRegex(script, r"(?:python3|bash|sh|node|npm|npx)\s+(?:--prefix\s+)?pr/", script)
            self.assertNotRegex(script, r"working-directory: pr")

    def test_classify_finds_affected_development_kustomizations(self) -> None:
        classify = jobs(read())["classify"]
        self.assertIn("base: ${{ steps.affected.outputs.base }}", classify)
        self.assertIn("python3 tools/development/affected_dev.py --base . --head pr", classify)

    def test_base_job_applies_the_pr_to_development_and_always_restores(self) -> None:
        base = jobs(read())["base"]
        self.assertIn("needs.classify.outputs.base == 'true'", job_if(base))
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", job_if(base))
        self.assertRegex(base, r"(?m)^    runs-on: homelab-dev$")
        self.assertRegex(base, r"(?m)^    timeout-minutes: \d+$")
        steps = re.split(r"\n      - ", base)
        run = [s for s in steps if "base_smoke.py" in s and "--head-dir pr" in s]
        self.assertEqual(len(run), 1)
        restore = [s for s in steps if "--recover-stale" in s]
        self.assertEqual(len(restore), 1)
        # Always, once there is a kubeconfig: a job that stopped before it never touched development,
        # and an empty --kubeconfig is a confusing "DEVELOPMENT DID NOT RECOVER"-class failure.
        self.assertIn("if: always() && steps.kubeconfig.outcome == 'success'", restore[0])
        self.assertTrue(any("id: kubeconfig" in s and "dev-kubeconfig" in s for s in steps))
        self.assertIn("--max-age-seconds 0", restore[0])
        self.assertTrue(any("upload-artifact" in s and "if: always()" in s for s in steps))

    def test_a_stale_merge_says_to_rerun_every_job(self) -> None:
        # Re-running only the failed job reuses classify's stale merge ref; a full re-run refreshes it.
        self.assertIn("re-run all jobs", jobs(read())["base"])

    def test_the_merge_must_be_onto_current_main(self) -> None:
        text = read()
        for job in ("classify", "smoke", "base"):
            block = jobs(text)[job]
            self.assertIn('git -C pr rev-parse HEAD^1', block, f"{job} must check the merge's first parent")
            self.assertIn("is not a merge onto current main", block, job)

    def test_base_job_publishes_the_merge_as_a_temporary_branch_and_always_deletes_it(self) -> None:
        base = jobs(read())["base"]
        self.assertRegex(base, r"(?m)^    permissions:\n      contents: write$")
        steps = re.split(r"\n      - ", base)
        publish = [s for s in steps if "Publish the merge" in s]
        self.assertEqual(len(publish), 1)
        self.assertIn('ref="refs/heads/base-smoke/pr-${PR_NUMBER}"', publish[0])
        self.assertIn("-X POST", publish[0])
        self.assertIn("${MERGE_SHA}", publish[0])
        delete = [s for s in steps if "-X DELETE" in s and "git/refs/heads/base-smoke/pr-${PR_NUMBER}" in s]
        self.assertEqual(len(delete), 1)
        self.assertIn("if: always()", delete[0])

    def test_runner_jobs_use_only_tools_the_runner_image_has(self) -> None:
        # The runner image has kubectl, flux, curl, node and python, but no gh CLI.
        for job in ("smoke", "base"):
            self.assertNotRegex(jobs(read())[job], r"(?m)^\s+(?:run: )?gh |\bgh api\b", job)

    def test_kubeconfig_comes_before_anything_the_always_steps_depend_on(self) -> None:
        base = jobs(read())["base"]
        steps = re.split(r"\n      - ", base)
        kubeconfig = next(i for i, s in enumerate(steps) if "dev-kubeconfig" in s)
        publish = next(i for i, s in enumerate(steps) if "Publish the merge" in s)
        self.assertLess(kubeconfig, publish, "a failed publish must still leave the restore step a kubeconfig")

    def test_base_smoke_receives_cancellation_signals_directly(self) -> None:
        # bash does not forward SIGINT/SIGTERM to a foreground child; a cancelled run would leave
        # base_smoke running underneath the always() restore.
        base = jobs(read())["base"]
        self.assertIn("exec python3 tools/development/base_smoke.py", base)

    def test_no_dead_upload_paths(self) -> None:
        self.assertNotIn("browser-results", read())

    def test_head_ref_is_passed_via_env(self) -> None:
        text = read()
        for script in indented_blocks(text, "run: |", 8):
            self.assertNotIn("${{ github.event.", script, "untrusted event data must reach scripts through env")

    def test_every_pr_gets_a_fresh_merge_onto_main(self) -> None:
        # The smoke job deploys the merge too, so classify asks for it whatever the PR is.
        classify = jobs(read())["classify"]
        step = next(s for s in re.split(r"\n      - ", classify) if "Ask GitHub for a fresh merge" in s)
        self.assertNotRegex(step, r"(?m)^        if: ")

    def test_smoke_job_deploys_the_merge_onto_main_not_the_pr_head(self) -> None:
        # The probes come from main. A head that is behind main would run them against the old
        # app, and a pass would not describe what merging lands (#433).
        smoke = jobs(read())["smoke"]
        self.assertNotIn("head.ref", smoke)
        self.assertRegex(smoke, r"(?m)^    permissions:\n      contents: write$")
        steps = re.split(r"\n      - ", smoke)
        publish = [s for s in steps if "Publish the merge" in s]
        self.assertEqual(len(publish), 1)
        self.assertIn('ref="refs/heads/pr-smoke/pr-${PR_NUMBER}"', publish[0])
        self.assertIn("${MERGE_SHA}", publish[0])
        run = [s for s in steps if "verify_branch_deploy.py" in s]
        self.assertEqual(len(run), 1)
        self.assertIn('--branch "pr-smoke/pr-${PR_NUMBER}"', run[0])
        delete = [s for s in steps if "-X DELETE" in s and "git/refs/heads/pr-smoke/pr-${PR_NUMBER}" in s]
        self.assertEqual(len(delete), 1)
        self.assertIn("if: always()", delete[0])
        self.assertLess(
            next(i for i, s in enumerate(steps) if "dev-kubeconfig" in s),
            steps.index(publish[0]),
        )

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
        self.assertRegex(block, r"(?m)^    needs: \[classify, smoke, base\]$")
        self.assertIn("needs.base.result", block)
        self.assertIn("not smoke-tested: ", block)
        self.assertIn("GITHUB_STEP_SUMMARY", block)
        self.assertIn("needs.smoke.result", block)
        self.assertIn("needs.classify.result", block)

    def report(self, **env: str) -> subprocess.CompletedProcess[str]:
        """Run the aggregator's script with the given job results and classifier outputs."""
        (script,) = indented_blocks(jobs(read())["dev-smoke"], "run: |", 8)
        values = {
            "CLASSIFY_RESULT": "success", "SMOKE_RESULT": "skipped", "BASE_RESULT": "skipped",
            "TESTED": "false", "BASE": "false", "AUTOMERGE": "false", "HEAD_REF": "codex/change",
            "REASON": "r", "BASE_REASON": "b", **env,
        }
        summary = self.enterContext(__import__("tempfile").NamedTemporaryFile())
        return subprocess.run(
            ["bash", "-c", "\n".join(line[10:] for line in script.splitlines())],
            env={**os.environ, **values, "GITHUB_STEP_SUMMARY": summary.name},
            capture_output=True,
            text=True,
        )

    def test_an_untested_renovate_pr_that_would_auto_merge_fails(self) -> None:
        result = self.report(HEAD_REF="renovate/whoami-1.x", AUTOMERGE="true", REASON="multiple apps: homepage, whoami")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("auto-merge", result.stdout)
        self.assertIn("multiple apps", result.stdout)

    def test_other_untested_prs_still_pass(self) -> None:
        self.assertEqual(self.report(HEAD_REF="codex/two-apps", AUTOMERGE="true").returncode, 0)
        self.assertEqual(self.report(HEAD_REF="renovate/pihole-1.x", AUTOMERGE="false").returncode, 0)

    def test_a_tested_renovate_pr_passes_on_its_smoke_result(self) -> None:
        renovate = {"HEAD_REF": "renovate/whoami-1.x", "AUTOMERGE": "true"}
        self.assertEqual(self.report(**renovate, TESTED="true", SMOKE_RESULT="success").returncode, 0)
        self.assertEqual(self.report(**renovate, TESTED="true", SMOKE_RESULT="failure").returncode, 1)
        self.assertEqual(self.report(**renovate, BASE="true", BASE_RESULT="success").returncode, 0)
        self.assertEqual(self.report(**renovate, BASE="true", BASE_RESULT="failure").returncode, 1)

    def test_classify_passes_the_auto_merge_flag_to_the_aggregator(self) -> None:
        all_jobs = jobs(read())
        self.assertIn("automerge: ${{ steps.classify.outputs.automerge }}", all_jobs["classify"])
        self.assertIn("echo \"automerge=$(jq -r '.automerge' classification.json)\"", all_jobs["classify"])
        self.assertRegex(all_jobs["dev-smoke"], r"(?m)^\s+AUTOMERGE: \$\{\{ needs\.classify\.outputs\.automerge \}\}$")
        self.assertRegex(all_jobs["dev-smoke"], r"(?m)^\s+HEAD_REF: \$\{\{ github\.event\.pull_request\.head\.ref \}\}$")

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
