#!/usr/bin/env python3
"""Check the structural rules of the Project Start Architectuur pages.

One language folder at a time (docs/nl/psa, docs/en/psa). The rules come from
specs/PSA/2026-11-06-psa-design.md:

  (a) every AB-NN cited on any page, fenced blocks included, exists in the
      chapter-11 register, and no register ID appears twice;
  (b) register tier and status values come from that language's vocabulary;
  (c) every decision with status deels/nog niet (partly/not yet) is named in
      the "Raakt"/"Affects" column of at least one risk; a retired decision
      (vervallen/retired) needs none; risk IDs read R-NN;
  (d) chapters 02-10 carry the four mandatory headings (Fasering/Phasing is
      optional);
  (e) no forbidden fragment: hostnames, routes and header values that would
      turn a generic gap description into instructions, and claims the
      component code does not support;
  (f) at most 12,000 words of prose (front matter, fenced blocks and table
      separator rows excluded);
  (g) all twelve page files exist.

With both languages, also:

  (h) the Dutch and English registers carry the same IDs with the same tier
      and status (mapped across the two vocabularies);
  (i) the committed template (templates/psa/<name>.md) equals a fresh
      generation by psa-template.py — after editing the pages, regenerate.

Usage:
  python .claude/skills/iou-document-patch/scripts/psa-check.py
  python .../psa-check.py docs/nl/psa docs/en/psa

Exit status 1 if any folder has a problem.
"""

import importlib.util
import pathlib
import re
import sys

WORD_BUDGET = 12000  # raised from 9,000 on 6 Nov 2026 (architect); condense later
AB = re.compile(r"\bAB-\d{2}\b")
RISK_ID = re.compile(r"R-\d{2}")

PAGES = [
    "index.md",
    "01-executive-summary.md",
    "02-context-and-scope.md",
    "03-architecture-frameworks.md",
    "04-functional-architecture.md",
    "05-application-architecture.md",
    "06-data-architecture.md",
    "07-integration-architecture.md",
    "08-security-and-privacy.md",
    "09-technical-infrastructure.md",
    "10-management-and-continuity.md",
    "11-decisions-and-risks.md",
]

VOCAB = {
    "nl": {
        "chapter_headings": ["Wat dit hoofdstuk in uw PSA vastlegt", "Wat IOU beslist", "Wat u invult", "Verder lezen"],
        "register": "Besluitenregister",
        "risks": "Risico's",
        "tiers": ["Kern", "Vervangbaar", "Eigen keuze"],
        "statuses": ["gerealiseerd", "deels", "nog niet", "vervallen"],
        "open": {"deels", "nog niet"},
    },
    "en": {
        "chapter_headings": ["What this chapter settles in your PSA", "What IOU decides", "What you fill in", "Further reading"],
        "register": "Decision register",
        "risks": "Risks",
        "tiers": ["Core", "Replaceable", "Organisation's own"],
        "statuses": ["realised", "partly", "not yet", "retired"],
        "open": {"partly", "not yet"},
    },
}

# Case-insensitive patterns. Service hostnames on open-regels.nl are forbidden;
# the issue tracker at git.open-regels.nl is not, because closed gaps link their
# issue. (Open security gaps get no link at all: see the weekly-pass skill.)
FORBIDDEN = [
    (r"(?<!git\.)open-regels\.nl", "open-regels.nl"),
    (r"triply\.cc", "triply.cc"),
    (r"engine-rest", "engine-rest"),
    (r"Access-Control-Allow-Origin", "Access-Control-Allow-Origin"),
    (r"CORS: \*", "CORS: *"),
    (r"origin: '\*'", "origin: '*'"),
    (r"signed builds?", "signed build"),
    (r"ondertekende builds?", "ondertekende build"),
    (r"compliance-grade", "compliance-grade"),
    (r"multi-region", "multi-region"),
    (r"NEN 7510", "NEN 7510"),
]

CHAPTERS = [f"{n:02d}-" for n in range(2, 11)]
REGISTER_FILE = "11-decisions-and-risks.md"


def language(root):
    parts = pathlib.Path(root).resolve().parts[-3:]
    if "nl" in parts:
        return "nl"
    if "en" in parts:
        return "en"
    raise ValueError(f"{root}: cannot tell the language — expected an 'nl' or 'en' folder")


def strip_front_matter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def prose(text):
    """Text outside front matter and fenced blocks, without table separator rows."""
    out, fenced = [], False
    for line in strip_front_matter(text).splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced or re.fullmatch(r"\s*\|[\s:|-]*\|\s*", line):
            continue
        out.append(line)
    return "\n".join(out)


def section_table(text, heading):
    """Rows (lists of cell strings) of the first table under `## heading`."""
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == f"## {heading}")
    except StopIteration:
        return None
    rows = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if line.strip().startswith("|"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif rows:
            break
    return [r for r in rows[2:]] if len(rows) >= 2 else []


def _pages(lang_root):
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(pathlib.Path(lang_root).glob("*.md"))}


def register(lang_root):
    """The chapter-11 register as dicts: id, statement, tier, status, note."""
    vocab = VOCAB[language(lang_root)]
    path = pathlib.Path(lang_root) / REGISTER_FILE
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    rows = section_table(text, vocab["register"]) or []
    keys = ("id", "statement", "tier", "status", "note")
    return [dict(zip(keys, row + [""] * (5 - len(row)))) for row in rows if len(row) >= 4]


