# proven-commons

Anthology of Lean builds from the Proven-Commons org.

## Purpose

This repo exists to collect, in one place, all the libraries and software
built in the Proven-Commons org in Lean: the parsers, codecs, extractors,
and their executables listed in the table below.

A reader who wants the whole collection should not have to track 24
separate library repos, each with its own version and toolchain. This repo gives
that reader one place to fetch, one toolchain, and one joint build, with
each item pinned to a specific upstream commit.

This repo is a compilation, not a new development home and not a fork.
Each library and piece of software stays in its own upstream repo, and
development, claims, issues, and pull requests stay there. Attribution
stays upstream. If this repo and an upstream repo disagree, the upstream
repo wins.

Scope: this repo covers the Proven-Commons library and software repos.
It does not cover the Proven-Commons mission repo, which holds the org's
structure and candidate lists, or its site repo. Contributors should go
to the upstream repo for the piece they want to work on, not here.

## What a Lean rewrite is for

Lean lets code and a proof about that code live together. A parser takes
input it does not control, such as a file or a network message. Tests check
only the inputs someone thought to try. A proof checks a stated property for
every input. That is why these libraries are rebuilt in Lean: to turn a
parser from something that seems to work into something whose stated
behavior is guaranteed for all inputs.

A proof only proves the properties that were written down. It does not prove
the specification itself is right, and it does not make the code fast. The
table below uses each upstream repo's own description. It does not claim a
proof status that has not been checked for that repo.

## Requirements

- A Lean toolchain manager, such as elan, that can install the toolchain in
  `lean-toolchain`.
- Lake, which ships with the Lean toolchain.
- Git.

This draft was written without Lake on the drafting machine, so the joint
build below has not been run yet. The first build, in CI or by a reviewer
with Lake installed, is the check that matters. See "Status of this draft".

## Use

Fetch the pinned libraries:

```
lake update
```

Build the whole collection through the aggregator library:

```
lake build Anthology
```

Build one library on its own, from its fetched copy:

```
lake build --dir .lake/packages/ip
```

The package names in `lakefile.toml` differ from the repo names in four
cases: `redis` is package `resp`, `utf` is package `utf8`, `rfc` is package
`rfc3339`, and `zip` is package `zip-pilot` with `tar` as `tar-pilot`. The
table uses repo names. The lakefile uses package names.

## Update pins

Pins are a point in time snapshot, checked 2026-10-26. Upstream moves, so a
pin goes stale. To refresh all pins to the current upstream main branch:

```
python3 scripts/update-pins.py
```

Review the resulting diff before committing it. A pin update is a change to
what this repo certifies, not a routine bump. Run `lake update` and
`lake build Anthology` after a pin update, and commit the generated
`lake-manifest.json` with the new pins.

## Libraries

All 18 libraries with a lakefile on upstream main are included as Lake
requirements. All use toolchain `leanprover/lean4:v4.35.0` upstream, and
none of them requires another library in this list, which is why a single
workspace works without dependency conflicts.

| Repo | What it is | Pinned commit | In workspace |
| --- | --- | --- | --- |
| bencode | Lean Bencode parser | de718a10ccbb | Yes |
| codec | Lean codec | 74ae50b94b14 | Yes |
| csv | Lean CSV parser and printer (RFC 4180) | 4ceedb42f999 | Yes |
| dns | Lean DNS wire header and question parser (RFC 1035) | a7cad62c0164 | Yes |
| ip | Lean IP address parser and canonical printer | 09f2a06fddcc | Yes |
| json | Lean JSON | 4642e51aa9d3 | Yes |
| pep440 | Lean PEP 440 version parser and precedence | 3ab869050a06 | Yes |
| png | Lean PNG chunk parser with CRC-32 check | df3035120ec6 | Yes |
| protobuf | Lean Protobuf wire format codec | babcab706e42 | Yes |
| redis | Lean Redis | 7ff41f249a92 | Yes |
| rfc | Lean RFC 3339 timestamp parser | 79f30cd0fbbd | Yes |
| semver | Lean semver | df74c98d5521 | Yes |
| tar | Lean-verified tar (ustar) extractor with a proved no-escape extraction gate | 7517a86223e6 | Yes |
| toml | Lean TOML parser and printer | ca8a615c0492 | Yes |
| utf | Lean UTF-8 codec | 276115161f6c | Yes |
| uuid | Lean UUID parser and printer (RFC 9562) | b5478df3c95b | Yes |
| websocket | Lean WebSocket frame parser (RFC 6455, section 5) | b8db7cd36428 | Yes |
| zip | Lean zip | 2cf824fde49f | Yes |

Six more upstream library repos are listed here but are not requirements
yet, because their main branch is a README only, with no lakefile:

| Repo | What it is | Main branch head |
| --- | --- | --- |
| bech32 | Lean rewrite - bech32: Bech32 and Bech32m strings (BIP 173, BIP 350) | 0097276e1fc4 |
| cbor | Lean CBOR decoder (RFC 8949) | 442c4fb80407 |
| hostname | Lean hostname | 9be3e5840e39 |
| http | Lean HTTP request-line and header parser (RFC 9112) | e3a22428d5db |
| messagepack | Lean MessagePack decoder | 491201adeddd |
| punycode | Lean punycode | 6b5bf7b24ab2 |

Add one of these to `lakefile.toml` and `Anthology.lean` when its upstream
main branch gains a lakefile and a library module. Do not add a branch
commit as a pin: pins track upstream main, so the anthology always reflects
merged work, not work in progress.

## Status

This repo is on branch `amp-sai/anthology-draft`, under PR #2, with
remaining work tracked in issue #1. The main branch still contains only
its initial README, two lines long, until PR #2 merges.

Build, verified twice on Lean 4.35.0, at the pinned commits:

- `lake update` fetched all 18 requirements with no errors. The
  generated `lake-manifest.json` is committed on this branch and matches
  the lakefile pins.
- `lake build Anthology` passed, 101 jobs. Warnings are linter warnings,
  mostly unused simp arguments in WebSocket, and deprecation warnings
  in ZipPilot.
- `scripts/build-all.sh` builds all 18 packages on their own. That run
  was verified by the PR reviewer. A second run on this machine also
  passed, printing "All packages built."
- `scripts/update-pins.py` reports no pin changes, so the pins still
  match upstream main HEAD as of the last check on 2026-10-26.

Proof scan, limited scope, at the pinned commits:

- No actual `sorry` or `admit` in code outside Spec files, and no
  custom `axiom` declarations in the 18 packages. A word scan finds
  162 `sorry` matches, of which 160 are in the root Spec.lean of six
  packages (bencode 24, codec 38, protobuf 12, rfc3339 33, semver 17,
  utf8 36) and 2 are comments stating that no sorry is present. The
  Spec definition files that proof modules import contain no sorry.
- The Spec.lean files hold statements only and are not part of the
  built library targets.
- A `#print axioms` check for each library's main theorems was not
  run. That check stays open in issue #1, and it is the one item that
  keeps this collection from being described as fully proof-audited.
  The table above repeats upstream descriptions. It does not replace
  that check.

Pin freshness: pins were checked 2026-10-26 and will drift as upstream
main moves. Re-run `scripts/update-pins.py` before merging, and rebuild
after any pin change. Do not merge on a stale pin check alone.
