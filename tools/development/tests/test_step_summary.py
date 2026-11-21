"""Smoke runs write what they checked and how it went to the GitHub job summary."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DEVELOPMENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DEVELOPMENT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import base_smoke  # noqa: E402
import devverify as verify  # noqa: E402
from devverify.summary import step_summary_path  # noqa: E402
from test_base_smoke import FakeCluster, config as base_config  # noqa: E402
from test_verify_branch_deploy import TEMPLATE, FakeRunner  # noqa: E402


def app_config(app: str = "whoami") -> verify.AppConfig:
    return verify.AppConfig(
        app=app, branch="codex/example-change", slug="example-change", kubeconfig=Path("/tmp/kubeconfig"),
        timeout=verify.parse_duration("2m"), push=False, terraform_apply=False, include_cluster_base=False,
        keep=False, ci=True,
    )


class VerifySummaryTest(unittest.TestCase):
    def acceptance(self, app: str, runner: FakeRunner) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.md"
            summary.write_text("earlier step\n", encoding="utf-8")
            try:
                verify.run_acceptance(app_config(app), runner=runner, repo_root=Path(tmp), template_text=TEMPLATE,
                                      step_summary=summary)
            except verify.VerificationError:
                pass
            return summary.read_text(encoding="utf-8")

    def test_a_pass_lists_the_app_branch_and_every_check(self) -> None:
        text = self.acceptance("homepage", FakeRunner())
        self.assertTrue(text.startswith("earlier step\n"), "appends, never truncates other steps' summaries")
        self.assertIn("homepage", text)
        self.assertIn("codex/example-change", text)
        self.assertIn("passed", text)
        self.assertIn("All pods in `homepage-example-change` Ready", text)
        self.assertIn("HTTPRoute `homepage-example-change` accepted", text)
        self.assertIn("/api/services", text)
        self.assertIn("Single sign-on", text, "the text the probe matched")
        self.assertNotIn("failed", text.lower())

    def test_a_failure_names_the_stage_and_the_error_and_marks_the_rest_not_reached(self) -> None:
        text = self.acceptance("whoami", FakeRunner(fail_on="wait pod/whoami-example-change-7d9c4"))
        self.assertIn("FAILED", text)
        self.assertRegex(text, r"App checks \| failed \| .*wait pod/whoami-example-change-7d9c4")
        self.assertRegex(text, r"Cleanup \| passed")

    def test_a_failed_probe_names_its_url_and_the_text_it_wanted(self) -> None:
        text = self.acceptance("homepage", FakeRunner(fail_on="p1-example-change"))
        row = next(line for line in text.splitlines() if line.startswith("| App checks"))
        self.assertIn("http://homepage-example-change:80/api/services", row)
        self.assertIn("Single sign-on", row)
        self.assertNotIn("--overrides", row)

    def test_nothing_is_written_without_a_summary_file(self) -> None:
        self.assertIsNone(step_summary_path({}))
        self.assertIsNone(step_summary_path({"GITHUB_STEP_SUMMARY": ""}))
        self.assertEqual(step_summary_path({"GITHUB_STEP_SUMMARY": "/x/s.md"}), Path("/x/s.md"))


class BaseSmokeSummaryTest(unittest.TestCase):
    def run_smoke(self, cluster: FakeCluster) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.md"
            cfg = base_config(Path(tmp))
            cfg = base_smoke.Config(**{**cfg.__dict__, "step_summary": summary})
            base_smoke.run(cfg, runner=cluster, sleep=lambda _s: None, clock=iter(range(0, 10_000, 5)).__next__)
            return summary.read_text(encoding="utf-8")

    def test_a_pass_shows_each_phase_and_that_development_was_restored(self) -> None:
        text = self.run_smoke(FakeCluster())
        self.assertIn("PR #7", text)
        self.assertIn(base_smoke_sha_prefix(), text)
        for phase in ("Development healthy before", "Apply the PR", "PR settled", "Canary whoami", "Restore main"):
            self.assertRegex(text, rf"{phase}[^|]*\| passed", phase)
        self.assertIn("passed", text.splitlines()[0].lower() + text)

    def test_a_failed_canary_is_named(self) -> None:
        text = self.run_smoke(FakeCluster(canary_ok=False))
        self.assertRegex(text, r"Canary whoami[^|]*\| failed")
        self.assertRegex(text, r"Restore main[^|]*\| passed")

    def test_a_development_that_did_not_recover_says_so(self) -> None:
        text = self.run_smoke(FakeCluster(recovers=False))
        self.assertIn("DEVELOPMENT DID NOT RECOVER", text)
        self.assertRegex(text, r"Restore main[^|]*\| failed")


def base_smoke_sha_prefix() -> str:
    from test_base_smoke import SHA
    return SHA[:12]


if __name__ == "__main__":
    unittest.main()
