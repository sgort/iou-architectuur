#!/usr/bin/env python3
"""Generate the downloadable PSA template from the guide pages.

The guide (docs/{nl,en}/psa/) is the single source. This script turns it into
the document an organisation fills in: IOU's decisions already written out per
chapter, with only the organisation's gaps and deviations left open, marked
[…]. See specs/PSA/2026-11-06-psa-template-design.md.

Outputs per language:
  templates/psa/<name>.md      the template (committed; checked for freshness
                               by psa-check.py)
  templates/psa/<name>.odt     made by pandoc (git-ignored)
  docs/assets/downloads/<name>.zip   both files, the site's download

Usage:
  python .claude/skills/iou-document-patch/scripts/psa-template.py          # nl and en
  python .../psa-template.py nl

Needs pypandoc_binary for the .odt: pip install -r requirements-dev.txt
"""

import importlib.util
import pathlib
import posixpath
import re
import sys
import zipfile

import yaml

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("psa_check", HERE / "psa-check.py")
psa_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(psa_check)

SITE = "https://iou-architectuur.open-regels.nl"
NAMES = {"nl": "psa-sjabloon-nl", "en": "psa-template-en"}
FILL = "[…]"

LABELS = {
    "nl": {
        "title": "Project Start Architectuur — [naam organisatie]",
        "fields": ["Organisatie", "Versie", "Status", "Datum", "Auteur", "Vastgesteld door"],
        "based_on": "Gebaseerd op de IOU PSA-gids, geverifieerd op {date} tegen {commits}.",
        "about": "Over dit sjabloon",
        "about_text": [
            "Dit sjabloon bevat de besluiten die IOU al heeft genomen, per hoofdstuk. "
            "U vult alleen in wat uw organisatie zelf bepaalt: overal waar […] staat.",
            "Besluiten in de laag **Kern** liggen vast. Van een besluit in de laag **Vervangbaar** "
            "mag u afwijken; leg dat vast in hoofdstuk 11 als afwijking (DEV-nn). Besluiten in de "
            "laag **Eigen keuze** vult u zelf in.",
            "De status bij IOU geeft aan hoe ver IOU zelf is met een besluit, op de datum hierboven.",
        ],
        "guide": "Toelichting in de gids:",
        "decisions": "Besluiten van IOU",
        "dec_header": "| ID | Besluit | Laag | Status bij IOU | Afwijken |",
        "closed": "niet open voor afwijking",
        "open": "mag; zie hieronder",
        "own": "uw eigen keuze",
        "copied": "Wat IOU beslist (overgenomen uit de IOU PSA-gids)",
        "phasing": "Fasering",
        "ours": "Onze invulling",
        "follow": "Volgen wij IOU's keuze voor {ab}? [ja / nee — zie afwijking DEV-…]",
        "summary_prompts": ["Doel", "Aanleiding", "Belangrijkste architectuurkeuzes", "Fasering"],
        "first": "IOU's eerste besluit, dat voor iedereen geldt: {ab} — {statement}",
        "register": "Besluitenregister van IOU",
        "deviations": "Onze afwijkingen",
        "risks": "Risico's",
        "risk_extra": " Geldt voor ons? | Onze maatregel |",
        "sections": ("Wat IOU beslist", "Fasering", "Wat u invult", "Besluitenregister",
                     "Afwijkingen vastleggen", "Risico's"),
    },
    "en": {
        "title": "Project Start Architecture — [organisation name]",
        "fields": ["Organisation", "Version", "Status", "Date", "Author", "Approved by"],
        "based_on": "Based on the IOU PSA guide, verified on {date} against {commits}.",
        "about": "About this template",
        "about_text": [
            "This template contains the decisions IOU has already taken, per chapter. "
            "You fill in only what your organisation decides itself: wherever […] appears.",
            "Decisions in the **Core** tier are fixed. You may deviate from a decision in the "
            "**Replaceable** tier; record it in chapter 11 as a deviation (DEV-nn). Decisions in "
            "the **Organisation's own** tier you fill in yourself.",
            "The status at IOU shows how far IOU itself has got with a decision, on the date above.",
        ],
        "guide": "Explained in the guide:",
        "decisions": "IOU's decisions",
        "dec_header": "| ID | Decision | Tier | Status at IOU | Deviation |",
        "closed": "not open to deviation",
        "open": "allowed; see below",
        "own": "your own choice",
        "copied": "What IOU decides (from the IOU PSA guide)",
        "phasing": "Phasing",
        "ours": "Our choices",
        "follow": "Do we follow IOU's choice for {ab}? [yes / no — see deviation DEV-…]",
        "summary_prompts": ["Purpose", "Rationale", "Key architectural choices", "Phasing"],
        "first": "IOU's first decision, which applies to everyone: {ab} — {statement}",
        "register": "IOU's decision register",
        "deviations": "Our deviations",
        "risks": "Risks",
        "risk_extra": " Applies to us? | Our measure |",
        "sections": ("What IOU decides", "Phasing", "What you fill in", "Decision register",
                     "Recording a deviation", "Risks"),
    },
}

