# Upstream Verified Bar Audits, Surface Scanner, and HTTP/1.1 Slice (2026-11-11)

This note records upstream formal-verification work across the `Proven-Commons` repositories collected by this anthology, how those changes connect to `scripts/audit.py` and `AnthologyProofs.lean` (`#4` and `#8`), and what must land upstream before refreshing the affected anthology pins.

## 1. Anthology and Meta-Verifier Surface Checking (`Proven-Commons/mission#35`)

`scripts/audit.py` checks kernel axioms (`collectAxioms`) on each pinned package's main and proof libraries, and notes in its docstring that upstream's Verified Bar adds source-level rules (`extern`, `implemented_by`, `csimp`, `unsafe`, `notation`, `macro`) that `collectAxioms` alone does not inspect.

A review of upstream `Proven-Commons/mission` `bar/check.py` (at `7bed38c`, tracked in `Proven-Commons/mission#35`) verified two gaps:
1. **String-erasure lookahead gap (`PROVEN` + `VERIFIED`):** `strip_lean` replaces string literals `"..."` with `""` before running the `FORBIDDEN` regexes, causing the positive lookahead `(?=.*"[^"]+")` on `notation`, `macro`, `syntax`, `elab`, and `infix` declarations to miss single-string notations and macros (`notation:50 lhs " = " rhs => True`). Line-start `^\s*` regexes also miss named-head macros, multi-line notations, semicolon-chained `axiom` declarations, and stacked or comma-separated attributes (`@[simp, csimp]`, `@[simp] @[extern "c"]`), catching 3 of 12 test cases.
2. **Incomplete `spec_hash` pinning (`VERIFIED`):** `spec_hash` hashes `bar["spec"]["files"]` only, omitting `lean-toolchain`, `lakefile.toml`, `lake-manifest.json`, `comparator.json`, and `[spec].code` module bytes.

**Added in this repo:** `scripts/surface_audit.py` and `scripts/test_surface_audit.py` implement a dependency-free Lean 4 token-stream scanner (`tokenize_lean4` + `scan_lean_tokens`) and `compute_pinned_spec_hash`, catching `12/12` forbidden surface test vectors with `0/4` benign false positives under `python3 -m unittest discover -s scripts -v`.

## 2. Upstream Archive Bar Reviews: `zip` and `tar` (`Proven-Commons/mission#36`, `Proven-Commons/zip#5`, `Proven-Commons/tar#6`)

Although `README.md` records `zip` (`aefc6be`) and `tar` (`ed0e68e`) from an earlier sync snapshot, upstream Verified Bar v2 reviews documented five specification and extraction-boundary findings that should be resolved upstream before marking updated pins Verified Bar v2 complete:
1. **`Z-F1` (`0x00` NUL-byte parser differential, `VERIFIED`):** Lean 4 `String.fromUTF8?` decodes `0x00` to `U+0000` (`Char.ofNat 0`). A 13-byte archive filename `"safe.txt\x00evil"` satisfies `Zip.SafeName` (`Proven-Commons/zip` `1cbcc1f`) and `Tar.PlainName` (`Proven-Commons/tar#6`) as well as Lean `Nodup` alongside `"safe.txt"`, whereas C/POSIX `open(2)` and Python 3.11 `zipfile` truncate at `0x00` to `"safe.txt"`. Fix: forbid `c.val < 0x20` and `c.val == 0x7F` in both `Zip.SafeName` and `Tar.PlainName`.
2. **`Z-F2` (`PROVEN`):** Export `'/' not-in c.toList` per path segment in `Zip.gate_sound`.
3. **`Z-F3` (`VERIFIED`):** Parse Central Directory `versionMadeBy` and `externalFileAttributes` so UNIX symlink entries (`st_mode = 0o120777`) are rejected by `SafeEntry`.
4. **`Z-F4` (`VERIFIED`):** Enforce pairwise disjoint byte extents `[localOffset_i, dataEnd_i)` in `SafeArchive` to prevent shared-offset (`localOffset = 0`) archive amplification.
5. **`Z-F5` (`VERIFIED`):** Move CLI dispatch from `Main.lean` into a pure verified function inside `[spec].code`.

Tracked upstream in `Proven-Commons/mission#36` (`reviews/zip/2026-11-11-bar-audit.md`), `Proven-Commons/zip#5`, and `Proven-Commons/tar#6`.

## 3. Upstream RFC 9112 Request Framing and Joint-Proof Layout (`Proven-Commons/http#4`)

`Proven-Commons/http#4` (`feat/rfc9112-request-framing`) introduces a Verified Bar v2 specification and Lean 4 (`v4.35.0`) module layout for strict RFC 9112 HTTP/1.1 request framing and chunked decoding:
- **Collision-free joint-proof namespace (Refs `#4`):** Uses `Http.Types`, `Http.Framing`, `Http.Spec.Defs`, `Http.Spec`, and `Http.Proofs` (`Proven-Commons/mission#22`), avoiding the top-level `Spec` / `Proofs` collision documented in `#4` so `Http.Proofs` can be imported directly into `AnthologyProofs.lean` once upstream pins advance to `v4.35.0`.
- **15 stated theorems and differential verification (`VERIFIED`):** Covers `splitCRLF_sound`, disjoint `Content-Length` / `Transfer-Encoding` framing (`CL.TE`, `TE.CL`, `HTTP/1.0` `Transfer-Encoding` per `EEF-CVE-2026-94194`, non-final `chunked`), strict `CRLF` chunk-data terminators (`CVE-2025-23167`), `parseRequest_prefix_free`, and `parseRequest_stream_unique` (`2,520` tested streams, `12/12` caught planted mutations, and `120` live TCP checks against Node.js `v18.20.4` `llhttp`).

## 4. Upstream-to-Anthology Acceptance Sequence

1. Complete `lake build && lake comparator --paranoid` on `Proven-Commons/http#4` (`v4.35.0`), obtain independent spec review, and merge upstream.
2. Land `tokenize_lean4` + `compute_pinned_spec_hash` in `Proven-Commons/mission` (`Proven-Commons/mission#35`) and merge `reviews/zip/2026-11-11-bar-audit.md` (`Proven-Commons/mission#36`).
3. Harden `Tar.PlainName` (`Proven-Commons/tar#6`) and `Zip.SafeName` + `SafeArchive` (`Proven-Commons/zip#5`) against `0x00..0x1F` / `0x7F`, `S_IFLNK`, and overlapping `localOffset` spans.
4. Run `scripts/sync.py`, `scripts/build-all.sh`, `scripts/audit.py`, and `scripts/surface_audit.py` to refresh the anthology pins and admit `Http.Proofs` into `AnthologyProofs.lean`.
