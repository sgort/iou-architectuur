"""Render the weekly ICTU assessment series as tables and inline SVG charts.

The scores live in one place — `docs/data/ictu-assessments.yml` — and every
rendering of them is generated from it at build time. A page asks for one by
leaving a placeholder on a line of its own:

    <!-- ictu:scores -->      the current assessment's score table
    <!-- ictu:totals -->      totals per component over time, as a line chart
    <!-- ictu:heatmap -->     the current per-recommendation scores, as a grid
    <!-- ictu:movement -->    what each week added, per component
    <!-- ictu:changes -->     the week-by-week reasons, as a table

Why generate rather than write the tables by hand: the series is re-scored
every week, and a hand-maintained table and chart drift apart the first time
someone edits one of them. The data file is the single record; if a score is
wrong it is wrong in exactly one place.

The charts are inline SVG, not a JavaScript library. Three reasons: the site's
Content-Security-Policy work (#98) is about removing third-party script
origins rather than adding one; an inline `<svg>` inherits Material's own CSS
variables, so it follows the palette into dark mode without a second theme
definition; and it renders with no network request and no layout shift.

Colours come from `var(--md-*)` and from the four `--ictu-*` variables defined
in `docs/stylesheets/extra.css`, so nothing here hard-codes a hex value that
would survive a palette change.

A missing or malformed data file is deliberately non-fatal: the placeholder is
replaced with an admonition saying so, and the rest of the page still builds.
"""

import os
from datetime import date

import yaml

DATA_REL = os.path.join("data", "ictu-assessments.yml")

# Chart geometry. The viewBox is fixed and the SVG scales to its container;
# `preserveAspectRatio` keeps the aspect on narrow screens.
W, H = 720, 300
PAD_L, PAD_R, PAD_T, PAD_B = 46, 118, 18, 34


def _esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _fmt_date(value):
    """'2026-09-20' or a date -> '20 Sep'."""
    if isinstance(value, str):
        value = date.fromisoformat(value)
    return f"{value.day} {value.strftime('%b')}"


def _load(config):
    path = os.path.join(config["docs_dir"], DATA_REL)
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    order = [key for key, _ in _recommendations(data)]
    for entry in data["assessments"]:
        for comp, scores in entry["scores"].items():
            if len(scores) != len(order):
                raise ValueError(
                    f"{entry['date']} {comp}: {len(scores)} scores, "
                    f"expected {len(order)}"
                )
    return data


def _recommendations(data):
    return [(item["id"], item) for item in data["recommendations"]]


def _components(data):
    return data["components"]


def _total(entry, comp_key):
    return sum(entry["scores"][comp_key])


def _measured(entry):
    return entry.get("kind", "measured") == "measured"


# --------------------------------------------------------------------------
# tables


def _scores_table(data):
    """The current assessment, one column per component, with the change."""
    latest = data["assessments"][-1]
    previous = data["assessments"][-2] if len(data["assessments"]) > 1 else None
    comps = _components(data)

    head = "| | Recommendation | " + " | ".join(c["name"] for c in comps) + " |"
    rule = "|---|---|" + ":-:|" * len(comps)
    rows = [head, rule]

    group = None
    for rid, rec in _recommendations(data):
        if rec.get("group") and rec["group"] != group:
            group = rec["group"]
            rows.append(f"| | **{group}** |" + " |" * len(comps))
        cells = []
        for comp in comps:
            index = [r for r, _ in _recommendations(data)].index(rid)
            score = latest["scores"][comp["key"]][index]
            if previous:
                delta = score - previous["scores"][comp["key"]][index]
                cells.append(f"{score} {_delta_badge(delta)}" if delta else str(score))
            else:
                cells.append(str(score))
        rows.append(f"| {rid} | {rec['short']} | " + " | ".join(cells) + " |")

    totals = [f"**{_total(latest, c['key'])}**" for c in comps]
    rows.append("| | **Total, of 55** | " + " | ".join(totals) + " |")
    return "\n".join(rows)


def _delta_badge(delta):
    return f"<span class=\"ictu-up\">+{delta}</span>" if delta > 0 else f"<span class=\"ictu-down\">{delta}</span>"


