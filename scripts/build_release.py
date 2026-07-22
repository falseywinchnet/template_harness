#!/usr/bin/env python3
"""Flatten the template manuscript and build a deterministic source archive."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re
import tarfile


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper" / "manuscript"
OUTPUT = ROOT / "paper" / "arxiv" / "main.tex"
ARCHIVE = ROOT / "paper" / "release.tar"
INPUT = re.compile(r"^\s*\\input\{([^}]+)\}\s*$")


def resolve_input(name: str, parent: Path) -> Path:
    relative = Path(name)
    if relative.suffix != ".tex":
        relative = relative.with_suffix(".tex")
    for candidate in (MANUSCRIPT / relative, parent / relative):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"unresolved TeX input: {name}")


def strip_comment(line: str) -> str:
    for index, character in enumerate(line):
        if character != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and line[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return line[:index].rstrip()
    return line.rstrip()


def expand(path: Path, stack: tuple[Path, ...] = ()) -> list[str]:
    if path in stack:
        raise RuntimeError(f"recursive TeX input: {path}")
    lines: list[str] = []
    for source in path.read_text(encoding="utf-8").splitlines():
        line = strip_comment(source)
        match = INPUT.match(line)
        if match:
            lines.extend(expand(resolve_input(match.group(1), path.parent), stack + (path,)))
        elif line:
            lines.append(line)
        elif lines and lines[-1] != "":
            lines.append("")
    return lines


def main() -> None:
    lines = expand(MANUSCRIPT / "main.tex")
    if any(INPUT.match(line) for line in lines):
        raise RuntimeError("flattening left an input directive")
    if sum(line.startswith(r"\documentclass") for line in lines) != 1:
        raise RuntimeError("flattened source must contain one document class")
    if lines.count(r"\begin{document}") != 1:
        raise RuntimeError("flattened source must contain one document beginning")
    if lines.count(r"\end{document}") != 1 or lines[-1] != r"\end{document}":
        raise RuntimeError("flattened source must end at its sole document boundary")
    data = ("\n".join(lines) + "\n").encode("utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(data)
    info = tarfile.TarInfo("main.tex")
    info.size = len(data)
    info.mode = 0o644
    info.mtime = 0
    with ARCHIVE.open("wb") as stream, tarfile.open(
        fileobj=stream, mode="w", format=tarfile.USTAR_FORMAT
    ) as archive:
        archive.addfile(info, BytesIO(data))
    print(f"wrote {OUTPUT.relative_to(ROOT)} and {ARCHIVE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
