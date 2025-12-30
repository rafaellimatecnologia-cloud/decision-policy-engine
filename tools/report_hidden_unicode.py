from __future__ import annotations

import subprocess
import unicodedata
from pathlib import Path

EXTS = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}
BIDI_BAD = {"LRE", "RLE", "PDF", "LRO", "RLO", "LRI", "RLI", "FSI", "PDI"}
ALLOWED_CC = {"\n", "\t"}  # o resto de Cc é suspeito

def git_ls_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]

def is_suspicious(ch: str) -> bool:
    cat = unicodedata.category(ch)
    if cat == "Cf":
        return True
    if unicodedata.bidirectional(ch) in BIDI_BAD:
        return True
    if cat == "Cc" and ch not in ALLOWED_CC:
        return True
    return False

def line_col(text: str, idx: int) -> tuple[int, int]:
    line = text.count("\n", 0, idx) + 1
    last_nl = text.rfind("\n", 0, idx)
    col = idx - (last_nl + 1)
    return line, col

def main() -> int:
    offenders = 0

    for rel in git_ls_files():
        p = Path(rel)
        if p.suffix.lower() not in EXTS:
            continue

        data = p.read_bytes()
        if data.startswith(b"\xEF\xBB\xBF"):
            offenders += 1
            print(f"[!] {rel}: UTF-8 BOM (EF BB BF)")
            continue

        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            offenders += 1
            print(f"[!] {rel}: not strict UTF-8")
            continue

        found = []
        for i, ch in enumerate(text):
            if is_suspicious(ch):
                ln, col = line_col(text, i)
                found.append(
                    (ln, col, f"U+{ord(ch):04X}", unicodedata.name(ch, "UNKNOWN"),
                     unicodedata.category(ch), unicodedata.bidirectional(ch))
                )

        if found:
            offenders += 1
            print(f"[!] {rel}")
            for ln, col, cp, name, cat, bidi in found[:50]:
                print(f"    - L{ln}:C{col} {cp} {name} cat={cat} bidi={bidi}")
            if len(found) > 50:
                print(f"    ... ({len(found)-50} more)")

    if offenders == 0:
        print("OK: no suspicious hidden/bidi/control Unicode found.")
        return 0

    print(f"\nFound issues in {offenders} file(s).")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
