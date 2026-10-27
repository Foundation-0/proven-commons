#!/bin/sh
# Build every library in this workspace on its own, in addition to the
# joint `lake build Anthology AnthologyProofs` build. Run from the repo
# root, after `lake update` (or `lake build Anthology`) has fetched the
# pinned libraries into .lake/packages.
#
# The joint build cannot import most proof libraries, because their
# module names collide across packages (issue #4). So this script builds
# each package's upstream default targets, then each library repos.json
# lists for it, by name, because upstream default targets do not always
# include them all (bencode's leave out Spec and Proofs).
#
# Builds every package, then lists each failing target and exits 1. With
# a file argument, it also writes the repo names of the failing packages
# to that file, one per line, for `scripts/sync.py --keep-pin`.
cd "$(dirname "$0")/.." || exit 1
if [ ! -d .lake/packages ] || [ -z "$(ls .lake/packages)" ]; then
  echo "No packages in .lake/packages. Run 'lake update' first."
  exit 1
fi
targets=$(python3 -c '
import json
for r in json.load(open("repos.json"))["repos"]:
    if r["state"] == "included":
        print(r["package"], r["repo"], *[lib["name"] for lib in r["libs"]])
') || exit 1
# Running Lake inside a package writes a lake-manifest.json there when
# upstream does not commit one. Remove it again, or a later `lake update`
# cannot check out an upstream commit that does commit one.
tidy() {
  git -C "$1" ls-files --error-unmatch lake-manifest.json > /dev/null 2>&1 || rm -f "$1/lake-manifest.json"
}
failed=""
failed_repos=""
while read -r name repo libs; do
  echo "Building $name"
  (cd ".lake/packages/$name" && lake build) || { failed="$failed $name"; failed_repos="$failed_repos $repo"; }
  echo "Building $name libraries: $libs"
  # $libs is unquoted on purpose: one argument per library.
  # shellcheck disable=SC2086
  (cd ".lake/packages/$name" && lake build $libs) || { failed="$failed $name:libraries"; failed_repos="$failed_repos $repo"; }
  tidy ".lake/packages/$name"
done <<TARGETS
$targets
TARGETS
if [ -n "${1:-}" ]; then
  # shellcheck disable=SC2086
  printf '%s\n' $failed_repos | sort -u | sed '/^$/d' > "$1"
fi
if [ -n "$failed" ]; then
  echo "FAILED:$failed"
  exit 1
fi
echo "All packages built."
