from __future__ import annotations

import subprocess
from pathlib import Path

BAD_CODEPOINTS = {
    0xFEFF,
    0x200B, 0x200C, 0x200D, 0x2060,
    0x061C, 0x200E, 0x200F,
    0x2028, 0x2029,
}
BAD_RANGES = [
    (0x202A, 0x202E),
    (0x2066, 0x2069),
]

EXTS = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}

def is_bad(cp: int) -> bool:
    if cp in BAD_CODEPOINTS:
        return True
    return any(lo <= cp <= hi for lo, hi in BAD_RANGES)

def git_ls_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]

def test_no_hidden_or_bidi_unicode_in_repo() -> None:
    offenders: list[str] = []

    for rel in git_ls_files():
        p = Path(rel)
        if p.suffix.lower() not in EXTS:
            continue

        data = p.read_bytes()

        # UTF-8 BOM bytes
        if data.startswith(b"\xEF\xBB\xBF"):
            offenders.append(f"{rel}: UTF-8 BOM (EF BB BF)")
            continue

        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            offenders.append(f"{rel}: not strict UTF-8")
            continue

        bads = sorted({ord(ch) for ch in text if is_bad(ord(ch))})
        if bads:
            offenders.append(f"{rel}: " + ", ".join([f"U+{cp:04X}" for cp in bads]))

    assert not offenders, "Hidden/bidi unicode detected:\n" + "\n".join(offenders)
