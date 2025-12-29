"""Remove hidden/bidi Unicode characters from text files."""

from __future__ import annotations

from pathlib import Path

HIDDEN_CHARS = {
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
    "\u200B",
    "\u200C",
    "\u200D",
    "\u2060",
    "\u2028",
    "\u2029",
}
BOM = "\ufeff"
SCAN_EXTENSIONS = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}


def sanitize_text(text: str) -> str:
    if text.startswith(BOM):
        text = text.lstrip(BOM)
    for char in HIDDEN_CHARS:
        text = text.replace(char, "")
    return text


def sanitize_repo(repo_root: Path) -> list[Path]:
    changed: list[Path] = []
    skip_dirs = {".git", ".venv", "__pycache__", ".mypy_cache"}
    for path in repo_root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix not in SCAN_EXTENSIONS:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        sanitized = sanitize_text(content)
        if sanitized != content:
            path.write_text(sanitized, encoding="utf-8")
            changed.append(path)
    return changed


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    changed = sanitize_repo(repo_root)
    if not changed:
        print("No hidden Unicode characters found.")
        return
    print("Sanitized files:")
    for path in changed:
        print(f"- {path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
