#!/usr/bin/env python3
"""Check that the pins agree everywhere this repo records them.

Run from the repo root:  python3 scripts/check-consistency.py
Needs no network and no Lean toolchain. Checks that:

- lakefile.toml, lean-toolchain, Anthology.lean, AnthologyProofs.lean and
  the generated block of README.md are exactly what scripts/sync.py
  renders from repos.json and audit.json, so none was edited by hand;
- every pin has a package in lake-manifest.json with the same name, URL
  and rev, and the manifest has no other package, except packages that a
  pinned package requires;
- audit.json has an audit of every pinned package at its pin, on the
  workspace toolchain, and no other.

Prints each mismatch and exits 1 if there is any.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync  # noqa: E402

ROOT = sync.ROOT
errors = []

state = json.loads(sync.STATE.read_text())
audit = sync.load_json(sync.AUDIT, {})
for path, text in sync.rendered(state, audit, sync.README.read_text()).items():
    if not (ROOT / path).is_file() or (ROOT / path).read_text() != text:
        errors.append(f"{path}: differs from what scripts/sync.py renders from repos.json "
                      "and audit.json; run python3 scripts/sync.py --render")

pins = {r["package"]: r for r in sync.included(state)}
manifest = json.loads((ROOT / "lake-manifest.json").read_text())
# The manifest quotes names that are not plain identifiers, e.g. «zip-pilot».
packages = {p["name"].strip("«»"): p for p in manifest["packages"]}
for name, rec in pins.items():
    pkg = packages.pop(name, None)
    if pkg is None:
        errors.append(f"{name}: pinned in lakefile.toml, not in lake-manifest.json; run lake update")
        continue
    if pkg["url"] != rec["url"]:
        errors.append(f"{name}: manifest url {pkg['url']}, pin {rec['url']}")
    if pkg["rev"] != rec["rev"] or pkg.get("inputRev") != rec["rev"]:
        errors.append(f"{name}: manifest rev {pkg['rev']}, pin {rec['rev']}; run lake update")
for name, pkg in packages.items():
    if not pkg.get("inherited"):
        errors.append(f"{name}: in lake-manifest.json, not in lakefile.toml; run lake update")

audited = audit.get("packages", {})
if audit and audit.get("toolchain") != state["toolchain"]:
    errors.append(f"audit.json: audited on {audit.get('toolchain')}, workspace is {state['toolchain']}")
for name, rec in pins.items():
    got = audited.get(name, {}).get("rev")
    if got != rec["rev"]:
        errors.append(f"{name}: audit.json audits {got[:12] if got else 'nothing'}, the pin is "
                      f"{rec['rev'][:12]}; build, then run scripts/audit.py")
for name in sorted(set(audited) - set(pins)):
    errors.append(f"{name}: in audit.json, not pinned")

for error in errors:
    print(error)
if errors:
    sys.exit(1)
print(f"{len(pins)} pins agree across repos.json, lakefile.toml, lake-manifest.json, "
      "audit.json and the generated files.")
