#!/usr/bin/env python3
"""Fix MkDocs admonition formatting after po2md output.

po2md collapses admonition blocks onto single/wrapped lines:
    !!! info "Title" Content here. More content
    wrapping onto the next line.

This script restores proper MkDocs format:
    !!! info "Title"
        Content here. More content
        wrapping onto the next line.
"""
import re
import sys
from pathlib import Path

ADMONITION_START = re.compile(
    r'^(!{3}|[\?]{3})\s+'     # !!! or ???
    r'(\w+)'                  # type (note, warning, tip, info, ...)
    r'(\s+"[^"]*")?'          # optional "Title"
    r'\s+'                    # space before inlined content
    r'(.+)$'                  # content that should be on next line(s)
)


def fix_file(filepath: Path) -> bool:
    lines = filepath.read_text(encoding="utf-8").splitlines(keepends=True)
    out = []
    i = 0
    changed = False

    while i < len(lines):
        line = lines[i]
        m = ADMONITION_START.match(line.rstrip("\n"))
        if m:
            changed = True
            marker, adtype, title, first_content = m.groups()
            title = title or ""
            out.append(f"{marker} {adtype}{title}\n")
            out.append(f"    {first_content}\n")
            i += 1
            # Collect continuation lines (non-blank, not a new block)
            while i < len(lines):
                cont = lines[i]
                stripped = cont.strip()
                if (not stripped
                    or stripped.startswith("!!!")
                    or stripped.startswith("???")
                    or stripped.startswith("#")
                    or stripped.startswith("```")
                    or stripped.startswith("---")):
                    break
                out.append(f"    {stripped}\n")
                i += 1
        else:
            out.append(line)
            i += 1

    if changed:
        filepath.write_text("".join(out), encoding="utf-8")
    return changed


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    files = [target] if target.is_file() else sorted(target.rglob("*.md"))
    fixed = sum(1 for f in files if fix_file(f))
    print(f"  Processed {len(files)} files, fixed admonitions in {fixed}.")


if __name__ == "__main__":
    main()