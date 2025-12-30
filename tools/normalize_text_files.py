from __future__ import annotations

import subprocess
import unicodedata
from pathlib import Path

EXTS = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}

# Bidi controls that GitHub warns about
BIDI_BAD = {"LRE", "RLE", "PDF", "LRO", "RLO", "LRI", "RLI", "FSI", "PDI"}
ALLOWED_CC = {"\n", "\t"}  # keep only LF and tab; drop other control chars

def git_ls_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]

def is_suspicious(ch: str) -> bool:
    cat = unicodedata.category(ch)
    if cat == "Cf":  # format chars (zero-width etc.)
        return True
    if unicodedata.bidirectional(ch) in BIDI_BAD:
        return True
    if cat == "Cc" and ch not in ALLOWED_CC:  # other control chars
        return True
    return False

def main() -> int:
    changed = 0

    for rel in git_ls_files():
        p = Path(rel)
        if p.suffix.lower() not in EXTS:
            continue

        raw = p.read_bytes()

        # utf-8-sig strips BOM automatically when decoding
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            continue

        # normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # remove suspicious chars
        cleaned = "".join(ch for ch in text if not is_suspicious(ch))

        # ensure final newline (nice hygiene)
        if cleaned and not cleaned.endswith("\n"):
            cleaned += "\n"

        if cleaned != text:
            p.write_text(cleaned, encoding="utf-8", newline="\n")
            changed += 1

    print(f"Normalized {changed} file(s).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
