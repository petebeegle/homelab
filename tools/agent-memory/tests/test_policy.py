from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_memory.consolidation import consolidate_candidates
from agent_memory.extraction import extract_candidates
from agent_memory.models import MemoryCandidate


class PolicyTests(unittest.TestCase):
    def test_secret_candidate_is_rejected(self):
        candidates = extract_candidates("Remember: api_key = supersecretvalue123", source="unit-test")

        self.assertEqual(len(candidates), 1)
        self.assertTrue(candidates[0].rejected)
        self.assertIn("secret", candidates[0].rejection_reason or "")

    def test_unreviewed_candidate_cannot_be_promoted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = MemoryCandidate(text="Keep this only after review.", source="unit-test")

            with self.assertRaisesRegex(ValueError, "not been reviewed"):
                consolidate_candidates([candidate], root=root, dry_run=False)

            self.assertFalse((root / "approved" / "memory.jsonl").exists())
