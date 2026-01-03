from __future__ import annotations

import unicodedata
from pathlib import Path

BIDI_CODEPOINTS = {
    0x202A,
    0x202B,
    0x202C,
    0x202D,
    0x202E,
    0x2066,
    0x2067,
    0x2068,
    0x2069,
    0x200E,
    0x200F,
    0x061C,
}
BIDI_CHARS = {chr(codepoint) for codepoint in BIDI_CODEPOINTS}

BIDI_CLASSES = {
    "LRE",
    "RLE",
    "LRO",
    "RLO",
    "PDF",
    "LRI",
    "RLI",
    "FSI",
    "PDI",
    "BN",
}

HIDDEN_CATEGORIES = {"Cf"}

SCAN_EXTENSIONS = {".json", ".jsonl", ".md", ".py", ".toml", ".yml", ".yaml", ".txt"}
SCAN_FILES = {"LICENSE"}


def _iter_files(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    skip_dirs = {".git", ".venv", "__pycache__", ".mypy_cache"}
    for path in repo_root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file() and (
            path.suffix in SCAN_EXTENSIONS or path.name in SCAN_FILES
        ):
            paths.append(path)
    return paths


def test_no_bidi_unicode_characters() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    offenders: set[str] = set()
    for path in _iter_files(repo_root):
        content = path.read_text(encoding="utf-8")
        for char in content:
            if char in BIDI_CHARS:
                offenders.add(str(path.relative_to(repo_root)))
                break
            if unicodedata.bidirectional(char) in BIDI_CLASSES:
                offenders.add(str(path.relative_to(repo_root)))
                break
            if unicodedata.category(char) in HIDDEN_CATEGORIES:
                offenders.add(str(path.relative_to(repo_root)))
                break

    assert not offenders, (
        "Found bidi/hidden Unicode characters in: "
        f"{sorted(offenders)}"
    )
