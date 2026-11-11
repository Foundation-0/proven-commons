#!/usr/bin/env python3
"""Token-stream Lean 4 source scanner for Verified Bar surface rules.

Complements scripts/audit.py (which checks kernel axioms via collectAxioms)
by scanning Lean source files for surface constructs that alter theorem
meaning or runtime code without adding kernel axioms: notation, macro,
syntax, elab, infix, @[extern], @[implemented_by], @[csimp], unsafe,
partial, opaque, sorry, admit, axiom, borrowed FFI (@&), and Lean/Lake
metaprogramming imports.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "repos.json"

@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    line: int
    col: int

FORBIDDEN_SOLO = {
    "sorry": "sorry", "admit": "admit", "axiom": "axiom",
    "unsafe": "unsafe", "partial": "partial", "opaque": "opaque",
    "local": "local modifier", "scoped": "scoped modifier",
}
FORBIDDEN_METAPROG = {
    "notation", "macro", "macro_rules", "syntax", "elab", "elab_rules",
    "infix", "infixl", "infixr", "prefix", "postfix",
}
FORBIDDEN_ATTRS = {
    "extern", "implemented_by", "csimp", "init", "builtin_init",
    "app_unexpander", "delab",
}
FORBIDDEN_PREFIXES = {
    ("Lean", "Elab"), ("Lean", "Meta"), ("Lean", "Parser"),
    ("IO", "Process"), ("IO", "FS"),
}

def tokenize_lean4(src: str) -> list[Token]:
    tokens: list[Token] = []
    n, i, line, col = len(src), 0, 1, 1
    def adv(k: int = 1) -> None:
        nonlocal i, line, col
        for _ in range(k):
            if i < n:
                line, col = (line + 1, 1) if src[i] == "\n" else (line, col + 1)
                i += 1
    while i < n:
        ch = src[i]
        if ch in " \t\r\n":
            adv(); continue
        if src.startswith("--", i):
            while i < n and src[i] != "\n": adv()
            continue
        if src.startswith("/-", i):
            depth = 1; adv(2)
            while i < n and depth > 0:
                if src.startswith("/-", i): depth += 1; adv(2)
                elif src.startswith("-/", i): depth -= 1; adv(2)
                else: adv()
            continue
        if ch == "r" and i + 1 < n and src[i + 1] in ("#", '"'):
            j, hashes = i + 1, 0
            while j < n and src[j] == "#": hashes += 1; j += 1
            if j < n and src[j] == '"':
                sl, sc = line, col; closer = '"' + ("#" * hashes); adv(j - i + 1)
                sb = i
                while i < n and not src.startswith(closer, i): adv()
                body = src[sb:i]
                if src.startswith(closer, i): adv(len(closer))
                tokens.append(Token("STRING", body, sl, sc)); continue
        if ch == '"':
            sl, sc = line, col; adv(); buf = []
            while i < n and src[i] != '"':
                if src[i] == "\\" and i + 1 < n: buf.append(src[i:i+2]); adv(2)
                else: buf.append(src[i]); adv()
            if i < n and src[i] == '"': adv()
            tokens.append(Token("STRING", "".join(buf), sl, sc)); continue
        if ch == "'" and i + 2 < n:
            if src[i + 1] == "\\" and i + 3 < n and src[i + 3] == "'":
                tokens.append(Token("CHAR", src[i:i+4], line, col)); adv(4); continue
            if src[i + 1] != "'" and src[i + 2] == "'":
                tokens.append(Token("CHAR", src[i:i+3], line, col)); adv(3); continue
        if ord(ch) == 0x00AB:
            sl, sc = line, col; adv(); sb = i
            while i < n and ord(src[i]) != 0x00BB: adv()
            ident = src[sb:i]
            if i < n and ord(src[i]) == 0x00BB: adv()
            tokens.append(Token("IDENT", ident, sl, sc)); continue
        if ch.isalpha() or ch == "_" or ord(ch) > 127:
            sl, sc, sb = line, col, i; adv()
            while i < n and (src[i].isalnum() or src[i] in ("_", "'", "?", "!") or ord(src[i]) > 127):
                if ord(src[i]) in (0x00AB, 0x00BB): break
                adv()
            tokens.append(Token("IDENT", src[sb:i], sl, sc)); continue
        if ch.isdigit():
            sl, sc, sb = line, col, i
            while i < n and (src[i].isalnum() or src[i] == "_"): adv()
            tokens.append(Token("NUMBER", src[sb:i], sl, sc)); continue
        if src.startswith("@&", i):
            tokens.append(Token("PUNCT", "@&", line, col)); adv(2); continue
        tokens.append(Token("PUNCT", ch, line, col)); adv()
    return tokens

def scan_lean_tokens(src: str, *, allow_sorry: bool = False) -> list[tuple[int, str]]:
    toks = tokenize_lean4(src)
    findings: list[tuple[int, str]] = []
    m = len(toks)
    for idx, tok in enumerate(toks):
        if tok.kind == "IDENT":
            if tok.text in FORBIDDEN_SOLO:
                if allow_sorry and tok.text == "sorry": continue
                findings.append((tok.line, FORBIDDEN_SOLO[tok.text]))
            if tok.text in FORBIDDEN_METAPROG:
                findings.append((tok.line, "notation or macro"))
            if tok.text in FORBIDDEN_ATTRS:
                back = [t.text for t in toks[max(0, idx - 8) : idx]]
                if "[" in back or "@" in back or "attribute" in back:
                    findings.append((tok.line, tok.text))
            if tok.text == "import" and idx + 1 < m and toks[idx + 1].kind == "IDENT":
                if toks[idx + 1].text in {"Lean", "Lake"}:
                    findings.append((tok.line, "import Lean/Lake"))
            if idx + 2 < m and toks[idx + 1].text == "." and toks[idx + 2].kind == "IDENT":
                pair = (tok.text, toks[idx + 2].text)
                if pair in FORBIDDEN_PREFIXES:
                    findings.append((tok.line, f"{pair[0]}.{pair[1]}"))
        elif tok.kind == "PUNCT" and tok.text == "@&":
            findings.append((tok.line, "borrowed FFI (@&)"))
    return findings

def compute_pinned_spec_hash(pkg_dir: Path, spec_files: Iterable[str], code_modules: Iterable[str]) -> str:
    h = hashlib.sha256()
    meta = ["lean-toolchain", "lakefile.toml", "lakefile.lean", "lake-manifest.json", "comparator.json"]
    paths = [pkg_dir / r for r in meta if (pkg_dir / r).is_file()]
    paths += [pkg_dir / r for r in sorted(set(spec_files)) if (pkg_dir / r).is_file()]
    for mod in sorted(set(code_modules)):
        p = pkg_dir / Path(*mod.split(".")).with_suffix(".lean")
        if p.is_file(): paths.append(p)
    seen: set[str] = set()
    for p in sorted(paths, key=lambda x: x.relative_to(pkg_dir).as_posix()):
        key = p.relative_to(pkg_dir).as_posix()
        if key in seen: continue
        seen.add(key); raw = p.read_bytes()
        h.update(f"FILE:{key}:{len(raw)}\n".encode("utf-8")); h.update(raw); h.update(b"\n")
    return h.hexdigest()

def scan_directory(pkg_dir: Path, spec_roots: set[str] | None = None) -> dict[str, list[tuple[int, str]]]:
    spec_roots = spec_roots or set()
    report: dict[str, list[tuple[int, str]]] = {}
    for path in sorted(pkg_dir.rglob("*.lean")):
        rel = path.relative_to(pkg_dir)
        if path.is_symlink() or any(p.startswith(".") for p in rel.parts): continue
        module = ".".join(rel.with_suffix("").parts)
        is_spec = module in spec_roots or module.endswith(".Spec") or module == "Spec"
        hits = scan_lean_tokens(path.read_text(encoding="utf-8", errors="replace"), allow_sorry=is_spec)
        if hits: report[rel.as_posix()] = hits
    return report

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="*", help="Lean package directories to scan")
    args = ap.parse_args(argv)
    targets: list[Path] = []
    if args.paths:
        targets = [Path(p) for p in args.paths]
    elif STATE.is_file():
        for rec in json.loads(STATE.read_text(encoding="utf-8")).get("repos", []):
            if rec.get("state") == "included":
                p = ROOT / ".lake" / "packages" / rec["package"]
                if p.is_dir(): targets.append(p)
    total = 0
    for pkg in targets:
        for rel, hits in scan_directory(pkg).items():
            for ln, reason in hits:
                print(f"{pkg.name}/{rel}:{ln}: {reason}"); total += 1
    print(f"Scanned {len(targets)} package(s); {total} surface finding(s).")
    return 1 if total else 0

if __name__ == "__main__":
    sys.exit(main())
