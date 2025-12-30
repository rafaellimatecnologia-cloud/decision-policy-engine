from __future__ import annotations

import unicodedata
from pathlib import Path

TARGETS = [
    Path(".github/workflows/ci.yml"),
    Path("CHANGELOG.md"),
]

BIDI_BAD = {"LRE", "RLE", "PDF", "LRO", "RLO", "LRI", "RLI", "FSI", "PDI"}

def is_bad(ch: str) -> bool:
    cat = unicodedata.category(ch)
    if cat == "Cf":  # format chars (zero-width etc.)
        return True
    if unicodedata.bidirectional(ch) in BIDI_BAD:
        return True
    if cat == "Cc" and ch not in ("\n", "\t"):  # remove other control chars
        return True
    return False

def scrub(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = "".join(ch for ch in text if not is_bad(ch))
    if cleaned and not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned

def main() -> None:
    rewrote = 0

    for p in TARGETS:
        if not p.exists():
            print("skip:", p)
            continue

        raw = p.read_bytes()
        had_bom = raw.startswith(b"\xEF\xBB\xBF")
        had_cr = (b"\r" in raw)

        text = raw.decode("utf-8-sig", errors="strict")  # strips BOM for decode
        cleaned = scrub(text)

        # FORCE rewrite if BOM existed, CRLF existed, or content changed after scrub
        if had_bom or had_cr or cleaned != text:
            p.write_text(cleaned, encoding="utf-8", newline="\n")
            rewrote += 1

    print(f"Rewrote {rewrote} file(s).")

if __name__ == "__main__":
    main()