def count_words(lang_root):
    return sum(len(prose(text).split()) for text in _pages(lang_root).values())


def check(lang_root):
    root = pathlib.Path(lang_root)
    vocab = VOCAB[language(root)]
    problems = []
    pages = _pages(root)

    for name in PAGES:
        if name not in pages:
            problems.append(f"{root}: missing page file {name}")

    register_text = pages.get(REGISTER_FILE, "")
    rows = section_table(register_text, vocab["register"])
    risks = section_table(register_text, vocab["risks"])
    if rows is None:
        problems.append(f"{REGISTER_FILE}: no '## {vocab['register']}' section")
        rows = []
    if risks is None:
        problems.append(f"{REGISTER_FILE}: no '## {vocab['risks']}' section")
        risks = []

    known, open_ids = set(), set()
    for row in rows:
        if len(row) < 4:
            problems.append(f"{REGISTER_FILE}: register row has {len(row)} cells: {' | '.join(row)}")
            continue
        ab, tier, status = row[0], row[2], row[3]
        if ab in known:
            problems.append(f"{REGISTER_FILE}: duplicate register ID {ab}")
        known.add(ab)
        if tier not in vocab["tiers"]:
            problems.append(f"{REGISTER_FILE}: {ab} tier '{tier}' not in {vocab['tiers']}")
        if status not in vocab["statuses"]:
            problems.append(f"{REGISTER_FILE}: {ab} status '{status}' not in {vocab['statuses']}")
        elif status in vocab["open"]:
            open_ids.add(ab)

    covered = set()
    for row in risks:
        if not RISK_ID.fullmatch(row[0]):
            problems.append(f"{REGISTER_FILE}: risk ID '{row[0]}' does not read R-NN")
        if len(row) >= 3:
            covered |= set(AB.findall(row[2]))
    for ab in sorted(open_ids - covered):
        problems.append(f"{REGISTER_FILE}: {ab} is not realised but no risk names it")

    words = 0
    for name, text in pages.items():
        body = strip_front_matter(text)
        words += len(prose(text).split())
        for ab in sorted(set(AB.findall(body)) - known):
            problems.append(f"{name}: cites {ab}, which is not in the register")
        for pattern, label in FORBIDDEN:
            if re.search(pattern, text, re.IGNORECASE):
                problems.append(f"{name}: contains forbidden fragment '{label}'")
        if any(name.startswith(prefix) for prefix in CHAPTERS):
            headings = {l.strip()[3:] for l in text.splitlines() if l.startswith("## ")}
            for heading in vocab["chapter_headings"]:
                if heading not in headings:
                    problems.append(f"{name}: missing heading '## {heading}'")

    if words > WORD_BUDGET:
        problems.append(f"{root}: {words} words of prose, over the {WORD_BUDGET} budget")
    return problems


def check_pair(nl_root, en_root):
    """The Dutch and English registers carry the same IDs, tiers and statuses."""
    tier = dict(zip(VOCAB["nl"]["tiers"], VOCAB["en"]["tiers"]))
    status = dict(zip(VOCAB["nl"]["statuses"], VOCAB["en"]["statuses"]))
    nl = {r["id"]: r for r in register(nl_root)}
    en = {r["id"]: r for r in register(en_root)}
    problems = []
    for ab in sorted(set(nl) | set(en)):
        if ab not in en:
            problems.append(f"{ab} is in the Dutch register but not in the English one")
        elif ab not in nl:
            problems.append(f"{ab} is in the English register but not in the Dutch one")
        else:
            if tier.get(nl[ab]["tier"]) != en[ab]["tier"]:
                problems.append(f"{ab}: tier '{nl[ab]['tier']}' (nl) vs '{en[ab]['tier']}' (en)")
            if status.get(nl[ab]["status"]) != en[ab]["status"]:
                problems.append(f"{ab}: status '{nl[ab]['status']}' (nl) vs '{en[ab]['status']}' (en)")
    return problems


TEMPLATES = {"nl": "templates/psa/psa-sjabloon-nl.md", "en": "templates/psa/psa-template-en.md"}


def check_template(lang_root, template_path):
    """The committed template matches what psa-template.py makes of the pages now."""
    spec = importlib.util.spec_from_file_location("psa_template", pathlib.Path(__file__).with_name("psa-template.py"))
    psa_template = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(psa_template)
    path = pathlib.Path(template_path)
    fresh = psa_template.build(lang_root)
    if not path.exists():
        return [f"{template_path}: missing — regenerate with psa-template.py"]
    if path.read_text(encoding="utf-8") != fresh:
        return [f"{template_path}: out of date with {lang_root} — regenerate with psa-template.py"]
    return []


def main(argv):
    roots = argv or ["docs/nl/psa", "docs/en/psa"]
    failed = False
    for root in roots:
        problems = check(root)
        print(f"{root}: words: {count_words(root)}")
        for problem in problems:
            print(f"  ✗ {problem}")
        failed |= bool(problems)
        lang = language(root)
        if not argv and lang in TEMPLATES:
            stale = check_template(root, TEMPLATES[lang])
            for problem in stale:
                print(f"  ✗ {problem}")
            failed |= bool(stale)
    by_language = {language(r): r for r in roots}
    if {"nl", "en"} <= set(by_language):
        problems = check_pair(by_language["nl"], by_language["en"])
        print(f"nl/en register parity: {'ok' if not problems else len(problems)}")
        for problem in problems:
            print(f"  ✗ {problem}")
        failed |= bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
