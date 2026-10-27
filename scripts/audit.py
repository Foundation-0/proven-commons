#!/usr/bin/env python3
"""Audit the axioms behind every declaration in the workspace packages.

Run from the repo root, after `lake build Anthology` and
`scripts/build-all.sh` have built every package and its proof library:

    python3 scripts/audit.py [--check]

For each package in repos.json, this imports its main and proof
libraries into one Lean file, and runs Lean's `collectAxioms`, the check
behind `#print axioms`, on every theorem and definition the package
declares. It records, per package, how many theorems the source states,
which declarations depend on `sorryAx` or on any axiom beyond the three
standard ones (propext, Classical.choice, Quot.sound), and any `axiom` the
package declares. For a package with a comparator.json, it also checks
that each named theorem is present in the proof library and uses only the
permitted axioms.

An `example` has no name, so `collectAxioms` cannot reach it. The audit
counts them, and reads the build log of the main and proof libraries,
which Lake replays from its cache, for `sorry` warnings, which covers
examples too.

It writes audit.json. With --check it writes nothing, and exits 1 if the
result differs from the committed audit.json, so the record in README.md
cannot drift from what the pinned code proves.

It does not import a package's `Spec` library: that holds the statements,
with `sorry`, under the same names as the proofs. The audit checks axioms
only. Upstream's verified bar adds source rules (no `implemented_by`,
`extern`, `unsafe` and so on) that this audit does not repeat.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from sync import strip_comments

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "repos.json"
AUDIT = ROOT / "audit.json"
STANDARD = {"propext", "Classical.choice", "Quot.sound"}
SORRY = "sorryAx"
TIMEOUT = 30 * 60
EXAMPLE = re.compile(r"(?m)^[ \t]*(@\[[^\]]*\][ \t]*)?example\b")
SORRY_WARNING = re.compile(r"warning: (\S+?):(\d+):\d+: declaration uses [`']sorry[`']")

LEAN = """import Lean
{imports}

open Lean

/-- Top-level module names of the audited package. -/
def auditNamespaces : Array Name := #[{namespaces}]

#eval show CoreM Unit from do
  let env ← getEnv
  for (name, info) in env.constants.map₁.toList do
    let some idx := env.getModuleIdxFor? name | continue
    let mod := env.header.moduleNames[idx.toNat]!
    unless auditNamespaces.contains mod.getRoot do continue
    let kind := match info with
      | .thmInfo _ => "theorem"
      | .axiomInfo _ => "axiom"
      | .defnInfo _ => "def"
      | .opaqueInfo _ => "opaque"
      | _ => ""
    if kind.isEmpty then continue
    -- Declarations the source states have a range; generated ones do not.
    let src := if (← findDeclarationRanges? name).isSome then "src" else "gen"
    let axs ← collectAxioms name
    IO.println s!"AUDIT\\t{{kind}}\\t{{src}}\\t{{name}}\\t{{",".intercalate (axs.toList.map toString)}}"
