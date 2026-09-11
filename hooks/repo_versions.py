"""Expose docs/repo-versions.json to the Jinja templates.

`repo-versions.json` records, per component, the version/commit/environment
this documentation was last synced from. It is served as a static asset and
read in the browser by `docs/javascripts/doc-status.js` for the home page's
documentation-status admonition.

The per-page metadata header (see `overrides/partials/doc-meta.html`) needs
the same data at *build* time, so it can render the component version
server-side next to the git dates instead of filling it in with JavaScript
after paint. This hook loads the file once during `on_config` and stashes it
on `config.extra`, where templates can reach it:

    config.extra.repo_versions["CPSV Editor"].version

A page opts into the header by declaring the matching component name in its
front matter:

    ---
    component: CPSV Editor
    ---

The lookup is keyed on the `name` field exactly as it appears in
`repo-versions.json`, so the two must agree.

Two derived or optional fields ride along:

- `commit_base` — a URL prefix that links *any* commit of the repository,
  not only the recorded one. Cross-cutting pages use it for their
  `verified.against` stamps. It is built from `ci_repo` — the repository where
  the component's deploy workflows run — because the point of a stamped SHA is
  that a reader can follow it to the deploy runs it triggered. For the three
  applications that is GitHub, where the Actions run, and not the GitLab
  mirror `repo_url` points at: a mirror carries the same SHAs, but lags, and
  shows none of the runs. Falls back to `repo_url` when `ci_repo` is absent.
- `build` — optional `{"sha", "run", "run_url"}`: the frontend build that was
  serving the recorded environment when the recorded commit was current, and
  the Actions run that produced it. It is deliberately a separate fact from
  `commit`: deploy workflows are path-filtered, so the build serving an
  environment is often older than the branch head, and a new build can reach
  an environment without a release bump. See
  docs/en/contributing/build-provenance.md.

Failing to read or parse the file is deliberately non-fatal: the header
degrades to showing only the git dates rather than breaking the build.
"""

import json
import os
import re

# GitLab (".../-/commit/<sha>") and GitHub (".../commit/<sha>") both end in a
# commit segment followed by the SHA. Strip only the SHA, keep the separator.
_COMMIT_URL = re.compile(r"^(.*/commit/)[0-9a-f]{7,40}/?$")


def _commit_base(repo_url):
    if not repo_url:
        return None
    match = _COMMIT_URL.match(repo_url)
    return match.group(1) if match else None


def _ci_commit_base(ci_repo):
    """GitHub links a commit at /commit/<sha>; GitLab at /-/commit/<sha>."""
    if not ci_repo:
        return None
    base = ci_repo.rstrip("/")
    return base + ("/commit/" if "github.com" in base else "/-/commit/")


def on_config(config, **kwargs):
    path = os.path.join(config["docs_dir"], "repo-versions.json")

    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        config["extra"]["repo_versions"] = {}
        config["extra"]["docs_built"] = None
        return config

    repositories = data.get("repositories", [])
    for repo in repositories:
        repo["commit_base"] = _ci_commit_base(repo.get("ci_repo")) or _commit_base(
            repo.get("repo_url")
        )
    config["extra"]["repo_versions"] = {
        repo["name"]: repo for repo in repositories if repo.get("name")
    }
    config["extra"]["docs_built"] = data.get("docs_built")

    return config
