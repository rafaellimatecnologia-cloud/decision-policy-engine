"""Report hidden/bidi Unicode characters in tracked text files."""

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


def scan_file(path: Path) -> list[str]:
    issues: list[str] = []
    data = path.read_bytes()
    if data.startswith(BOM_BYTES):
        issues.append("BOM")
    text = data.decode("utf-8", errors="ignore")
    found = sorted({f"U+{ord(ch):04X}" for ch in text if ord(ch) in CODEPOINTS})
    issues.extend(found)
    return issues


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    flagged: dict[str, list[str]] = {}
    for path in iter_tracked_files(repo_root):
        issues = scan_file(path)
        if issues:
            flagged[str(path.relative_to(repo_root))] = issues

    if not flagged:
        print("No hidden Unicode found.")
        return

    print("Hidden Unicode report:")
    for path, issues in flagged.items():
        print(f"- {path}: {', '.join(issues)}")


if __name__ == "__main__":
    main()
