import importlib.util
import pathlib
import subprocess
import unittest
from unittest.mock import Mock

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "verify.py"
spec = importlib.util.spec_from_file_location("verification_contract", SCRIPT)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class VerificationContractTests(unittest.TestCase):
    def test_passes_when_all_checks_pass(self):
        runner = Mock(return_value=subprocess.CompletedProcess([], 0))
        self.assertEqual(verify.run_commands([("check-a",), ("check-b",)], runner=runner), 0)
        self.assertEqual(runner.call_count, 2)

    def test_fails_closed_and_stops_on_failure(self):
        runner = Mock(return_value=subprocess.CompletedProcess([], 9))
        self.assertEqual(verify.run_commands([("check-a",), ("check-b",)], runner=runner), 9)
        self.assertEqual(runner.call_count, 1)

    def test_missing_command_fails_closed(self):
        runner = Mock(side_effect=FileNotFoundError("missing"))
        self.assertEqual(verify.run_commands([("missing",)], runner=runner), 127)

    def test_harness_profile_gates_dev_verifier_tests_and_drops_removed_runner(self):
        flat = [" ".join(command) for command in verify.PROFILES["harness"]]
        self.assertTrue(any("-s tools/development/tests -p test_verify_branch_deploy.py" in c for c in flat))
        self.assertFalse(any("tools/development/runner" in c for c in flat))


if __name__ == "__main__":
    unittest.main()
