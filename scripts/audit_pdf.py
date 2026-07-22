#!/usr/bin/env python3
"""Audit objective TeX log, PDF metadata, and font-embedding gates."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess


FAIL_PATTERNS = (
    (re.compile(r"LaTeX Warning:.*undefined", re.IGNORECASE), "undefined LaTeX reference/citation"),
    (re.compile(r"There were undefined references", re.IGNORECASE), "undefined references"),
    (re.compile(r"Overfull \\[hv]box"), "overfull box"),
    (re.compile(r"! (?:LaTeX|Package).*Error"), "LaTeX/package error"),
    (re.compile(r"Emergency stop", re.IGNORECASE), "emergency stop"),
)

FONT_ROW = re.compile(
    r"^(?P<name>\S+)\s+(?P<type>.+?)\s+(?P<encoding>\S+)\s+"
    r"(?P<embedded>yes|no)\s+(?P<subset>yes|no)\s+(?P<unicode>yes|no)\s+"
    r"\d+\s+\d+\s*$",
    re.IGNORECASE,
)


def command_output(command: list[str]) -> str:
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(f"command failed: {' '.join(command)}\n{completed.stderr.strip()}")
    return completed.stdout


def audit_log(path: Path) -> tuple[list[str], int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    failures: list[str] = []
    for pattern, label in FAIL_PATTERNS:
        if pattern.search(text):
            failures.append(f"{path}: {label}")
    underfull = len(re.findall(r"Underfull \\[hv]box", text))
    return failures, underfull


def audit_pdf(path: Path) -> tuple[list[str], dict[str, str]]:
    failures: list[str] = []
    if not path.is_file() or path.stat().st_size < 1024:
        return [f"{path}: missing or implausibly small PDF"], {}
    if not path.read_bytes().startswith(b"%PDF-"):
        failures.append(f"{path}: missing PDF signature")
    metadata: dict[str, str] = {}
    if shutil.which("pdfinfo"):
        for line in command_output(["pdfinfo", str(path)]).splitlines():
            key, separator, value = line.partition(":")
            if separator:
                metadata[key.strip()] = value.strip()
        for key in ("Title", "Author", "Pages", "Page size"):
            if not metadata.get(key):
                failures.append(f"{path}: PDF metadata field {key!r} is empty")
    else:
        print("PDF AUDIT warning: pdfinfo unavailable; metadata fields not checked")
    if shutil.which("pdffonts"):
        rows = command_output(["pdffonts", str(path)]).splitlines()[2:]
        for row in rows:
            match = FONT_ROW.match(row)
            if match and match.group("embedded").casefold() != "yes":
                failures.append(f"{path}: font is not embedded: {match.group('name')}")
    else:
        print("PDF AUDIT warning: pdffonts unavailable; embedding not checked")
    return failures, metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    failures, underfull = audit_log(args.log)
    pdf_failures, metadata = audit_pdf(args.pdf)
    failures.extend(pdf_failures)
    if failures:
        print("PDF AUDIT failed")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    if underfull:
        print(f"PDF AUDIT warning: underfull_boxes={underfull}; visual review required")
    print(
        "PDF AUDIT passed "
        f"pages={metadata.get('Pages', 'unchecked')} "
        f"title={metadata.get('Title', 'unchecked')!r} underfull_boxes={underfull}"
    )


if __name__ == "__main__":
    main()
