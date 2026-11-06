"""Tests for the profiles of stamp-staleness.py.

Run: venv/Scripts/python.exe -m unittest discover -s .claude/skills/iou-document-patch/scripts -p "test_*.py" -v
"""

import importlib.util
import pathlib
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

    def test_cprmv_uses_its_only_remote(self):
        # The cprmv clone has a single remote, origin, which is GitLab.
        self.assertEqual(stamp_staleness.COMPONENTS["CPRMV"], ("cprmv", "main", "origin"))


if __name__ == "__main__":
    unittest.main()
