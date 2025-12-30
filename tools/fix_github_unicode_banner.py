from __future__ import annotations

import unicodedata
from pathlib import Path

BIDI_BAD = {"LRE", "RLE", "PDF", "LRO", "RLO", "LRI", "RLI", "FSI", "PDI"}

# Foque apenas nos arquivos que o GitHub está marcando na PR
TARGETS = [
    Path(".github/workflows/ci.yml"),
    Path("CHANGELOG.md"),
    Path("CONTRIBUTING.md"),
    Path("LICENSE"),
    Path("README.md"),
    Path("SECURITY.md"),
    Path("pyproject.toml"),
    Path("examples/demo_cli.py"),
]

def scrub(text: str) -> str:
    # Normaliza line separators e NBSP
    text = (
        text.replace("\u2028", "\n")
            .replace("\u2029", "\n")
            .replace("\u00A0", " ")
            .replace("\r\n", "\n")
            .replace("\r", "\n")
    )

    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        bidi = unicodedata.bidirectional(ch)

        # remove "format chars" (zero-width etc.) e bidi controls
        if cat == "Cf" or bidi in BIDI_BAD:
            continue

        # remove control chars, exceto TAB e LF
        if cat == "Cc" and ch not in ("\n", "\t"):
            continue

        out.append(ch)

    cleaned = "".join(out)
    if cleaned and not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned

def main() -> None:
    changed = 0

    for p in TARGETS:
        if not p.exists():
            continue

        raw = p.read_bytes()
        # utf-8-sig remove BOM automaticamente
        text = raw.decode("utf-8-sig", errors="strict")

        cleaned = scrub(text)
        if cleaned != text:
            p.write_text(cleaned, encoding="utf-8", newline="\n")
            changed += 1

    print(f"Fixed {changed} file(s).")

if __name__ == "__main__":
    main()
