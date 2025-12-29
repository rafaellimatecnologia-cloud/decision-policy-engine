"""Remove hidden/bidi Unicode characters from tracked text files."""

from __future__ import annotations

import subprocess
from pathlib import Path

BOM_BYTES = b"\xef\xbb\xbf"

CODEPOINTS = {
    0xFEFF,
    0x200B,
    0x200C,
    0x200D,
    0x2060,
    0x061C,
    0x200E,
    0x200F,
    0x2028,
    0x2029,
}
CODEPOINTS.update(range(0x202A, 0x202F))
CODEPOINTS.update(range(0x2066, 0x206A))

SCAN_EXTENSIONS = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}


def sanitize_text(text: str) -> str:
    return "".join(ch for ch in text if ord(ch) not in CODEPOINTS)


def iter_tracked_files(repo_root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = []
    for line in result.stdout.splitlines():
        path = repo_root / line
        if path.suffix in SCAN_EXTENSIONS:
            paths.append(path)
    return paths


def sanitize_repo(repo_root: Path) -> list[Path]:
    changed: list[Path] = []
    for path in iter_tracked_files(repo_root):
        data = path.read_bytes()
        if data.startswith(BOM_BYTES):
            data = data[len(BOM_BYTES) :]
        text = data.decode("utf-8", errors="ignore")
        sanitized = sanitize_text(text)
        if sanitized != text:
            path.write_text(sanitized, encoding="utf-8", newline="\n")
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
