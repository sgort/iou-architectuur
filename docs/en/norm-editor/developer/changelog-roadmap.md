---
component: Norm Editor
---

# Changelog & Roadmap

---

## Changelog

### v2026.09.15-2 — Interpreting and Viewing in Three Panes (September 2026)

> How it works now: [Interpreting sources](../user-guide/interpreting-sources.md) and [Frame visualisation](../features/visualisation.md). The code: [Frontend](frontend.md).

**Interpret sources is laid out as three panes under a status bar.** The source text, the Frames list and a separate frame editor sit side by side, and a one-line status bar above them says what the editor expects next. While a role or condition is being chosen the bar turns orange and offers **Cancel**. Open frames become tabs across the editor pane instead of a list down its side, and new frames come from a **+ New** menu.

**The frame forms read as forms.** Each carries its type as a coloured badge. Roles are set with a **Select** button that reads **Change** once the role is filled, and an empty role says *Not set*. Role detection moved into the Roles header as a **Detect roles** button beside the model choice, and **Show in source** replaces *Scroll to source*, disabled when the frame has no source. Deleting asks *Delete this act?* with **Keep** and **Delete**.

**View interpretation shows the dependencies between acts.** The tab became three panes: the frames, a network of acts and claim-duties linked where one act creates what the next needs, and a details panel for the selected frame. That panel lists its roles, conditions, what enables it and what it enables, and opens the frame in the editor. The network fits itself to the pane, can be zoomed, re-laid out and filtered by hiding nodes, and a legend explains its shapes. It replaces the overlay tree drawn over the selected node.

**The DNS zone moved to the shared resource group**, so one zone serves every environment: production on the apex, any other environment on `acc.` ([Deployment](deployment.md)).

---

### v2026.09.15 — A Name and an Icon (September 2026)

**The application calls itself the Norm Editor.** The product name is *Norm Editor - RONL*, replacing *Regel Gui*, and the GUI ships a new favicon set and a web app manifest in the IOU colours.

---

### v2026.09.13 — Re-tag (September 2026)

Carries no change of its own: it marks the same work as v2026.09.12, tagged again the same day.

---

### v2026.09.12 — The IOU Style, and a Registry Shared Across Environments (September 2026)

