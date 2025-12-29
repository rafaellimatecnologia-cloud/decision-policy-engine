from __future__ import annotations

from pathlib import Path

FORBIDDEN_CHARS = {
    "\u202A",
    "\u202B",
    "\u202C",
    "\u202D",
    "\u202E",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
    "\u200E",
    "\u200F",
    "\u061C",
    "\ufeff",
    "\u200B",
    "\u200C",
    "\u200D",
    "\u2060",
    "\u00AD",
}

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
    offenders: list[str] = []
    for path in _iter_files(repo_root):
        content = path.read_text(encoding="utf-8", errors="ignore")
        if any(char in content for char in FORBIDDEN_CHARS):
            offenders.append(str(path.relative_to(repo_root)))

    assert not offenders, f"Found bidi/hidden Unicode characters in: {offenders}"