def _changes_table(data):
    """Every cell that moved, per assessment, with the reason."""
    comps = {c["key"]: c["name"] for c in _components(data)}
    rows = ["| Week | Component | | Change | Why |", "|---|---|---|---|---|"]
    for entry in data["assessments"]:
        for change in entry.get("changes", []):
            rows.append(
                "| {date} | {comp} | {rid} | {frm} → {to} | {why} |".format(
                    date=_fmt_date(entry["date"]),
                    comp=comps.get(change["component"], change["component"]),
                    rid=change["recommendation"],
                    frm=change["from"],
                    to=change["to"],
                    why=change["why"],
                )
            )
    if len(rows) == 2:
        return "*No scored change recorded yet.*"
    return "\n".join(rows)


# --------------------------------------------------------------------------
# charts


def _svg_open(title, desc, width=W, height=H):
    return (
        f'<svg class="ictu-chart" viewBox="0 0 {width} {height}" role="img" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'aria-label="{_esc(title)}">'
        f"<title>{_esc(title)}</title><desc>{_esc(desc)}</desc>"
    )


def _totals_chart(data):
    entries = data["assessments"]
    comps = _components(data)
    xs = [PAD_L + i * (W - PAD_L - PAD_R) / max(len(entries) - 1, 1) for i in range(len(entries))]

    values = [_total(e, c["key"]) for e in entries for c in comps]
    top = max(values) + 4
    bottom = max(min(values) - 4, 0)

    def y(value):
        return PAD_T + (top - value) * (H - PAD_T - PAD_B) / (top - bottom)

    out = [
        _svg_open(
            "ICTU guideline score per component, per week",
            "Total score out of 55 for each application at each weekly assessment.",
        ),
        "<g class='ictu-grid'>",
    ]
    step = 5
    tick = bottom + (step - bottom % step) % step
    while tick <= top:
        out.append(
            f"<line x1='{PAD_L}' x2='{W - PAD_R + 8}' y1='{y(tick):.1f}' y2='{y(tick):.1f}'/>"
            f"<text class='ictu-axis' x='{PAD_L - 8}' y='{y(tick) + 4:.1f}' text-anchor='end'>{tick}</text>"
        )
        tick += step
    out.append("</g><g class='ictu-axis'>")
    for i, entry in enumerate(entries):
        out.append(
            f"<text x='{xs[i]:.1f}' y='{H - PAD_B + 18}' text-anchor='middle'>{_fmt_date(entry['date'])}</text>"
        )
    out.append("</g>")

    for n, comp in enumerate(comps, start=1):
        points = [(xs[i], y(_total(e, comp["key"]))) for i, e in enumerate(entries)]
        path = " ".join(
            ("M" if i == 0 else "L") + f"{px:.1f},{py:.1f}" for i, (px, py) in enumerate(points)
        )
        out.append(f"<path class='ictu-line ictu-s{n}' d='{path}'/>")
        for i, (px, py) in enumerate(points):
            hollow = "" if _measured(entries[i]) else " ictu-hollow"
            out.append(f"<circle class='ictu-dot ictu-s{n}{hollow}' cx='{px:.1f}' cy='{py:.1f}' r='4'/>")
        last_x, last_y = points[-1]
        out.append(
            f"<text class='ictu-label ictu-s{n}' x='{last_x + 10:.1f}' y='{last_y + 4:.1f}'>"
            f"{_esc(comp['name'])} {_total(entries[-1], comp['key'])}</text>"
        )
    out.append("</svg>")
    return "".join(out)


