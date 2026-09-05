---
scope: cross-cutting
---

# Build Provenance

*Answering "which build am I looking at?" from inside the running app*

Every IOU application shows a version in its changelog. That version comes from
`package.json` or `changelog.json` and is written by hand at release time, so it
identifies a **release** — not a **build** of that release. Those are not the same
thing, and the difference matters exactly when something is behaving oddly and the
first question is whether the environment is even serving what you think it is.

Three cases where a version string cannot answer that:

- **Acceptance and production can serve different builds of the same version**,
  because they deploy from different branches at different times.
- **Redeploying unchanged code** produces a new artifact carrying an identical
  version. Nothing in the running app distinguishes the two.
- **A release can be rebuilt** after a workflow change, a dependency resolution
  difference, or a re-run of a failed job — same source, different artifact.

Shipped across the three applications in September 2026.

---

## What it looks like

One recessive monospace line directly beneath the changelog heading:

```
build 570fd98 · #412
```

The full 40-character SHA sits on the `title` attribute, so it can be copied for a
lookup without cluttering the display. With nothing injected the line reads
**`local build`**. It is never blank, and it never resembles a deployed artifact
when it is not one.

### Why two values rather than one

| Value | Answers |
|---|---|
| Commit SHA | *What source was built?* |
| Run number | *Which build of that source is this?* |

The SHA alone is a **code id**, not a build id — two deployments of the identical
commit share it. The run number is what makes the pair unique per artifact.

---

## Half-configured counts as untracked

A run number with no SHA renders `local build`, not `#412`: showing a run number
with no commit behind it implies a provenance the bundle does not have. A SHA with
no run number is equally untracked, because it cannot distinguish two builds of one
commit.

Blank and whitespace-only values are treated as absent, because Vite substitutes an
empty string rather than `undefined` in some build configurations — without that
rule the panel renders `build  · #`.

!!! danger "Never derive the SHA from git at build time"
    No `git rev-parse` in a build script. In two of the three applications the build
    runs inside a container where neither `git` nor `.git` is guaranteed to exist,
    and **a build id that silently fails to resolve is worse than none — it lies.**
    The values are passed in from the workflow, where they are always available.

---

## The same feature, three implementations

The module and its tests ported unchanged. Everything else had to be re-derived per
repository.

| | CPSV Editor | RONL Business API | Linked Data Explorer |
|---|---|---|---|
| Language | JavaScript | TypeScript | TypeScript |
| Tests | 5 | 8 | 8 |
| Monorepo | no | yes (`packages/frontend`) | yes (`packages/frontend`) |
| Changelog UI | tab | lazily-loaded drawer | full page |
| **Who builds** | **Oryx**, in the deploy container | **the runner** | **Oryx**, in the deploy container |
| **`env:` goes on** | **deploy step** | **build step** | **deploy step** |
| String lands in | main bundle | lazy chunk `ChangelogPanelContent-*.js` | main `index-*.js` |

### Where the `env:` block goes, and why it moves

This is the single most important difference, and getting it wrong produces a change
that **passes every test and puts nothing in the artifact**.

The rule is not per-repository preference — it follows directly from *who runs the
build*:

**Where the runner builds, the variables go on the build step.** RONL Business API
runs `npm run build:acc` as its own step and passes `skip_app_build: true` to the
Static Web Apps action, which then only uploads `dist/`:

```yaml
- name: Build frontend for ACC
  working-directory: packages/frontend
  env:
    VITE_BUILD_SHA: ${{ github.sha }}
    VITE_BUILD_RUN: ${{ github.run_number }}
  run: npm run build:acc
```

**Where Oryx builds, they go on the deploy step.** The CPSV Editor and the Linked
Data Explorer have no build step at all — the Static Web Apps action builds inside
its own container, and forwards the runner's environment into it:

```yaml
- name: Build And Deploy
  uses: Azure/static-web-apps-deploy@<pinned-sha> # v1
  env:
    VITE_BUILD_SHA: ${{ github.sha }}
    VITE_BUILD_RUN: ${{ github.run_number }}
  with:
    app_location: '/packages/frontend'
    output_location: 'dist'
    app_build_command: 'npm run build:acc'
```

Whether Oryx forwards the runner's environment into its container **could not be
answered locally**. It was settled by a deployed preview.

