import importlib.util
import pathlib
import subprocess
import tempfile
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
        self.assertTrue(any("-p test_classify_pr.py" in c for c in flat))
        self.assertTrue(any("-p test_cleanup_pr_envs.py" in c for c in flat))
        self.assertTrue(any("-p test_runner_image.py" in c for c in flat))
        self.assertTrue(any("-p test_dev_smoke_workflow.py" in c for c in flat))
        self.assertTrue(any("-p test_branch_overlay_render.py" in c for c in flat))
        self.assertTrue(any("-p test_dev_heartbeat.py" in c for c in flat))
        self.assertTrue(any("-p test_dev_heartbeat_workflows.py" in c for c in flat))
        self.assertFalse(any("tools/development/runner" in c for c in flat))

    def test_every_test_file_is_gated_or_excluded_with_a_reason(self):
        """A test nobody runs is not a test. New test files must be picked up without editing verify.py."""
        flat = [" ".join(command) for command in verify.PROFILES["harness"]]
        python_tests = sorted(p for p in verify.ROOT.glob("tools/**/test_*.py") if "__pycache__" not in p.parts)
        self.assertGreater(len(python_tests), 20)
        for path in python_tests:
            relative = path.relative_to(verify.ROOT).as_posix()
            gated = any(f"-s {path.parent.relative_to(verify.ROOT).as_posix()} -p {path.name}" in c for c in flat)
            self.assertTrue(gated or verify.EXCLUDED.get(relative), f"{relative} is neither run by the harness nor excluded with a reason")
            self.assertFalse(gated and relative in verify.EXCLUDED, f"{relative} is both run and excluded")
        for relative in verify.node_test_files(verify.ROOT):
            gated = any(c == f"node --test {relative}" for c in flat)
            self.assertTrue(gated or verify.EXCLUDED.get(relative), f"{relative} is neither run by the harness nor excluded with a reason")

    def test_exclusions_point_at_real_files_and_say_why(self):
        for relative, reason in verify.EXCLUDED.items():
            self.assertTrue((verify.ROOT / relative).is_file(), f"stale exclusion: {relative}")
            self.assertGreater(len(reason), 20, f"exclusion for {relative} needs a real reason")

    def test_a_new_test_file_is_picked_up_without_editing_the_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "tools" / "newthing" / "tests").mkdir(parents=True)
            (root / "tools" / "newthing" / "tests" / "test_new.py").write_text("")
            (root / "kubernetes" / "apps" / "x").mkdir(parents=True)
            (root / "kubernetes" / "apps" / "x" / "thing.test.js").write_text("")
            (root / "node_modules" / "dep").mkdir(parents=True)
            (root / "node_modules" / "dep" / "dep.test.js").write_text("")
            flat = [" ".join(command) for command in verify.harness_commands(root)]
        self.assertTrue(any("-s tools/newthing/tests -p test_new.py" in c for c in flat))
        self.assertIn("node --test kubernetes/apps/x/thing.test.js", flat)
        self.assertFalse(any("node_modules" in c for c in flat))


if __name__ == "__main__":
    unittest.main()