"""

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_']*")


def lean_name(module):
    return ".".join(p if IDENT.fullmatch(p) else f"«{p}»" for p in module.split("."))


def tidy(pkg_dir):
    """Running Lake inside a package writes a lake-manifest.json there when
    upstream does not commit one. Remove it again, or a later `lake update`
    cannot check out an upstream commit that does commit one."""
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "lake-manifest.json"],
                             cwd=pkg_dir, capture_output=True).returncode == 0
    if not tracked:
        (pkg_dir / "lake-manifest.json").unlink(missing_ok=True)


def audit_package(rec):
    """The audit record for one package, from a fresh Lean run."""
    pkg_dir = ROOT / ".lake" / "packages" / rec["package"]
    try:
        return run_audit(rec, pkg_dir)
    finally:
        if pkg_dir.is_dir():
            tidy(pkg_dir)


def run_audit(rec, pkg_dir):
    result = {"repo": rec["repo"], "rev": rec["rev"]}
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=pkg_dir, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return dict(result, error="package not fetched; run lake update")
    if head != rec["rev"]:
        return dict(result, error=f"fetched copy is at {head[:12]}, not the pin; run lake update")
    imports = [m for lib in rec["libs"] if lib["kind"] in ("main", "proofs") for m in lib["roots"]]
    src = LEAN.format(imports="\n".join(f"import {lean_name(m)}" for m in imports),
                      namespaces=", ".join(f"Name.mkSimple {json.dumps(n)}" for n in rec["namespaces"]))
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Audit.lean"
        path.write_text(src)
        try:
            run = subprocess.run(["lake", "env", "lean", str(path)], cwd=pkg_dir,
                                 capture_output=True, text=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return dict(result, error=f"Lean did not finish in {TIMEOUT // 60} minutes")
    rows = [line.split("\t")[1:] for line in run.stdout.splitlines() if line.startswith("AUDIT\t")]
    if run.returncode != 0 or not rows:
        tail = " / ".join((run.stdout + run.stderr).strip().splitlines()[-3:])
        return dict(result, error=f"Lean exited {run.returncode}: {tail[:300]}")
    libs = [lib["name"] for lib in rec["libs"] if lib["kind"] in ("main", "proofs")]
    build = subprocess.run(["lake", "build", *libs], cwd=pkg_dir, capture_output=True,
                           text=True, timeout=TIMEOUT)
    if build.returncode != 0:
        return dict(result, error=f"lake build {' '.join(libs)} failed; run scripts/build-all.sh")
    sorry_lines = sorted({f"{f}:{n}" for f, n in SORRY_WARNING.findall(build.stdout + build.stderr)},
                         key=lambda x: (x.split(":")[0], int(x.split(":")[1])))
    axioms = {name: set(filter(None, axs.split(","))) for _, _, name, axs in rows}
    nonstandard = {}
    for name, axs in axioms.items():
        for ax in axs - STANDARD - {SORRY}:
            nonstandard.setdefault(ax, []).append(name)
    result.update(
        declarations=len(rows),
        theorems=sum(1 for kind, src, _, _ in rows if kind == "theorem" and src == "src"),
        examples=count_examples(pkg_dir, rec),
        sorry_in_build=sorry_lines,
        axioms=sorted(set().union(*axioms.values())),
        sorry=sorted(n for n, axs in axioms.items() if SORRY in axs),
        nonstandard={ax: sorted(ns) for ax, ns in sorted(nonstandard.items())},
        package_axioms=sorted(name for kind, _, name, _ in rows if kind == "axiom"),
        spec=named_check(pkg_dir, rows, axioms),
    )
    return result


def count_examples(pkg_dir, rec):
    """The `example`s in the package's own modules, except the spec
    library roots, which the audit does not import."""
    skip = {m for lib in rec["libs"] if lib["kind"] == "spec" for m in lib["roots"]}
    count = 0
    for path in sorted(pkg_dir.rglob("*.lean")):
        rel = path.relative_to(pkg_dir)
        if path.is_symlink() or any(p.startswith(".") for p in rel.parts):
            continue
        module = ".".join(rel.with_suffix("").parts)
        if module in skip or module.split(".")[0] not in rec["namespaces"]:
            continue
        count += len(EXAMPLE.findall(strip_comments(path.read_text(errors="replace"))))
    return count


def named_check(pkg_dir, rows, axioms):
    """For a package with a comparator.json: are its named theorems
    present in the proof library, with only the permitted axioms?"""
    path = pkg_dir / "comparator.json"
    if not path.is_file():
        return None
    cfg = json.loads(path.read_text())
    names = cfg.get("theorem_names") or []
    permitted = set(cfg.get("permitted_axioms") or STANDARD) & STANDARD
    theorems = {name for kind, _, name, _ in rows if kind == "theorem"}
    missing = sorted(n for n in names if n not in theorems)
    unproved = sorted(n for n in names if n in theorems and not axioms[n] <= permitted)
    return {"named": len(names), "proved": len(names) - len(missing) - len(unproved),
            "missing": missing, "unproved": unproved}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    state = json.loads(STATE.read_text())
    packages = {}
    for rec in state["repos"]:
        if rec["state"] != "included":
            continue
        print(f"Auditing {rec['package']}", flush=True)
        packages[rec["package"]] = audit_package(rec)
        a = packages[rec["package"]]
        print("  " + (a.get("error") or f"{a['theorems']} theorems, {a['declarations']} declarations, "
                      f"axioms: {', '.join(a['axioms']) or 'none'}"), flush=True)
    audit = {"toolchain": state["toolchain"], "packages": dict(sorted(packages.items()))}
    text = json.dumps(audit, indent=2) + "\n"
    failed = [p for p, a in packages.items() if a.get("error")]
    if args.check:
        old = json.loads(AUDIT.read_text()) if AUDIT.is_file() else {}
        if old != audit:
            for p in sorted(set(old.get("packages", {})) | set(packages)):
                if old.get("packages", {}).get(p) != packages.get(p):
                    print(f"{p}: audit.json records {json.dumps(old.get('packages', {}).get(p))}, "
                          f"the audit now gives {json.dumps(packages.get(p))}")
            if old.get("toolchain") != audit["toolchain"]:
                print(f"toolchain: audit.json records {old.get('toolchain')}, workspace is {audit['toolchain']}")
            print("audit.json is out of date. Run scripts/audit.py, then scripts/sync.py --render.")
            return 1
        print(f"audit.json matches the audit of {len(packages)} packages.")
        return 1 if failed else 0
    AUDIT.write_text(text)
    print(f"wrote audit.json ({len(packages)} packages)")
    if failed:
        print(f"audit failed for: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
