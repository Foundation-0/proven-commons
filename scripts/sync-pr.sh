#!/bin/sh
# Open, update or close the sync pull request, from the folder that
# scripts/sync-build.sh wrote. Run from a checkout of main:
#
#   scripts/sync-pr.sh SYNC_DIR
#
# This runs in the workflow job that can write to the repo. So it copies
# only the files the sync generates, and runs nothing that came from
# upstream. Needs gh, with GH_TOKEN set. Set DISPATCH_CI=true when GH_TOKEN
# is the workflow's own token: GitHub does not start CI for a pull request
# that token opens or pushes to, so this starts the CI workflow itself.
set -eu
src=${1:?usage: scripts/sync-pr.sh SYNC_DIR}
branch=sync/upstream
title="Sync with upstream Proven-Commons"
FILES="repos.json lakefile.toml lean-toolchain Anthology.lean AnthologyProofs.lean README.md lake-manifest.json audit.json"
for f in $FILES; do
  [ -f "$src/$f" ] && cp "$src/$f" "$f"
done
open=$(gh pr list --head "$branch" --base main --state open --json number --jq '.[0].number // empty')

# shellcheck disable=SC2086
if git diff --quiet -- $FILES; then
  echo "main already matches upstream."
  if [ -n "$open" ]; then
    gh pr close "$open" --delete-branch \
      --comment "main already matches upstream, so this sync is no longer needed."
  fi
  exit 0
fi

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git checkout -q -B "$branch"
# shellcheck disable=SC2086
git add -- $FILES
git commit -q -F "$src/commit-message.txt"

# Push only when the content differs from what the branch already holds,
# so a daily run with nothing new does not restart CI, dismiss an
# approval, or reopen a sync pull request someone closed.
if git fetch -q origin "$branch" 2>/dev/null && git diff --quiet FETCH_HEAD HEAD; then
  echo "The $branch branch already holds these changes."
  [ -z "$open" ] && echo "Its pull request was closed. It opens again once upstream moves."
  exit 0
fi
git push -q -f origin "$branch"
if [ -n "$open" ]; then
  gh pr edit "$open" --title "$title" --body-file "$src/pr-body.md"
else
  gh pr create --base main --head "$branch" --title "$title" --body-file "$src/pr-body.md"
fi
if [ "${DISPATCH_CI:-false}" = "true" ]; then
  gh workflow run ci.yml --ref "$branch"
fi
