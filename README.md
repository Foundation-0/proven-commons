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

Snapshot of the [Proven-Commons](https://github.com/Proven-Commons) org, synced 2026-10-31: 37 library repos, 28 of them in the workspace. Each workspace library is pinned to a commit of its upstream default branch whose `lean-toolchain` is `leanprover/lean4:v4.35.0`, the toolchain of this workspace. None of them requires another package.

| Repo | Upstream description | Pinned commit | Proof audit | Verified bar | License |
| --- | --- | --- | --- | --- | --- |
| [bech32](https://github.com/Proven-Commons/bech32) | Lean rewrite - bech32: Bech32 and Bech32m strings (BIP 173, BIP 350) | [`a69fc6e07a43`](https://github.com/Proven-Commons/bech32/commit/a69fc6e07a43a7ea4ea578140788b77d11dc5a99) | 129 theorems; standard axioms only; all 15 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [bencode](https://github.com/Proven-Commons/bencode) | lean Bencode parser | [`dcaa91d82709`](https://github.com/Proven-Commons/bencode/commit/dcaa91d827096d57e424f28af6465ce106017972) | 26 theorems, 2 `example`s §; standard axioms only; all 23 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [clienthello](https://github.com/Proven-Commons/clienthello) | Lean TLS ClientHello parser (RFC 8446, section 4.1.2) | [`abcc7aa36200`](https://github.com/Proven-Commons/clienthello/commit/abcc7aa36200354b1310e96165c8de20a96851c9) | 114 theorems; standard axioms only; all 37 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [codec](https://github.com/Proven-Commons/codec) | lean codec | [`860b895c1a64`](https://github.com/Proven-Commons/codec/commit/860b895c1a6449506d99f4b8b6c9dd8a9c5117e6) | 187 theorems, 19 `example`s §; standard axioms only; all 37 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [csv](https://github.com/Proven-Commons/csv) | lean CSV parser and printer (RFC 4180) | [`9d15dc85f786`](https://github.com/Proven-Commons/csv/commit/9d15dc85f786e7b99b2bb6c6e6b72db79ee1c9b4) | 13 theorems; standard axioms only | no bar.toml | Apache-2.0 |
| [dns](https://github.com/Proven-Commons/dns) | lean DNS wire header and question parser (RFC 1035) | [`915383c5bebb`](https://github.com/Proven-Commons/dns/commit/915383c5bebbe6fb197c943d79fce074af3c287e) | 17 theorems; standard axioms only | no bar.toml | Apache-2.0 |
| [hostname](https://github.com/Proven-Commons/hostname) | Lean hostname | [`6ccb18b0a040`](https://github.com/Proven-Commons/hostname/commit/6ccb18b0a0406a7d3c84e05d70e1236093803bbb) | 127 theorems; standard axioms only; all 22 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [hpack](https://github.com/Proven-Commons/hpack) | Lean HPACK stateless part (RFC 7541): prefix integers, Huffman strings, static table | [`1c0d17cacbb6`](https://github.com/Proven-Commons/hpack/commit/1c0d17cacbb62dfb6a1e5a523eb8556f55331e39) | 102 theorems; standard axioms only; all 17 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [ip](https://github.com/Proven-Commons/ip) | lean IP address parser and canonical printer | [`7243f5a6108e`](https://github.com/Proven-Commons/ip/commit/7243f5a6108e11ffa8a40c35d5d4984d686356a0) | 82 theorems; standard axioms only | no bar.toml | Apache-2.0 |
| [json](https://github.com/Proven-Commons/json) | lean json | [`4ff8eb6483e2`](https://github.com/Proven-Commons/json/commit/4ff8eb6483e21ec87da03a80abdb0af45ba9b7f2) | 95 theorems; standard axioms only; all 16 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [messagepack](https://github.com/Proven-Commons/messagepack) | lean MessagePack decoder | [`1dc7b3cb470d`](https://github.com/Proven-Commons/messagepack/commit/1dc7b3cb470dac712bf2245d70d76659dbff880c) | 100 theorems; standard axioms only; all 13 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [mqtt](https://github.com/Proven-Commons/mqtt) | Lean MQTT 5.0 packet framing | [`904310e58f37`](https://github.com/Proven-Commons/mqtt/commit/904310e58f37626341660959ed23222379562319) | 202 theorems; standard axioms only; all 37 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [path](https://github.com/Proven-Commons/path) | Lean lexical path cleaning (Go path.Clean rules) | [`41e5ffdba9f4`](https://github.com/Proven-Commons/path/commit/41e5ffdba9f450f8b5280b4cc2bd1cace3029fd9) | 89 theorems; standard axioms only; all 10 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [pep440](https://github.com/Proven-Commons/pep440) | lean PEP 440 version parser and precedence | [`873bd0fe38b3`](https://github.com/Proven-Commons/pep440/commit/873bd0fe38b33be95bde78a5adf8b72764e67677) | 170 theorems; standard axioms only | no bar.toml | Apache-2.0 |
| [png](https://github.com/Proven-Commons/png) | lean PNG chunk parser with CRC-32 check | [`244746910677`](https://github.com/Proven-Commons/png/commit/2447469106774beea9f809f4b6f8efd6cb3086cd) | 12 theorems; standard axioms only | no bar.toml | Apache-2.0 |
| [protobuf](https://github.com/Proven-Commons/protobuf) | lean Protobuf wire format codec | [`78a20edd8e68`](https://github.com/Proven-Commons/protobuf/commit/78a20edd8e689851835b1c5c3fb77a3b0e689f80) | 68 theorems, 10 `example`s §; standard axioms only; all 11 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [punycode](https://github.com/Proven-Commons/punycode) | Lean punycode | [`767ad95be176`](https://github.com/Proven-Commons/punycode/commit/767ad95be1760c70d4867865027f9678eae6bd85) | 149 theorems; standard axioms only; all 9 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [redis](https://github.com/Proven-Commons/redis) (package `resp`) | Lean redis | [`072ee45f118d`](https://github.com/Proven-Commons/redis/commit/072ee45f118dd77aa42dee8f54100a8666075b7a) | 65 theorems; standard axioms only | no bar.toml | Apache-2.0 |
| [rfc](https://github.com/Proven-Commons/rfc) (package `rfc3339`) | lean RFC 3339 timestamp parser | [`7ca89c914c9d`](https://github.com/Proven-Commons/rfc/commit/7ca89c914c9d9dcba41fd5db4ec52ce87de0ca41) | 252 theorems, 18 `example`s §; standard axioms only; all 32 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [semver](https://github.com/Proven-Commons/semver) | lean semver | [`67c70edde6b4`](https://github.com/Proven-Commons/semver/commit/67c70edde6b47e7ed46ed049aa5d058332948321) | 110 theorems, 15 `example`s §; standard axioms only; all 16 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [ssh](https://github.com/Proven-Commons/ssh) | Lean ssh rewrite | [`3f6169b690b5`](https://github.com/Proven-Commons/ssh/commit/3f6169b690b59b002613c3527a7800fd62b281bf) | 114 theorems; standard axioms only; all 37 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [tar](https://github.com/Proven-Commons/tar) (package `tar-pilot`) | Lean-verified tar (ustar) extractor with a proved no-escape extraction gate. A Proven Commons project. † | [`9012f46eec2e`](https://github.com/Proven-Commons/tar/commit/9012f46eec2e218bfc458c415e48f734152aa172) | 4 theorems; standard axioms only | no bar.toml | Apache-2.0 |
| [toml](https://github.com/Proven-Commons/toml) | lean TOML parser and printer | [`e38687b8c0c2`](https://github.com/Proven-Commons/toml/commit/e38687b8c0c2c377e46c5a9d9c2e87d7200fe1df) | 2 theorems, 37 `example`s §; standard axioms only | no bar.toml | Apache-2.0 |
| [utf](https://github.com/Proven-Commons/utf) (package `utf8`) | lean UTF-8 codec | [`2cdbc294327a`](https://github.com/Proven-Commons/utf/commit/2cdbc294327a5c7c07fe731b351c06f81578cb47) | 242 theorems, 23 `example`s §; standard axioms only; all 35 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [uuid](https://github.com/Proven-Commons/uuid) | lean UUID parser and printer (RFC 9562) | [`956d8cef465b`](https://github.com/Proven-Commons/uuid/commit/956d8cef465b9e66b74fc76ba4e7066b4572715c) | 32 theorems; standard axioms only | no bar.toml | Apache-2.0 |
| [websocket](https://github.com/Proven-Commons/websocket) | lean WebSocket frame parser (RFC 6455, section 5) | [`ecd4a26456e7`](https://github.com/Proven-Commons/websocket/commit/ecd4a26456e7ba108b797dd3beec7c41fd014551) | 15 theorems; standard axioms only | no bar.toml | Apache-2.0 |
| [xml](https://github.com/Proven-Commons/xml) | Lean XML safe subset parser (no document type declarations, no entities) | [`71d77b4951d2`](https://github.com/Proven-Commons/xml/commit/71d77b4951d279b6ebdc3b3cf120c25bbfc38ee4) | 225 theorems; standard axioms only; all 25 theorems named in comparator.json proved | in progress | Apache-2.0 |
| [zip](https://github.com/Proven-Commons/zip) (package `zip-pilot`) | lean zip | [`1cbcc1ffe4c2`](https://github.com/Proven-Commons/zip/commit/1cbcc1ffe4c2572d9507286250e5250679d9b0e4) | 52 theorems; standard axioms only | no bar.toml | Apache-2.0 |

† The upstream description says verified, but the project has not met the [verified bar](https://github.com/Proven-Commons/mission#the-verified-bar). Read it as the project's goal, not as a checked status.

§ An `example` has no name, so `#print axioms` cannot audit it. The build compiles it, which checks it, and the audit reads the build log for `sorry`.

Not in the workspace yet:

| Repo | Upstream description | Why not yet | License |
| --- | --- | --- | --- |
| [cbor](https://github.com/Proven-Commons/cbor) | lean CBOR decoder (RFC 8949) | Top-level module Spec is also used by rfc | Apache-2.0 |
| [cedar](https://github.com/Proven-Commons/cedar) | Lean Cedar-style policy engine: permit and forbid decisions | No lakefile on its default branch | none |
| [der](https://github.com/Proven-Commons/der) | Lean ASN.1 DER element reader (X.690) | Top-level module Spec is also used by rfc | Apache-2.0 |
| [dhcpv4](https://github.com/Proven-Commons/dhcpv4) | Lean DHCPv4 wire message parser | No lakefile on its default branch | Apache-2.0 |
| [http](https://github.com/Proven-Commons/http) | lean HTTP request-line and header parser (RFC 9112) | No lakefile on its default branch | Apache-2.0 |
| [jws](https://github.com/Proven-Commons/jws) | Lean JWS compact serialization parser and claim checks | Top-level module Json is also used by json | Apache-2.0 |
| [ntp](https://github.com/Proven-Commons/ntp) | Lean NTP wire packet parser | Top-level module Spec is also used by rfc | Apache-2.0 |
| [sqlite](https://github.com/Proven-Commons/sqlite) | Lean SQLite file format reader: header, pages, records | Top-level module Spec is also used by rfc | Apache-2.0 |
| [uri](https://github.com/Proven-Commons/uri) | Lean URI reference resolution (RFC 3986, sections 3 and 5.2) | No lakefile on its default branch | Apache-2.0 |

Joint proof build: `AnthologyProofs` imports the proof libraries of 12 packages (bencode, codec, csv, dns, ip, json, pep440, png, protobuf, semver, toml, uuid). 12 packages (bech32, clienthello, hostname, hpack, messagepack, mqtt, path, punycode, rfc, ssh, utf, xml) have proof libraries whose top-level module names are also used by other packages. `scripts/build-all.sh` builds those one package at a time. See issue #4.

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
package at its current pin and says so in the pull request. If
`AnthologyProofs` fails to build with a proof library, which happens
when two packages declare the same theorem name, it keeps that library
out and says so, and it keeps first the libraries that were already in
and whose pin did not move. A library held out is tried again whenever
a sync finds anything else to change. The pull request lists each pin
move with a link to the upstream diff.

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
  library, and each proof library whose module and theorem names are
  unique in the workspace.
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