def _movement_chart(data):
    """What each week added, per component: grouped bars of the weekly delta."""
    entries = data["assessments"]
    comps = _components(data)
    weeks = list(zip(entries, entries[1:]))
    if not weeks:
        return ""

    height = 260
    pad_b = 46
    deltas = [
        [_total(to, c["key"]) - _total(frm, c["key"]) for c in comps] for frm, to in weeks
    ]
    top = max(max(row) for row in deltas) or 1
    slot = (W - PAD_L - 16) / len(weeks)
    bar = min(slot / (len(comps) + 1.4), 26)

    def y(value):
        return PAD_T + (top - value) * (height - PAD_T - pad_b) / top

    out = [
        _svg_open(
            "Points added per week, per component",
            "The change in each application's total from one weekly assessment to the next.",
            height=height,
        ),
        f"<line class='ictu-base' x1='{PAD_L}' x2='{W - 16}' y1='{y(0):.1f}' y2='{y(0):.1f}'/>",
    ]
    for w, (frm, to) in enumerate(weeks):
        centre = PAD_L + slot * (w + 0.5)
        for n, comp in enumerate(comps, start=1):
            delta = deltas[w][n - 1]
            x = centre + (n - (len(comps) + 1) / 2) * bar
            if delta:
                out.append(
                    f"<rect class='ictu-bar ictu-s{n}' x='{x - bar / 2:.1f}' y='{y(delta):.1f}' "
                    f"width='{bar:.1f}' height='{y(0) - y(delta):.1f}' rx='2'/>"
                    f"<text class='ictu-barlabel' x='{x:.1f}' y='{y(delta) - 5:.1f}' text-anchor='middle'>+{delta}</text>"
                )
        out.append(
            f"<text class='ictu-axis' x='{centre:.1f}' y='{y(0) + 18:.1f}' text-anchor='middle'>"
            f"{_fmt_date(frm['date'])}&#8202;→&#8202;{_fmt_date(to['date'])}</text>"
        )
    out.append(_legend(comps, height))
    out.append("</svg>")
    return "".join(out)


def _legend(comps, height):
    parts = ["<g class='ictu-legend'>"]
    x = PAD_L
    for n, comp in enumerate(comps, start=1):
        parts.append(
            f"<rect class='ictu-bar ictu-s{n}' x='{x}' y='{height - 20}' width='10' height='10' rx='2'/>"
            f"<text class='ictu-axis' x='{x + 15}' y='{height - 11}'>{_esc(comp['name'])}</text>"
        )
        x += 24 + 7.0 * len(comp["name"])
    parts.append("</g>")
    return "".join(parts)


def _heatmap(data):
    """Current score per recommendation, per component, as a 0–5 grid."""
    latest = data["assessments"][-1]
    comps = _components(data)
    recs = _recommendations(data)

    cell, gap = 34, 4
    left, top_pad = 40, 58
    width = left + len(recs) * (cell + gap) + 130
    height = top_pad + len(comps) * (cell + gap) + 26

    out = [
        _svg_open(
            "Score per recommendation, per component",
            "Each recommendation scored 0 to 5 for each application at the latest assessment.",
            width=width,
            height=height,
        )
    ]
    for i, (rid, _rec) in enumerate(recs):
        x = left + i * (cell + gap) + cell / 2
        out.append(f"<text class='ictu-axis' x='{x:.1f}' y='{top_pad - 10}' text-anchor='middle'>{rid}</text>")
    for r, comp in enumerate(comps):
        y = top_pad + r * (cell + gap)
        out.append(
            f"<text class='ictu-axis' x='{left + len(recs) * (cell + gap) + 8}' y='{y + cell / 2 + 4:.1f}'>"
            f"{_esc(comp['name'])} {_total(latest, comp['key'])}</text>"
        )
        for i, _ in enumerate(recs):
            score = latest["scores"][comp["key"]][i]
            x = left + i * (cell + gap)
            out.append(
                f"<rect class='ictu-cell ictu-v{score}' x='{x}' y='{y}' width='{cell}' height='{cell}' rx='4'/>"
                f"<text class='ictu-cellv ictu-t{score}' x='{x + cell / 2}' y='{y + cell / 2 + 5:.1f}' "
                f"text-anchor='middle'>{score}</text>"
            )
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------
# the test work of the same weeks