> The changes: [Frontend](frontend.md#styling) and [Deployment](deployment.md).

**The Norm Editor adopts the IOU style.** A navy title bar carries the name, a *What's new* button, a link to the repository and the load/save menu; the six steps sit below it as tabs. The palette, buttons and panels follow the IOU tokens defined once in `quasar.variables.scss`, and Roboto Mono is self-hosted for hashes and versions, so the editor makes no request to Google Fonts.

**The changelog names the commit it was built from.** *What's new* shows the latest commit and links every hash to the repository. `build_gui` regenerates the changelog before building the image; see [Testing](testing.md#what-ci-actually-gates) for why that step is not yet reliable.

**Deployments are per environment, with a shared registry.** `deploy.sh` deploys at subscription scope into `{name}-{environment}-rg`, with `ENVIRONMENT` defaulting to `acceptance`, while the container registry and the identity that pulls from it live in `{name}-general-rg`.

**Model files left the repository.** The bundled `bertje_2022_e4` files are gone; locally, Docker Compose mounts `nlp_api/API_NLP/models` at `/mnt/models` for `nlp-api` and the backend, and in Azure the same path is the model file share. The Container Apps were given more CPU and memory, `nlp-api` most of all.

---

### v2026.09.1 — Choosing the NLP Model (September 2026)

> How to use it: [Using NLP suggestions](../user-guide/using-nlp-suggestions.md). The endpoint: [API endpoints](../reference/api-endpoints.md#post-apipredict).

**The interpreter chooses which model labels the text.** Role detection had one model, fixed at deploy time by the `MODEL_PATH` environment variable. `nlp-api` now carries a registry of selectable models — `bertje_2022_e4`, the existing default, and `legal-bert-dutch-english` — and `POST /api/predict` takes an optional `model` field naming one. The Act frame form gained an **NLP model** dropdown beside the suggestion controls, so the choice is per request rather than per deployment.

**Unknown and missing keys fall back rather than fail.** A `model` value the registry does not know, or no value at all, resolves to the default, and the response echoes the model actually used — so a caller can always tell which one produced the labels rather than assuming its request was honoured. Adding a model to the registry is what exposes it in the GUI; there is no separate list to keep in step.

**A missing model file is reported, not guessed at.** The resolved path is checked before loading, and an absent directory answers `500` with *"Model does not exist on filesystem."* rather than surfacing a loader traceback. That check matters because model files are no longer part of the image.

**Model storage moved out of the container.** `nlp-api` takes its model root from configuration, and the Azure infrastructure adds a **storage account** to hold the model files. Previously a model shipped inside the image, so adding one meant rebuilding and redeploying the service; they are now mounted, and the registry decides which of them a request loads.

**The state-debug panel is removed** — it slowed the editor down enough to be worth losing.

---

### v2026.07.4 — Python Packaging and Pipeline Steps (July 2026)

**The Python services gain `pyproject.toml` files** and their packages are upgraded, `nlp-api` among them. **The backend's tests move to `light-my-request`**, which exercises Fastify's routes in-process rather than over a real socket — faster, and with no port to collide on.

**The GitLab pipeline gains its build steps**, completing the two-stage shape that the test jobs from v2026.07.3 had started.

---

### v2026.07.3 — A Test Suite and a CI Pipeline (July 2026)

> Measured inventory and commands: [Testing](testing.md).

**Automated tests arrive across the stack**, in one release: the GUI's domain logic, the backend, and the wrap-up API. This is the release that took the Norm Editor from no automated tests to a suite covering both languages it is written in.

**A GitLab CI pipeline runs them.** `.gitlab-ci.yml` defines a `test` stage with five jobs — `test_gui` and `test_backend` on `node:24`, `test_wrap_up_api`, `test_unwrap_api` and `test_nlp_api` on `python:3.14.6` — ahead of a `build` stage that builds and pushes a container image per service to Azure Container Registry. The Norm Editor is the only IOU component whose CI runs on GitLab rather than GitHub Actions; see [Code Standards](../../contributing/code-standards.md#the-norm-editor-is-shaped-differently).

---

### v2026.07.2 — Changelog Generation on Commit (July 2026)

**A pre-commit hook regenerates the changelog**, so `gui/public/changelog.json` — which the in-app changelog viewer reads — stays in step with the git history rather than being regenerated by hand at release time.

---

### v2026.07.1 — Filesystem Import Fixed (July 2026)

**Importing an interpretation from the filesystem was reading the wrong format** and failing. Fixed, and the GUI version bumped.

---

### v2026.07.0 — First Tagged Release (July 2026)

**The Norm Editor starts version-tagged releases.** Previously the component shipped without
git tags or a generated changelog; `2026.07.0` is the first annotated release tag, and
`scripts/generate-changelog.mjs` now builds `gui/public/changelog.json` from
[Conventional Commits](https://www.conventionalcommits.org/) history for the in-app changelog
page. Commit messages are enforced as Conventional Commits via git hooks going forward. This
entry therefore documents everything in the tag's range, not just what changed since a prior
release — most of the application's core functionality (task definition, source collection,
annotation, FLINT frame authoring, NLP suggestions, TriplyDB round-trip) predates this tag and
is described in the [Features](../features/overview.md) and [User Guide](../user-guide/getting-started.md)
pages rather than here.

**Server-side rendering removed; the frontend is now a plain SPA.** `src-ssr/` (the Quasar SSR
server, its Triply-fetching middleware, and the render pipeline) was deleted. Client-side
routing (`router/routes.js`) now drives six routes — task, sources, interpretation,
visualization, executable, execute — each a thin `pages/*.vue` wrapper around the existing
`views/*.vue` step UIs. See [Frontend](frontend.md) and [Architecture](architecture.md), both
updated to describe the current SPA + router setup instead of the removed SSR mode.

**In-app changelog page restyled.** The changelog viewer (`gui/src/components/Changelog.vue`)
now renders status pills, emoji-grouped sections, and a document header for the JSON produced
by `generate-changelog.mjs`.

**Internals backported from the TNO mirror.** Graph-processing internals, several
`wrap-up-api` endpoints, and UI styling/layout were backported from the TNO mirror of the
project, alongside removal of duplicate view components and assorted small style/layout
fixes.

**Deployment and infrastructure hardening.** Azure Container App templates gained a
`revisionSuffix` (`utcNow`) so `./deploy.sh` always forces a new revision instead of an ACA
deploy silently reusing a cached image; a DNS zone was added; SSL termination and the release
workflow (tagging, changelog generation, redeploy) were documented in the repository `README.md`;
and a Docker Compose port conflict on the `web` host mapping was resolved.

---

## Roadmap

### Planned

The editor shows six steps as tabs. The last two are placeholders that render
"Coming soon" (`pages/ExecutablePage.vue` and `pages/ExecutePage.vue`):

| Feature | Stage |
|---|---|
| Make interpretations executable | `executable` route |
| Execute task | `execute` route |
