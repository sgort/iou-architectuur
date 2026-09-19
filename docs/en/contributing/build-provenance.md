---
scope: cross-cutting
verified:
  date: 2026-09-19
  against:
    Linked Data Explorer: "ec4792f"
---

# Build Provenance

!!! info "Verification status"
    The **Linked Data Explorer**'s claims were re-checked on **19 September 2026**
    against `ec4792f`, the v2026.09.5 promotion. The **CPSV Editor** and **RONL
    Business API** columns were last re-checked on 12 September 2026, against
    `f5bae6a` and `311d732`; the page stamp names only what was verified on its date.
    The RONL Business API's two columns had been the unverified ones until then, and
    the reason they could not be verified went on 12 September: **both of its
    surfaces reached production that day**, so all four implementations have run
    there.

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

Shipped across three applications in September 2026, and to a fourth — the RONL
public site — on 10 September 2026. All four have since been exercised in production,
the last two on 12 September 2026.

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

## The same feature, four implementations

The module and its tests ported unchanged. Everything else had to be re-derived per
**deployable**, which is not the same as per repository — see the fourth column.

| | CPSV Editor | RONL Business API (frontend) | RONL Business API (public site) | Linked Data Explorer |
|---|---|---|---|---|
| Language | JavaScript | TypeScript | TypeScript | TypeScript |
| Tests | 5 | 8 | 8, plus 4 on the footer | 8 |
| Monorepo | no | yes (`packages/frontend`) | yes (`packages/public-site`) | yes (`packages/frontend`) |
| Surface | changelog tab | lazily-loaded changelog drawer | site footer — no changelog | changelog full page |
| **Who builds** | **Oryx**, in the deploy container | **the runner** | **the runner** | **Oryx**, in the deploy container |
| **`env:` goes on** | **deploy step** | **build step** | **build step** | **deploy step** |
| String lands in | lazy chunk `ChangelogTab-*.js` | lazy chunk `ChangelogPanelContent-*.js` | main `index-*.js` | main `index-*.js` |

The **Surface** row was called *Changelog UI* while every adopter had a changelog.
The public site has none: it is a citizen-facing site whose foot already carried its
origin and version, so the build id joins them on that line rather than acquiring a
panel of its own. Step 4 of the checklist below — match the existing layout — is what
decides this, and it is why the module ports but the markup never does.

### Where the `env:` block goes, and why it moves

This is the single most important difference, and getting it wrong produces a change
that **passes every test and puts nothing in the artifact**.

The rule is not per-repository preference, and it is not per-repository at all — it
follows directly from *who runs the build*, which is a property of a **workflow**.
RONL Business API is the proof: its frontend and its public site live in one
repository, are built by two separate pairs of workflows, and could perfectly well
have answered this question differently. They do not, but nothing about sharing a
repository guaranteed that. Read `skip_app_build` in the workflow you are editing;
do not infer it from a sibling package.

**Where the runner builds, the variables go on the build step.** Both RONL Business
API packages run `npm run build:acc` as a step of their own and pass
`skip_app_build: true` to the Static Web Apps action, which then only uploads
`dist/`:

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

**The CPSV Editor joined it in v2026.09.2**, when its four heaviest tabs were
lazy-loaded to cut the entry chunk from 685.71 to 392.74 kB. `ChangelogTab` is one of
them and the only importer of the build-info module, so the string moved out of the main
bundle into `ChangelogTab-*.js` — and this page's comparison table went on saying *main
bundle* for two releases, because nothing about a correct build id changed. Confirmed on
11 September 2026 with a marker build of v2026.09.4: the injected SHA and run number
appear in `dist/assets/ChangelogTab-*.js` and nowhere else. **A code-splitting change
elsewhere in the app moves where to grep**, which is one more reason to grep all of
`dist/`.

**Grep for the injected values, not the rendered label.** `build 570fd98 · #412` is
assembled at runtime from `` `build ${shortSha} · #${run}` ``, so that string is in no
artifact, however correct the build. What ships is the **full** SHA and the run
number as two separate literals, next to the template. Searching for the label a
user would read returns nothing on a perfectly good build and looks exactly like the
failure this check exists to catch.

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
| RONL Business API (frontend) | `build 1224298 · #265` | `build 66940d9 · #266` |
| RONL Business API (public site) | `build 34002e8 · #76` | `build 0068444 · #77` |
| Linked Data Explorer | `build b669689 · #186` | `build 9db0ab3 · #188` |

