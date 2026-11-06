import importlib.util
import pathlib
import unittest
from unittest.mock import patch

path = pathlib.Path(__file__).resolve().parents[1] / "lifecycle.py"
spec = importlib.util.spec_from_file_location("runner_lifecycle", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LifecycleTests(unittest.TestCase):
    def test_cleanup_after_guest_failure(self):
        calls = []
        def fake_ssh(host, cmd, *, input=None):
            calls.append((host, cmd))
            if host == "guest":
                raise RuntimeError("job failed")
        with patch.object(module, "ssh", side_effect=fake_ssh):
            with self.assertRaises(RuntimeError):
                module.lifecycle("pve", 900, 901, "dev-runner-901", "guest", "redacted")
        self.assertEqual([c[1].split()[1] for c in calls if c[0] == "pve"], ["clone", "start", "stop", "destroy"])

    def test_no_delete_if_clone_failed(self):
        calls = []
        def fake_ssh(host, cmd, *, input=None):
            calls.append(cmd)
            raise RuntimeError("clone failed")
        with patch.object(module, "ssh", side_effect=fake_ssh):
            with self.assertRaises(RuntimeError):
                module.lifecycle("pve", 900, 901, "dev-runner-901", "guest", "redacted")
        self.assertEqual(len(calls), 1)

    def test_invalid_name_rejected(self):
        with self.assertRaises(ValueError):
            module.lifecycle("pve", 900, 901, "bad; rm -rf /", "guest", "redacted")


if __name__ == "__main__":
    unittest.main()
