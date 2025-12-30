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

def sanitize_text(s: str) -> str:
    return "".join(ch for ch in s if not is_bad(ord(ch)))

def main() -> int:
    changed = 0
    for rel in git_ls_files():
        p = Path(rel)
        if p.suffix.lower() not in EXTS:
            continue

        raw = p.read_bytes()
        if raw.startswith(b"\xEF\xBB\xBF"):
            raw = raw[3:]  # strip BOM bytes

        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            continue

        clean = sanitize_text(text).replace("\r\n", "\n")
        if clean != text:
            p.write_bytes(clean.encode("utf-8"))
            changed += 1

    print(f"Sanitized {changed} file(s).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