LINK = re.compile(r"\]\(([^)\s]+)\)")


def _page_url(lang, path, site=SITE):
    """Absolute URL for a docs path relative to docs/<lang>/ (e.g. 'psa/index.md#x')."""
    path, _, anchor = path.partition("#")
    prefix = "" if lang == "en" or path.startswith("assets/") else "/nl"
    if path.endswith(".md"):
        path = path[:-3]
        path = "" if path == "index" else (path[:-len("index")] if path.endswith("/index") else path + "/")
    url = f"{site}{prefix}/{path}"
    return url + (f"#{anchor}" if anchor else "")


def absolute_links(text, lang, page, site=SITE):
    """Rewrite relative Markdown links in `text`, written on psa/<page>, to the live site."""
    def fix(match):
        target = match.group(1)
        if re.match(r"[a-z]+:", target):
            return match.group(0)
        if target.startswith("#"):
            return f"]({_page_url(lang, 'psa/' + page, site)}{target})"
        return f"]({_page_url(lang, posixpath.normpath(posixpath.join('psa', target)), site)})"
    return LINK.sub(fix, text)


def _section(text, heading):
    """Lines under `## heading` up to the next `## `, or None."""
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == f"## {heading}")
    except StopIteration:
        return None
    out = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        out.append(line)
    return out


def _without_fences(lines):
    out, fenced = [], False
    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return out


def _demote(lines):
    return [("#" + l) if l.startswith("#") else l for l in lines]


def _bullets(lines):
    """Top-level '- ' bullets, continuation lines joined."""
    items = []
    for line in lines:
        if line.startswith("- "):
            items.append(line[2:].strip())
        elif items and line.startswith("  ") and line.strip():
            items[-1] += " " + line.strip()
    return items


def _trim(lines):
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


def _front_matter(text):
    """The YAML front matter of a page, parsed (not split on every '---')."""
    if not text.startswith("---"):
        return {}
    end = text.find(chr(10) + "---", 3)
    return (yaml.safe_load(text[3:end]) or {}) if end != -1 else {}


def _title(text):
    return next(l[2:].strip() for l in psa_check.strip_front_matter(text).splitlines() if l.startswith("# "))


