#!/usr/bin/env python3
"""version-gap.py — compute the documentation sync gap for /iou-document-patch.

Compares the latest documented version of a component (the CPSV Editor by
default) against the latest version recorded in that component's source
changelog, and prints the ordered list of versions that the documentation is
missing, together with the changelog sections for each missing version.

Inputs (all overridable via flags):
  --changelog   Path to the component source changelog.json
                (default: ../ttl-editor/src/data/changelog.json, relative to
                 the docs repo root passed as --docs-root).
  --docs-root   Path to the iou-architectuur docs repo root (default: cwd).
  --component   Name of the component as it appears in repo-versions.json
                (default: "CPSV Editor").
  --json        Emit machine-readable JSON instead of the human summary.

The "documented" version is read from docs/repo-versions.json (the field the
home-page doc-status admonition renders). It is cross-checked, for reporting
only, against the top ### vX.Y.Z heading in the developer changelog-roadmap.md.

Exit code is 0 whether or not a gap exists; a gap is reported in the output.
Exit code is non-zero only on a hard error (missing/unparseable inputs).
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Windows consoles default to cp1252, which cannot encode the status emoji.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def parse_semver(v):
    """Return a comparable tuple from a version string like '1.10.6' or 'v1.10.6'."""
    v = v.strip().lstrip("vV")
    parts = re.split(r"[.\-+]", v)
    nums = []
    for p in parts:
        m = re.match(r"^(\d+)", p)
        if m:
            nums.append(int(m.group(1)))
        else:
            break
    # pad to 3 components so (1,10) sorts consistently against (1,10,6)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums[:3])


# Conventional-commit type -> (icon, section title), for components whose
# changelog is git-log-derived (a top-level "releases" array of {version, date,
# changes: {type: [commit, ...]}, commits: [...]}) rather than hand-curated
# release notes (a top-level "versions" array of {version, date, sections: [...]})
CONVENTIONAL_TYPE_META = {
    "feat": ("✨", "Features"),
    "fix": ("🐛", "Fixes"),
    "docs": ("📚", "Documentation"),
    "chore": ("🧹", "Chores"),
    "refactor": ("♻️", "Refactoring"),
    "perf": ("⚡", "Performance"),
    "test": ("✅", "Tests"),
    "style": ("💅", "Style"),
    "build": ("🏗️", "Build"),
    "ci": ("🤖", "CI"),
    "other": ("🔧", "Other"),
}


def normalize_conventional_release(release):
    """Reshape a git-log-derived release ({version, date, changes: {type:
    [commit,...]}}) into the {version, date, status, sections: [{title, icon,
    items}]} shape the rest of this script (and the human-readable report)
    expects from a curated changelog."""
    changes = release.get("changes", {}) or {}
    sections = []
    for type_key, commits in changes.items():
        icon, title = CONVENTIONAL_TYPE_META.get(type_key, ("•", type_key.capitalize()))
        items = [c.get("description") or c.get("subject", "") for c in commits]
        sections.append({"title": title, "icon": icon, "items": items, "type": type_key})
    date = release.get("date", "") or ""
    return {
        "version": release.get("version", "").strip(),
        "date": date.split("T")[0] if "T" in date else date,
        "status": "",
        "sections": sections,
    }


def load_changelog_versions(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    releases = data.get("releases")
    if isinstance(releases, list) and releases:
        # git-log-derived changelog (see scripts/generate-changelog.mjs in the
        # component repo). "Unreleased" is not a real version — drop it.
        tagged = [
            r for r in releases if r.get("version", "").strip().lower() != "unreleased"
        ]
        return [normalize_conventional_release(r) for r in tagged]

    versions = data.get("versions", [])
    if not versions:
        raise ValueError(f"No 'versions' or 'releases' array found in {path}")
    if not isinstance(versions, list):
        raise ValueError(
            f"'versions' in {path} is a {type(versions).__name__}, not a list of "
            "releases — this looks like a per-service version map (e.g. "
            '{"gui": "0.5.2", ...}), not a changelog. Check for a "releases" '
            "array in the same file instead."
        )
    return versions


def documented_version(docs_root, component):
    rv_path = Path(docs_root) / "docs" / "repo-versions.json"
    data = json.loads(rv_path.read_text(encoding="utf-8"))
    for repo in data.get("repositories", []):
        if repo.get("name", "").strip().lower() == component.strip().lower():
            return repo.get("version", "").strip(), rv_path
    raise ValueError(f"Component '{component}' not found in {rv_path}")


def component_slug(component):
    """'CPSV Editor' -> 'cpsv-editor', 'Linked Data Explorer' -> 'linked-data-explorer'."""
    return re.sub(r"[^a-z0-9]+", "-", component.strip().lower()).strip("-")


def roadmap_top_version(docs_root, component, roadmap_override=None):
    """Best-effort: read the newest ### vX.Y.Z heading in the component's
    developer changelog-roadmap.md. The path is derived from the component name
    (docs/en/<slug>/developer/changelog-roadmap.md) unless overridden."""
    rm = (
        Path(roadmap_override)
        if roadmap_override
        else Path(docs_root)
        / "docs"
        / "en"
        / component_slug(component)
        / "developer"
        / "changelog-roadmap.md"
    )
    if not rm.exists():
        return None
    for line in rm.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^###\s+v?(\d+\.\d+\.\d+)", line.strip())
        if m:
            return m.group(1)
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--docs-root", default=".")
    ap.add_argument("--changelog", default=None)
    ap.add_argument("--component", default="CPSV Editor")
    ap.add_argument(
        "--roadmap",
        default=None,
        help="Path to the component's changelog-roadmap.md "
        "(default: docs/en/<component-slug>/developer/changelog-roadmap.md)",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    docs_root = Path(args.docs_root).resolve()
    changelog_path = (
        Path(args.changelog)
        if args.changelog
        else docs_root.parent / "ttl-editor" / "src" / "data" / "changelog.json"
    )

    versions = load_changelog_versions(changelog_path)
    latest = versions[0].get("version", "").strip()
    doc_ver, rv_path = documented_version(docs_root, args.component)
    roadmap_ver = roadmap_top_version(docs_root, args.component, args.roadmap)

    doc_key = parse_semver(doc_ver)
    gap = [
        v
        for v in versions
        if parse_semver(v.get("version", "")) > doc_key
    ]
    # oldest-first so docs are written in release order
    gap_sorted = sorted(gap, key=lambda v: parse_semver(v.get("version", "")))

    result = {
        "component": args.component,
        "changelog_path": str(changelog_path),
        "repo_versions_path": str(rv_path),
        "documented_version": doc_ver,
        "roadmap_top_version": roadmap_ver,
        "latest_version": latest,
        "gap_versions": [v.get("version") for v in gap_sorted],
        "in_sync": len(gap_sorted) == 0,
        "gap_entries": gap_sorted,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"Component            : {args.component}")
    print(f"Source changelog     : {changelog_path}")
    print(f"repo-versions.json   : {doc_ver}")
    print(f"changelog-roadmap.md : {roadmap_ver}")
    print(f"Latest in source     : {latest}")
    if result["in_sync"]:
        print("\n✅ Documentation is already in sync — no gap.")
        return 0
    print(f"\n⚠️  Gap: {len(gap_sorted)} version(s) to document (oldest first):")
    for v in gap_sorted:
        print(f"\n  ── v{v.get('version')}  ({v.get('date','?')}) — {v.get('status','')}")
        for sec in v.get("sections", []):
            title = sec.get("title", "")
            print(f"       {sec.get('icon','•')} {title}")
            for item in sec.get("items", []):
                # first sentence only, for a scannable plan
                first = re.split(r"(?<=[.])\s", item.strip(), maxsplit=1)[0]
                print(f"          - {first}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
