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


def _tracked_files(repo_root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        repo_root / line
        for line in result.stdout.splitlines()
        if (repo_root / line).suffix in SCAN_EXTENSIONS
    ]


def test_no_hidden_unicode_characters() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    offenders: list[str] = []
    for path in _tracked_files(repo_root):
        data = path.read_bytes()
        if data.startswith(BOM_BYTES):
            offenders.append(f"{path.relative_to(repo_root)}: BOM")
            continue
        text = data.decode("utf-8", errors="ignore")
        found = sorted({f"U+{ord(ch):04X}" for ch in text if ord(ch) in CODEPOINTS})
        if found:
            offenders.append(f"{path.relative_to(repo_root)}: {', '.join(found)}")

    assert not offenders, f"Found hidden Unicode characters in: {offenders}"
