#!/bin/sh
# Install elan on a CI runner. elan then installs the toolchain that
# lean-toolchain names. elan is pinned to one release and checked against
# its SHA-256, as in Proven-Commons/mission bar/setup-lean.sh, so a change
# upstream cannot change the toolchain installer this repo trusts. To move
# to a new release, update both lines below together.
set -eu

ELAN_VERSION=v4.2.4
ELAN_SHA256=42b94d4244e8353142c456ec0e4ca6528fd898a6c604d4059f494e706e431f63

tmp=$(mktemp -d)
curl -sSfL -o "$tmp/elan.tar.gz" \
  "https://github.com/leanprover/elan/releases/download/$ELAN_VERSION/elan-x86_64-unknown-linux-gnu.tar.gz"
echo "$ELAN_SHA256  $tmp/elan.tar.gz" | sha256sum -c -
tar -xzf "$tmp/elan.tar.gz" -C "$tmp"
"$tmp/elan-init" -y --default-toolchain none
rm -rf "$tmp"
if [ -n "${GITHUB_PATH:-}" ]; then
  echo "$HOME/.elan/bin" >> "$GITHUB_PATH"
fi
