#!/usr/bin/env python3
"""Check the structural rules of the Project Start Architectuur pages.

One language folder at a time (docs/nl/psa, docs/en/psa). The rules come from
specs/PSA/2026-11-06-psa-design.md:

  (a) every AB-NN cited on any page exists in the chapter-11 register;
  (b) register tier and status values come from that language's vocabulary;
  (c) every decision with status deels/nog niet (partly/not yet) is named in
      the "Raakt"/"Affects" column of at least one risk;
  (d) chapters 02-10 carry the four mandatory headings (Fasering/Phasing is
      optional);
  (e) no forbidden fragment: hostnames, routes and header values that would
      turn a generic gap description into instructions, and claims the
      component code does not support;
  (f) at most 9,000 words of prose (front matter, fenced blocks and table
      separator rows excluded).

Usage:
  python .claude/skills/iou-document-patch/scripts/psa-check.py
  python .../psa-check.py docs/nl/psa docs/en/psa

Exit status 1 if any folder has a problem.
"""

import pathlib
import re
import sys

WORD_BUDGET = 9000
AB = re.compile(r"\bAB-\d{2}\b")

VOCAB = {
    "nl": {
        "chapter_headings": ["Wat dit hoofdstuk in uw PSA vastlegt", "Wat IOU beslist", "Wat u invult", "Verder lezen"],
        "register": "Besluitenregister",
        "risks": "Risico's",
        "tiers": {"Kern", "Vervangbaar", "Eigen keuze"},
        "statuses": {"gerealiseerd", "deels", "nog niet"},
        "open": {"deels", "nog niet"},
    },
    "en": {
        "chapter_headings": ["What this chapter settles in your PSA", "What IOU decides", "What you fill in", "Further reading"],
        "register": "Decision register",
        "risks": "Risks",
        "tiers": {"Core", "Replaceable", "Organisation's own"},
        "statuses": {"realised", "partly", "not yet"},
        "open": {"partly", "not yet"},
    },
}

# Case-insensitive patterns. Service hostnames on open-regels.nl are forbidden;
# the issue tracker at git.open-regels.nl is not, because gaps link their issue.
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
    parts = pathlib.Path(root).resolve().parts
    return "en" if "en" in parts[-3:] else "nl"


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


def check(lang_root):
    root = pathlib.Path(lang_root)
    vocab = VOCAB[language(root)]
    problems = []
    pages = {p.name: p.read_text(encoding="utf-8") for p in sorted(root.glob("*.md"))}

    register_text = pages.get(REGISTER_FILE, "")
    register = section_table(register_text, vocab["register"])
    risks = section_table(register_text, vocab["risks"])
    if register is None:
        problems.append(f"{REGISTER_FILE}: no '## {vocab['register']}' section")
        register = []
    if risks is None:
        problems.append(f"{REGISTER_FILE}: no '## {vocab['risks']}' section")
        risks = []

    known, open_ids = set(), set()
    for row in register:
        if len(row) < 4:
            problems.append(f"{REGISTER_FILE}: register row has {len(row)} cells: {' | '.join(row)}")
            continue
        ab, tier, status = row[0], row[2], row[3]
        known.add(ab)
        if tier not in vocab["tiers"]:
            problems.append(f"{REGISTER_FILE}: {ab} tier '{tier}' not in {sorted(vocab['tiers'])}")
        if status not in vocab["statuses"]:
            problems.append(f"{REGISTER_FILE}: {ab} status '{status}' not in {sorted(vocab['statuses'])}")
        elif status in vocab["open"]:
            open_ids.add(ab)

    covered = set()
    for row in risks:
        if len(row) >= 3:
            covered |= set(AB.findall(row[2]))
    for ab in sorted(open_ids - covered):
        problems.append(f"{REGISTER_FILE}: {ab} is not realised but no risk names it")

    words = 0
    for name, text in pages.items():
        body = prose(text)
        words += len(body.split())
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
    check.words = words
    return problems


def main(argv):
    roots = argv or ["docs/nl/psa", "docs/en/psa"]
    failed = False
    for root in roots:
        problems = check(root)
        print(f"{root}: words: {check.words}")
        for problem in problems:
            print(f"  ✗ {problem}")
        failed |= bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