!!! note "`skip_app_build` is the tell, and it is the same flag that governs pinning"
    A repository that sets `skip_app_build: true` builds on the runner; one that
    does not hands the build to Oryx. That single flag decides which step the `env:`
    block belongs on — and it is the same flag that decides whether lockfile
    integrity covers what ships or only what is tested. See
    [Supply-Chain Pinning](supply-chain.md#what-this-does-not-protect), where it
    appears for the second reason.

### Vite specifics

The `VITE_` prefix is **not optional** — Vite exposes only variables carrying its
`envPrefix` to `import.meta.env`, and anything else is invisible to the bundle. A
Create React App project would need `REACT_APP_` and `process.env`; Next.js would
need `NEXT_PUBLIC_`.

Vite merges `VITE_`-prefixed variables from `process.env` **over** the mode file
(`.env.acceptance`, `.env.production`). No env file needs editing, and none of the
three repositories defines these variables in one — CI is deliberately the only
source, so every local run falls through to `local build`.

---

## Two implementation decisions worth keeping

**A separate module, not logic in the component.** The fallback rules become
testable without rendering anything; most of each test file exercises paths that
would otherwise need a mounted component.

**Read the environment *inside* the function, never at module scope.** This is the
one that bites:

```ts
const SHA = import.meta.env.VITE_BUILD_SHA; // ← evaluated once, at import
```

A module-scope capture is evaluated a single time when the module is first imported
and cannot be stubbed per test afterwards, which makes the fallback path untestable
without `vi.resetModules` gymnastics. Reading inside the function lets `vi.stubEnv`
and `vi.unstubAllEnvs` work cleanly.

---

## Verifying it

A build-time injection is precisely the kind of change that passes unit tests and
ships an artifact containing nothing. **Unit tests alone are insufficient.**

**Build both directions and grep the whole of `dist/`** — not just the entry bundle.
In RONL Business API the changelog is deliberately code-split, so the string lands
in a `ChangelogPanelContent-*.js` chunk; grepping only `index.js` returns nothing
and looks exactly like failure. Confirm the chunk hash changes between the two
builds — if it does not, the second build did not run.

**Check the exit code, not a grep of the output.** Grepping for `PASS`/`FAIL` misses
failure modes the chosen pattern does not match. A command either succeeded or it
did not, and no pattern can filter that away. Watch the same trap in shell chains: a
failed `cd` in `cd dir && npm run lint` means lint never ran, and the non-zero exit
is the `cd`. That produced a false "clean build" reading during development — the
build never executed and the grep examined the *previous* build's `dist/`.

**Then check the deployed preview.** Only that proves the workflow `env:` block
reaches the builder; the local greps prove the code path and nothing more.

### `github.sha` on a pull request is not a commit in your branch

On a pull request, `github.sha` is **the merge commit GitHub synthesises**, not the
head of the branch. The SHA shown on a preview deployment therefore matches no
commit in the branch history and cannot be found with `git log`.

This is correct — that synthesised commit is genuinely what got built — but it will
be reported as a bug unless the pull request says so. On a push to an integration
branch, `github.sha` is the real commit. Observed:

| | Preview (synthesised) | After merge (real commit) |
|---|---|---|
| RONL Business API | `build 1224298 · #265` | `build 66940d9 · #266` |
| Linked Data Explorer | `build b669689 · #186` | `build 9db0ab3 · #188` |

---

## Known gaps

- **Production is wired everywhere and exercised nowhere.** All six workflow files
  carry the `env:` block, but only the three acceptance workflows have run. Worth
  one glance at the changelog on each application's first production release.
- **Backend versions are unaffected.** The line describes the frontend bundle being
  viewed; backends ship their versions separately.

---

## Adding this to a fourth application

1. **Confirm the bundler first.** `VITE_` and `import.meta.env` are Vite-specific.
2. **Find out who builds** — the runner, or a container the deploy action owns. This
   decides which step the `env:` block belongs on, and it is the decision most likely
   to be wrong. `skip_app_build` is the tell.
3. **Port the `buildInfo` module and its tests unchanged.** This part genuinely
   transfers.
4. **Match the existing changelog layout** rather than importing another
   application's markup.
5. **Verify with real builds in both directions**, grepping all of `dist/`.
6. **Confirm on the deployed preview.** Nothing local substitutes for it.