The public-site pair was **read out of the deployed bundles**, not derived from the
workflow runs: fetch the page, follow its `/assets/index-*.js`, and the two injected
literals sit next to the template that renders them. That is worth doing once per
adopter, because it is the only check that distinguishes "the workflow ran green"
from "the values reached the artifact".

---

## Known gaps

- **Production has now run in all four.** All eight workflow files carry the
  `env:` block. Two applications promoted v2026.09.2 to `main` on 9 September 2026 and
  both production workflows ran green:

    | | Commit | Run | Changelog should read |
    |---|---|--:|---|
    | CPSV Editor (*Deploy PROD*) | `bbda389` | 88 | `build bbda389 · #88` |
    | Linked Data Explorer | `007b350` | 39 | `build 007b350 · #39` |

    The CPSV Editor has promoted twice more since, both on 11 September: v2026.09.3 as
    `build f7e127a · #92` and v2026.09.4 as **`build f5bae6a · #94`**, each from
    *Deploy PROD (white-sky)*.

    The Linked Data Explorer has promoted twice more since, both on 11 September:
    v2026.09.3 as `build 35a44f8 · #41` and v2026.09.4 as **`build be6bc54 · #44`**,
    each from *Deploy Frontend to Production*. The gaps in the run numbers are the
    pull-request runs of the same workflow, which build previews rather than
    production. v2026.09.4 is also the first promotion under the widened `paths:`
    filter, where a change to the root lockfile alone redeploys the frontend.

    Its v2026.09.5 promotion on 19 September 2026 is **`build ec4792f · #51`** — and
    that one was read out of the deployed bundle rather than derived from the run: the
    production `/assets/index-*.js` carries `"ec4792f09c289f8fee6c68da5184fd775a27ccc9"`
    and `"51"` as the two injected literals.

    Of those four strings, two were **read off the running application** — the CPSV
    Editor's `build bbda389 · #88` and the Linked Data Explorer's `build 007b350 · #39`,
    both confirmed by eye on 9 September. The later ones are derived from the workflow
    runs, which is the weaker check: it distinguishes *the workflow ran green* from
    nothing at all, where a glance at the application distinguishes it from *the values
    reached the artifact*.

    **The RONL Business API closed its own gap on 12 September 2026.** Its frontend
    production workflow had last run on 17 July, before this feature existed, and its
    public site had never had a production run at all. Its promotion of v2026.09.6 that
    morning exercised both at once, and both were confirmed by eye rather than inferred:

    | | Commit | Run | Read on the running application |
    |---|---|--:|---|
    | RONL Business API (frontend) | `04840ed` | 12 | `build 04840ed · #12` in the caseworker changelog |
    | RONL Business API (public site) | `04840ed` | 2 | `publiek.open-regels.nl · v2026.09.6 · build 04840ed · #2` in the footer |

    Two details from that first run are worth carrying to the next adopter. **The same
    commit produced two different run numbers**, 12 and 2, because the run number counts
    executions of a workflow and not commits — which is exactly why the pair is a pair.
    And **the public site's footer is client-rendered**, so grepping the prerendered HTML
    for the string finds nothing and reads as failure; the check is the rendered page, or
    the injected literals inside `/assets/index-*.js`.

    The promotion of v2026.09.7 the same afternoon moved both on again, to run 13 and run
    3 at `311d732`.
- **The line describes the frontend bundle being viewed**, not the backend behind it.
  A backend needs its own answer, and the Linked Data Explorer's backend has one since
  v2026.09.5: `/v1/health` reports a `build` block with **the same shape and
  semantics** as the frontend's `BuildInfo` — tracked only when both SHA and run are
  present, `local build` otherwise, never affecting `status`. The identity travels in a
  `deploy/build-info.json` both backend workflows write into the artifact, **not** in
  an App Service setting, because settings persist across deploys and can describe a
  build that is no longer the one running. The post-deploy check then waits until
  `build.sha` equals the deployed commit, so a deploy that left the previous artifact
  serving fails instead of passing. On 19 September 2026 production's backend reported
  `build ec4792f · #19` — the same commit as its frontend, from a different workflow,
  with a different run number, for the reason given above.

---

## Adding this to another application

The fourth adopter, the RONL public site, followed these six steps exactly as they
were written here and needed no deviation. Step 2 was again the one that decided
everything, and step 4 was the one that produced a visibly different result.

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
