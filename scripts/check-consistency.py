#!/usr/bin/env python3
"""Check that the pins agree everywhere this repo records them.

Run from the repo root:  python3 scripts/check-consistency.py
Needs no network and no Lean toolchain. Checks that:

- every require in lakefile.toml has a package in lake-manifest.json with
  the same name, URL and rev, and the manifest has no other package;
- every require has a row in the README library table whose pinned
  commit is the first 12 characters of its rev.

Prints each mismatch and exits 1 if there is any.
"""
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []

requires = tomllib.loads((ROOT / "lakefile.toml").read_text()).get("require", [])
manifest = json.loads((ROOT / "lake-manifest.json").read_text())
# The manifest quotes names that are not plain identifiers, e.g. «zip-pilot».
packages = {p["name"].strip("«»"): p for p in manifest["packages"]}

for req in requires:
    name, url, rev = req["name"], req["git"], req["rev"]
    pkg = packages.pop(name, None)
    if pkg is None:
        errors.append(f"{name}: in lakefile.toml, not in lake-manifest.json")
        continue
    if pkg["url"] != url:
        errors.append(f"{name}: manifest url {pkg['url']}, lakefile {url}")
    if pkg["rev"] != rev or pkg.get("inputRev") != rev:
        errors.append(f"{name}: manifest rev {pkg['rev']}, lakefile {rev}")
for name in packages:
    errors.append(f"{name}: in lake-manifest.json, not in lakefile.toml")

# Library table rows: | repo | description | pinned commit | In workspace |
rows = dict(re.findall(
    r"^\| ([\w-]+) \|.*\| ([0-9a-f]{12}) \| Yes \|$",
    (ROOT / "README.md").read_text(), re.M,
))
for req in requires:
    repo = req["git"].rstrip("/").rsplit("/", 1)[-1]
    row = rows.pop(repo, None)
    if row is None:
        errors.append(f"{repo}: no row in the README library table")
    elif row != req["rev"][:12]:
        errors.append(f"{repo}: README pins {row}, lakefile {req['rev'][:12]}")
for repo in rows:
    errors.append(f"{repo}: in the README library table, not in lakefile.toml")

for error in errors:
    print(error)
if errors:
    sys.exit(1)
print(f"{len(requires)} pins agree across lakefile.toml, lake-manifest.json and README.md.")
