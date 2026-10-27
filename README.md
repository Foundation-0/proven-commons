# proven-commons

Anthology of Lean builds from the Proven-Commons org.

## Purpose

This repo exists to collect, in one place, all the libraries and software
built in the Proven-Commons org in Lean: the parsers, codecs, extractors,
and their executables listed in the table below.

A reader who wants the whole collection should not have to track each
library repo separately, each with its own version and toolchain. This repo
gives that reader one place to fetch, one toolchain, and one joint build,
with each item pinned to a specific upstream commit.

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
table below uses each upstream repo's own description, and puts beside it
what this repo has checked: the axiom audit of the pinned code, and the
verified bar status the upstream repo records.

## Requirements

- A Lean toolchain manager, such as elan, that can install the toolchain in
  `lean-toolchain`.
- Lake, which ships with the Lean toolchain.
- Git.
- Python 3.11 or later, for the scripts.

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

`lakefile.toml` uses Lake package names. Where a package name differs
from its repo name, the table below gives both.

## Libraries

<!-- BEGIN GENERATED: libraries. scripts/sync.py writes this block; do not edit it by hand. -->

Snapshot of the [Proven-Commons](https://github.com/Proven-Commons) org, synced 2026-10-27: 24 library repos, 18 of them in the workspace. Each workspace library is pinned to a commit of its upstream default branch whose `lean-toolchain` is `leanprover/lean4:v4.35.0`, the toolchain of this workspace. None of them requires another package.

| Repo | Upstream description | Pinned commit | Proof audit | Verified bar | License |
| --- | --- | --- | --- | --- | --- |
| [bencode](https://github.com/Proven-Commons/bencode) | Lean Bencode parser | [`de718a10ccbb`](https://github.com/Proven-Commons/bencode/commit/de718a10ccbbd837c8b9eda32674254db7cf619a) | 26 theorems, 2 `example`s §; standard axioms only; all 23 theorems named in comparator.json proved | in progress | none |
| [codec](https://github.com/Proven-Commons/codec) | Lean codec | [`74ae50b94b14`](https://github.com/Proven-Commons/codec/commit/74ae50b94b14dcf2c916865b6e7a95b42fabed9e) | 187 theorems, 19 `example`s §; standard axioms only; all 37 theorems named in comparator.json proved | in progress | none |
| [csv](https://github.com/Proven-Commons/csv) | Lean CSV parser and printer (RFC 4180) | [`4ceedb42f999`](https://github.com/Proven-Commons/csv/commit/4ceedb42f999cc35a6a606396d866a3a69961e78) | 13 theorems; standard axioms only | no bar.toml | none |
| [dns](https://github.com/Proven-Commons/dns) | Lean DNS wire header and question parser (RFC 1035) | [`a7cad62c0164`](https://github.com/Proven-Commons/dns/commit/a7cad62c0164cd0c1ba5ba4c838e11472741dea1) | 17 theorems; standard axioms only | no bar.toml | none |
| [ip](https://github.com/Proven-Commons/ip) | Lean IP address parser and canonical printer | [`09f2a06fddcc`](https://github.com/Proven-Commons/ip/commit/09f2a06fddccb8bdace48de5672eef3e8c2ce4f2) | 82 theorems; standard axioms only | no bar.toml | none |
| [json](https://github.com/Proven-Commons/json) | Lean JSON | [`4642e51aa9d3`](https://github.com/Proven-Commons/json/commit/4642e51aa9d3e8f566b06707e7ec3537a799117c) | 41 theorems; standard axioms only | no bar.toml | none |
| [pep440](https://github.com/Proven-Commons/pep440) | Lean PEP 440 version parser and precedence | [`3ab869050a06`](https://github.com/Proven-Commons/pep440/commit/3ab869050a0625b0cb889c44e0cf215799d67f6c) | 122 theorems; standard axioms only | no bar.toml | none |
| [png](https://github.com/Proven-Commons/png) | Lean PNG chunk parser with CRC-32 check | [`df3035120ec6`](https://github.com/Proven-Commons/png/commit/df3035120ec6a42abb42e75b496e66cb5f2cb5fb) | 12 theorems; standard axioms only | no bar.toml | none |
| [protobuf](https://github.com/Proven-Commons/protobuf) | Lean Protobuf wire format codec | [`babcab706e42`](https://github.com/Proven-Commons/protobuf/commit/babcab706e425b670da74b3ea0de1e9e4a0e61fb) | 68 theorems, 10 `example`s §; standard axioms only; all 11 theorems named in comparator.json proved | in progress | none |
| [redis](https://github.com/Proven-Commons/redis) (package `resp`) | Lean Redis | [`7ff41f249a92`](https://github.com/Proven-Commons/redis/commit/7ff41f249a9236f75911c002e9c1052349781f13) | 65 theorems; standard axioms only | no bar.toml | none |
| [rfc](https://github.com/Proven-Commons/rfc) (package `rfc3339`) | Lean RFC 3339 timestamp parser | [`79f30cd0fbbd`](https://github.com/Proven-Commons/rfc/commit/79f30cd0fbbd01ecfcf10bd8c98693fe8daf4238) | 252 theorems, 18 `example`s §; standard axioms only; all 32 theorems named in comparator.json proved | in progress | none |
| [semver](https://github.com/Proven-Commons/semver) | Lean semver | [`df74c98d5521`](https://github.com/Proven-Commons/semver/commit/df74c98d5521710895d90a216fa5cad1c31e44f6) | 110 theorems, 15 `example`s §; standard axioms only; all 16 theorems named in comparator.json proved | in progress | none |
| [tar](https://github.com/Proven-Commons/tar) (package `tar-pilot`) | Lean-verified tar (ustar) extractor with a proved no-escape extraction gate † | [`7517a86223e6`](https://github.com/Proven-Commons/tar/commit/7517a86223e6741b0a6b5c0b3b0fabcf68347bee) | 4 theorems; standard axioms only | no bar.toml | none |
| [toml](https://github.com/Proven-Commons/toml) | Lean TOML parser and printer | [`ca8a615c0492`](https://github.com/Proven-Commons/toml/commit/ca8a615c0492e7717034ef33b602a1bf13fbc298) | 0 theorems, 37 `example`s §; standard axioms only | no bar.toml | none |
| [utf](https://github.com/Proven-Commons/utf) (package `utf8`) | Lean UTF-8 codec | [`276115161f6c`](https://github.com/Proven-Commons/utf/commit/276115161f6c33f3b6f80436ebe07474fe5085e9) | 242 theorems, 23 `example`s §; standard axioms only; all 35 theorems named in comparator.json proved | in progress | none |
| [uuid](https://github.com/Proven-Commons/uuid) | Lean UUID parser and printer (RFC 9562) | [`b5478df3c95b`](https://github.com/Proven-Commons/uuid/commit/b5478df3c95bb4117781cba4ebe908d8cf067062) | 32 theorems; standard axioms only | no bar.toml | none |
| [websocket](https://github.com/Proven-Commons/websocket) | Lean WebSocket frame parser (RFC 6455, section 5) | [`b8db7cd36428`](https://github.com/Proven-Commons/websocket/commit/b8db7cd364286818d88f5fdb358079943bc4d189) | 15 theorems; standard axioms only | no bar.toml | none |
| [zip](https://github.com/Proven-Commons/zip) (package `zip-pilot`) | Lean zip | [`2cf824fde49f`](https://github.com/Proven-Commons/zip/commit/2cf824fde49fb336c217c89190891ddb753cfe10) | 4 theorems; standard axioms only | no bar.toml | none |

† The upstream description says verified, but the project has not met the [verified bar](https://github.com/Proven-Commons/mission#the-verified-bar). Read it as the project's goal, not as a checked status.

§ An `example` has no name, so `#print axioms` cannot audit it. The build compiles it, which checks it, and the audit reads the build log for `sorry`.

Not in the workspace yet:

| Repo | Upstream description | Why not yet | License |
| --- | --- | --- | --- |
| [bech32](https://github.com/Proven-Commons/bech32) | Lean rewrite - bech32: Bech32 and Bech32m strings (BIP 173, BIP 350) | No lakefile on its default branch | none |
| [cbor](https://github.com/Proven-Commons/cbor) | Lean CBOR decoder (RFC 8949) | No lakefile on its default branch | none |
| [hostname](https://github.com/Proven-Commons/hostname) | Lean hostname | No lakefile on its default branch | none |
| [http](https://github.com/Proven-Commons/http) | Lean HTTP request-line and header parser (RFC 9112) | No lakefile on its default branch | none |
| [messagepack](https://github.com/Proven-Commons/messagepack) | Lean MessagePack decoder | No lakefile on its default branch | none |
| [punycode](https://github.com/Proven-Commons/punycode) | Lean punycode | No lakefile on its default branch | none |

Joint proof build: `AnthologyProofs` imports the proof libraries of 0 packages. 14 packages (bencode, codec, csv, dns, ip, json, pep440, png, protobuf, rfc, semver, toml, utf, uuid) have proof libraries whose top-level module names are also used by other packages, so `scripts/build-all.sh` builds them one package at a time. See issue #4.

<!-- END GENERATED: libraries -->

## How it stays up to date

The [sync workflow](.github/workflows/sync.yml) runs every day, and on
demand from the Actions tab. It runs `scripts/sync.py`, which lists every
public repo in the org, except the non-library repos that `sync.toml`
excludes, and reads the head of each one's default branch. A repo joins
the workspace, pinned at that head, when all of these hold:

- Its default branch has a `lakefile.toml`, with at least one library
  that is not a `Spec`, `Proofs` or test library, and a `lean-toolchain`
  that pins a Lean release.
- Its toolchain is the workspace toolchain. That is the toolchain most
  library repos use on their default branch, the current one on a tie,
  unless `sync.toml` sets one.
- Its Lake package name, and every top-level module name its main
  library imports, are its own in the workspace.

A repo already in the workspace whose new head fails one of these keeps
its current pin, and the table says why. A new repo in the org appears in
the table as soon as it exists, with the reason it is not in the
workspace yet, and joins once its default branch passes. Pins track the
default branch only, so the anthology reflects merged work, not work in
progress.

When anything changes, the workflow updates `repos.json`, `lakefile.toml`,
`lean-toolchain`, `Anthology.lean`, `AnthologyProofs.lean`, this README's
table and `lake-manifest.json`. It then builds everything, runs the proof
audit, and opens a pull request, or updates the open one, on the branch
`sync/upstream`. If a package's new head fails to build, it keeps that
package at its current pin and says so in the pull request. The pull
request lists each pin move with a link to the upstream diff.

A pin update changes what this repo certifies, so a sync pull request is
not a routine bump. It merges like any other, under the org's merge SOP:
a maintainer reviews the upstream diffs and the audit changes, and
approves it.

To hold a repo at an older commit of its default branch, or to exclude a
repo that is not a library, edit `sync.toml` in a pull request. The next
sync applies it.

The workflow needs the repository setting "Allow GitHub Actions to create
and approve pull requests". With only the default token, GitHub does not
start CI for a pull request that a workflow opens, so the workflow starts
the CI workflow on the sync branch itself. If a `SYNC_TOKEN` secret holds
a token that can push to this repo and open pull requests, the workflow
uses that instead, and CI starts as usual.

To run a sync by hand:

```
python3 scripts/sync.py      # pins, lakefile, aggregators, README table
lake update                  # lake-manifest.json
lake build Anthology AnthologyProofs
scripts/build-all.sh
python3 scripts/audit.py     # audit.json
python3 scripts/sync.py --render
```

`python3 scripts/sync.py --check` writes nothing, and exits 1 if upstream
has moved since the last sync.

## Checks

CI runs these on every pull request, on every push to main, and once a
week:

- `scripts/check-consistency.py` checks that the generated files match
  `repos.json` and `audit.json`, and that `lake-manifest.json` records
  the same pins as `lakefile.toml`. It also runs the sync's unit tests.
  It needs no network and no Lean toolchain.
- `lake build Anthology AnthologyProofs` builds each package's main
  library, and each proof library whose module names are unique in the
  workspace.
- `scripts/build-all.sh` builds each package on its own: its upstream
  default targets, then each of its libraries, so every `Proofs` and
  `Spec` library is compiled even when upstream default targets leave
  one out.
- `scripts/audit.py --check` reruns the proof audit, and fails if the
  result differs from the committed `audit.json`.

## Proof audit

`scripts/audit.py` imports each package's main and proof libraries and
runs Lean's `collectAxioms`, the check behind `#print axioms`, on every
theorem and definition the package declares. The table's "Proof audit"
column gives the number of theorems the package's source states, and
whether every declaration uses only the standard axioms: `propext`,
`Classical.choice` and `Quot.sound`. It names any use of `sorry` or of
another axiom, and any `axiom` the package declares. For a package with
a `comparator.json`, it also counts how many of the theorems named there
the proof library proves with only the permitted axioms.

The audit does not import a package's `Spec` library. By upstream design
that library states the theorems with `sorry`, and the `Proofs` library
proves them under the same names. The audit is narrower than upstream's
[verified bar](https://github.com/Proven-Commons/mission#the-verified-bar):
it does not check that a statement says what its claim says, it does not
apply the bar's source rules (no `implemented_by`, `extern`, `unsafe`,
native evaluation and so on), and it does not rerun differential tests.
The "Verified bar" column repeats the status each upstream `bar.toml`
records.

## License

This repo's own files are under the Apache License 2.0, in `LICENSE`.
The libraries it pins are not part of this repo, and each carries the
license of its upstream repo, as the table's "License" column records.
