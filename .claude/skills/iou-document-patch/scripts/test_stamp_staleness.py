"""Tests for the profiles of stamp-staleness.py.

Run: venv/Scripts/python.exe -m unittest discover -s .claude/skills/iou-document-patch/scripts -p "test_*.py" -v
"""

import importlib.util
import pathlib
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("stamp_staleness", HERE / "stamp-staleness.py")
stamp_staleness = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(stamp_staleness)


class ProfileTest(unittest.TestCase):
    def test_profile_contributing_unchanged(self):
        settings = stamp_staleness.profile_settings("contributing")
        self.assertEqual(settings["roots"], ["docs/en/contributing"])
        self.assertIsNone(settings["branch"])
        self.assertEqual(settings["paths"], stamp_staleness.CI_PATHS)

    def test_profile_psa(self):
        settings = stamp_staleness.profile_settings("psa")
        self.assertEqual(settings["roots"], ["docs/nl/psa", "docs/en/psa"])
        self.assertEqual(settings["branch"], "main")
        self.assertIn(":(glob)**/Caddyfile", settings["paths"])
        self.assertIn(":(glob)**/src/auth/**", settings["paths"])
        self.assertLessEqual(set(stamp_staleness.CI_PATHS), set(settings["paths"]))

    def test_cprmv_remote_resolved_by_url_not_by_name(self):
        # The cprmv clone's remote has been called `gitlab` in one clone and
        # `origin` in another; a fixed name silently reads a stale ref.
        self.assertIsNone(stamp_staleness.COMPONENTS["CPRMV"][2])
        self.assertIn("CPRMV", stamp_staleness.REMOTE_URLS)


class ResolveRemoteTest(unittest.TestCase):
    def _clone(self, remotes):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        subprocess.run(["git", "init", "-q", tmp.name], check=True)
        for name, url in remotes.items():
            subprocess.run(["git", "-C", tmp.name, "remote", "add", name, url], check=True)
        return tmp.name

    def test_finds_remote_named_gitlab(self):
        repo = self._clone({"gitlab": "https://git.open-regels.nl/standards/cprmv.git"})
        self.assertEqual(stamp_staleness.resolve_remote(repo, "git.open-regels.nl/standards/cprmv"), "gitlab")

    def test_finds_remote_named_origin_among_others(self):
        repo = self._clone({"github": "https://github.com/someone/cprmv.git",
                            "origin": "https://git.open-regels.nl/standards/cprmv.git"})
        self.assertEqual(stamp_staleness.resolve_remote(repo, "git.open-regels.nl/standards/cprmv"), "origin")

    def test_no_matching_remote(self):
        repo = self._clone({"origin": "https://github.com/someone/cprmv.git"})
        self.assertIsNone(stamp_staleness.resolve_remote(repo, "git.open-regels.nl/standards/cprmv"))


if __name__ == "__main__":
    unittest.main()
