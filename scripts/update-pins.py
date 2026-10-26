#!/usr/bin/env python3
"""Refresh every Proven-Commons rev in lakefile.toml to upstream main HEAD.

Run from the repo root:  python3 scripts/update-pins.py
Prints each change. Review the diff before committing: a pin update
changes what this repo certifies. Run `lake update` and
`lake build Anthology` after a pin update.
"""
import re
import subprocess
import sys
from pathlib import Path

LAKEFILE = Path(__file__).resolve().parent.parent / "lakefile.toml"
text = LAKEFILE.read_text()

# Each require block looks like:
#   [[require]]
#   name = "ip"
#   git = "https://github.com/Proven-Commons/ip"
#   rev = "<sha>"
pattern = re.compile(
    r'(git = "https://github\.com/Proven-Commons/([^"/]+)"\nrev = ")'
    r'[0-9a-f]{40}(")'
)


def head_sha(repo: str) -> str:
    out = subprocess.run(
        ["git", "ls-remote", f"https://github.com/Proven-Commons/{repo}.git", "HEAD"],
        capture_output=True, text=True, check=True, timeout=60,
    ).stdout
    return out.split()[0]


changed = False


def replace(match: re.Match) -> str:
    global changed
    repo = match.group(2)
    new = head_sha(repo)
    old = match.group(0)
    if new not in old:
        print(f"{repo}: {old.split('rev = ')[1]} -> {new}")
        changed = True
        return f'{match.group(1)}{new}{match.group(3)}'
    return old


text = pattern.sub(replace, text)
if changed:
    LAKEFILE.write_text(text)
    print("lakefile.toml updated. Review the diff before committing.")
else:
    print("No pin changes.")
    sys.exit(0)
