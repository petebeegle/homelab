from __future__ import annotations

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ACTION = REPO_ROOT / ".github" / "actions" / "pr-merge" / "action.yml"

# Plays the GitHub REST API for the action's curl calls. Every call is logged; the merges
# endpoint answers with $FAKE_MERGE_STATUS, and the temporary branch exists if $FAKE_BRANCH_EXISTS.
FAKE_CURL = r"""#!/usr/bin/env bash
out=""; fmt=""; method=GET; data=""; url=""
while [ $# -gt 0 ]; do
  case "$1" in
    -o) out="$2"; shift 2 ;;
    -w) fmt="$2"; shift 2 ;;
    -X) method="$2"; shift 2 ;;
    -d) data="$2"; shift 2 ;;
    -H) shift 2 ;;
    -*) shift ;;
    *) url="$1"; shift ;;
  esac
done
echo "$method $url $data" >> "$FAKE_LOG"
case "$method $url" in
  "GET "*/git/ref/heads/main) echo '{"object":{"sha":"main111"}}' ;;
  "GET "*/pulls/7) echo '{"head":{"sha":"head222"}}' ;;
  "GET "*/git/ref/heads/*) [ -n "$FAKE_BRANCH_EXISTS" ] || exit 22; echo '{}' ;;
  "POST "*/merges)
    [ "$FAKE_MERGE_STATUS" = 201 ] && echo '{"sha":"merge333"}' > "$out"
    [ "$FAKE_MERGE_STATUS" = 409 ] && echo '{"message":"Merge conflict"}' > "$out"
    [ "$FAKE_MERGE_STATUS" = 204 ] && : > "$out"
    printf "$FAKE_MERGE_STATUS" ;;
  *) echo '{}' ;;
esac
"""


def action_script() -> str:
    text = ACTION.read_text(encoding="utf-8")
    match = re.search(r"(?m)^      run: \|\n((?:        .*\n|\n)+)", text)
    assert match, "no run script in the action"
    return "\n".join(line[8:] for line in match.group(1).splitlines())


class PrMergeActionTest(unittest.TestCase):
    def run_action(self, merge_status: str, *, branch_exists: bool = False) -> tuple[subprocess.CompletedProcess[str], dict[str, str], list[str]]:
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            curl = bin_dir / "curl"
            curl.write_text(FAKE_CURL, encoding="utf-8")
            curl.chmod(0o755)
            output = Path(tmp) / "output"
            log = Path(tmp) / "log"
            env = {
                **os.environ,
                "PATH": f"{bin_dir}:{os.environ['PATH']}",
                "GH_TOKEN": "token",
                "BRANCH": "pr-smoke/pr-7",
                "PR_NUMBER": "7",
                "GITHUB_API_URL": "https://api.example",
                "GITHUB_REPOSITORY": "owner/repo",
                "GITHUB_OUTPUT": str(output),
                "RUNNER_TEMP": tmp,
                "FAKE_LOG": str(log),
                "FAKE_MERGE_STATUS": merge_status,
                "FAKE_BRANCH_EXISTS": "1" if branch_exists else "",
            }
            result = subprocess.run(["bash", "-c", action_script()], env=env, capture_output=True, text=True)
            outputs = dict(
                line.split("=", 1) for line in (output.read_text().splitlines() if output.exists() else []) if "=" in line
            )
            calls = log.read_text().splitlines() if log.exists() else []
            return result, outputs, calls

    def test_resets_the_branch_to_current_main_then_merges_the_pr_head_into_it(self) -> None:
        result, outputs, calls = self.run_action("201")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs, {"mergeable": "true", "sha": "merge333", "main": "main111"})
        create = next(c for c in calls if c.startswith("POST https://api.example/repos/owner/repo/git/refs "))
        self.assertIn('"ref":"refs/heads/pr-smoke/pr-7"', create)
        self.assertIn('"sha":"main111"', create)
        merge = next(c for c in calls if "/merges" in c)
        self.assertIn('"base":"pr-smoke/pr-7"', merge)
        self.assertIn('"head":"head222"', merge)
        self.assertLess(calls.index(create), calls.index(merge))

    def test_a_branch_left_from_an_earlier_run_is_forced_back_to_main(self) -> None:
        result, _, calls = self.run_action("201", branch_exists=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        reset = [c for c in calls if c.startswith("PATCH https://api.example/repos/owner/repo/git/refs/heads/pr-smoke/pr-7 ")]
        self.assertEqual(len(reset), 1)
        self.assertIn('"sha":"main111"', reset[0])
        self.assertIn('"force":true', reset[0])

    def test_a_conflict_is_not_mergeable_and_says_rebase(self) -> None:
        result, outputs, _ = self.run_action("409")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs["mergeable"], "false")
        self.assertIn("rebase", outputs["reason"])
        self.assertNotIn("sha", outputs)

    def test_a_pr_main_already_contains_is_not_mergeable(self) -> None:
        _, outputs, _ = self.run_action("204")
        self.assertEqual(outputs["mergeable"], "false")
        self.assertIn("already contains", outputs["reason"])

    def test_any_other_answer_fails_the_step(self) -> None:
        result, _, _ = self.run_action("500")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("HTTP 500", result.stdout + result.stderr)

    def test_uses_curl_not_gh_because_the_runner_image_has_no_gh(self) -> None:
        self.assertNotRegex(action_script(), r"(?m)^\s*gh |\bgh api\b")


if __name__ == "__main__":
    unittest.main()
