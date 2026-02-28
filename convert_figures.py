#!/usr/bin/env python3
"""
convert_figures.py

Converts image + italic caption patterns to <figure markdown> / <figcaption>
across all .md files under a given directory (default: docs/).

Handles two variants found in the codebase:

  Variant A — caption on same line:
    ![alt](path)*caption*

  Variant B — caption on next line:
    ![alt](path)
    *caption*

Both become:
    <figure markdown>
      ![alt](path)
      <figcaption>caption</figcaption>
    </figure>

Usage:
    python convert_figures.py              # scans ./docs/
    python convert_figures.py path/to/dir  # scans given directory
    python convert_figures.py --dry-run    # preview without writing
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Variant A: image and *caption* on the same line
PATTERN_SAME_LINE = re.compile(
    r'(!\[[^\]]*\]\([^)]*\))'   # image tag
    r'[ \t]*'                    # optional horizontal whitespace
    r'\*([^*\n]+)\*'             # *caption* (no newlines inside)
)

# Variant B: image on one line, *caption* on the very next line
PATTERN_NEXT_LINE = re.compile(
    r'(!\[[^\]]*\]\([^)]*\))'   # image tag
    r'[ \t]*\n'                  # end of image line
    r'\*([^*\n]+)\*'             # *caption* on following line
)

REPLACEMENT = '<figure markdown>\n  \\1\n  <figcaption>\\2</figcaption>\n</figure>'


def convert(text: str) -> tuple[str, int]:
    """Apply both patterns and return (converted_text, total_replacements)."""
    count = 0

    # Variant B first — it matches across a newline, so process before
    # same-line to avoid partial matches after variant A removes the caption.
    result, n = PATTERN_NEXT_LINE.subn(REPLACEMENT, text)
    count += n

    result, n = PATTERN_SAME_LINE.subn(REPLACEMENT, result)
    count += n

    return result, count


def process_file(path: Path, dry_run: bool) -> int:
    original = path.read_text(encoding='utf-8')
    converted, count = convert(original)

    if count == 0:
        return 0

    if dry_run:
        print(f"  [DRY RUN] {path}  —  {count} replacement(s)")
    else:
        path.write_text(converted, encoding='utf-8')
        print(f"  {path}  —  {count} replacement(s)")

    return count


def main():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    args = [a for a in args if a != '--dry-run']

    root = Path(args[0]) if args else Path('docs')

    if not root.exists():
        print(f"Error: directory '{root}' not found.")
        sys.exit(1)

    md_files = sorted(root.rglob('*.md'))
    total_files = 0
    total_replacements = 0

    print(f"Scanning {len(md_files)} .md files under '{root}/'...")
    if dry_run:
        print("(dry run — no files will be written)\n")

    for path in md_files:
        n = process_file(path, dry_run)
        if n:
            total_files += 1
            total_replacements += n

    print(f"\nDone. {total_replacements} replacement(s) in {total_files} file(s).")


if __name__ == '__main__':
    main()