def _tests_chart(data):
    """Test files added since the first week, per component.

    Absolute counts would be unreadable together — one application starts at
    15 files and another at 235 — and indexing them as percentages would flatter
    whichever started smallest. Growth from a common zero compares the work
    itself, and the table beneath carries the absolute numbers.
    """
    series = data.get("tests") or []
    comps = _components(data)
    if len(series) < 2:
        return ""

    xs = [PAD_L + i * (W - PAD_L - PAD_R) / (len(series) - 1) for i in range(len(series))]
    base = {c["key"]: series[0][c["key"]]["files"] for c in comps}
    top = max(entry[c["key"]]["files"] - base[c["key"]] for entry in series for c in comps)
    top = max(top + 6, 10)

    def y(value):
        return PAD_T + (top - value) * (H - PAD_T - PAD_B) / top

    out = [
        _svg_open(
            "Test files added per component, per week",
            "Growth in the number of test files in each application since 16 August 2026.",
        ),
        "<g class='ictu-grid'>",
    ]
    tick = 0
    while tick <= top:
        out.append(
            f"<line x1='{PAD_L}' x2='{W - PAD_R + 8}' y1='{y(tick):.1f}' y2='{y(tick):.1f}'/>"
            f"<text class='ictu-axis' x='{PAD_L - 8}' y='{y(tick) + 4:.1f}' text-anchor='end'>+{tick}</text>"
        )
        tick += 20
    out.append("</g><g class='ictu-axis'>")
    for i, entry in enumerate(series):
        out.append(
            f"<text x='{xs[i]:.1f}' y='{H - PAD_B + 18}' text-anchor='middle'>{_fmt_date(entry['date'])}</text>"
        )
    out.append("</g>")

    for n, comp in enumerate(comps, start=1):
        key = comp["key"]
        points = [(xs[i], y(e[key]["files"] - base[key])) for i, e in enumerate(series)]
        path = " ".join(
            ("M" if i == 0 else "L") + f"{px:.1f},{py:.1f}" for i, (px, py) in enumerate(points)
        )
        out.append(f"<path class='ictu-line ictu-s{n}' d='{path}'/>")
        for px, py in points:
            out.append(f"<circle class='ictu-dot ictu-s{n}' cx='{px:.1f}' cy='{py:.1f}' r='4'/>")
        last_x, last_y = points[-1]
        added = series[-1][key]["files"] - base[key]
        out.append(
            f"<text class='ictu-label ictu-s{n}' x='{last_x + 10:.1f}' y='{last_y + 4:.1f}'>"
            f"{_esc(comp['name'])} +{added}</text>"
        )
    out.append("</svg>")
    return "".join(out)


def _tests_table(data):
    """Test files, end-to-end specs and the gates around them, week by week."""
    series = data.get("tests") or []
    comps = _components(data)
    if not series:
        return "*No test measurements recorded.*"

    head = "| Week | " + " | ".join(
        f"{c['name']}<br>files · e2e · CI · floor" for c in comps
    ) + " |"
    rows = [head, "|---|" + ":-:|" * len(comps)]
    for entry in series:
        cells = []
        for comp in comps:
            item = entry[comp["key"]]
            floor = "✅" if item["floor"] else "—"
            cells.append(
                f"{item['files']} · {item['e2e'] or '—'} · {item['ci']}/{item['workflows']} · {floor}"
            )
        rows.append(f"| {_fmt_date(entry['date'])} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


# --------------------------------------------------------------------------
# MkDocs hooks

RENDERERS = {
    "scores": _scores_table,
    "totals": _totals_chart,
    "movement": _movement_chart,
    "heatmap": _heatmap,
    "changes": _changes_table,
    "tests": _tests_chart,
    "testgates": _tests_table,
}


def on_config(config, **kwargs):
    try:
        config["extra"]["ictu"] = _load(config)
    except (OSError, ValueError, KeyError) as error:
        config["extra"]["ictu"] = None
        config["extra"]["ictu_error"] = str(error)
    return config


def on_page_markdown(markdown, page, config, **kwargs):
    if "<!-- ictu:" not in markdown:
        return markdown

    data = config["extra"].get("ictu")
    for name, render in RENDERERS.items():
        token = f"<!-- ictu:{name} -->"
        if token not in markdown:
            continue
        if data is None:
            body = (
                '!!! failure "The assessment data could not be read"\n\n'
                f"    `docs/{DATA_REL}`: {config['extra'].get('ictu_error', 'unknown error')}\n"
            )
        else:
            body = render(data)
        markdown = markdown.replace(token, body)
    return markdown
