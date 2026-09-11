#!/usr/bin/env python3
"""Report how stale each cross-cutting page's `verified` stamp is.

A cross-cutting page (scope: cross-cutting) may declare which commit of each
component its claims were last re-checked against:

    verified:
      date: 2026-09-09
      against:
        CPSV Editor: "bbda389"
        Linked Data Explorer: "007b350"

For every stamped component this script asks the component's own clone one
question: which commits touching CI-relevant paths have landed on the branch
of record since that commit? That is `git log <sha>..<remote>/<branch> -- <paths>`
— deterministic, offline, and precise in a way comparing build ids cannot be,
because deploy workflows are path-filtered and most of what a contributing
page describes changes without producing a new frontend build at all.

The header links each stamped SHA to the commit in the component's `ci_repo`
(docs/repo-versions.json) — GitHub for the three applications, where their
deploy workflows run. So the script also asks GitHub whether that SHA actually
triggered a successful deploy run, since that is what lets a reader follow the
link to a build they can compare with the running application. And it checks
every `build` recorded in repo-versions.json against the Actions run its
`run_url` names.

It does NOT fetch. Stage 0 of the skill fetches every clone first; run this
after that, or pass --fetch. The GitHub checks need `gh`; pass --offline to
skip them.

Checks, per stamp:
  - the SHA is a quoted string (an unquoted all-digit SHA is parsed by YAML as
    an integer — and one with a leading zero as octal — so its value is lost);
  - the component name exists in docs/repo-versions.json;
  - the SHA resolves to a commit in the clone;
  - the SHA is on a branch of the remote that hosts CI (warning — the header's
    link 404s until it is pushed there);
  - the SHA triggered a successful deploy run on GitHub (warning — a commit
    that changed only CI configuration can legitimately trigger none);
  - CI-relevant commits on the branch of record since the SHA.

Per recorded build: the run named by `run_url` exists, was a push, succeeded,
and carries the recorded SHA and run number.

Exit status: 1 if any stamp or build record is malformed or contradicts
GitHub; 0 otherwise. Staleness is information, not failure.

Usage:
  python .claude/skills/iou-document-patch/scripts/stamp-staleness.py
  python .../stamp-staleness.py --json
  python .../stamp-staleness.py --fetch
  python .../stamp-staleness.py --offline
  python .../stamp-staleness.py --page docs/en/contributing/supply-chain.md
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: run with the docs venv (venv/bin/python)")

# Component name (as in repo-versions.json) ->
#   (sibling clone, branch of record, remote that hosts its CI)
COMPONENTS = {
    "CPSV Editor": ("ttl-editor", "acc", "origin"),
    "Linked Data Explorer": ("linked-data-explorer", "acc", "origin"),
    "RONL Business API": ("ronl-business-api", "acc", "origin"),
    "Norm Editor": ("editor", "main", "origin"),  # origin is GitLab; no acc branch
    "CPRMV": ("cprmv", "main", "gitlab"),  # GitLab CI; origin is a GitHub copy
}

# What a contributing page makes claims about: CI, hooks, the supply-chain
# register, runner configs and their thresholds, formatting and lint config.
# Deliberately not package.json: every dependency bump touches it, and the
# noise would drown the signal.
CI_PATHS = [
    ".github",
    ".gitlab-ci.yml",
    ".husky",
    ".githooks",
    "SECURITY-PIPELINE.md",
    "renovate.json",
    "scripts/check-supply-chain.mjs",
    ":(glob)**/jest.config.*",
    ":(glob)**/vite.config.*",
    ":(glob)**/vitest.config.*",
    ":(glob)**/.prettierrc*",
    ":(glob)**/.prettierignore",
    ":(glob)**/eslint.config.*",
    ":(glob)**/.eslintrc*",
    ":(glob)**/.nvmrc",
    ":(glob)**/.lintstagedrc*",
    ":(glob)**/commitlint.config.*",
]

# Workflow names that deploy something. Supply-chain audits and backend builds
# run on the same push but ship nothing a reader can see.
DEPLOY_WORKFLOW = re.compile(r"deploy|static web apps", re.IGNORECASE)
GITHUB_REPO = re.compile(r"github\.com/([^/]+/[^/]+?)/?$")
GITHUB_RUN = re.compile(r"github\.com/([^/]+/[^/]+)/actions/runs/(\d+)")


def git(repo, *args):
    result = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def gh_api(path):
    """Return parsed JSON, or None when gh is missing or the call fails."""
    if not shutil.which("gh"):
        return None
    result = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except ValueError:
        return None


def front_matter(path):
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[3:end]) or {}


def cross_cutting_pages(docs_root):
    for base, _dirs, files in os.walk(docs_root):
        for name in sorted(files):
            if name.endswith(".md"):
                path = os.path.join(base, name)
                meta = front_matter(path)
                if meta.get("scope") == "cross-cutting":
                    yield path, meta


def github_slug(record):
    match = GITHUB_REPO.search(record.get("ci_repo") or "")
    return match.group(1) if match else None


def deploy_runs(slug, full_sha):
    data = gh_api(f"repos/{slug}/actions/runs?head_sha={full_sha}&event=push&per_page=50")
    if data is None:
        return None
    return [
        f"{run['name']} #{run['run_number']}"
        for run in data.get("workflow_runs", [])
        if DEPLOY_WORKFLOW.search(run.get("name", "")) and run.get("conclusion") == "success"
    ]


def check_stamp(component, value, siblings_root, records, offline):
    finding = {"component": component, "sha": value, "problems": [], "warnings": []}

    if not isinstance(value, str):
        finding["problems"].append(
            f"unquoted SHA parsed by YAML as {type(value).__name__} ({value!r}) — quote it"
        )
        return finding
    if component not in records:
        finding["problems"].append("component not in docs/repo-versions.json")
        return finding
    if component not in COMPONENTS:
        finding["problems"].append("no clone mapping in stamp-staleness.py")
        return finding

    clone, branch, remote = COMPONENTS[component]
    repo = os.path.join(siblings_root, clone)
    finding.update(clone=clone, branch=branch, remote=remote)
    if not os.path.isdir(repo):
        finding["problems"].append(f"clone not found at {repo}")
        return finding

    code, full = git(repo, "rev-parse", "--verify", "--quiet", f"{value}^{{commit}}")
    if code != 0:
        finding["problems"].append(f"{value} does not resolve to a commit in {clone}")
        return finding

    _code, out = git(repo, "branch", "-r", "--contains", value)
    if not any(line.strip().startswith(f"{remote}/") for line in out.splitlines()):
        finding["warnings"].append(
            f"not on any {remote}/* branch — the header's commit link 404s until it is pushed there"
        )

    slug = github_slug(records[component])
    if slug and not offline:
        runs = deploy_runs(slug, full)
        if runs is None:
            finding["warnings"].append("could not ask GitHub for deploy runs (gh missing or failed)")
        elif not runs:
            finding["warnings"].append(
                "triggered no successful deploy run on GitHub — the reader cannot match it to a build"
            )
        else:
            finding["deploys"] = runs

    ref = f"{remote}/{branch}"
    code, out = git(repo, "log", "--oneline", "--no-decorate", f"{value}..{ref}", "--", *CI_PATHS)
    if code != 0:
        finding["problems"].append(f"git log {value}..{ref} failed")
        return finding
    finding["ci_commits"] = out.splitlines() if out else []
    _code, head = git(repo, "rev-parse", "--short", ref)
    finding["head"] = head
    return finding


def check_build(name, record, offline):
    build = record.get("build")
    if not isinstance(build, dict):
        return None
    finding = {"component": name, "build": build, "problems": [], "warnings": []}
    sha, run, url = build.get("sha"), build.get("run"), build.get("run_url")
    if not isinstance(sha, str):
        finding["problems"].append("build.sha must be a string")
    if not url:
        finding["warnings"].append("no run_url — the header cannot link the deploy run")
        return finding
    match = GITHUB_RUN.search(url)
    if not match:
        finding["warnings"].append("run_url is not a GitHub Actions run")
        return finding
    if offline:
        return finding
    data = gh_api(f"repos/{match.group(1)}/actions/runs/{match.group(2)}")
    if data is None:
        finding["warnings"].append("could not fetch the run from GitHub")
        return finding
    finding["run_name"] = data.get("name")
    if not data.get("head_sha", "").startswith(str(sha)):
        finding["problems"].append(f"run built {data.get('head_sha', '')[:7]}, not {sha}")
    if data.get("run_number") != run:
        finding["problems"].append(f"run is #{data.get('run_number')}, not #{run}")
    if data.get("event") != "push":
        finding["problems"].append(f"run was a {data.get('event')} event, not a push")
    if data.get("conclusion") != "success":
        finding["problems"].append(f"run concluded {data.get('conclusion')}")
    if not DEPLOY_WORKFLOW.search(data.get("name", "")):
        finding["warnings"].append(f"'{data.get('name')}' does not look like a deploy workflow")
    return finding


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--fetch", action="store_true", help="fetch each clone first")
    parser.add_argument("--offline", action="store_true", help="skip the GitHub checks")
    parser.add_argument("--page", action="append", help="limit to these page paths")
    parser.add_argument("--docs-root", default="docs/en/contributing")
    parser.add_argument("--siblings", default="..", help="directory holding the clones")
    args = parser.parse_args()

    with open("docs/repo-versions.json", encoding="utf-8") as handle:
        records = {r["name"]: r for r in json.load(handle).get("repositories", [])}

    if args.fetch:
        for clone, _branch, _remote in COMPONENTS.values():
            repo = os.path.join(args.siblings, clone)
            if os.path.isdir(repo):
                git(repo, "fetch", "--quiet", "--all", "--prune")

    pages, malformed = [], False
    for path, meta in cross_cutting_pages(args.docs_root):
        if args.page and path not in args.page:
            continue
        verified = meta.get("verified")
        entry = {"page": path, "stamped": False}
        if isinstance(verified, dict) and isinstance(verified.get("against"), dict):
            date = verified.get("date")
            entry.update(
                stamped=True,
                date=date.isoformat() if isinstance(date, datetime.date) else date,
                components=[
                    check_stamp(name, sha, args.siblings, records, args.offline)
                    for name, sha in verified["against"].items()
                ],
            )
            malformed |= any(c["problems"] for c in entry["components"])
        pages.append(entry)

    builds = [b for b in (check_build(n, r, args.offline) for n, r in records.items()) if b]
    malformed |= any(b["problems"] for b in builds)

    if args.json:
        print(json.dumps({"pages": pages, "builds": builds}, indent=2, default=str))
        return 1 if malformed else 0

    for entry in (e for e in pages if e["stamped"]):
        print(f"\n{entry['page']}  — verified {entry['date']}")
        for c in entry["components"]:
            if c["problems"]:
                print(f"  ✗ {c['component']} {c['sha']}: " + "; ".join(c["problems"]))
                continue
            n = len(c["ci_commits"])
            mark = "✓" if n == 0 else "⚠"
            print(
                f"  {mark} {c['component']:<22} {c['sha']}  →  {c['remote']}/{c['branch']} {c['head']}"
                f"  —  {n} CI-relevant commit{'s' if n != 1 else ''} since"
            )
            if c.get("deploys"):
                print(f"        deployed by: {', '.join(c['deploys'])}")
            for line in c["ci_commits"][:8]:
                print(f"        {line}")
            if n > 8:
                print(f"        … and {n - 8} more")
            for w in c["warnings"]:
                print(f"      ! {w}")

    if builds:
        print("\nRecorded builds (docs/repo-versions.json):")
        for b in builds:
            label = f"build {b['build'].get('sha')} · #{b['build'].get('run')}"
            if b["problems"]:
                print(f"  ✗ {b['component']:<22} {label}: " + "; ".join(b["problems"]))
            else:
                via = f"  ←  {b['run_name']}" if b.get("run_name") else ""
                print(f"  ✓ {b['component']:<22} {label}{via}")
            for w in b["warnings"]:
                print(f"      ! {w}")

    unstamped = [e["page"] for e in pages if not e["stamped"]]
    if unstamped:
        print(f"\nUnstamped cross-cutting pages ({len(unstamped)}):")
        for page in unstamped:
            print(f"  · {page}")
    return 1 if malformed else 0


if __name__ == "__main__":
    sys.exit(main())
