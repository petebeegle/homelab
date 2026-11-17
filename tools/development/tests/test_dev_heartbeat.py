from __future__ import annotations

import importlib.util
import io
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "dev_heartbeat.py"
NOW = datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc)
LIMIT = 12 * 3600


def load():
    assert MODULE_PATH.exists(), f"missing: {MODULE_PATH}"
    spec = importlib.util.spec_from_file_location("dev_heartbeat", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stamp(age: timedelta) -> str:
    return (NOW - age).strftime("%Y-%m-%dT%H:%M:%SZ")


def job(
    age: timedelta | None,
    *,
    conclusion: str = "success",
    labels: tuple[str, ...] = ("homelab-dev",),
    workflow: str = "dev-cleanup",
    name: str = "cleanup",
    runner: str | None = "homelab-dev-abc12-runner-xyz",
) -> dict:
    return {
        "workflow_name": workflow,
        "name": name,
        "conclusion": conclusion,
        "labels": list(labels),
        "runner_name": runner,
        "completed_at": stamp(age) if age is not None else None,
    }


def run_raw(text: str, *, max_age: int = LIMIT) -> tuple[int, str]:
    heartbeat = load()
    out, err = io.StringIO(), io.StringIO()
    code = heartbeat.main(
        ["--runner-label", "homelab-dev", "--max-age-seconds", str(max_age)],
        stdin=io.StringIO(text),
        stdout=out,
        stderr=err,
        now=NOW,
    )
    return code, out.getvalue() + err.getvalue()


def run(jobs: list[dict], *, max_age: int = LIMIT) -> tuple[int, str]:
    """The workflow feeds one job object per line (`gh api .../jobs --jq '.jobs[]'`)."""
    return run_raw("".join(json.dumps(j) + "\n" for j in jobs), max_age=max_age)


class DevHeartbeatTest(unittest.TestCase):
    def test_a_recent_dev_cleanup_success_is_healthy(self) -> None:
        code, text = run([job(timedelta(minutes=20))])
        self.assertEqual(0, code, text)
        self.assertIn("dev-cleanup", text)

    def test_a_recent_dev_smoke_success_counts_when_dev_cleanup_is_stale(self) -> None:
        code, text = run(
            [
                job(timedelta(hours=20)),
                job(timedelta(hours=1), workflow="dev-smoke", name="smoke"),
            ]
        )
        self.assertEqual(0, code, text)
        self.assertIn("dev-smoke / smoke", text)

    def test_a_skipped_smoke_job_does_not_count(self) -> None:
        # A PR that is not smoke-tested still lists the smoke job with the homelab-dev
        # label, but it never ran anywhere.
        code, text = run(
            [
                job(timedelta(hours=20)),
                job(timedelta(minutes=5), workflow="dev-smoke", name="smoke", conclusion="skipped", runner=None),
            ]
        )
        self.assertEqual(1, code, text)
        self.assertIn("20h00m", text)

    def test_a_success_on_a_github_hosted_runner_does_not_count(self) -> None:
        code, text = run(
            [
                job(timedelta(hours=20)),
                job(timedelta(minutes=5), workflow="dev-smoke", name="classify", labels=("ubuntu-latest",)),
            ]
        )
        self.assertEqual(1, code, text)

    def test_a_success_older_than_the_limit_fails_and_says_how_old(self) -> None:
        code, text = run([job(timedelta(hours=13, minutes=5))])
        self.assertEqual(1, code)
        self.assertIn("13h05m", text)
        self.assertIn("12h00m", text)
        self.assertIn("homelab-dev", text)

    def test_exactly_at_the_limit_is_still_healthy(self) -> None:
        code, text = run([job(timedelta(seconds=LIMIT))])
        self.assertEqual(0, code, text)

    def test_one_second_past_the_limit_fails(self) -> None:
        code, _ = run([job(timedelta(seconds=LIMIT + 1))])
        self.assertEqual(1, code)

    def test_no_jobs_at_all_fails(self) -> None:
        code, text = run_raw("")
        self.assertEqual(1, code)
        self.assertIn("no successful", text)

    def test_the_newest_success_counts_whatever_the_order(self) -> None:
        code, text = run([job(timedelta(hours=19)), job(timedelta(minutes=10)), job(timedelta(hours=15))])
        self.assertEqual(0, code, text)
        self.assertIn("0h10m", text)

    def test_a_recent_failed_job_does_not_count_as_a_success(self) -> None:
        code, text = run([job(timedelta(minutes=5), conclusion="failure"), job(timedelta(hours=16))])
        self.assertEqual(1, code)
        self.assertIn("16h00m", text)

    def test_unreadable_input_fails_rather_than_passing(self) -> None:
        code, text = run_raw("not json\n")
        self.assertEqual(1, code)
        self.assertIn("could not read", text)

    def test_a_successful_job_missing_its_timestamp_fails_rather_than_passing(self) -> None:
        code, _ = run([job(None)])
        self.assertEqual(1, code)


if __name__ == "__main__":
    unittest.main()
