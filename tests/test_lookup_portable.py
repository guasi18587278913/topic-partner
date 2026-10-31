"""A fresh install must distinguish complete local material from index-only entries."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PortableLookup(unittest.TestCase):
    def run_lookup(self, *args):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/lookup.py"), *args],
                                capture_output=True, text=True, cwd=ROOT)
        return result.returncode, json.loads(result.stdout)

    def test_full_snapshot_can_be_read_without_any_connector(self):
        snapshot = json.loads((ROOT / "references/method-originals.jsonl").read_text().splitlines()[0])
        code, data = self.run_lookup("--read", snapshot["slug"])
        self.assertEqual(code, 0)
        self.assertEqual(data["page"]["compiled_truth"], snapshot["compiled_truth"])

    def test_index_only_entry_does_not_claim_to_supply_full_text(self):
        snapshots = {json.loads(line)["slug"] for line in (ROOT / "references/method-originals.jsonl").read_text().splitlines()}
        index = [json.loads(line) for line in (ROOT / "references/source-index.jsonl").read_text().splitlines()]
        slug = next(row["slug"] for row in index if row["slug"] not in snapshots)
        code, data = self.run_lookup("--read", slug)
        self.assertEqual(code, 3)
        self.assertEqual(data["status"], "not_bundled")
        self.assertNotIn("page", data)
        self.assertIn("optional_wiki", data)

    def test_search_marks_which_results_can_be_read_locally(self):
        snapshots = {json.loads(line)["slug"] for line in (ROOT / "references/method-originals.jsonl").read_text().splitlines()}
        code, data = self.run_lookup("--query", "", "--limit", "100")
        self.assertEqual(code, 0)
        self.assertTrue(data["results"])
        for row in data["results"]:
            self.assertEqual(row["has_local_snapshot"], row["slug"] in snapshots)


if __name__ == "__main__":
    unittest.main()