def build(lang_root, site=SITE):
    lang = psa_check.language(lang_root)
    L = LABELS[lang]
    copied_h, phasing_h, invult_h, register_h, deviation_h, risks_h = L["sections"]
    root = pathlib.Path(lang_root)
    pages = {p.stem: p.read_text(encoding="utf-8") for p in sorted(root.glob("*.md"))}
    register = {r["id"]: r for r in psa_check.register(lang_root)}

    meta = _front_matter(pages["index"])["verified"]
    commits = ", ".join(f"{k} {v}" for k, v in meta["against"].items())

    out = [f"# {L['title']}", "", "| | |", "|---|---|"]
    out += [f"| {field} | {FILL} |" for field in L["fields"]]
    out += ["", L["based_on"].format(date=meta["date"], commits=commits), "", f"## {L['about']}", ""]
    for paragraph in L["about_text"]:
        out += [paragraph, ""]

    def guide_line(stem):
        return [f"{L['guide']} <{_page_url(lang, 'psa/' + stem + '.md', site)}>", ""]

    # Chapter 1: prompts only, plus IOU's first decision.
    stem = "01-executive-summary"
    out += [f"## {_title(pages[stem])}", ""] + guide_line(stem)
    first = register.get("AB-01")
    if first:
        out += [L["first"].format(ab="AB-01", statement=first["statement"]), ""]
    for prompt in L["summary_prompts"]:
        out += [f"**{prompt}.** {FILL}", ""]

    for n in range(2, 11):
        stem = next(s for s in pages if s.startswith(f"{n:02d}-"))
        text = pages[stem]
        out += [f"## {_title(text)}", ""] + guide_line(stem)

        cited = sorted(set(psa_check.AB.findall(psa_check.strip_front_matter(text))) & set(register),
                       key=lambda ab: int(ab[3:]))
        if cited:
            out += [f"### {L['decisions']}", "", L["dec_header"], "|---|---|---|---|---|"]
            tiers = psa_check.VOCAB[lang]["tiers"]
            for ab in cited:
                r = register[ab]
                column = {tiers[0]: L["closed"], tiers[1]: L["open"], tiers[2]: L["own"]}.get(r["tier"], "")
                out.append(f"| {ab} | {r['statement']} | {r['tier']} | {r['status']} | {column} |")
            out.append("")

        copied = _section(text, copied_h)
        if copied:
            body = _trim(_demote(_without_fences(copied)))
            out += [f"### {L['copied']}", ""] + [absolute_links(l, lang, stem + ".md", site) for l in body] + [""]

        phasing = _section(text, phasing_h)
        if phasing:
            body = _trim(_demote(_without_fences(phasing)))
            out += [f"### {L['phasing']}", ""] + [absolute_links(l, lang, stem + ".md", site) for l in body] + [""]

        out += [f"### {L['ours']}", ""]
        for i, prompt in enumerate(_bullets(_section(text, invult_h) or []), 1):
            out += [f"{i}. {absolute_links(prompt, lang, stem + '.md', site)}", "", f"   {FILL}", ""]
        for ab in cited:
            if register[ab]["tier"] == psa_check.VOCAB[lang]["tiers"][1]:
                out += [L["follow"].format(ab=ab), ""]

    # Chapter 11: the full register, an empty deviation table, the risks with two columns more.
    stem = "11-decisions-and-risks"
    text = pages[stem]
    out += [f"## {_title(text)}", ""] + guide_line(stem)
    for heading, label in ((register_h, L["register"]),):
        table = [l for l in (_section(text, heading) or []) if l.startswith("|")]
        out += [f"### {label}", ""] + [absolute_links(l, lang, stem + ".md", site) for l in table] + [""]
    deviation = [l for l in (_section(text, deviation_h) or []) if l.startswith("|")]
    if deviation:
        cells = deviation[0].count("|") - 1
        out += [f"### {L['deviations']}", "", deviation[0], deviation[1],
                "| DEV-01 |" + f" {FILL} |" * (cells - 1), ""]
    risks = [l for l in (_section(text, risks_h) or []) if l.startswith("|")]
    if risks:
        out += [f"### {L['risks']}", "", risks[0].rstrip() + L["risk_extra"], risks[1].rstrip() + "---|---|"]
        out += [absolute_links(l.rstrip(), lang, stem + ".md", site) + f" {FILL} | {FILL} |" for l in risks[2:]]
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def write(lang, repo_root="."):
    """Write templates/psa/<name>.md and .odt and docs/assets/downloads/<name>.zip."""
    import pypandoc  # dev dependency: requirements-dev.txt

    repo = pathlib.Path(repo_root)
    name = NAMES[lang]
    md = repo / "templates" / "psa" / f"{name}.md"
    odt = md.with_suffix(".odt")
    zipped = repo / "docs" / "assets" / "downloads" / f"{name}.zip"
    md.parent.mkdir(parents=True, exist_ok=True)
    zipped.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(build(str(repo / "docs" / lang / "psa")), encoding="utf-8", newline="\n")
    pypandoc.convert_file(str(md), "odt", format="markdown", outputfile=str(odt))
    with zipfile.ZipFile(zipped, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(md, md.name)
        archive.write(odt, odt.name)
    return str(md), str(odt), str(zipped)


def main(argv):
    for lang in argv or ["nl", "en"]:
        for path in write(lang):
            print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
