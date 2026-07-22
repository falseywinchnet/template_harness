#!/usr/bin/env python3
"""Fast policy checks that are reliable enough to enforce automatically."""

from __future__ import annotations

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


def audit_lean() -> list[str]:
    failures: list[str] = []
    patterns = (
        (re.compile(r"\b(?:sorry|admit)\b"), "placeholder"),
        (re.compile(r"(?m)^\s*(?:axiom|constant)\s+"), "custom axiom/constant"),
        (re.compile(r"(?m)^\s*unsafe\s+(?:def|theorem|opaque|instance)\b"), "unsafe declaration"),
    )
    for path in sorted((ROOT / "formal").rglob("*.lean")):
        if ".lake" in path.parts:
            continue
        try:
            code = lean_without_comments(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        for pattern, label in patterns:
            for match in pattern.finditer(code):
                line = code.count("\n", 0, match.start()) + 1
                failures.append(f"{path.relative_to(ROOT)}:{line}: forbidden {label}")
    return failures


def audit_required_controls() -> list[str]:
    required = (
        "docs/LEAN_ENGINEERING.md",
        "docs/COMPUTE_DESIGN.md",
        "docs/PYTHON_COMPUTATION.md",
        "docs/PDF_HOUSE_STYLE.md",
        "computations/COMPUTE_PLAN.md",
        "formal/AXIOMS.md",
        "formal/PERFORMANCE.md",
        "paper/manuscript/metadata.tex",
    )
    return [f"missing required control: {path}" for path in required if not (ROOT / path).is_file()]


def main() -> None:
    failures = audit_required_controls() + audit_lean()
    if failures:
        print("POLICY AUDIT failed")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    lean_count = sum(
        1 for path in (ROOT / "formal").rglob("*.lean") if ".lake" not in path.parts
    )
    print(f"POLICY AUDIT passed lean_files={lean_count} controls=8")


if __name__ == "__main__":
    main()
