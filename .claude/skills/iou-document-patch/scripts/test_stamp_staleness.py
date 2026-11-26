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

    def test_no_remote_names_are_hardcoded(self):
        # Remote names have not been stable (CPRMV: `gitlab`, then `origin`, and
        # on 26 November 2026 a move to GitHub); the CI remote comes from ci_repo.
        for clone_and_branch in stamp_staleness.COMPONENTS.values():
            self.assertEqual(len(clone_and_branch), 2)
        self.assertFalse(hasattr(stamp_staleness, "REMOTE_URLS"))


class CiUrlFragmentTest(unittest.TestCase):
    def test_github(self):
        self.assertEqual(stamp_staleness.ci_url_fragment({"ci_repo": "https://github.com/open-regels/cprmv"}),
                         "github.com/open-regels/cprmv")

    def test_trailing_slash_git_suffix_and_credentials(self):
        self.assertEqual(stamp_staleness.ci_url_fragment({"ci_repo": "https://user@git.open-regels.nl/standards/cprmv.git/"}),
                         "git.open-regels.nl/standards/cprmv")

    def test_missing(self):
        self.assertEqual(stamp_staleness.ci_url_fragment({}), "")


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

    def test_github_origin_beside_gitlab_after_the_move(self):
        repo = self._clone({"gitlab": "https://git.open-regels.nl/standards/cprmv.git",
                            "origin": "https://github.com/open-regels/cprmv.git"})
        self.assertEqual(stamp_staleness.resolve_remote(repo, "github.com/open-regels/cprmv"), "origin")

    def test_old_owner_is_not_matched_after_an_org_move(self):
        repo = self._clone({"origin": "https://github.com/sgort/ttl-editor.git"})
        self.assertIsNone(stamp_staleness.resolve_remote(repo, "github.com/open-regels/ttl-editor"))

    def test_match_ignores_case(self):
        repo = self._clone({"origin": "https://github.com/Open-Regels/CPRMV.git"})
        self.assertEqual(stamp_staleness.resolve_remote(repo, "github.com/open-regels/cprmv"), "origin")


if __name__ == "__main__":
    unittest.main()
