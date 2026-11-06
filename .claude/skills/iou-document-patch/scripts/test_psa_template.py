"""Tests for psa-template.py.

Run: venv/Scripts/python.exe -m unittest discover -s .claude/skills/iou-document-patch/scripts -p "test_*.py" -v
"""

import importlib.util
import pathlib
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("psa_template", HERE / "psa-template.py")
psa_template = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(psa_template)

NL_ = chr(10)
SITE = "https://iou-architectuur.open-regels.nl"
SHAS = {"CPSV Editor": "0412e9b", "Linked Data Explorer": "814c4bb", "RONL Business API": "ff6c362",
        "Norm Editor": "c47096b", "CPRMV": "8262d3e"}

LANG = {
    "nl": {
        "intro": "Over deze PSA",
        "headings": ["Wat dit hoofdstuk in uw PSA vastlegt", "Wat IOU beslist", "Fasering", "Wat u invult", "Verder lezen"],
        "register": "Besluitenregister", "deviation": "Afwijkingen vastleggen", "risks": "Risico's",
        "reg_header": "| ID | Besluit | Laag | Status | Toelichting |",
        "reg_rows": ["| AB-01 | Open formaten. | Kern | gerealiseerd | |",
                     "| AB-02 | IOU kiest Operaton. | Vervangbaar | deels | x |"],
        "dev_header": "| ID | Wijkt af van | Reden | Strijdig met principe | Kosten | Weg terug |",
        "dev_row": "| DEV-01 | AB-02: Operaton | Contract. | AB-01 | Geld. | Terug. |",
        "risk_header": "| ID | Risico | Raakt | Wat u ondertussen doet | Issue |",
        "risk_row": "| R-01 | Engine open. | AB-02 | Afschermen. | — |",
        "sub": "### Hoofdfuncties",
        "invult": ["- Welke functies u gebruikt.", "- Welke rollen bij uw", "  organisatie horen."],
    },
    "en": {
        "intro": "About this PSA",
        "headings": ["What this chapter settles in your PSA", "What IOU decides", "Phasing", "What you fill in", "Further reading"],
        "register": "Decision register", "deviation": "Recording a deviation", "risks": "Risks",
        "reg_header": "| ID | Decision | Tier | Status | Note |",
        "reg_rows": ["| AB-01 | Open formats. | Core | realised | |",
                     "| AB-02 | IOU chooses Operaton. | Replaceable | partly | x |"],
        "dev_header": "| ID | Deviates from | Reason | Conflicts with principle | Cost | Way back |",
        "dev_row": "| DEV-01 | AB-02: Operaton | Contract. | AB-01 | Money. | Back. |",
        "risk_header": "| ID | Risk | Affects | What you do meanwhile | Issue |",
        "risk_row": "| R-01 | Engine open. | AB-02 | Shield it. | — |",
        "sub": "### Main functions",
        "invult": ["- Which functions you use.", "- Which roles belong to your", "  organisation."],
    },
}

CHAPTERS = ["02-context-and-scope", "03-architecture-frameworks", "04-functional-architecture",
            "05-application-architecture", "06-data-architecture", "07-integration-architecture",
            "08-security-and-privacy", "09-technical-infrastructure", "10-management-and-continuity"]


def sep(header):
    return "|" + "---|" * (header.count("|") - 1)


def front(title):
    lines = ["---", f'title: "{title}"', "scope: cross-cutting", "verified:", "  date: 2026-11-06", "  against:"]
    lines += [f'    {k}: "{v}"' for k, v in SHAS.items()]
    return NL_.join(lines + ["---", ""])


def write_fixture(root, lang):
    L = LANG[lang]
    root = pathlib.Path(root)
    (root / "index.md").write_text(front(L["intro"]) + NL_ + "# " + L["intro"] + NL_, encoding="utf-8")
    (root / "01-executive-summary.md").write_text(front("1. Summary") + "# 1. Summary" + NL_ + NL_ + "AB-01." + NL_, encoding="utf-8")
    h = L["headings"]
    for name in CHAPTERS:
        cites = "AB-01 en AB-02" if name == "04-functional-architecture" else "AB-01"
        body = [f"# {name[:2].lstrip('0')}. Title {name}", "",
                f"## {h[0]}", "", "Explanation that stays out.", "",
                f"## {h[1]}", "", f"**A decision** ({cites}).", ""]
        if name == "04-functional-architecture":
            body += [L["sub"], "", "| Function | Component |", "|---|---|", "| Publish | CPSV Editor |", "",
                     "See [tasks](../ronl-business-api/features/tasks.md), [tiers](index.md#drie-lagen),",
                     "[chapter 7](07-integration-architecture.md) and [elsewhere](https://example.org/x).", "",
                     "```mermaid", "flowchart LR", "    A --> B", "```", "",
                     f"## {h[2]}", "", "| | One | Now | Two |", "|---|---|---|---|", "| Roles | a | b | c |", ""]
        body += [f"## {h[3]}", ""] + L["invult"] + ["", f"## {h[4]}", "", "- [more](../x.md)", ""]
        (root / f"{name}.md").write_text(front(name) + NL_.join(body), encoding="utf-8")
    ch11 = ["# 11. Decisions", "", f"## {L['register']}", "", L["reg_header"], sep(L["reg_header"])] + L["reg_rows"] + [
        "", f"## {L['deviation']}", "", L["dev_header"], sep(L["dev_header"]), L["dev_row"], "",
        f"## {L['risks']}", "", L["risk_header"], sep(L["risk_header"]), L["risk_row"], ""]
    (root / "11-decisions-and-risks.md").write_text(front("11") + NL_.join(ch11), encoding="utf-8")
    return str(root)


class TemplateTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = pathlib.Path(self._tmp.name)
        (base / "nl" / "psa").mkdir(parents=True)
        (base / "en" / "psa").mkdir(parents=True)
        self.nl = psa_template.build(write_fixture(base / "nl" / "psa", "nl"))
        self.en = psa_template.build(write_fixture(base / "en" / "psa", "en"))

    def tearDown(self):
        self._tmp.cleanup()

    def chapter(self, text, number):
        start = text.index(f"\n## {number}. ")
        end = text.find("\n## ", start + 1)
        return text[start:end if end != -1 else None]

    def test_title_and_verified_line(self):
        self.assertIn("Project Start Architectuur — [naam organisatie]", self.nl)
        self.assertIn("2026-11-06", self.nl)
        for sha in SHAS.values():
            self.assertIn(sha, self.nl)

    def test_chapter_decision_table(self):
        ch4 = self.chapter(self.nl, 4)
        row = next(l for l in ch4.splitlines() if l.startswith("| AB-01 |"))
        for cell in ("Open formaten.", "Kern", "gerealiseerd", "niet open voor afwijking"):
            self.assertIn(cell, row)

    def test_wat_iou_beslist_copied(self):
        ch4 = self.chapter(self.nl, 4)
        self.assertIn("Hoofdfuncties", ch4)
        self.assertIn("| Publish | CPSV Editor |", ch4)
        self.assertIn("**A decision** (AB-01 en AB-02).", ch4)
        self.assertNotIn("Explanation that stays out.", ch4)

    def test_prompts_from_wat_u_invult(self):
        ch4 = self.chapter(self.nl, 4)
        self.assertIn("1. Welke functies u gebruikt.", ch4)
        self.assertIn("2. Welke rollen bij uw organisatie horen.", ch4)
        after_first = ch4.split("1. Welke functies u gebruikt.", 1)[1]
        self.assertTrue(after_first.lstrip().startswith("[…]"))

    def test_replaceable_question(self):
        self.assertIn("Volgen wij IOU's keuze voor AB-02?", self.chapter(self.nl, 4))
        self.assertNotIn("Volgen wij IOU's keuze", self.chapter(self.nl, 5))

    def test_links_absolute(self):
        ch4 = self.chapter(self.nl, 4)
        self.assertIn(f"({SITE}/nl/ronl-business-api/features/tasks/)", ch4)
        self.assertIn(f"({SITE}/nl/psa/#drie-lagen)", ch4)
        self.assertIn(f"({SITE}/nl/psa/07-integration-architecture/)", ch4)
        self.assertIn("(https://example.org/x)", ch4)
        en4 = self.chapter(self.en, 4)
        self.assertIn(f"({SITE}/ronl-business-api/features/tasks/)", en4)
        self.assertIn(f"({SITE}/psa/07-integration-architecture/)", en4)

    def test_mermaid_and_further_reading_excluded(self):
        self.assertNotIn("```", self.nl)
        self.assertNotIn("Verder lezen", self.nl)
        self.assertNotIn("Further reading", self.en)

    def test_guide_link_per_chapter(self):
        self.assertIn(f"{SITE}/nl/psa/04-functional-architecture/", self.chapter(self.nl, 4))

    def test_chapter11_register_dev_and_risks(self):
        ch11 = self.chapter(self.nl, 11)
        self.assertIn("| AB-01 |", ch11)
        self.assertIn("| AB-02 |", ch11)
        self.assertIn("| DEV-01 | […] |", ch11)
        self.assertNotIn("Contract.", ch11)
        header = next(l for l in ch11.splitlines() if l.startswith("| ID | Risico |"))
        self.assertTrue(header.endswith("Geldt voor ons? | Onze maatregel |"))
        self.assertIn("| R-01 |", ch11)

    def test_english_labels(self):
        self.assertIn("Project Start Architecture — [organisation name]", self.en)
        self.assertIn("IOU's decisions", self.en)
        self.assertIn("Our choices", self.en)
        self.assertIn("Do we follow IOU's choice for AB-02?", self.en)
        self.assertIn("Applies to us? | Our measure |", self.en)


_check_spec = importlib.util.spec_from_file_location("psa_check_for_template", HERE / "psa-check.py")
psa_check = importlib.util.module_from_spec(_check_spec)
_check_spec.loader.exec_module(psa_check)
REPO = HERE.parents[3]


class FreshnessTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = pathlib.Path(self._tmp.name)
        (base / "nl" / "psa").mkdir(parents=True)
        self.root = write_fixture(base / "nl" / "psa", "nl")
        self.template = base / "psa-sjabloon-nl.md"

    def tearDown(self):
        self._tmp.cleanup()

    def test_template_fresh(self):
        self.template.write_text(psa_template.build(self.root), encoding="utf-8")
        self.assertEqual(psa_check.check_template(self.root, str(self.template)), [])

    def test_template_stale(self):
        self.template.write_text(psa_template.build(self.root) + "old line" + NL_, encoding="utf-8")
        problems = psa_check.check_template(self.root, str(self.template))
        self.assertEqual(len(problems), 1)
        self.assertIn("regenerate", problems[0])

    def test_template_missing(self):
        problems = psa_check.check_template(self.root, str(self.template))
        self.assertEqual(len(problems), 1)
        self.assertIn("regenerate", problems[0])


class RealPagesTest(unittest.TestCase):
    def test_real_pages_template(self):
        out = psa_template.build(str(REPO / "docs" / "nl" / "psa"))
        for n in range(1, 33):
            self.assertIn(f"AB-{n:02d}", out)
        self.assertIn("Volgen wij IOU's keuze voor AB-32?", out)


if __name__ == "__main__":
    unittest.main()
