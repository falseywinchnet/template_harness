#!/usr/bin/env python3
"""Fast policy checks that are reliable enough to enforce automatically."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def lean_without_comments(text: str) -> str:
    """Remove nested block and line comments while preserving line numbers."""
    output: list[str] = []
    index = 0
    depth = 0
    while index < len(text):
        if depth == 0 and text.startswith("--", index):
            end = text.find("\n", index)
            if end < 0:
                output.extend(" " for _ in text[index:])
                break
            output.extend(" " for _ in text[index:end])
            output.append("\n")
            index = end + 1
        elif text.startswith("/-", index):
            depth += 1
            output.extend("  ")
            index += 2
        elif depth and text.startswith("-/", index):
            depth -= 1
            output.extend("  ")
            index += 2
        elif depth:
            output.append("\n" if text[index] == "\n" else " ")
            index += 1
        else:
            output.append(text[index])
            index += 1
    if depth:
        raise ValueError("unterminated Lean block comment")
    return "".join(output)


def audit_lean(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    patterns = (
        (re.compile(r"\b(?:sorry|admit|sorryAx)\b"), "placeholder"),
        (re.compile(r"(?m)^\s*(?:axiom|constant)\s+"), "custom axiom/constant"),
        (re.compile(r"(?m)^\s*unsafe\s+"), "unsafe declaration"),
        (re.compile(r"\bnative_decide\b"), "native-evaluation proof shortcut"),
        (re.compile(r"\b(?:Lean\.)?ofReduceBool\b"), "native reduction trust bridge"),
        (re.compile(r"\brun_tac\b"), "runtime tactic"),
        (re.compile(r"(?m)^\s*#(?:eval|reduce)\b"), "evaluation command in theorem tree"),
        (re.compile(r"(?m)^\s*partial\s+def\b"), "partial declaration"),
        (re.compile(r"(?m)^\s*extern\s+"), "foreign declaration"),
        (re.compile(r"@\[implemented_by\b"), "external implementation bridge"),
        (re.compile(r"@\[extern\b"), "foreign declaration attribute"),
        (
            re.compile(r"\bset_option\s+(?:maxHeartbeats|maxRecDepth|synthInstance\.maxHeartbeats)\b"),
            "local resource-limit override",
        ),
        (
            re.compile(r"\bset_option\s+(?:autoImplicit|relaxedAutoImplicit)\s+true\b"),
            "implicit-variable policy override",
        ),
    )
    for path in sorted((root / "formal").rglob("*.lean")):
        if ".lake" in path.parts:
            continue
        try:
            code = lean_without_comments(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            failures.append(f"{path.relative_to(root)}: {exc}")
            continue
        for pattern, label in patterns:
            for match in pattern.finditer(code):
                line = code.count("\n", 0, match.start()) + 1
                failures.append(f"{path.relative_to(root)}:{line}: forbidden {label}")
    return failures


def audit_required_controls(root: Path = ROOT) -> list[str]:
    required = (
        "docs/LEAN_ENGINEERING.md",
        "docs/LEAN_CLAIM_STANDARD.md",
        "docs/COMPUTE_DESIGN.md",
        "docs/PYTHON_COMPUTATION.md",
        "docs/PAPER_NARRATIVE.md",
        "docs/PDF_HOUSE_STYLE.md",
        "docs/RESOURCE_SAFETY.md",
        "harness/runtime.py",
        "computations/COMPUTE_PLAN.md",
        "computations/requirements-sympy.txt",
        "formal/AXIOMS.md",
        "formal/CLAIMS.json",
        "formal/Formal/ClaimContract.lean",
        "formal/PERFORMANCE.md",
        "paper/manuscript/metadata.tex",
        "paper/EDITORIAL_AUDIT.md",
        "paper/PAPER_MAP.md",
    )
    return [f"missing required control: {path}" for path in required if not (root / path).is_file()]


def audit_claim_controls(root: Path = ROOT) -> list[str]:
    required_markers = {
        "research/TARGET.md": (
            "## Objective target interior",
            "## Initialization and containment",
            "Counterexample(x)",
        ),
        "research/NON_VACUITY.md": (
            "Objective target interior",
            "Falsifier equivalence",
            "Initialization",
        ),
        "research/FORMALIZATION.md": (
            "## Required declaration chain",
            "## Definition and interpretation audit",
            "## Adversarial derivation audit",
        ),
        "docs/LEAN_CLAIM_STANDARD.md": (
            "## 1. Falsification normal form",
            "## 2. Objective target interior",
            "## 3. Containment and invariant claims",
        ),
    }
    failures: list[str] = []
    for relative, markers in required_markers.items():
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            failures.append(f"cannot audit claim control {relative}: {exc}")
            continue
        for marker in markers:
            if marker not in text:
                failures.append(f"claim control marker missing in {relative}: {marker}")
    return failures


def audit_paper_controls(root: Path = ROOT) -> list[str]:
    required_markers = {
        "docs/PAPER_NARRATIVE.md": (
            "## 1. Freeze the public claim spine",
            "## 2. Build reader order from dependency order",
            "## 11. Revision identity and change classes",
            "## 12. Model editing protocol",
        ),
        "paper/PAPER_MAP.md": (
            "## Public claim spine",
            "Reader question",
            "Entry dependencies",
            "Exit state",
            "## Excluded and supplemental branches",
        ),
        "paper/EDITORIAL_AUDIT.md": (
            "## Public claim spine",
            "## Section burden audit",
            "## Revision decision",
            "## Adversarial summary",
        ),
        "paper/REVISION_HISTORY.md": (
            "## Change classification",
            "strengthened presentation",
            "gap repair",
            "corrigendum/retraction",
        ),
    }
    failures: list[str] = []
    for relative, markers in required_markers.items():
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            failures.append(f"cannot audit paper control {relative}: {exc}")
            continue
        for marker in markers:
            if marker not in text:
                failures.append(f"paper control marker missing in {relative}: {marker}")
    return failures


def audit_claim_registry(root: Path = ROOT) -> list[str]:
    path = root / "formal/CLAIMS.json"
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"formal claim registry is unreadable: {exc}"]
    if not isinstance(registry, dict) or registry.get("schema_version") != 1:
        return ["formal claim registry schema_version must be 1"]
    claims = registry.get("claims")
    if not isinstance(claims, list):
        return ["formal claim registry claims must be a list"]
    failures: list[str] = []
    linked_text: dict[str, str] = {}
    for relative in ("formal/Formal/Audit.lean", "research/TARGET.md", "research/CLAIM_INDEX.md"):
        try:
            linked_text[relative] = (root / relative).read_text(encoding="utf-8")
        except OSError as exc:
            linked_text[relative] = ""
            if claims:
                failures.append(f"cannot validate formal claim links in {relative}: {exc}")

    statuses = (
        "KERNEL_CHECKED",
        "TARGET_INSTANTIATED",
        "STATEMENT_FAITHFUL",
        "FORMALLY_PROVED",
    )
    kinds = {
        "universal",
        "containment",
        "invariant",
        "existential",
        "identity",
        "exact-order",
        "nonexistence",
        "other",
    }
    base = ("claim_id", "kind", "target_version", "declaration", "axiom_audit")
    instantiated = ("object_identity", "domain_witness", "actual_instantiation")
    faithful = (
        "counterexample_equivalence",
        "fidelity_forward",
        "fidelity_reverse",
        "definition_audit",
        "independent_reviewer",
    )
    proved = ("audit_declarations", "release_gate")
    seen: set[str] = set()

    def present(claim: dict[str, object], field: str) -> bool:
        value = claim.get(field)
        if field == "axiom_audit":
            return isinstance(value, list) and all(isinstance(item, str) and item for item in value)
        if field == "audit_declarations":
            return (
                isinstance(value, list)
                and bool(value)
                and all(isinstance(item, str) and item for item in value)
            )
        return isinstance(value, str) and bool(value.strip())

    for index, claim in enumerate(claims, 1):
        label = f"formal claim entry {index}"
        if not isinstance(claim, dict):
            failures.append(f"{label} must be an object")
            continue
        ident = claim.get("claim_id")
        if not isinstance(ident, str) or not re.fullmatch(r"C\d{3,6}", ident):
            failures.append(f"{label} has invalid claim_id")
        elif ident in seen:
            failures.append(f"duplicate formal claim_id: {ident}")
        else:
            seen.add(ident)
            label = ident
        status = claim.get("status")
        if status not in statuses:
            failures.append(f"{label}: invalid formal status {status!r}")
            continue
        if claim.get("kind") not in kinds:
            failures.append(f"{label}: invalid claim kind {claim.get('kind')!r}")
        declaration = claim.get("declaration")
        if isinstance(declaration, str) and declaration.strip():
            audit_marker = f"#print axioms {declaration}"
            if audit_marker not in linked_text["formal/Formal/Audit.lean"]:
                failures.append(f"{label}: declaration missing from Formal/Audit.lean")
        target_version = claim.get("target_version")
        if isinstance(target_version, str) and target_version.strip():
            if target_version not in linked_text["research/TARGET.md"]:
                failures.append(f"{label}: target_version is absent from research/TARGET.md")
        if isinstance(ident, str) and ident not in linked_text["research/CLAIM_INDEX.md"]:
            failures.append(f"{label}: claim_id is absent from research/CLAIM_INDEX.md")
        required = list(base)
        level = statuses.index(status)
        if level >= 1:
            required.extend(instantiated)
        if level >= 2:
            required.extend(faithful)
        if level >= 3:
            required.extend(proved)
        kind = claim.get("kind")
        if level >= 2 and kind == "nonexistence":
            required.extend(("ambient_domain_witness", "nonexistence_boundary"))
        elif level >= 2:
            required.extend(("objective_interior", "interior_dependency_audit"))
        if kind in {"containment", "invariant"} and level >= 1:
            required.append("initialization")
        if kind in {"containment", "invariant"} and level >= 2:
            required.append("initialization_dependency_audit")
        if kind == "invariant" and level >= 1:
            required.extend(("preservation", "reachability"))
        if kind == "invariant" and level >= 2:
            required.append("dynamics_dependency_audit")
        if kind == "exact-order" and level >= 2:
            required.append("exterior_witness")
        for field in required:
            if not present(claim, field):
                failures.append(f"{label}: status {status} requires {field}")
    return failures


def audit_runtime_policy() -> list[str]:
    failures: list[str] = []
    runtime = (ROOT / "harness/runtime.py").read_text(encoding="utf-8")
    lake = (ROOT / "formal/lakefile.toml").read_text(encoding="utf-8")
    sympy = (ROOT / "computations/requirements-sympy.txt").read_text(encoding="utf-8")
    required_runtime = (
        "MAX_SECONDS = 240",
        "DEFAULT_NICE = 10",
        "start_new_session=True",
        "signal.SIGKILL",
        '"OMP_NUM_THREADS": "1"',
    )
    required_lake = (
        "pp.unicode.fun = true",
        "relaxedAutoImplicit = false",
        "weak.linter.mathlibStandardSet = true",
        "maxSynthPendingDepth = 3",
        'rev = "v4.32.0"',
    )
    for marker in required_runtime:
        if marker not in runtime:
            failures.append(f"runtime safety marker missing: {marker}")
    for marker in required_lake:
        if marker not in lake:
            failures.append(f"Lean configuration marker missing: {marker}")
    if "sympy==1.14.0" not in sympy:
        failures.append("known-good SymPy pin missing: sympy==1.14.0")
    return failures


def main() -> None:
    failures = (
        audit_required_controls()
        + audit_claim_controls()
        + audit_paper_controls()
        + audit_claim_registry()
        + audit_runtime_policy()
        + audit_lean()
    )
    if failures:
        print("POLICY AUDIT failed")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    lean_count = sum(
        1 for path in (ROOT / "formal").rglob("*.lean") if ".lake" not in path.parts
    )
    print(
        f"POLICY AUDIT passed lean_files={lean_count} controls=18 "
        "claim_standard=strict paper_narrative=audited runtime=guarded"
    )


if __name__ == "__main__":
    main()
