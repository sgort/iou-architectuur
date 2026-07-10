# Changelog & Roadmap

---

## Changelog

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

The five-stage interpretation workflow described in the [Overview](../index.md) has two
stages still scaffolded as placeholders in the router (`pages/ExecutablePage.vue` and
`pages/ExecutePage.vue` both render a "Coming soon" state):

| Feature | Stage |
|---|---|
| Validate — making an interpretation executable | `executable` route |
| Perform — executing a task | `execute` route |
