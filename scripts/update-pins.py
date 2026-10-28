#!/usr/bin/env python3
"""Refresh every Proven-Commons rev in lakefile.toml to upstream main HEAD.

Run from the repo root:  python3 scripts/update-pins.py [--check]
Prints each change, and updates the pinned commit column of the README
table to match. Review the diff before committing: a pin update changes
what this repo certifies. Run `lake update` and `lake build Anthology`
after a pin update, and commit the regenerated lake-manifest.json.

With --check, writes nothing, and exits 1 if any pin is behind upstream.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAKEFILE = ROOT / "lakefile.toml"
README = ROOT / "README.md"
check = "--check" in sys.argv[1:]
text = LAKEFILE.read_text()
readme = README.read_text()

# Each require block looks like:
#   [[require]]
#   name = "ip"
#   git = "https://github.com/Proven-Commons/ip"
#   rev = "<sha>"
pattern = re.compile(
    r'(git = "https://github\.com/Proven-Commons/([^"/]+)"\nrev = ")'
    r'([0-9a-f]{40})(")'
)


def head_sha(repo: str) -> str:
    try:
        out = subprocess.run(
            ["git", "ls-remote", f"https://github.com/Proven-Commons/{repo}.git", "HEAD"],
            capture_output=True, text=True, check=True, timeout=60,
        ).stdout
    except subprocess.CalledProcessError as e:
        reason = ((e.stderr or "") + (e.stdout or "")).strip() or f"git exited with status {e.returncode}"
        print(f"Failed to fetch HEAD for repository '{repo}': {reason}", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"Failed to fetch HEAD for repository '{repo}': timed out after 60s", file=sys.stderr)
        sys.exit(1)
    try:
        return out.split()[0]
    except IndexError:
        print(f"Failed to fetch HEAD for repository '{repo}': empty response from ls-remote", file=sys.stderr)
        sys.exit(1)


changed = False

# Report require blocks the pin pattern does not cover so none are silently skipped.
require_re = re.compile(r'\[\[require\]\]\nname = "([^"]+)"\ngit = "([^"]+)"\nrev = "([^"]+)"')
for req in require_re.finditer(text):
    req_name, git_url = req.group(1), req.group(2)
    if not pattern.search(req.group(0)):
        print(f"Skipped {req_name}: git URL {git_url} did not match Proven-Commons pin pattern; leaving pin unchanged.")


def replace(match: re.Match) -> str:
    global changed, readme
    repo, old = match.group(2), match.group(3)
    new = head_sha(repo)
    if new == old:
        return match.group(0)
    print(f"{repo}: {old} -> {new}")
    changed = True
    row = f"| {old[:12]} |"
    if row in readme:
        readme = readme.replace(row, f"| {new[:12]} |")
    else:
        print(f"  README has no row with {old[:12]}; update it by hand.")
    return f"{match.group(1)}{new}{match.group(4)}"


text = pattern.sub(replace, text)
if not changed:
    print("No pin changes.")
elif check:
    print("Pins are behind upstream main. Run scripts/update-pins.py.")
    sys.exit(1)
else:
    LAKEFILE.write_text(text)
    README.write_text(readme)
    print("lakefile.toml and README.md updated. Review the diff before committing.")
