#!/usr/bin/env python3
"""
fix_figures.py

Adds style="width:100%; margin:0;" to every <figure> and <figure markdown>
tag in all .md files that does not already have a style attribute.

Usage:
    python fix_figures.py              # scans ./docs/
    python fix_figures.py path/to/dir  # scans given directory
    python fix_figures.py --dry-run    # preview without writing
"""

import re
import sys
from pathlib import Path

# Matches <figure> or <figure markdown> or <figure markdown anything>
# but NOT tags that already contain style="..."
PATTERN = re.compile(
    r'<figure(?P<attrs>[^>]*)>',
)


def fix_tag(match: re.Match) -> str:
    attrs = match.group('attrs')
    if 'style=' in attrs:
        return match.group(0)  # already has a style attribute — leave untouched
    return f'<figure{attrs} style="width:100%; margin:0;">'


def convert(text: str) -> tuple[str, int]:
    result, count = PATTERN.subn(fix_tag, text)
    return result, count


def process_file(path: Path, dry_run: bool) -> int:
    original = path.read_text(encoding='utf-8')
    converted, count = convert(original)

    if count == 0:
        return 0

    if dry_run:
        print(f"  [DRY RUN] {path}  —  {count} tag(s)")
    else:
        path.write_text(converted, encoding='utf-8')
        print(f"  {path}  —  {count} tag(s)")

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
    total_tags = 0

    print(f"Scanning {len(md_files)} .md files under '{root}/'...")
    if dry_run:
        print("(dry run — no files will be written)\n")

    for path in md_files:
        n = process_file(path, dry_run)
        if n:
            total_files += 1
            total_tags += n

    print(f"\nDone. {total_tags} tag(s) updated in {total_files} file(s).")


if __name__ == '__main__':
    main()