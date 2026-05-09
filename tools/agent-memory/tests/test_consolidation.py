from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent_memory.consolidation import consolidate_candidates
from agent_memory.models import MemoryCandidate


def reviewed_candidate(text: str = "Use local JSONL storage for memory.") -> MemoryCandidate:
    return MemoryCandidate(text=text, source="unit-test", reviewed=True)


class ConsolidationTests(unittest.TestCase):
    def test_consolidation_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = consolidate_candidates([reviewed_candidate()], root=root, dry_run=True)

            self.assertEqual(plan.to_record()["promoted_count"], 1)
            self.assertFalse((root / "approved" / "memory.jsonl").exists())

    def test_consolidation_apply_reviewed_writes_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = reviewed_candidate()
            plan = consolidate_candidates([candidate], root=root, dry_run=False)

            memory_path = root / "approved" / "memory.jsonl"
            records = [json.loads(line) for line in memory_path.read_text(encoding="utf-8").splitlines()]

            self.assertEqual(plan.to_record()["candidate_ids"], [candidate.candidate_id])
            self.assertEqual(records[0]["candidate_id"], candidate.candidate_id)
            self.assertTrue(records[0]["consolidated_at"])
