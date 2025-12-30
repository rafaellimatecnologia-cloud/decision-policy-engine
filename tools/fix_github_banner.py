from __future__ import annotations

import unicodedata
from pathlib import Path

TARGETS = [
    Path(".editorconfig"),
    Path(".github/workflows/ci.yml"),
    Path("CHANGELOG.md"),
    Path("CONTRIBUTING.md"),
    Path("LICENSE"),
    Path("README.md"),
    Path("SECURITY.md"),
    Path("examples/demo_cli.py"),
    Path("pyproject.toml"),
]

BIDI_BAD = {"LRE", "RLE", "PDF", "LRO", "RLO", "LRI", "RLI", "FSI", "PDI"}

def is_bad(ch: str) -> bool:
    cat = unicodedata.category(ch)
    if cat == "Cf":  # zero-width / format chars
        return True
    if unicodedata.bidirectional(ch) in BIDI_BAD:
        return True
    if cat == "Cc" and ch not in ("\n", "\t"):  # keep LF + TAB only
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
        text = raw.decode("utf-8-sig", errors="strict")  # strips BOM if present
        cleaned = scrub(text)

        # FORCE rewrite (UTF-8 no BOM + LF) even if "looks the same"
        p.write_text(cleaned, encoding="utf-8", newline="\n")
        rewrote += 1

    print(f"Rewrote {rewrote} file(s).")

if __name__ == "__main__":
    main()
