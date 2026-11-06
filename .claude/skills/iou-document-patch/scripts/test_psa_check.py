"""Tests for psa-check.py.

Run: venv/Scripts/python.exe -m unittest discover -s .claude/skills/iou-document-patch/scripts -p "test_*.py" -v
"""

import importlib.util
import pathlib
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("psa_check", HERE / "psa-check.py")
psa_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(psa_check)

CHAPTERS = [
    "02-context-and-scope.md",
    "03-architecture-frameworks.md",
    "04-functional-architecture.md",
    "05-application-architecture.md",
    "06-data-architecture.md",
    "07-integration-architecture.md",
    "08-security-and-privacy.md",
    "09-technical-infrastructure.md",
    "10-management-and-continuity.md",
]

NL = {
    "chapter_headings": ["Wat dit hoofdstuk in uw PSA vastlegt", "Wat IOU beslist", "Wat u invult", "Verder lezen"],
    "register": "Besluitenregister",
    "register_header": "| ID | Besluit | Laag | Status | Toelichting |",
    "risks": "Risico's",
    "risks_header": "| ID | Risico | Raakt | Wat u ondertussen doet | Issue |",
    "deviation": "Afwijkingen vastleggen",
}
EN = {
    "chapter_headings": ["What this chapter settles in your PSA", "What IOU decides", "What you fill in", "Further reading"],
    "register": "Decision register",
    "register_header": "| ID | Decision | Tier | Status | Note |",
    "risks": "Risks",
    "risks_header": "| ID | Risk | Affects | What you do meanwhile | Issue |",
    "deviation": "Recording a deviation",
}

NL_REGISTER = [
    "| AB-01 | Open formaten | Kern | gerealiseerd | Alle componenten |",
    "| AB-12 | Engine afgeschermd | Kern | deels | RBA wel, engine niet |",
]
NL_RISKS = ["| R-01 | Engine bereikbaar | AB-12 | Afschermen in eigen netwerk | #415 |"]
EN_REGISTER = [
    "| AB-01 | Open formats | Core | realised | All components |",
    "| AB-12 | Engine shielded | Replaceable | partly | RBA yes, engine no |",
]
EN_RISKS = ["| R-01 | Engine reachable | AB-12 | Shield it in your own network | #415 |"]


def separator(header):
    return "|" + "---|" * (header.count("|") - 1)


def build(root, lang=NL, register=None, risks=None, chapter_body="Zie AB-01.", overrides=None):
    """Write a minimal but complete PSA language folder into root."""
    register = NL_REGISTER if register is None else register
    risks = NL_RISKS if risks is None else risks
    root = pathlib.Path(root)
    (root / "index.md").write_text("---\ntitle: x\n---\n\n# Intro\n\nTekst.\n", encoding="utf-8")
    (root / "01-executive-summary.md").write_text("# Samenvatting\n\nAB-12 telt.\n", encoding="utf-8")
    for name in CHAPTERS:
        body = "# Hoofdstuk\n\n" + "".join(f"## {h}\n\n{chapter_body}\n\n" for h in lang["chapter_headings"])
        (root / name).write_text(body, encoding="utf-8")
    ch11 = [
        "# 11", "",
        f"## {lang['register']}", "", lang["register_header"], separator(lang["register_header"]), *register, "",
        f"## {lang['deviation']}", "", "Tekst.", "",
        f"## {lang['risks']}", "", lang["risks_header"], separator(lang["risks_header"]), *risks, "",
    ]
    (root / "11-decisions-and-risks.md").write_text("\n".join(ch11), encoding="utf-8")
    for name, text in (overrides or {}).items():
        (root / name).write_text(text, encoding="utf-8")
    return str(root)


class PsaCheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self._tmp.name) / "nl" / "psa"
        self.dir.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def test_clean_fixture_passes(self):
        self.assertEqual(psa_check.check(build(self.dir)), [])

    def test_unknown_ab_id(self):
        root = build(self.dir, overrides={"05-application-architecture.md":
            "".join(f"## {h}\n\nZie AB-31.\n\n" for h in NL["chapter_headings"])})
        problems = psa_check.check(root)
        self.assertEqual(len(problems), 1)
        self.assertIn("AB-31", problems[0])

    def test_partial_without_risk(self):
        root = build(self.dir, register=[
            "| AB-01 | Open formaten | Kern | gerealiseerd | x |",
            "| AB-12 | Engine afgeschermd | Kern | nog niet | x |",
        ], risks=["| R-01 | Iets anders | AB-01 | x | — |"])
        problems = psa_check.check(root)
        self.assertEqual(len(problems), 1)
        self.assertIn("AB-12", problems[0])

    def test_bad_status_value(self):
        root = build(self.dir, register=[
            "| AB-01 | Open formaten | Kern | klaar | x |",
            "| AB-12 | Engine afgeschermd | Kern | deels | x |",
        ])
        problems = psa_check.check(root)
        self.assertEqual(len(problems), 1)
        self.assertIn("klaar", problems[0])

    def test_bad_tier_value(self):
        root = build(self.dir, register=[
            "| AB-01 | Open formaten | Verplicht | gerealiseerd | x |",
            "| AB-12 | Engine afgeschermd | Kern | deels | x |",
        ])
        problems = psa_check.check(root)
        self.assertEqual(len(problems), 1)
        self.assertIn("Verplicht", problems[0])

    def test_missing_heading(self):
        headings = [h for h in NL["chapter_headings"] if h != "Wat u invult"]
        root = build(self.dir, overrides={"04-functional-architecture.md":
            "".join(f"## {h}\n\nAB-01\n\n" for h in headings)})
        problems = psa_check.check(root)
        self.assertEqual(len(problems), 1)
        self.assertIn("04-functional-architecture.md", problems[0])
        self.assertIn("Wat u invult", problems[0])

    def test_forbidden_detail(self):
        root = build(self.dir, chapter_body="De engine-rest is open.")
        problems = psa_check.check(root)
        self.assertTrue(problems)
        self.assertTrue(all("engine-rest" in p for p in problems))

    def test_issue_link_on_gitlab_allowed(self):
        root = build(self.dir, chapter_body="AB-01, zie https://git.open-regels.nl/regels/editor/-/work_items/2.")
        self.assertEqual(psa_check.check(root), [])

    def test_service_hostname_forbidden(self):
        root = build(self.dir, overrides={"index.md": "# Intro\n\nDe engine draait op operaton.open-regels.nl.\n"})
        problems = psa_check.check(root)
        self.assertEqual(len(problems), 1)
        self.assertIn("open-regels.nl", problems[0])

    def test_word_budget(self):
        words = " ".join(["woord"] * 9001)
        over = build(self.dir, overrides={"index.md": f"# Intro\n\n{words}\n"})
        problems = psa_check.check(over)
        self.assertEqual(len(problems), 1)
        self.assertIn("9000", problems[0])
        inside = build(self.dir, overrides={"index.md": f"# Intro\n\n```mermaid\n{words}\n```\n"})
        self.assertEqual(psa_check.check(inside), [])

    def test_english_vocabulary(self):
        en_dir = pathlib.Path(self._tmp.name) / "en" / "psa"
        en_dir.mkdir(parents=True)
        root = build(en_dir, lang=EN, register=EN_REGISTER, risks=EN_RISKS, chapter_body="See AB-01.")
        self.assertEqual(psa_check.check(root), [])
        dutch_status = [EN_REGISTER[0], "| AB-12 | Engine shielded | Core | deels | x |"]
        root = build(en_dir, lang=EN, register=dutch_status, risks=EN_RISKS, chapter_body="See AB-01.")
        problems = psa_check.check(root)
        self.assertEqual(len(problems), 1)
        self.assertIn("deels", problems[0])


if __name__ == "__main__":
    unittest.main()
