#!/usr/bin/env python3
"""
fix_heading_separators.py

Ensures every level-2 heading (## ...) in Markdown files is preceded by a
horizontal rule with correct blank-line spacing:

    (...content...)

    ---

    ## Heading

Rules applied:
  - Skip headings that appear as the very first non-blank content in a file
    (nothing meaningful precedes them — no separator needed).
  - Skip headings inside fenced code blocks (``` or ~~~).
  - When a heading IS preceded by --- but has no blank line between them,
    normalise to exactly one blank line on each side.
  - When a heading is NOT preceded by ---, insert the full separator block.

Usage:
    python fix_heading_separators.py [--dry-run] [path]

    path        Root directory to scan, or a single .md file.
                Defaults to  docs/
    --dry-run   Report issues without modifying any file.

Exit codes:
    0  No issues found (or all fixed in non-dry-run mode).
    1  Issues found in dry-run mode (nothing written).
"""

import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def process_lines(lines: list[str]) -> tuple[list[tuple[int, str]], list[str]]:
    """
    Analyse and repair heading separators in a list of lines.

    Returns:
        issues   — list of (1-based line number, heading text) that needed fixing
        result   — repaired line list (may equal original if nothing changed)
    """
    issues: list[tuple[int, str]] = []
    result: list[str] = []
    in_fence = False

    for i, line in enumerate(lines):
        # Track fenced code blocks (``` or ~~~, with optional language tag)
        stripped = line.strip()
        if re.match(r'^(`{3,}|~{3,})', stripped):
            in_fence = not in_fence

        if in_fence or not re.match(r'^## ', line):
            result.append(line)
            continue

        # --- We have a level-2 heading outside a code block. ---

        # Find the last non-blank line already appended to result.
        j = len(result) - 1
        while j >= 0 and result[j].strip() == '':
            j -= 1

        prev_nonblank = result[j] if j >= 0 else None

        if prev_nonblank is None:
            # Nothing real precedes this heading — it is the first content.
            result.append(line)
            continue

        if prev_nonblank.strip() == '---':
            # Separator already present.
            # Normalise spacing: strip trailing blanks after ---, add exactly one.
            while result and result[-1].strip() == '':
                result.pop()
            result.append('')
            result.append(line)
            continue

        # Missing separator — record and repair.
        issues.append((i + 1, line.rstrip()))

        # Strip trailing blank lines from result, then insert separator block.
        while result and result[-1].strip() == '':
            result.pop()
        result.append('')
        result.append('---')
        result.append('')
        result.append(line)

    return issues, result


def handle_file(path: Path, dry_run: bool) -> list[str]:
    """
    Process a single file. Returns human-readable report lines (may be empty).
    """
    try:
        original = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        return [f"  ERROR reading {path}: {exc}"]

    lines = original.split('\n')
    issues, repaired_lines = process_lines(lines)

    if not issues:
        return []

    report = []
    for lineno, heading in issues:
        report.append(f"  line {lineno:>4}: {heading}")

    if not dry_run:
        new_content = '\n'.join(repaired_lines)
        try:
            path.write_text(new_content, encoding='utf-8')
        except OSError as exc:
            report.append(f"  ERROR writing {path}: {exc}")

    return report


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    args = sys.argv[1:]

    dry_run = '--dry-run' in args
    args = [a for a in args if a != '--dry-run']

    root = Path(args[0]) if args else Path('docs')

    if root.is_file():
        md_files = [root]
    elif root.is_dir():
        md_files = sorted(root.rglob('*.md'))
    else:
        print(f"ERROR: path not found: {root}", file=sys.stderr)
        return 2

    mode_label = "DRY RUN — no files will be modified" if dry_run else "FIXING files"
    print(f"fix_heading_separators.py  [{mode_label}]")
    print(f"Scanning: {root.resolve()}")
    print(f"Files:    {len(md_files)}")
    print()

    total_issues = 0
    total_files_affected = 0

    for md_file in md_files:
        report = handle_file(md_file, dry_run)
        if report:
            total_issues += len(report)
            total_files_affected += 1
            rel = md_file.relative_to(root) if root.is_dir() else md_file
            action = "needs fixing" if dry_run else "fixed"
            print(f"{rel}  [{action}]")
            for line in report:
                print(line)
            print()

    # Summary
    if total_issues == 0:
        print("✓ All headings already have correct separators.")
        return 0

    if dry_run:
        print(f"Found {total_issues} heading(s) without separators "
              f"in {total_files_affected} file(s).")
        print("Run without --dry-run to fix.")
        return 1
    else:
        print(f"Fixed {total_issues} heading(s) in {total_files_affected} file(s).")
        return 0


if __name__ == '__main__':
    sys.exit(main())
