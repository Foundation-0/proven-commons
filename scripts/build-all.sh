#!/bin/sh
# Build every library in this workspace on its own, in addition to the
# joint `lake build Anthology` build. Run from the repo root, after
# `lake update` (or `lake build Anthology`) has fetched the pinned
# libraries into .lake/packages.
#
# `lake build Anthology` imports each package's main library only, so it
# compiles no proofs. This script builds each package's upstream default
# targets, then its `Proofs` library if it has one, because upstream
# default targets do not always include it (bencode's do not).
#
# Builds every package, then lists each failing target and exits 1.
cd "$(dirname "$0")/.." || exit 1
if [ ! -d .lake/packages ] || [ -z "$(ls .lake/packages)" ]; then
  echo "No packages in .lake/packages. Run 'lake update' first."
  exit 1
fi
failed=""
for pkg in .lake/packages/*; do
  name=$(basename "$pkg")
  echo "Building $name"
  (cd "$pkg" && lake build) || failed="$failed $name"
  if grep -qE '^name = "Proofs"|^lean_lib Proofs' "$pkg"/lakefile.* 2>/dev/null; then
    echo "Building $name Proofs"
    (cd "$pkg" && lake build Proofs) || failed="$failed $name:Proofs"
  fi
done
if [ -n "$failed" ]; then
  echo "FAILED:$failed"
  exit 1
fi
echo "All packages built."
