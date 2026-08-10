from __future__ import annotations

import base64
import contextlib
import importlib.util
import io
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools/onepassword/validate_secret_parity.py"


class ValidateSecretParityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("validate_secret_parity", MODULE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load parity validator")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    @staticmethod
    def secret(values: dict[str, bytes], secret_type: str = "Opaque") -> dict:
        return {
            "type": secret_type,
            "data": {
                key: base64.b64encode(value).decode("ascii")
                for key, value in values.items()
            },
        }

    def test_exact_type_keys_and_bytes_pass(self) -> None:
        legacy = self.secret({"password": b"same\nbytes"})
        generated = self.secret({"password": b"same\nbytes"})
        self.module.compare_pair(legacy, generated, {"password"}, "Opaque")

    def test_byte_mismatch_names_neither_key_nor_values(self) -> None:
        legacy_value = "legacy-secret-sentinel"
        generated_value = "generated-secret-sentinel"
        with self.assertRaisesRegex(ValueError, "byte mismatch") as raised:
            self.module.compare_pair(
                self.secret({"sensitive-key-name": legacy_value.encode()}),
                self.secret({"sensitive-key-name": generated_value.encode()}),
                {"sensitive-key-name"},
                "Opaque",
            )
        message = str(raised.exception)
        self.assertNotIn("sensitive-key-name", message)
        self.assertNotIn(legacy_value, message)
        self.assertNotIn(generated_value, message)

    def test_key_set_mismatch_reports_count_only(self) -> None:
        with self.assertRaisesRegex(ValueError, "key set mismatch") as raised:
            self.module.compare_pair(
                self.secret({"legacy-key": b"value"}),
                self.secret({"generated-key": b"value"}),
                {"legacy-key"},
                "Opaque",
            )
        self.assertNotIn("legacy-key", str(raised.exception))
        self.assertNotIn("generated-key", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
