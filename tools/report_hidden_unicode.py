from __future__ import annotations

import subprocess
from pathlib import Path

BAD_CODEPOINTS = {
    0xFEFF,  # BOM as codepoint
    0x200B, 0x200C, 0x200D, 0x2060,  # zero-width
    0x061C, 0x200E, 0x200F,          # bidi marks
    0x2028, 0x2029,                  # separators
}
BAD_RANGES = [
    (0x202A, 0x202E),  # LRE..RLO
    (0x2066, 0x2069),  # LRI..PDI
]

EXTS = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}

def is_bad(cp: int) -> bool:
    if cp in BAD_CODEPOINTS:
        return True
    return any(lo <= cp <= hi for lo, hi in BAD_RANGES)

def git_ls_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]

def main() -> int:
    offenders = 0
    for rel in git_ls_files():
        p = Path(rel)
        if p.suffix.lower() not in EXTS:
            continue

        data = p.read_bytes()
        has_bom = data.startswith(b"\xEF\xBB\xBF")

        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            continue

        bads = sorted({ord(ch) for ch in text if is_bad(ord(ch))})
        if has_bom or bads:
            offenders += 1
            print(f"[!] {rel}")
            if has_bom:
                print("    - UTF-8 BOM (EF BB BF)")
            for cp in bads:
                print(f"    - U+{cp:04X}")
    if offenders == 0:
        print("OK: no hidden/bidi unicode markers found.")
        return 0
    print(f"\nFound issues in {offenders} file(s).")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
