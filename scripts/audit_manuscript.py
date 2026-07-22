#!/usr/bin/env python3
"""Find high-confidence prose slop and misplaced implementation artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


DEDICATED_ARTIFACT_FILE = re.compile(
    r"(?:^|[-_])(?:reproduc\w*|verif\w*|availab\w*|declaration\w*|"
    r"artifact\w*|provenance\w*|software\w*|code|data|references?)(?:[-_.]|$)",
    re.IGNORECASE,
)

INFRASTRUCTURE_FILES = {"main.tex", "metadata.tex", "preamble.tex"}

SLOP_PATTERNS = (
    (
        "contrastive negation",
        re.compile(
            r"\b(?:is|are|was|were|does|do|did|has|have)\s+not\b"
            r"[^.;:\n]{0,120}\b(?:but|rather|instead)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "contrastive negation",
        re.compile(r"\bnot\s+(?:merely|simply|just|only)\b", re.IGNORECASE),
    ),
    (
        "scope disclaimer",
        re.compile(
            r"\b(?:we|this\s+(?:paper|article|work|result|theorem)|"
            r"the\s+(?:paper|article|work|result|theorem))\s+"
            r"(?:do|does|is|are|will|can|could|should|would|has|have)\s+not\s+"
            r"(?:claim|attempt|address|consider|cover|imply|prove|disprove|"
            r"establish|require|rely|use)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "unused-route disclaimer",
        re.compile(
            r"\b(?:is|are|was|were)\s+not\s+(?:used|needed|required|premises?)\b|"
            r"\bneither\b[^.;:\n]{0,120}\b(?:is|are|was|were)\s+"
            r"(?:used|needed|required)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "evidence disclaimer",
        re.compile(
            r"\b(?:is|are|was|were)\s+not\s+"
            r"(?:inferred|derived|obtained|established|proved)\s+from\b|"
            r"\bno\s+(?:floating[- ]point|interval\s+subdivision|"
            r"numerical\s+sampling)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "scope disclaimer",
        re.compile(
            r"\b(?:has|have|with)\s+no\s+implication\b|"
            r"\b(?:outside|beyond)\s+the\s+scope\b|"
            r"\bmakes?\s+no\s+claim\b",
            re.IGNORECASE,
        ),
    ),
    (
        "performative intensifier",
        re.compile(
            r"\b(?:clearly|obviously|evidently|trivially|straightforwardly|"
            r"remarkably|importantly|crucially|interestingly|reassuringly|"
            r"notably|deliberately)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "authorial stage direction",
        re.compile(
            r"\b(?:we\s+(?:emphasize|stress|note|remark|point\s+out|wish\s+to)|"
            r"it\s+is\s+worth\s+(?:noting|emphasizing)|"
            r"for\s+(?:clarity|completeness|orientation|reference)|"
            r"the\s+reader\s+(?:can|may|should)|skeptical\s+reader)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "status declaration",
        re.compile(
            r"\b(?:the\s+remainder\s+is\s+exact|all\s+load-bearing|"
            r"(?:fully|entirely|completely)\s+(?:rigorous|exact|explicit|"
            r"self-contained|verified)|(?:the\s+)?(?:proof|argument)\s+is\s+"
            r"(?:complete|rigorous|exact|self-contained)|"
            r"the\s+distinction\s+between\b[^.;:\n]{0,100}\b"
            r"(?:is|remains)\s+(?:clear|explicit|maintained))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "performative figure of speech",
        re.compile(
            r"\b(?:load-bearing|critical\s+path|closes?\s+the\s+gap|"
            r"opens?\s+the\s+door|paves?\s+the\s+way|sheds?\s+light|"
            r"at\s+the\s+heart\s+of|cornerstone|quiet\s+kill|"
            r"proof\s+machinery|argument\s+machinery|proof\s+route)\b",
            re.IGNORECASE,
        ),
    ),
)

ARTIFACT_PATTERNS = (
    (
        "code or path typesetting",
        re.compile(r"\\(?:path|texttt)\s*\{"),
    ),
    (
        "tool or model name",
        re.compile(
            r"\b(?:Python|SymPy|Lean(?:\s*4)?|Mathlib|Arb|FLINT|Mathematica|"
            r"Maple|MATLAB|NumPy|SciPy|SageMath|Jupyter|Codex|ChatGPT|Claude)\b"
        ),
    ),
    (
        "computational artifact",
        re.compile(
            r"\b(?:source\s+code|scripts?|verifiers?|replays?|repository|commit|"
            r"GitHub|GitLab|SHA-?256|hash(?:es)?|proof\s+assistant|"
            r"formalization)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "internal path",
        re.compile(
            r"(?:^|[\s{(`/])(?:scripts|work|proof|formal|paper|research|sources|"
            r"computations)/",
            re.IGNORECASE | re.MULTILINE,
        ),
    ),
    (
        "artifact filename",
        re.compile(
            r"\.(?:py|lean|ipynb|json|toml|ya?ml|csv|tsv|log|tar|lock)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "internal project identifier",
        re.compile(r"\b(?:CERT|P|R)\d{3,6}\b"),
    ),
)


def without_comments(text: str) -> str:
    """Remove unescaped LaTeX comments while preserving line numbers."""
    output: list[str] = []
    for line in text.splitlines(keepends=True):
        cut = len(line)
        for index, character in enumerate(line):
            if character != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                cut = index
                break
        if cut == len(line):
            output.append(line)
        else:
            suffix = "\n" if line.endswith("\n") else ""
            output.append(line[:cut] + suffix)
    return "".join(output)


def source_line(text: str, position: int) -> tuple[int, str]:
    line_number = text.count("\n", 0, position) + 1
    line = text.splitlines()[line_number - 1].strip()
    return line_number, " ".join(line.split())[:180]


def audit_manuscript(root: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(root.rglob("*.tex")):
        if path.name in INFRASTRUCTURE_FILES:
            continue
        relative = path.relative_to(root)
        reference_file = "reference" in path.name.casefold()
        dedicated = bool(DEDICATED_ARTIFACT_FILE.search(path.name))
        text = without_comments(path.read_text(encoding="utf-8", errors="replace"))
        seen: set[tuple[str, int]] = set()

        if not reference_file:
            for label, pattern in SLOP_PATTERNS:
                for match in pattern.finditer(text):
                    line_number, snippet = source_line(text, match.start())
                    key = (label, line_number)
                    if key not in seen:
                        findings.append(
                            f"{relative}:{line_number}: {label}: {snippet}"
                        )
                        seen.add(key)

        if not dedicated and not reference_file:
            for label, pattern in ARTIFACT_PATTERNS:
                for match in pattern.finditer(text):
                    line_number, snippet = source_line(text, match.start())
                    key = (label, line_number)
                    if key not in seen:
                        findings.append(
                            f"{relative}:{line_number}: misplaced {label}: {snippet}"
                        )
                        seen.add(key)
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("paper/manuscript"))
    parser.add_argument(
        "--release",
        action="store_true",
        help="fail when any negative-style or artifact-containment finding remains",
    )
    args = parser.parse_args()
    findings = audit_manuscript(args.root)
    if findings:
        status = "failed" if args.release else "review"
        print(f"MANUSCRIPT STYLE AUDIT {status} findings={len(findings)}")
        for finding in findings:
            print(f"- {finding}")
        if args.release:
            raise SystemExit(1)
        return
    print("MANUSCRIPT STYLE AUDIT passed findings=0")


if __name__ == "__main__":
    main()
