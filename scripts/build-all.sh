#!/bin/sh
# Build every library in this workspace on its own, in addition to the
# joint `lake build Anthology` build. Run from the repo root, after
# `lake update` has fetched the pinned libraries into .lake/packages.
# Stops at the first failing library. Prints the failing package name.
set -e
cd "$(dirname "$0")/.."
for pkg in .lake/packages/*; do
  name=$(basename "$pkg")
  echo "Building $name"
  (cd "$pkg" && lake build) || { echo "FAILED: $name"; exit 1; }
done
echo "All packages built."
