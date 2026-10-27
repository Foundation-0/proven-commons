#!/bin/sh
# Run a full sync, as the sync workflow does, and put the result in a
# folder for scripts/sync-pr.sh. Run from a clean checkout of main, with
# elan installed:
#
#   scripts/sync-build.sh OUT_DIR
#
# Syncs the pins, regenerates lake-manifest.json, builds every package,
# the joint build and the proof audit, and renders the README. A repo
# whose new default branch head fails to build keeps its current pin, or
# stays out of the workspace if it is new, and the build runs again.
#
# OUT_DIR gets the generated files, pr-body.md and commit-message.txt.
# A failing build does not stop the script: the pull request reports it,
# and its CI fails. A sync that cannot read upstream exits 1.
set -u
cd "$(dirname "$0")/.." || exit 1
out=${1:?usage: scripts/sync-build.sh OUT_DIR}
mkdir -p "$out"
tmp=$(mktemp -d)
FILES="repos.json lakefile.toml lean-toolchain Anthology.lean AnthologyProofs.lean README.md lake-manifest.json audit.json"
cp repos.json "$tmp/previous.json"
cp audit.json "$tmp/previous-audit.json"

python3 scripts/sync.py --previous "$tmp/previous.json" --report "$tmp/changes.md" || exit 1
# shellcheck disable=SC2086
if git diff --quiet -- $FILES; then
  echo "Upstream has not moved. Nothing to build."
  for f in $FILES; do cp "$f" "$out/$f"; done
  exit 0
fi

result() { if [ "$2" -eq 0 ]; then echo "- $1: passed" >> "$tmp/results.md"; else echo "- $1: **failed**" >> "$tmp/results.md"; fi; }
: > "$tmp/results.md"

# Clear manifests that earlier Lake runs inside packages left untracked,
# for example in a restored cache; see scripts/build-all.sh.
for pkg in .lake/packages/*/; do
  [ -d "$pkg" ] || continue
  git -C "$pkg" ls-files --error-unmatch lake-manifest.json > /dev/null 2>&1 || rm -f "$pkg/lake-manifest.json"
done
lake update
result "\`lake update\`" $?
scripts/build-all.sh "$tmp/failed"
status=$?
if [ -s "$tmp/failed" ]; then
  kept=$(tr '\n' ' ' < "$tmp/failed" | sed 's/ *$//')
  echo "Keeping the current pin of: $kept"
  # shellcheck disable=SC2086
  python3 scripts/sync.py --previous "$tmp/previous.json" --report "$tmp/changes.md" --keep-pin $kept || exit 1
  lake update
  scripts/build-all.sh
  status=$?
  echo "- These repos failed to build at their new head, so each keeps its current pin, or stays out of the workspace if it is new: $kept." >> "$tmp/results.md"
fi
result "\`scripts/build-all.sh\`, every package and library on its own" $status
lake build Anthology AnthologyProofs
result "\`lake build Anthology AnthologyProofs\`" $?
python3 scripts/audit.py
result "\`scripts/audit.py\`, the proof audit" $?
python3 scripts/sync.py --render > /dev/null
python3 scripts/check-consistency.py
result "\`scripts/check-consistency.py\`" $?

# How each package's audit changed, from the README cells.
python3 - "$tmp/previous.json" "$tmp/previous-audit.json" > "$tmp/audit.md" <<'PY'
import json, sys
sys.path.insert(0, "scripts")
import sync
old_state, old_audit = (json.load(open(p)) for p in sys.argv[1:3])
new_state, new_audit = json.load(open("repos.json")), json.load(open("audit.json"))
old = {r["repo"]: sync.audit_cell(r, old_audit) for r in sync.included(old_state)}
for r in sync.included(new_state):
    cell = sync.audit_cell(r, new_audit)
    if old.get(r["repo"]) != cell:
        print(f"- **{r['repo']}**: {old.get(r['repo'], 'not in the workspace')} → {cell}")
PY

for f in $FILES; do cp "$f" "$out/$f"; done
{
  echo "Sync with upstream Proven-Commons"
  echo
  cat "$tmp/changes.md"
} > "$out/commit-message.txt"
{
  echo "The [sync workflow](${RUN_URL:-.github/workflows/sync.yml}) found changes in the Proven-Commons org."
  echo
  echo "## Changes"
  echo
  cat "$tmp/changes.md"
  echo
  echo "## Proof audit changes"
  echo
  if [ -s "$tmp/audit.md" ]; then cat "$tmp/audit.md"; else echo "- None."; fi
  echo
  echo "## Build"
  echo
  cat "$tmp/results.md"
  echo
  echo "## Review"
  echo
  echo "A pin update changes what this repo certifies. Before approving, read the upstream diff"
  echo "behind each pin move, and the audit changes above. This merges under the org's merge SOP."
  echo
  echo "This branch is rewritten on each sync run. To fix a problem, fix it upstream, or hold"
  echo "the repo in \`sync.toml\` through a pull request to main, rather than pushing here."
} > "$out/pr-body.md"
echo "Wrote the sync result to $out."
