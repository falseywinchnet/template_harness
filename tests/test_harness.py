from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from harness.parser import PlanParseError, parse_plan_text
from harness.reports import recovery_brief
from harness.store import HarnessError, Store, atomic_json


class HarnessTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        state = self.root / ".harness"
        state.mkdir()
        atomic_json(
            state / "config.json",
            {
                "schema_version": 1,
                "stages": ["hypothesis", "analysis", "publication"],
                "checks": [],
            },
        )
        atomic_json(
            state / "register.json",
            {
                "schema_version": 1,
                "project": {"title": "Test", "status": "active"},
                "next_item": 1,
                "next_round": 1,
                "active_round": None,
                "items": {},
                "rounds": {},
            },
        )
        (state / "events.jsonl").write_text("", encoding="utf-8")
        self.store = Store(self.root)

    def tearDown(self):
        self.temporary.cleanup()

    def register(self, text: str) -> None:
        self.store.register_items(parse_plan_text(text), "test plan")

    def test_parser_accepts_compact_task(self):
        item = parse_plan_text(
            "- [ ] P007 | Prove edge | stage=analysis | mode=advance | "
            "tags=core,edge | depends=P001 | accept=All endpoints"
        )[0]
        self.assertEqual(item.ident, "P007")
        self.assertEqual(item.tags, ("core", "edge"))
        self.assertEqual(item.depends, ("P001",))
        self.assertEqual(item.acceptance, "All endpoints")

    def test_parser_rejects_non_task_text(self):
        with self.assertRaises(PlanParseError):
            parse_plan_text("A natural-language paragraph.")

    def test_registration_allocates_and_preserves_runtime_status(self):
        self.register("- [ ] First | stage=hypothesis | mode=advance")
        self.assertIn("P001", self.store.items)
        self.store.transition(["P001"], "done")
        self.store.register_items(
            parse_plan_text("- [ ] P001 | Better title | stage=hypothesis | mode=advance"),
            "revised",
        )
        self.assertEqual(self.store.items["P001"]["title"], "Better title")
        self.assertEqual(self.store.items["P001"]["status"], "done")

    def test_missing_dependency_is_rejected_without_replacing_file(self):
        before = (self.root / ".harness" / "register.json").read_text(encoding="utf-8")
        with self.assertRaises(HarnessError):
            self.register(
                "- [ ] P001 | Broken | stage=hypothesis | mode=advance | depends=P999"
            )
        after = (self.root / ".harness" / "register.json").read_text(encoding="utf-8")
        self.assertEqual(before, after)

    def test_dependency_cycle_is_rejected(self):
        with self.assertRaises(HarnessError):
            self.register(
                "\n".join(
                    [
                        "- [ ] P001 | One | stage=analysis | mode=either | depends=P002",
                        "- [ ] P002 | Two | stage=analysis | mode=either | depends=P001",
                    ]
                )
            )

    def test_mode_and_tag_selection_respects_dependencies(self):
        self.register(
            "\n".join(
                [
                    "- [ ] P001 | First | stage=hypothesis | mode=advance | tags=core",
                    "- [ ] P002 | Audit | stage=analysis | mode=refine | tags=core | depends=P001",
                ]
            )
        )
        self.assertEqual(self.store.ready("advance", {"core"}), ["P001"])
        self.assertEqual(self.store.ready("refine", {"core"}), [])
        self.store.transition(["P001"], "done")
        self.assertEqual(self.store.ready("refine", {"core"}), ["P002"])

    def test_round_lock_is_exclusive_and_recoverable(self):
        self.register("- [ ] P001 | First | stage=hypothesis | mode=advance | tags=core")
        record = self.store.start_round("advance", ["core"])
        self.assertEqual(record["round_id"], "R0001")
        self.assertEqual(self.store.items["P001"]["status"], "active")
        with self.assertRaises(HarnessError):
            self.store.start_round("advance", ["core"])
        brief = recovery_brief(self.store)
        self.assertIn("R0001", brief)
        self.assertIn("P001", brief)

    def test_resume_repairs_provisional_lock(self):
        self.register("- [ ] P001 | First | stage=hypothesis | mode=advance")
        provisional = {
            "schema_version": 1,
            "round_id": "R0001",
            "mode": "advance",
            "tags": [],
            "items": ["P001"],
            "status": "open",
            "started_at": "2026-01-01T00:00:00+00:00",
            "workdir": "work/R0001-advance-hypothesis",
            "phase": "provisional",
        }
        self.store.acquire_lock(provisional)
        record = self.store.resume_round()
        self.assertEqual(record["resume_count"], 1)
        self.assertTrue((self.root / record["workdir"] / "ROUND.md").is_file())
        self.assertEqual(self.store.register["active_round"], "R0001")

    def test_resume_finalizes_close_interrupted_before_lock_release(self):
        self.register("- [ ] P001 | First | stage=hypothesis | mode=advance")
        record = self.store.start_round("advance", [])
        record["status"] = "closed"
        record["closed_at"] = "2026-01-01T00:05:00+00:00"
        record["summary"] = "Close was committed before interruption"
        self.store.items["P001"]["status"] = "done"
        self.store.items["P001"]["active_round"] = None
        self.store.register["active_round"] = None
        self.store.save()
        recovered = self.store.resume_round()
        self.assertEqual(recovered["recovery_action"], "finalized_close")
        self.assertFalse(self.store.lock_path.exists())
        results = (self.root / record["workdir"] / "RESULTS.md").read_text(encoding="utf-8")
        self.assertIn("Close was committed before interruption", results)

    def test_note_and_close_leave_durable_round(self):
        self.register("- [ ] P001 | First | stage=hypothesis | mode=advance")
        record = self.store.start_round("advance", [])
        self.store.note("Found the invariant", "Write the exact lemma", item="P001")
        closed = self.store.close_round("Invariant recorded", ["P001"])
        self.assertEqual(closed["status"], "closed")
        self.assertEqual(self.store.items["P001"]["status"], "done")
        self.assertFalse(self.store.lock_path.exists())
        notes = (self.root / record["workdir"] / "NOTES.md").read_text(encoding="utf-8")
        self.assertIn("Found the invariant", notes)

    def test_item_cannot_complete_before_dependency(self):
        self.register(
            "\n".join(
                [
                    "- [ ] P001 | First | stage=hypothesis | mode=advance",
                    "- [ ] P002 | Second | stage=analysis | mode=advance | depends=P001",
                ]
            )
        )
        with self.assertRaises(HarnessError):
            self.store.transition(["P002"], "done")

    def test_dropped_optional_dependency_is_settled(self):
        self.register(
            "\n".join(
                [
                    "- [ ] P001 | Optional formalization | stage=analysis | mode=either",
                    "- [ ] P002 | Audit | stage=publication | mode=refine | depends=P001",
                ]
            )
        )
        self.store.transition(["P001"], "dropped", "Not justified by project risk")
        self.assertEqual(self.store.ready("refine"), ["P002"])
        self.store.transition(["P002"], "done")
        self.assertEqual(self.store.items["P002"]["status"], "done")

    def test_register_digest_is_stable_for_unchanged_state(self):
        first = self.store.digest()
        second = Store(self.root).digest()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
