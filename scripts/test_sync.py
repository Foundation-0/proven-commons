#!/usr/bin/env python3
"""Tests for scripts/sync.py. They need git and no network: each test
builds small upstream repos in a temporary folder and syncs against them.

Run from the repo root:  python3 -m unittest discover -s scripts -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync  # noqa: E402

TC = "leanprover/lean4:v4.35.0"
TC_NEW = "leanprover/lean4:v4.36.0"


def run(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


class Upstream:
    """A folder of git repos standing in for the org."""

    def __init__(self, base):
        self.base = Path(base)
        self.meta = {}

    def commit(self, repo, files, description="", remove=()):
        path = self.base / repo
        if not path.exists():
            path.mkdir(parents=True)
            run("git", "init", "-q", "-b", "main", cwd=path)
            run("git", "config", "uploadpack.allowAnySHA1InWant", "true", cwd=path)
        for name in remove:
            (path / name).unlink()
        for name, text in files.items():
            (path / name).parent.mkdir(parents=True, exist_ok=True)
            (path / name).write_text(text)
        run("git", "add", "-A", cwd=path)
        run("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
            "--allow-empty", "-m", "c", cwd=path)
        self.meta.setdefault(repo, {"name": repo, "description": description,
                                    "default_branch": "main", "archived": False, "license": None})
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True,
                              text=True, check=True).stdout.strip()

    def empty(self, repo):
        path = self.base / repo
        path.mkdir(parents=True)
        run("git", "init", "-q", "-b", "main", cwd=path)
        self.meta[repo] = {"name": repo, "description": "", "default_branch": "main",
                           "archived": False, "license": None}

    def listing(self):
        path = self.base / "listing.json"
        path.write_text(json.dumps(list(self.meta.values())))
        return str(path)


def library(main, proofs="Proofs", spec="Spec", toolchain=TC, package=None, main_imports=()):
    """Files of a library repo laid out like the mission template."""
    package = package or main.lower()
    files = {
        "lean-toolchain": toolchain + "\n",
        "lakefile.toml": "\n".join([
            f'name = "{package}"', 'version = "0.1.0"', "",
            "[[lean_lib]]", f'name = "{main}"', "",
            *([f"[[lean_lib]]", f'name = "{spec}"', f'roots = ["{spec}"]', ""] if spec else []),
            *([f"[[lean_lib]]", f'name = "{proofs.replace(".", "")}"', f'roots = ["{proofs}"]', ""] if proofs else []),
            "[[lean_exe]]", f'name = "{package}"', 'root = "Main"', ""]),
        f"{main}.lean": "".join(f"import {m}\n" for m in main_imports) + "def x := 1\n",
        "Main.lean": f"import {main}\ndef main : IO Unit := pure ()\n",
    }
    if spec:
        files[spec.replace(".", "/") + ".lean"] = f"import {spec}.Defs\ntheorem t : True := sorry\n"
        files[spec.replace(".", "/") + "/Defs.lean"] = f"import {main}\n"
    if proofs:
        files[proofs.replace(".", "/") + ".lean"] = f"/- header -/\nimport {spec}.Defs\n-- c\nimport {main}\ntheorem t : True := trivial\n" if spec else f"import {main}\n"
    return files


class SyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.up = Upstream(self.tmp.name)
        os.environ["SYNC_GIT_BASE"] = "file://" + self.tmp.name
        self.cfg = {"org": "Org", "exclude": ["mission"], "hold": {}}

    def tearDown(self):
        os.environ.pop("SYNC_GIT_BASE", None)
        self.tmp.cleanup()

    def sync(self, previous=None, keep=(), cfg=None):
        previous = previous or {"toolchain": TC}
        cfg = cfg or self.cfg
        found = sync.discover(cfg, previous, set(keep), self.up.listing())
        return sync.decide(found, previous, cfg)

    def repo(self, state, name):
        return next(r for r in state["repos"] if r["repo"] == name)

    def test_libraries_join_and_readme_only_repos_wait(self):
        a = self.up.commit("alpha", library("Alpha"), "Lean alpha")
        self.up.commit("beta", {"README.md": "soon\n"}, "Lean beta")
        self.up.commit("mission", {"README.md": "org\n"})
        state = self.sync()
        self.assertEqual([r["repo"] for r in state["repos"]], ["alpha", "beta"])
        alpha, beta = self.repo(state, "alpha"), self.repo(state, "beta")
        self.assertEqual((alpha["state"], alpha["rev"]), ("included", a))
        self.assertEqual(alpha["main_namespaces"], ["Alpha"])
        self.assertEqual(alpha["namespaces"], ["Alpha", "Proofs", "Spec"])
        self.assertEqual(beta["state"], "pending")
        self.assertIn("no lakefile", beta["reason"])
        lakefile = sync.render_lakefile(state)
        self.assertIn(f'rev = "{a}"', lakefile)
        self.assertIn("import Alpha  -- alpha", sync.render_anthology(state))

    def test_pin_follows_head_and_report_links_the_diff(self):
        a1 = self.up.commit("alpha", library("Alpha"))
        first = self.sync()
        a2 = self.up.commit("alpha", {"Alpha.lean": "def x := 2\n"})
        second = self.sync(first)
        self.assertEqual(self.repo(second, "alpha")["rev"], a2)
        self.assertIn(f"compare/{a1}...{a2}", sync.report(first, second))

    def test_new_repo_in_the_org_joins(self):
        self.up.commit("alpha", library("Alpha"))
        first = self.sync()
        self.up.commit("gamma", library("Gamma"))
        second = self.sync(first)
        self.assertEqual(self.repo(second, "gamma")["state"], "included")
        self.assertIn("**gamma** joins the workspace", sync.report(first, second))

    def test_readme_only_repo_joins_once_main_has_a_lakefile(self):
        self.up.commit("beta", {"README.md": "soon\n"})
        first = self.sync()
        self.up.commit("beta", library("Beta"))
        self.assertEqual(self.repo(self.sync(first), "beta")["state"], "included")

    def test_head_on_another_toolchain_keeps_the_current_pin(self):
        a1 = self.up.commit("alpha", library("Alpha"))
        self.up.commit("beta", library("Beta"))
        self.up.commit("gamma", library("Gamma"))
        first = self.sync()
        self.up.commit("alpha", {"lean-toolchain": TC_NEW + "\n"})
        second = self.sync(first)
        alpha = self.repo(second, "alpha")
        self.assertEqual(second["toolchain"], TC)
        self.assertEqual((alpha["state"], alpha["rev"]), ("included", a1))
        self.assertIn(f"uses {TC_NEW}", alpha["note"])

    def test_workspace_follows_the_toolchain_most_repos_use(self):
        self.up.commit("alpha", library("Alpha"))
        self.up.commit("beta", library("Beta"))
        self.up.commit("gamma", library("Gamma"))
        first = self.sync()
        self.up.commit("alpha", {"lean-toolchain": TC_NEW + "\n"})
        self.up.commit("beta", {"lean-toolchain": TC_NEW + "\n"})
        second = self.sync(first)
        self.assertEqual(second["toolchain"], TC_NEW)
        gamma = self.repo(second, "gamma")
        self.assertEqual(gamma["state"], "pending")
        self.assertIn("leaves the workspace", sync.report(first, second))
        self.assertEqual(sync.rendered(second, {}, sync.BEGIN + sync.END)["lean-toolchain"], TC_NEW + "\n")

    def test_forced_toolchain_wins(self):
        self.up.commit("alpha", library("Alpha", toolchain=TC_NEW))
        state = self.sync(cfg=dict(self.cfg, toolchain=TC))
        self.assertEqual(state["toolchain"], TC)
        self.assertEqual(self.repo(state, "alpha")["state"], "pending")

    def test_newcomer_cannot_take_module_names_already_in_use(self):
        self.up.commit("zeta", library("Zeta"))
        first = self.sync()
        # alpha sorts first, but zeta was there first, and alpha's main
        # library imports a module under Zeta.
        self.up.commit("alpha", dict(library("Alpha", main_imports=["Zeta.Util"]),
                                     **{"Zeta/Util.lean": "def y := 1\n"}))
        second = self.sync(first)
        self.assertEqual(self.repo(second, "zeta")["state"], "included")
        alpha = self.repo(second, "alpha")
        self.assertEqual(alpha["state"], "pending")
        self.assertIn("top-level module Zeta is also used by zeta", alpha["reason"])

    def test_package_name_clash(self):
        self.up.commit("alpha", library("Alpha", package="same"))
        self.up.commit("beta", library("Beta", package="same"))
        state = self.sync()
        self.assertIn("package name same", self.repo(state, "beta")["reason"])

    def test_shared_proofs_and_spec_names_are_allowed_but_not_joint(self):
        self.up.commit("alpha", library("Alpha"))
        self.up.commit("beta", library("Beta"))
        self.up.commit("gamma", library("Gamma", proofs="Gamma.Proofs", spec="Gamma.Spec"))
        state = self.sync()
        self.assertTrue(all(r["state"] == "included" for r in state["repos"]))
        joint = {r["repo"]: r["joint_proofs"] for r in state["repos"]}
        self.assertEqual(joint, {"alpha": False, "beta": False, "gamma": True})
        proofs = sync.render_proofs(state)
        self.assertIn("import Gamma.Proofs  -- gamma", proofs)
        self.assertIn("-- alpha, beta.", proofs)

    def test_hold_joint_keeps_new_proof_libraries_out(self):
        self.up.commit("alpha", library("Alpha"))
        first = self.sync()
        # beta's plain Proofs and Spec collide with alpha's; gamma's and
        # delta's module names are their own.
        self.up.commit("beta", library("Beta"))
        self.up.commit("gamma", library("Gamma", proofs="Gamma.Proofs", spec="Gamma.Spec"))
        self.up.commit("delta", library("Delta", proofs="Delta.Proofs", spec="Delta.Spec"))
        found = sync.discover(self.cfg, first, set(), self.up.listing())
        held = sync.decide(found, first, self.cfg, hold_joint={"gamma", "delta"})
        gamma = self.repo(held, "gamma")
        self.assertFalse(gamma["joint_proofs"])
        self.assertIn("joint proof build fails", gamma["joint_note"])
        proofs = sync.render_proofs(held)
        self.assertNotIn("import Gamma.Proofs", proofs)
        self.assertIn("the joint build fails with them", proofs)
        self.assertIn("-- delta, gamma.", proofs)
        self.assertIn("-- alpha, beta.", proofs)
        self.assertIn("stays out of `AnthologyProofs`", sync.report(first, held))
        # Only the named repos are held. alpha's proof library collides
        # with beta's, so it is not joint, and holding it changes nothing.
        partial = sync.decide(found, first, self.cfg, hold_joint={"delta", "alpha"})
        self.assertTrue(self.repo(partial, "gamma")["joint_proofs"])
        self.assertFalse(self.repo(partial, "delta")["joint_proofs"])
        self.assertNotIn("joint_note", self.repo(partial, "alpha"))
        joined = sync.decide(found, first, self.cfg)
        self.assertIn("**gamma**: its proof library joins `AnthologyProofs`", sync.report(first, joined))
        # alpha was joint while it was alone.
        self.assertIn("**alpha**: its proof library leaves `AnthologyProofs`", sync.report(first, joined))
        self.assertIn("its proof library leaves `AnthologyProofs`",
                      sync.report(joined, sync.decide(found, joined, self.cfg, hold_joint={"gamma"})))

    def test_hold_pins_an_older_commit(self):
        a1 = self.up.commit("alpha", library("Alpha"))
        self.up.commit("alpha", {"Alpha.lean": "def x := 2\n"})
        cfg = dict(self.cfg, hold={"alpha": {"rev": a1, "reason": "upstream bug"}})
        alpha = self.repo(self.sync(cfg=cfg), "alpha")
        self.assertEqual(alpha["rev"], a1)
        self.assertIn("upstream bug", alpha["note"])

    def test_bad_hold_stops_the_sync(self):
        self.up.commit("alpha", library("Alpha"))
        cfg = dict(self.cfg, hold={"alpha": {"rev": "abc"}})
        with self.assertRaises(sync.SyncError):
            self.sync(cfg=cfg)

    def test_keep_pin(self):
        a1 = self.up.commit("alpha", library("Alpha"))
        first = self.sync()
        self.up.commit("alpha", {"Alpha.lean": "def x := 2\n"})
        alpha = self.repo(self.sync(first, keep=["alpha"]), "alpha")
        self.assertEqual(alpha["rev"], a1)
        self.assertIn("fails to build", alpha["note"])

    def test_keep_pin_leaves_a_failing_newcomer_out(self):
        self.up.commit("alpha", library("Alpha"))
        self.assertIn("fails to build", self.repo(self.sync(keep=["alpha"]), "alpha")["reason"])

    def test_empty_repo_is_pending(self):
        self.up.empty("fresh")
        self.assertIn("no commits yet", self.repo(self.sync(), "fresh")["reason"])

    def test_unreachable_repo_stops_the_sync(self):
        self.up.commit("alpha", library("Alpha"))
        self.up.meta["ghost"] = {"name": "ghost", "description": "", "default_branch": "main",
                                 "archived": False, "license": None}
        with self.assertRaises(sync.SyncError):
            self.sync()

    def test_repo_removed_from_the_org_leaves(self):
        self.up.commit("alpha", library("Alpha"))
        self.up.commit("beta", library("Beta"))
        first = self.sync()
        del self.up.meta["beta"]
        second = self.sync(first)
        self.assertEqual([r["repo"] for r in second["repos"]], ["alpha"])
        self.assertIn("**beta** leaves the anthology, because it is no longer a public repo",
                      sync.report(first, second))
        self.assertIn("sync.toml now excludes it", sync.report(first, second, excluded=["beta"]))

    def test_unchanged_upstream_keeps_the_date(self):
        self.up.commit("alpha", library("Alpha"))
        first = dict(self.sync(), synced="2000-01-01")
        self.assertEqual(self.sync(first)["synced"], "2000-01-01")

    def test_new_commit_on_a_pending_repo_changes_nothing(self):
        self.up.commit("beta", {"README.md": "soon\n"})
        first = self.sync()
        self.up.commit("beta", {"README.md": "sooner\n"})
        self.assertEqual(self.sync(first)["repos"], first["repos"])

    def test_malformed_lakefile_marks_only_that_repo(self):
        self.up.commit("alpha", library("Alpha"))
        self.up.commit("beta", {"lakefile.toml": "[[lean_lib]]\nroots = 3\n", "lean-toolchain": TC})
        state = self.sync()
        self.assertEqual(self.repo(state, "alpha")["state"], "included")
        self.assertIn("not in the shape", self.repo(state, "beta")["reason"])

    def test_lakefile_lean_is_reported(self):
        self.up.commit("alpha", {"lakefile.lean": "import Lake\n", "lean-toolchain": TC})
        self.assertIn("lakefile.lean", self.repo(self.sync(), "alpha")["reason"])


class ParseTest(unittest.TestCase):
    def test_header_imports(self):
        src = "/- a /- nested -/ still -/\nmodule\n-- c\npublic import A.B\nimport «C-d»\n\ndef x := 1\nimport Late\n"
        self.assertEqual(sync.header_imports(src), ["A.B", "C-d"])

    def test_version_order(self):
        order = sorted(["leanprover/lean4:v4.36.0", "leanprover/lean4:v4.36.0-rc1",
                        "leanprover/lean4:v4.9.0"], key=sync.version)
        self.assertEqual(order, ["leanprover/lean4:v4.9.0", "leanprover/lean4:v4.36.0-rc1",
                                 "leanprover/lean4:v4.36.0"])

    def test_readme_needs_markers(self):
        with self.assertRaises(SystemExit):
            sync.render_readme({"repos": []}, {}, "no markers")


if __name__ == "__main__":
    unittest.main()
