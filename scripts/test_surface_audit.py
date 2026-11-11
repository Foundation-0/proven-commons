import tempfile
import unittest
from pathlib import Path

import surface_audit


class SurfaceAuditTests(unittest.TestCase):
    def test_catches_all_twelve_adversarial_vectors(self):
        vectors = {
            "V1_notation": 'notation:50 lhs " = " rhs => True',
            "V2_infix": 'infix:50 " = " => fun _ _ => True',
            "V3_infixl": 'infixl:65 (priority := high) " + " => fun a _ => a',
            "V4_macro_str": 'macro "prove_it" : tactic => `(tactic| trivial)',
            "V5_macro_id": 'macro m:ident : command => `(command| def $m := 0)',
            "V6_multiline_notation": 'notation:50\n  lhs " = " rhs => True',
            "V7_stacked_extern": '@[simp] @[extern "c_evil"] def f (x : Nat) : Nat := x',
            "V8_semicolon_axiom": "def ok : Nat := 1; axiom falsity : False",
            "V9_guillemet_sorry": "theorem bad : True := \u00absorry\u00bb",
            "V10_guillemet_extern": '@[\u00abextern\u00bb "evil"] def g : Nat := 0',
            "V11_comma_csimp": "@[simp, csimp] theorem swap_impl : f = g := rfl",
            "V12_comment_import": "/- inline -/ import Lean.Elab.Command",
        }
        for name, src in vectors.items():
            with self.subTest(vector=name):
                hits = surface_audit.scan_lean_tokens(src)
                self.assertTrue(hits, f"expected {name} to be flagged")

    def test_zero_false_positives_on_benign_lean(self):
        benign = {
            "B1_primes": "def step (x x' : Nat) : Nat := x + x'",
            "B2_comments": "-- sorry axiom notation @[extern] unsafe\n/- @[csimp] macro -/\ndef clean := 42",
            "B3_strings": 'def msg : String := "notation axiom sorry @[extern] @[csimp]"',
            "B4_raw_string": 'def raw : String := r#"macro "x" => sorry"#',
        }
        for name, src in benign.items():
            with self.subTest(case=name):
                self.assertEqual(surface_audit.scan_lean_tokens(src), [])

    def test_allow_sorry_only_in_spec_modules(self):
        spec_src = "theorem target : 1 + 1 = 2 := sorry"
        self.assertEqual(surface_audit.scan_lean_tokens(spec_src, allow_sorry=True), [])
        self.assertEqual(len(surface_audit.scan_lean_tokens(spec_src, allow_sorry=False)), 1)
        bad_spec = 'notation:50 a " = " b => True\ntheorem target : 1 = 2 := sorry'
        hits = surface_audit.scan_lean_tokens(bad_spec, allow_sorry=True)
        self.assertEqual([r for _, r in hits], ["notation or macro"])

    def test_pinned_spec_hash_tracks_toolchain_and_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp)
            (pkg / "lean-toolchain").write_text("leanprover/lean4:v4.35.0\n")
            (pkg / "SPEC.md").write_text("# Spec\n")
            (pkg / "Http").mkdir()
            (pkg / "Http" / "Framing.lean").write_text("def x := 1\n")
            h1 = surface_audit.compute_pinned_spec_hash(pkg, ["SPEC.md"], ["Http.Framing"])
            (pkg / "lean-toolchain").write_text("leanprover/lean4:v4.11.0\n")
            h2 = surface_audit.compute_pinned_spec_hash(pkg, ["SPEC.md"], ["Http.Framing"])
            self.assertNotEqual(h1, h2)
            (pkg / "Http" / "Framing.lean").write_text("def x := 2\n")
            h3 = surface_audit.compute_pinned_spec_hash(pkg, ["SPEC.md"], ["Http.Framing"])
            self.assertNotEqual(h2, h3)


if __name__ == "__main__":
    unittest.main()
