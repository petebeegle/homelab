from __future__ import annotations

import importlib.util
import io
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "dev_heartbeat.py"
NOW = datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc)


def load():
    assert MODULE_PATH.exists(), f"missing: {MODULE_PATH}"
    spec = importlib.util.spec_from_file_location("dev_heartbeat", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(updated: list[timedelta], *, max_age: int = 7200) -> tuple[int, str]:
    heartbeat = load()
    payload = {"workflow_runs": [{"conclusion": "success", "updated_at": (NOW - age).strftime("%Y-%m-%dT%H:%M:%SZ")} for age in updated]}
    out, err = io.StringIO(), io.StringIO()
    code = heartbeat.main(["--max-age-seconds", str(max_age)], stdin=io.StringIO(json.dumps(payload)), stdout=out, stderr=err, now=NOW)
    return code, out.getvalue() + err.getvalue()


class DevHeartbeatTest(unittest.TestCase):
    def test_a_recent_success_is_healthy(self) -> None:
        code, text = run([timedelta(minutes=20)])
        self.assertEqual(0, code, text)

    def test_a_success_older_than_the_limit_fails_and_says_how_old(self) -> None:
        code, text = run([timedelta(hours=3, minutes=5)])
        self.assertEqual(1, code)
        self.assertIn("3h05m", text)
        self.assertIn("dev-cleanup", text)

    def test_exactly_at_the_limit_is_still_healthy(self) -> None:
        code, text = run([timedelta(seconds=7200)])
        self.assertEqual(0, code, text)

    def test_one_second_past_the_limit_fails(self) -> None:
        code, _ = run([timedelta(seconds=7201)])
        self.assertEqual(1, code)

    def test_no_successful_run_at_all_fails(self) -> None:
        code, text = run([])
        self.assertEqual(1, code)
        self.assertIn("no successful", text)

    def test_the_newest_run_counts_whatever_the_list_order(self) -> None:
        code, text = run([timedelta(hours=9), timedelta(minutes=10), timedelta(hours=5)])
        self.assertEqual(0, code, text)

    def test_a_recent_failed_run_does_not_count_as_a_success(self) -> None:
        heartbeat = load()
        err = io.StringIO()
        payload = json.dumps(
            {
                "workflow_runs": [
                    {"conclusion": "failure", "updated_at": (NOW - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")},
                    {"conclusion": "success", "updated_at": (NOW - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ")},
                ]
            }
        )
        code = heartbeat.main(["--max-age-seconds", "7200"], stdin=io.StringIO(payload), stdout=io.StringIO(), stderr=err, now=NOW)
        self.assertEqual(1, code)
        self.assertIn("6h00m", err.getvalue())

    def test_unreadable_input_fails_rather_than_passing(self) -> None:
        heartbeat = load()
        err = io.StringIO()
        code = heartbeat.main(["--max-age-seconds", "7200"], stdin=io.StringIO("not json"), stdout=io.StringIO(), stderr=err, now=NOW)
        self.assertEqual(1, code)
        self.assertIn("could not read", err.getvalue())

    def test_a_run_missing_its_timestamp_fails_rather_than_passing(self) -> None:
        heartbeat = load()
        err = io.StringIO()
        payload = json.dumps({"workflow_runs": [{"conclusion": "success"}]})
        code = heartbeat.main(["--max-age-seconds", "7200"], stdin=io.StringIO(payload), stdout=io.StringIO(), stderr=err, now=NOW)
        self.assertEqual(1, code)


if __name__ == "__main__":
    unittest.main()
