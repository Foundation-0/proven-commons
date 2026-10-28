# Joint-proof integration acceptance

Issue 4 remains open. The sync and audit implementation is merged, but it does
not rename upstream modules or declarations. The current recorded inventory
has 14 proof-bearing packages and admits none to the joint proof aggregator.
The separate per-package builds and audits remain necessary.

## Reproduce the remaining-work inventory

```sh
python3 scripts/joint-proof-status.py > /tmp/joint-proof-status.json
python3 scripts/joint-proof-status.py --require-complete
```

The second command currently returns 1. It lists every proof-bearing package,
its exact pin, proof roots, shared namespace owners, admission flag and whether
its audit matches that pin and toolchain. It reads `repos.json` and `audit.json`
without network access. Those files describe the last sync, not upstream heads.
The output is metadata evidence, not a new Lean build or proof check.

The pending packages at the inventory dated 27 October 2026 are bencode,
codec, csv, dns, ip, json, pep440, png, protobuf, rfc, semver, toml, utf and uuid.
Regenerate the report after every pin update instead of treating this list as
permanent. Repositories without a proof library are outside this count.

## Acceptance sequence for each package

1. Record upstream agreement on module and declaration naming. The existing
   convention proposal is [Proven-Commons/mission issue 22](https://github.com/Proven-Commons/mission/issues/22).
   This draft opens no upstream issue and claims no upstream acceptance.
2. Link the package's upstream rename change and its merged revision. Include
   proof and specification submodules and declaration names, not only the
   root library name. Track bencode's default proof targets explicitly.
3. Let the sync move the pin to a merged upstream revision. Inspect its
   `joint_proofs` and `joint_note` fields and the generated `AnthologyProofs.lean`.
   A namespace rename alone does not establish a successful joint build.
4. Run the actual acceptance commands below. If declaration collisions still
   cause the sync to hold a library out, keep that package pending and record
   the failing declaration and upstream change needed. Do not substitute a
   green main-library build for proof coverage.

```sh
python3 scripts/check-consistency.py
lake build Anthology AnthologyProofs
scripts/build-all.sh
python3 scripts/audit.py --check
python3 scripts/joint-proof-status.py --require-complete
```

A completed issue needs evidence that every proof-bearing package at the
accepted pins is jointly admitted, the actual joint build passes, and all
per-package audit records agree with those pins and the toolchain. Preserve
per-package fallback coverage until that acceptance is demonstrated. Green
checks on this inventory script alone do not satisfy it.

The issue's upstream convention and per-repository tracking checklist remains
open separately from the merged sync mechanism. This draft provides an
executable inventory and acceptance workflow, not the upstream renames or
permission to contact maintainers.

Prepared by gpt-forge (OpenAI) for Ahraz Arifuddin.
