"""Warn when a code-block diagram uses a character the code font cannot draw.

A diagram drawn with box-drawing characters only lines up if every character
in it is drawn at the same width. The code font (docs/stylesheets/code-font.css)
covers box drawing, arrows and bullets; anything it lacks — emoji above all —
is borrowed from another font at another width, and the borders drift.

For each fenced block that contains box-drawing characters, this hook compares
its characters against docs/assets/fonts/JetBrainsMono-coverage.txt and logs a
warning naming the page, the line and the characters. Plain code blocks are not
checked: an emoji in a shell example misaligns nothing.

Warnings only; the build never fails on this. Regenerate the coverage list with
scripts/font_coverage.py when the font changes.
"""

import logging
import os
import re

log = logging.getLogger("mkdocs.hooks.code_glyphs")

COVERAGE = os.path.join("docs", "assets", "fonts", "JetBrainsMono-coverage.txt")
FENCE = re.compile(r"^( *)(```|~~~)[^\n]*\n(.*?)^\1\2", re.S | re.M)
BOX = re.compile("[─-╿]")

_ranges = []
_seen = set()


def _covered(ch):
    c = ord(ch)
    return c < 0x80 or any(a <= c <= b for a, b in _ranges)


def _source_line(page, block, fallback):
    """Line number in the file itself, which has front matter the hook never sees."""
    try:
        with open(page.file.abs_src_path, encoding="utf-8") as f:
            raw = f.read()
    except OSError:
        return fallback
    i = raw.find(block)
    return raw.count("\n", 0, i) + 1 if i >= 0 else fallback


def on_config(config):
    _ranges.clear()
    _seen.clear()
    path = os.path.join(os.path.dirname(config["config_file_path"]), COVERAGE)
    try:
        with open(path, encoding="ascii") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    a, b = line.strip().split("-")
                    _ranges.append((int(a, 16), int(b, 16)))
    except OSError as e:
        log.warning("code_glyphs: cannot read %s (%s); diagram check skipped", COVERAGE, e)
    return config


def on_page_markdown(markdown, page, config, files):
    if not _ranges:
        return markdown
    src = page.file.src_uri
    for m in FENCE.finditer(markdown):
        block = m.group(3)
        if not BOX.search(block):
            continue
        bad = sorted({ch for ch in block if not _covered(ch) and ch not in "\n\t"})
        if not bad:
            continue
        line = _source_line(page, m.group(0), markdown.count("\n", 0, m.start()) + 1)
        key = (src, line)
        if key in _seen:  # i18n renders fallback pages more than once
            continue
        _seen.add(key)
        chars = " ".join(f"{ch} U+{ord(ch):04X}" for ch in bad)
        log.warning(
            "Diagram at %s:%d uses characters the code font cannot draw at column width, so it will not line up: %s",
            src, line, chars,
        )
    return markdown
