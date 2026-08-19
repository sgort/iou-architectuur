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

Failing to read or parse the file is deliberately non-fatal: the header
degrades to showing only the git dates rather than breaking the build.
"""

import json
import os


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
    config["extra"]["repo_versions"] = {
        repo["name"]: repo for repo in repositories if repo.get("name")
    }
    config["extra"]["docs_built"] = data.get("docs_built")

    return config
