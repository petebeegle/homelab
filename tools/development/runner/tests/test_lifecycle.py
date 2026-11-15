import importlib.util
import pathlib
import re
import signal
import subprocess
import unittest
from unittest.mock import patch

path = pathlib.Path(__file__).resolve().parents[1] / "lifecycle.py"
spec = importlib.util.spec_from_file_location("runner_lifecycle", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

TOKEN = "REGTOKEN-should-never-appear-in-argv"


def fail(cmd="x"):
    return subprocess.CalledProcessError(255, ["ssh", cmd])


class FakeProxmox:
    """Tiny stateful stand-in for `qm` on the Proxmox host and a guest."""

    def __init__(self, *, existing=None, fail_on=None, guest_error=None, guest_ready_after=0):
        self.vms = dict(existing or {})  # vmid -> config text
        self.fail_on = fail_on or {}  # verb -> exception
        self.guest_error = guest_error
        self.guest_ready_after = guest_ready_after
        self.calls = []  # (host, command)
        self.stdin = []

    def ssh(self, host, command, *, input=None, timeout=0, capture=False):
        self.calls.append((host, command))
        if input is not None:
            self.stdin.append(input)
        if host == "guest":
            if command == "true":
                if self.guest_ready_after > 0:
                    self.guest_ready_after -= 1
                    raise fail(command)
                return ""
            if self.guest_error:
                raise self.guest_error
            return ""
        parts = command.split()
        verb, vmid = parts[1], int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
        if verb in self.fail_on:
            raise self.fail_on[verb]
        if verb == "status":
            if vmid not in self.vms:
                raise fail(command)
            return "status: running"
        if verb == "clone":
            name = parts[parts.index("--name") + 1]
            desc = parts[parts.index("--description") + 1]
            self.vms[int(parts[3])] = f"name: {name}\ndescription: {desc}\n"
            return ""
        if verb == "config":
            if vmid not in self.vms:
                raise fail(command)
            return self.vms[vmid] if capture else ""
        if verb == "destroy":
            self.vms.pop(vmid, None)
            return ""
        return ""

    def verbs(self):
        return [c.split()[1] for h, c in self.calls if h == "pve" and c.startswith("qm ")]


class LifecycleTests(unittest.TestCase):
    def run_lifecycle(self, fake, **kwargs):
        with patch.object(module, "ssh", side_effect=fake.ssh), \
             patch.object(module, "delete_registration", return_value=True) as deleter, \
             patch.object(module.time, "sleep"):
            try:
                module.lifecycle("pve", 900, 901, "dev-runner-901", "guest", TOKEN, github_token="adm", **kwargs)
                error = None
            except BaseException as exc:  # noqa: BLE001
                error = exc
        return error, deleter

    def test_happy_path_destroys_vm_and_registration(self):
        fake = FakeProxmox()
        error, deleter = self.run_lifecycle(fake)
        self.assertIsNone(error)
        self.assertNotIn(901, fake.vms)
        deleter.assert_called_once()
        self.assertTrue(deleter.call_args[0][1].startswith("dev-runner-901-"))

    def test_cleanup_after_guest_failure_and_primary_error_kept(self):
        fake = FakeProxmox(guest_error=RuntimeError("job failed"))
        error, _ = self.run_lifecycle(fake)
        self.assertIsInstance(error, RuntimeError)
        self.assertEqual(str(error), "job failed")
        self.assertNotIn(901, fake.vms)
        self.assertEqual(fake.verbs()[-2:], ["stop", "destroy"])

    def test_refuses_existing_vmid_and_never_destroys_it(self):
        fake = FakeProxmox(existing={901: "name: someone-elses-vm\n"})
        error, deleter = self.run_lifecycle(fake)
        self.assertIsInstance(error, RuntimeError)
        self.assertIn(901, fake.vms)
        self.assertNotIn("clone", fake.verbs())
        self.assertNotIn("destroy", fake.verbs())
        deleter.assert_not_called()

    def test_partial_clone_is_cleaned_when_it_carries_our_marker(self):
        class Fake(FakeProxmox):
            def ssh(self, host, command, **kw):
                if host == "pve" and command.startswith("qm clone"):
                    super().ssh(host, command, **kw)  # VM now exists...
                    raise fail(command)  # ...but clone reports failure
                return super().ssh(host, command, **kw)
        fake = Fake()
        error, _ = self.run_lifecycle(fake)
        self.assertIsInstance(error, subprocess.CalledProcessError)
        self.assertNotIn(901, fake.vms)

    def test_clone_failure_with_nothing_created_destroys_nothing(self):
        fake = FakeProxmox(fail_on={"clone": fail("clone")})
        error, _ = self.run_lifecycle(fake)
        self.assertIsInstance(error, subprocess.CalledProcessError)
        self.assertNotIn("destroy", fake.verbs())

    def test_refuses_to_destroy_vm_without_our_marker(self):
        class Fake(FakeProxmox):
            def ssh(self, host, command, **kw):
                out = super().ssh(host, command, **kw)
                if host == "pve" and command.startswith("qm start"):
                    self.vms[901] = "name: dev-runner-901\ndescription: other\n"  # replaced under us
                return out
        fake = Fake(guest_error=RuntimeError("job failed"))
        with patch("sys.stderr"):
            error, _ = self.run_lifecycle(fake)
        self.assertEqual(str(error), "job failed")
        self.assertIn(901, fake.vms)
        self.assertNotIn("destroy", fake.verbs())

    def test_stop_failure_does_not_block_destroy_or_mask_job_error(self):
        fake = FakeProxmox(fail_on={"stop": fail("stop")}, guest_error=RuntimeError("job failed"))
        with patch("sys.stderr"):
            error, _ = self.run_lifecycle(fake)
        self.assertEqual(str(error), "job failed")
        self.assertIn("destroy", fake.verbs())
        self.assertNotIn(901, fake.vms)

    def test_destroy_failure_is_reported_when_job_succeeded(self):
        fake = FakeProxmox(fail_on={"destroy": fail("destroy")})
        with patch("sys.stderr"):
            error, _ = self.run_lifecycle(fake)
        self.assertIsInstance(error, RuntimeError)
        self.assertIn("leaked", str(error))

    def test_deadline_expiry_raises_and_still_tears_down(self):
        fake = FakeProxmox(guest_ready_after=10**6)
        times = iter([0.0] + [10_000.0] * 500)  # clock jumps far past the deadline
        with patch.object(module.time, "monotonic", side_effect=lambda: next(times)):
            error, _ = self.run_lifecycle(fake, deadline_seconds=600)
        self.assertIsInstance(error, TimeoutError)
        self.assertNotIn(901, fake.vms)

    def test_token_only_on_stdin_never_in_any_command(self):
        fake = FakeProxmox()
        self.run_lifecycle(fake)
        self.assertTrue(any(TOKEN in s for s in fake.stdin))
        self.assertFalse(any(TOKEN in cmd for _, cmd in fake.calls))

    def test_sigterm_handler_unwinds_so_finally_runs(self):
        with self.assertRaises(SystemExit) as cm:
            module._terminate(signal.SIGTERM, None)
        self.assertEqual(cm.exception.code, 128 + signal.SIGTERM)

    def test_invalid_inputs_rejected(self):
        for kwargs in (
            dict(name="bad; rm -rf /"),
            dict(guest="-oProxyCommand=evil"),
            dict(host="pve host"),
        ):
            args = dict(host="pve", template=900, vmid=901, name="dev-runner-901", guest="guest")
            args.update(kwargs)
            with self.assertRaises(ValueError):
                module.lifecycle(args["host"], args["template"], args["vmid"], args["name"], args["guest"], TOKEN)
        with self.assertRaises(ValueError):
            module.lifecycle("pve", 900, 900, "dev-runner-900", "guest", TOKEN)

    def test_ssh_uses_option_terminator_and_timeouts(self):
        with patch.object(module.subprocess, "run") as run:
            module.ssh("pve", "true", timeout=5)
        argv = run.call_args[0][0]
        self.assertEqual(argv[argv.index("--") + 1], "pve")
        self.assertIn("ConnectTimeout=10", argv)

    def test_github_errors_do_not_leak_bodies(self):
        import io, urllib.error
        err = urllib.error.HTTPError("u", 401, "bad", {}, io.BytesIO(b"secret-echo"))
        with patch.object(module.urllib.request, "urlopen", side_effect=err):
            with self.assertRaises(RuntimeError) as cm:
                module.registration_token("adm")
        self.assertIn("401", str(cm.exception))
        self.assertNotIn("secret-echo", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
