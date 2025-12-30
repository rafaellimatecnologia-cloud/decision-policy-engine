from __future__ import annotations

from pathlib import Path
import unicodedata

# Pastas/arquivos que não queremos mexer
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "dist", "build", ".mypy_cache", ".ruff_cache"}

# Extensões tratadas como texto
TEXT_EXTS = {".py", ".md", ".toml", ".yml", ".yaml", ".txt", ".ini", ".cfg"}

# Arquivos sem extensão comuns em repositórios
TEXT_NAMES = {".editorconfig", "LICENSE", "SECURITY.md", "CHANGELOG.md", "CONTRIBUTING.md", "README.md"}

BIDI_BAD = {"LRE", "RLE", "PDF", "LRO", "RLO", "LRI", "RLI", "FSI", "PDI"}

def is_suspicious(ch: str) -> bool:
    # Remove “format chars” (inclui zero-width e BOM se estiver no meio do texto)
    if unicodedata.category(ch) == "Cf":
        return True
    # Remove controles bidi clássicos
    if unicodedata.bidirectional(ch) in BIDI_BAD:
        return True
    # Remove outros controles (exceto \n e \t)
    if unicodedata.category(ch) == "Cc" and ch not in ("\n", "\t"):
        return True
    return False

def normalize_text(text: str) -> str:
    # Normaliza quebras de linha
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    out = []
    changed = False

    for ch in text:
        # 1) remove caracteres suspeitos invisíveis
        if is_suspicious(ch):
            changed = True
            continue

        # 2) troca espaços unicode “especiais” por espaço normal
        # (NBSP, narrow no-break, etc.)
        if ch.isspace() and ch not in (" ", "\n", "\t"):
            out.append(" " if ch != "\n" else "\n")
            changed = True
            continue

        out.append(ch)

    result = "".join(out)

    # Garante newline final
    if result and not result.endswith("\n"):
        result += "\n"
        changed = True

    return result, changed

def should_process(p: Path) -> bool:
    if p.name in TEXT_NAMES:
        return True
    return p.suffix.lower() in TEXT_EXTS

def main() -> None:
    root = Path(".").resolve()
    touched = 0
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if not p.is_file():
            continue
        if not should_process(p):
            continue

        # Lê bytes e decodifica removendo BOM do início (utf-8-sig)
        raw = p.read_bytes()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            # Se não for UTF-8, não mexe (evita quebrar binários)
            continue

        normalized, changed = normalize_text(text)
        if changed:
            p.write_text(normalized, encoding="utf-8", newline="\n")
            touched += 1

    print(f"Normalized {touched} file(s).")

if __name__ == "__main__":
    main()
