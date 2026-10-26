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

The package names in `lakefile.toml` differ from the repo names in five
cases: `redis` is package `resp`, `utf` is package `utf8`, `rfc` is package
`rfc3339`, `zip` is package `zip-pilot`, and `tar` is package `tar-pilot`. The
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
`lake-manifest.json` with the new pins. The script also updates the
pinned commit column of the library table below.

To check for drift without changing anything, which exits 1 if any pin is
behind upstream main:

```
python3 scripts/update-pins.py --check
```

## Checks

CI runs these on every pull request and on every push to main:

- `scripts/check-consistency.py` checks that `lakefile.toml`,
  `lake-manifest.json` and the library table below record the same pins.
  It needs no network and no Lean toolchain.
- `lake build Anthology` builds each package's main library. It does not
  compile any package's `Proofs` library.
- `scripts/build-all.sh` builds each package on its own: its upstream
  default targets, then its `Proofs` library if it has one. This is the
  step that compiles the proofs.

A weekly scheduled run runs all of the checks above, plus
`scripts/update-pins.py --check`, and fails when upstream main has
moved past a pin.

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

Build record for the pins in `lakefile.toml`, checked 2026-10-26 on
Lean 4.35.0. Remaining work is tracked in issue #1.

- `lake update` fetched all 18 requirements with no errors. The
  committed `lake-manifest.json` matches the lakefile pins.
- `lake build Anthology` passed, 101 jobs. Warnings are linter warnings,
  mostly unused simp arguments in WebSocket, and deprecation warnings
  in ZipPilot.
- `scripts/build-all.sh` built all 18 packages on their own, on two
  separate machines.
- `scripts/update-pins.py` reported no pin changes, so the pins matched
  upstream main HEAD as of 2026-10-26.

Proof scan, limited scope, at the pinned commits:

- No actual `sorry` or `admit` in code outside Spec files, and no
  custom `axiom` declarations in the 18 packages. A word scan finds
  162 `sorry` matches, of which 160 are in the root Spec.lean of six
  packages (bencode 24, codec 38, protobuf 12, rfc3339 33, semver 17,
  utf8 36) and 2 are comments stating that no sorry is present. The
  Spec definition files that proof modules import contain no sorry.
- `lake build Anthology` builds each package's main library only. It
  does not compile any package's `Proofs` library. `scripts/build-all.sh`
  builds each package's upstream default targets, then its `Proofs`
  library explicitly if it has one, so it builds `Proofs` for all 14
  packages that have one, including bencode.
- The root Spec.lean files hold the statements, with `sorry`, by
  upstream design. The `Proofs` libraries prove them under the same
  names.
- A `#print axioms` check for each library's main theorems was not
  run. That check stays open in issue #1, and it is the one item that
  keeps this collection from being described as fully proof-audited.
  The table above repeats upstream descriptions. It does not replace
  that check.

Pin freshness: pins were checked 2026-10-26 and will drift as upstream
main moves. Re-run `scripts/update-pins.py` before trusting the pins,
and rebuild after any pin change.
