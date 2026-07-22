from __future__ import annotations

import io
import json
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from harness.cli import (
    _json_report,
    _project_markdown,
    main as harness_main,
    parser as cli_parser,
)
from harness.context import handoff_status, render_handoff, save_handoff
from harness.mind import render as render_mind
from harness.mind import validate_index
from harness.parser import PlanParseError, parse_plan_text
from harness.reports import full_report, recovery_brief
from harness.runtime import (
    RuntimeBusy,
    RuntimeControlError,
    paths,
    run_guarded,
    runtime_snapshot,
)
from harness.store import HarnessError, Store, atomic_json


POLICY = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/audit_project.py"))
REPO_ROOT = Path(__file__).resolve().parents[1]
PDF_POLICY = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/audit_pdf.py"))
MANUSCRIPT_POLICY = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/audit_manuscript.py")
)


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

    def run_quietly(self, *args, **kwargs):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return run_guarded(*args, **kwargs)

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

    def test_bootstrap_preserves_compute_contract(self):
        fields = {
            "title": "Test",
            "question": "Question",
            "hypothesis": "",
            "falsifier": "Counterexample",
            "deliverable": "Paper",
            "field": "",
            "audience": "",
            "constraints": "",
            "formalization": "",
            "compute": "Exact rationals; 2 GB; resumable.",
            "interior": "A raw admissible witness with strict margin.",
            "containment": "Initialization and preservation are separate.",
            "model_budget": "One bounded round under one dollar.",
            "context_reserve": "Checkpoint with 30 percent remaining.",
        }
        project = _project_markdown(fields)
        self.assertIn("## Computational scale and resources", project)
        self.assertIn(fields["compute"], project)
        self.assertIn(fields["interior"], project)
        self.assertIn(fields["containment"], project)
        self.assertIn(fields["model_budget"], project)
        self.assertIn(fields["context_reserve"], project)
        args = cli_parser().parse_args(
            [
                "bootstrap",
                "--compute",
                "small",
                "--interior",
                "witness",
                "--model-budget",
                "bounded",
                "--context-reserve",
                "30 percent",
            ]
        )
        self.assertEqual(args.compute, "small")
        self.assertEqual(args.interior, "witness")
        self.assertEqual(args.model_budget, "bounded")
        self.assertEqual(args.context_reserve, "30 percent")

    def test_mind_cards_are_bounded_and_have_one_more_tier(self):
        self.assertEqual(validate_index(REPO_ROOT), [])
        hot = render_mind(REPO_ROOT, "sympy")
        warm = render_mind(REPO_ROOT, "python", more=True)
        self.assertIn("MORE ./mind how python more", hot)
        self.assertIn("FULL docs/PYTHON_COMPUTATION.md", warm)
        self.assertNotIn("\n\n", hot)

    def test_sydney_persona_is_exact(self):
        self.assertEqual(POLICY["audit_persona"](REPO_ROOT), [])

    def test_context_handoff_detects_register_change(self):
        self.assertEqual(handoff_status(self.store)[0], "EMPTY")
        save_handoff(
            self.store,
            {
                "state": "C003 reduced to two cases",
                "next": "check the singular endpoint",
                "why": "endpoint decides the target",
                "files": "research/TARGET.md",
                "risks": "orientation unknown",
                "verify": "algebra replay passed",
            },
        )
        self.assertEqual(handoff_status(self.store), ("FRESH", []))
        self.assertIn("NEXT check the singular endpoint", render_handoff(self.store))
        self.register("- [ ] New item | stage=analysis | mode=advance")
        status, reasons = handoff_status(self.store)
        self.assertEqual(status, "STALE")
        self.assertIn("register changed", reasons)

    def test_context_save_also_updates_open_round_checkpoint(self):
        self.register("- [ ] P001 | Analyze | stage=analysis | mode=advance | tags=core")
        self.store.start_round("advance", ["core"])
        with redirect_stdout(io.StringIO()):
            result = harness_main(
                [
                    "context",
                    "save",
                    "--state",
                    "two cases remain",
                    "--next",
                    "check the endpoint",
                    "--why",
                    "endpoint decides C001",
                ],
                root=self.root,
            )
        self.assertEqual(result, 0)
        refreshed = Store(self.root)
        record = refreshed.rounds[refreshed.register["active_round"]]
        self.assertEqual(record["last_note"]["text"], "two cases remain")
        self.assertEqual(record["last_note"]["next"], "check the endpoint")
        round_text = (self.root / record["workdir"] / "ROUND.md").read_text(encoding="utf-8")
        self.assertIn("Model: Sydney, OpenAI Codex", round_text)
        self.assertEqual(handoff_status(refreshed), ("FRESH", []))

    def test_context_handoff_detects_worktree_change(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "harness@example.invalid"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Harness Test"], cwd=self.root, check=True
        )
        subprocess.run(["git", "add", ".harness"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "baseline"], cwd=self.root, check=True
        )
        save_handoff(self.store, {"state": "baseline", "next": "continue"})
        self.assertEqual(handoff_status(self.store), ("FRESH", []))
        (self.root / "result.txt").write_text("new result\n", encoding="utf-8")
        status, reasons = handoff_status(self.store)
        self.assertEqual(status, "STALE")
        self.assertIn("worktree changed", reasons)

    def test_context_hook_blocks_stale_manual_compaction_and_injects_on_resume(self):
        pre = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts/context_hook.py")],
            input=json.dumps({"hook_event_name": "PreCompact", "trigger": "manual"}),
            check=True,
            capture_output=True,
            text=True,
        )
        pre_output = json.loads(pre.stdout)
        self.assertFalse(pre_output["continue"])
        resumed = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts/context_hook.py")],
            input=json.dumps({"hook_event_name": "SessionStart"}),
            check=True,
            capture_output=True,
            text=True,
        )
        resumed_output = json.loads(resumed.stdout)
        self.assertIn("additionalContext", resumed_output["hookSpecificOutput"])

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

    def test_unchanged_registration_is_a_noop(self):
        text = "- [ ] P001 | First | stage=hypothesis | mode=advance"
        parsed = parse_plan_text(text)
        self.store.register_items(parsed, "stable source")
        register_before = (self.root / ".harness" / "register.json").read_bytes()
        events_before = (self.root / ".harness" / "events.jsonl").read_bytes()
        created, updated = self.store.register_items(parsed, "stable source")
        self.assertEqual((created, updated), ([], []))
        self.assertEqual((self.root / ".harness" / "register.json").read_bytes(), register_before)
        self.assertEqual((self.root / ".harness" / "events.jsonl").read_bytes(), events_before)

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

    def test_guarded_run_records_limits_and_success(self):
        code = (
            "import os; "
            "assert os.environ['OMP_NUM_THREADS'] == '1'; "
            "assert os.environ['OPENBLAS_NUM_THREADS'] == '1'; "
            "assert os.getpriority(os.PRIO_PROCESS, 0) >= 10"
        )
        result = self.run_quietly(
            self.root,
            [sys.executable, "-c", code],
            label="unit-success",
            timeout_seconds=2,
        )
        self.assertEqual(result, 0)
        snapshot = runtime_snapshot(self.root)
        self.assertEqual(snapshot["lock_state"], "none")
        self.assertEqual(snapshot["last_run"]["status"], "passed")
        self.assertEqual(snapshot["last_run"]["thread_limits"]["MKL_NUM_THREADS"], "1")

    def test_guarded_timeout_kills_group_and_records_audit(self):
        result = self.run_quietly(
            self.root,
            [sys.executable, "-c", "import time; time.sleep(5)"],
            label="unit-timeout",
            timeout_seconds=0.1,
        )
        self.assertEqual(result, 124)
        snapshot = runtime_snapshot(self.root)
        self.assertEqual(snapshot["lock_state"], "none")
        self.assertEqual(snapshot["last_run"]["status"], "timeout")
        self.assertIn(snapshot["last_run"]["termination"], {"terminated", "killed"})
        self.assertIsInstance(snapshot["last_run"]["process_audit"], list)

    def test_guarded_timeout_forcibly_kills_term_resistant_group(self):
        code = (
            "import signal, time; "
            "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            "time.sleep(5)"
        )
        with mock.patch("harness.runtime.TERM_GRACE_SECONDS", 0.05):
            result = self.run_quietly(
                self.root,
                [sys.executable, "-c", code],
                label="unit-force-kill",
                timeout_seconds=0.1,
            )
        self.assertEqual(result, 124)
        self.assertEqual(runtime_snapshot(self.root)["last_run"]["termination"], "killed")

    def test_active_compute_lock_blocks_replacement(self):
        lock = {
            "schema_version": 1,
            "token": "occupied",
            "status": "running",
            "label": "first-run",
            "started_at": "2026-01-01T00:00:00+00:00",
            "parent_pid": os.getpid(),
            "child_pid": None,
        }
        atomic_json(paths(self.root).lock, lock)
        with self.assertRaises(RuntimeBusy):
            run_guarded(
                self.root,
                [sys.executable, "-c", "pass"],
                label="replacement",
                timeout_seconds=1,
            )

    def test_stale_compute_lock_is_recovered(self):
        lock = {
            "schema_version": 1,
            "token": "stale",
            "status": "running",
            "label": "lost-run",
            "started_at": "2026-01-01T00:00:00+00:00",
            "parent_pid": 999_999_998,
            "child_pid": 999_999_999,
        }
        atomic_json(paths(self.root).lock, lock)
        result = self.run_quietly(
            self.root,
            [sys.executable, "-c", "pass"],
            label="recovered-run",
            timeout_seconds=1,
        )
        self.assertEqual(result, 0)
        self.assertEqual(runtime_snapshot(self.root)["lock_state"], "none")

    def test_guard_rejects_limit_evasion(self):
        with self.assertRaises(RuntimeControlError):
            run_guarded(self.root, [sys.executable, "-c", "pass"], timeout_seconds=241)
        with self.assertRaises(RuntimeControlError):
            run_guarded(self.root, ["nohup", sys.executable, "-c", "pass"])

    def test_lean_policy_rejects_trust_and_runtime_shortcuts(self):
        formal = self.root / "formal"
        formal.mkdir()
        (formal / "Bad.lean").write_text(
            """
axiom wish : False
unsafe def hidden : Nat := 0
example : True := by native_decide
example : True := by exact Lean.ofReduceBool (Eq.refl true)
run_tac pure ()
#eval 1
partial def loop : Nat := loop
extern \"foreign_value\" foreignValue : Nat
@[implemented_by foreignValue] def claimedValue : Nat := 0
@[extern \"foreign_prop\"] opaque foreignProp : True
set_option maxHeartbeats 0 in
example : True := by trivial
set_option autoImplicit true in
example : True := by trivial
""",
            encoding="utf-8",
        )
        failures = POLICY["audit_lean"](self.root)
        joined = "\n".join(failures)
        for label in (
            "custom axiom/constant",
            "unsafe declaration",
            "native-evaluation proof shortcut",
            "native reduction trust bridge",
            "runtime tactic",
            "evaluation command",
            "partial declaration",
            "foreign declaration",
            "external implementation bridge",
            "foreign declaration attribute",
            "local resource-limit override",
            "implicit-variable policy override",
        ):
            self.assertIn(label, joined)

    def test_lean_policy_ignores_forbidden_words_in_comments(self):
        formal = self.root / "formal"
        formal.mkdir()
        (formal / "Safe.lean").write_text(
            "/- sorry native_decide set_option maxHeartbeats 0 -/\n"
            "-- axiom fake : False\n"
            "example : True := by trivial\n",
            encoding="utf-8",
        )
        self.assertEqual(POLICY["audit_lean"](self.root), [])

    def test_pdf_release_text_policy_rejects_placeholder_and_private_path(self):
        failures = PDF_POLICY["audit_extracted_text"](
            "Scientific Project Title Replace with results /Users/alice/private/data.csv",
            "Scientific Project Title",
            {"Title": "Scientific Project Title"},
            release=True,
        )
        joined = "\n".join(failures)
        self.assertIn("private local path", joined)
        self.assertIn("placeholder text", joined)

    def test_pdf_text_policy_checks_release_title(self):
        failures = PDF_POLICY["audit_extracted_text"](
            "A complete scientific manuscript with enough extracted text " * 5,
            "A different visible title",
            {"Title": "Expected title"},
            release=True,
        )
        self.assertIn("metadata title does not appear", "\n".join(failures))

    def test_paper_policy_rejects_missing_narrative_marker(self):
        docs = self.root / "docs"
        paper = self.root / "paper"
        docs.mkdir()
        paper.mkdir()
        (docs / "PAPER_NARRATIVE.md").write_text(
            "## 1. Freeze the public claim spine\n",
            encoding="utf-8",
        )
        (paper / "PAPER_MAP.md").write_text("", encoding="utf-8")
        (paper / "EDITORIAL_AUDIT.md").write_text("", encoding="utf-8")
        (paper / "REVISION_HISTORY.md").write_text("", encoding="utf-8")
        failures = "\n".join(POLICY["audit_paper_controls"](self.root))
        self.assertIn("Build reader order from dependency order", failures)
        self.assertIn("Public claim spine", failures)
        self.assertIn("Change classification", failures)

    def test_manuscript_policy_finds_slop_and_artifact_leakage(self):
        manuscript = self.root / "manuscript"
        manuscript.mkdir()
        (manuscript / "S02-theory.tex").write_text(
            "Clearly, this is not merely sampled but exact. "
            "The Python script verifier lives in scripts/check.py.\n",
            encoding="utf-8",
        )
        findings = "\n".join(MANUSCRIPT_POLICY["audit_manuscript"](manuscript))
        self.assertIn("performative intensifier", findings)
        self.assertIn("contrastive negation", findings)
        self.assertIn("misplaced tool or model name", findings)
        self.assertIn("misplaced internal path", findings)

    def test_manuscript_policy_allows_artifacts_only_in_dedicated_section(self):
        manuscript = self.root / "manuscript"
        manuscript.mkdir()
        (manuscript / "S05-verification.tex").write_text(
            "Python runs the verifier script from scripts/check.py.\n",
            encoding="utf-8",
        )
        self.assertEqual(MANUSCRIPT_POLICY["audit_manuscript"](manuscript), [])

    def test_manuscript_policy_preserves_mathematical_negation(self):
        manuscript = self.root / "manuscript"
        manuscript.mkdir()
        (manuscript / "S03-results.tex").write_text(
            "Theorem 3 proves that f is not continuous on D.\n",
            encoding="utf-8",
        )
        self.assertEqual(MANUSCRIPT_POLICY["audit_manuscript"](manuscript), [])

    def test_formal_claim_registry_rejects_status_leap(self):
        formal = self.root / "formal"
        formal.mkdir()
        (formal / "CLAIMS.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "claims": [
                        {
                            "claim_id": "C001",
                            "kind": "containment",
                            "target_version": "TARGET-v1",
                            "declaration": "Formal.claim",
                            "status": "FORMALLY_PROVED",
                            "axiom_audit": [],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        failures = "\n".join(POLICY["audit_claim_registry"](self.root))
        self.assertIn("requires objective_interior", failures)
        self.assertIn("requires interior_dependency_audit", failures)
        self.assertIn("requires initialization", failures)
        self.assertIn("requires initialization_dependency_audit", failures)
        self.assertIn("requires release_gate", failures)

    def test_formal_claim_registry_accepts_kernel_checked_entry(self):
        formal = self.root / "formal"
        formal.mkdir()
        formal_source = formal / "Formal"
        formal_source.mkdir()
        (formal_source / "Audit.lean").write_text(
            "#print axioms Formal.claim\n", encoding="utf-8"
        )
        research = self.root / "research"
        research.mkdir()
        (research / "TARGET.md").write_text("Target version: TARGET-v1\n", encoding="utf-8")
        (research / "CLAIM_INDEX.md").write_text("| C001 |\n", encoding="utf-8")
        (formal / "CLAIMS.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "claims": [
                        {
                            "claim_id": "C001",
                            "kind": "universal",
                            "target_version": "TARGET-v1",
                            "declaration": "Formal.claim",
                            "status": "KERNEL_CHECKED",
                            "axiom_audit": [],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual(POLICY["audit_claim_registry"](self.root), [])
        report = full_report(self.store)
        self.assertIn("C001", report)
        self.assertIn("KERNEL_CHECKED", report)
        self.assertEqual(_json_report(self.store)["formal_claims"][0]["claim_id"], "C001")


if __name__ == "__main__":
    unittest.main()
