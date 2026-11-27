---
component: CPRMV
---

# CI/CD

CPRMV is developed on GitHub, in [open-regels/cprmv](https://github.com/open-regels/cprmv), and its pipeline runs on GitHub Actions. Four workflows check every pull request and every push to `acc` and `main`, and a fifth keeps a bill of materials per release; a push to either branch also publishes the API image and waits until the tier's VM runs it. GitLab keeps one job: it publishes the ReSpec specification.

---

## Branches and tiers

Two long-lived branches each drive a tier. `acc` is the default and integration branch and runs on acceptance; `main` is the stable release. Feature branches start from `acc`; only release pull requests go from `acc` into `main`. Nothing reaches either branch except through a pull request.

| Tier | Branch | Host | Image tags | GitHub environment |
|---|---|---|---|---|
| acceptance | `acc` | `acc.cprmv.open-regels.nl` | `sha-<commit>`, `acc` | `acceptance` |
| stable | `main` | `cprmv.open-regels.nl`, alias `cprmv.open-rules.eu` | `sha-<commit>`, `stable`, `<version>`, `vYYYY.MM.N` | `stable` |

`scripts/ci-tier.sh` maps the branch to the tier, host, environment and branch name; any other ref, a tag included, has no tier and fails. A merge into `acc` or `main` is therefore a deploy: see [VM Deployment](vm-deployment.md).

---

## The workflows

| Workflow | File | Runs on | Jobs |
|---|---|---|---|
| CI | `ci.yml` | pull requests into `acc` or `main`; pushes to `acc` and `main`; by hand | `test`, `build`, `publish`, `deploy` |
| Supply-chain audit | `zizmor.yml` | every pull request; pushes to `acc` and `main` | `audit` |
| Semgrep | `semgrep.yml` | every pull request; pushes to `acc` and `main` | `scan` |
| Dependency audit | `dependency-audit.yml` | daily at 05:17 UTC; by hand; pull requests that change the audit itself | `dependency-audit` |
| Release SBOM | `sbom.yml` | pushes to `main`; by hand; pull requests that change the workflow, the SBOM script or its tests, `docs/sbom/`, `serve_api/requirements.txt`, `serve_api/pyproject.toml` or `serve_api/RELEASE` | `release-sbom` |

`audit` and `scan` have no branch or path filter on pull requests, so a pull request cannot avoid a required check by its base branch or the files it touches. CI has no path filter on pushes either: the VM maps every commit of its branch to one image, and a commit without an image would stall it. The Actions layer cache keeps a documentation-only rebuild cheap.

Every job runs on `ubuntu-24.04` with a read-only token, except `publish` (packages, attestations and the OIDC token for signing) and the dependency audit (issues). Pull-request runs of CI and Semgrep are cancelled when a newer commit arrives; pushes queue, so a commit being published is never cancelled half way.

### CI (`ci.yml`)

**`test`** installs `serve_api/requirements-dev.txt` with `--require-hashes` on Python 3.14, compiles and imports the API (`py_compile src/serve.py`, `from src.serve import app`), runs `pytest` from `serve_api/`, runs shellcheck over every tracked `*.sh` outside `rdf/` and over the reconciler's test stubs, and runs the bats suites in `scripts/test` and `deployment/vm/reconciler/test` (bats-core v1.14.0, checked out by commit). See [Testing](testing.md).

**`build`** builds the image from `serve_api/` with the commit, the run number and the release number as build arguments, loads it locally and runs `scripts/smoke-health.sh`: it starts the container, waits up to 60 seconds for `GET /health`, and fails unless `build.sha` equals the commit. The layer cache is read on every run and written only by pushes, so a pull request cannot poison it. `scripts/read-release.sh` reads the release number from `serve_api/RELEASE` and fails the job on anything but one line `vYYYY.MM.N`; without the file, before the first release, the number is empty.

**`publish`** runs only on a push to `acc` or `main`, and is the only job with write permissions. It resolves the tier and pushes the image to `ghcr.io/open-regels/cprmv-api` as `sha-<commit>` and the tier tag (`acc` or `stable`) and, on `main`, as the vocabulary version from `serve_api/pyproject.toml`, refused unless it is `MAJOR.MINOR.PATCH`, and as the release number, when there is one. The push carries a BuildKit SBOM attestation. It then pulls what the registry holds, by digest, runs the same smoke test on it, and attests build provenance for that digest.

**`deploy`** runs after `publish`, in the tier's GitHub environment, and pushes nothing. `scripts/wait-for-deploy.sh` polls the tier's `https://<host>/deploy-status.json` every 20 seconds for up to 15 minutes. It passes when the VM reports `running.sha` equal to the commit **and** `https://<host>/health` reports the same `build.sha`; it fails at once when the VM reports state `broken`, or reports this commit as `failed` or `restored`; and it passes as *superseded* when the branch has already moved to a newer commit, which the VM will deploy instead. Anything it cannot fetch or parse is not a verdict: it keeps polling until the time-out.

### Supply-chain audit (`zizmor.yml`)

One job, **`audit`**, checks the supply-chain policy and reports on every part even when one fails: zizmor 1.29.0 over the workflows (every action reference must be a commit hash, first-party actions included, as `.github/zizmor.yml` records); the Renovate configuration, with `renovate-config-validator --strict`; that `requirements.txt` and `requirements-dev.txt` are exactly what `pip-compile.sh` produces from `pyproject.toml` on the runner; and that every requirement carries a hash.

### Semgrep (`semgrep.yml`)

**`scan`** runs `semgrep ci` (Semgrep 1.176.1, Code and Supply Chain) on the full history, so the scan is diff-aware. It fails on findings the Semgrep policy marks as blocking, and on a scanner that cannot run. A pull request from a fork gets no `SEMGREP_APP_TOKEN`, so `scan` fails for it ([open-regels/cprmv#4](https://github.com/open-regels/cprmv/issues/4)); contributors push a branch to the repository instead.

### Dependency audit (`dependency-audit.yml`)

Every day the audit runs `pip-audit` 2.10.1 over the pinned requirements of both `acc` and `main` (`scripts/audit-requirements.sh`). Any known advisory in a shipped dependency (`serve_api/requirements.txt`) fails it; pip-audit grades no severity. Advisories in development-only dependencies are listed and do not fail it. An audit that cannot run counts as a failure, never as clean. Outside pull requests it opens, updates and closes one tracking issue, labelled `security` and `ci`. Accepted advisories would be listed in `scripts/pip-audit-accepted.txt`; there are none. It is not a merge check.

### Release SBOM (`sbom.yml`)

**`release-sbom`** keeps a CycloneDX bill of materials for every release (ICTU recommendation 10). `scripts/write-sbom.py` runs `cyclonedx-bom` 8.0.1 on `serve_api/requirements.txt`, the shipped and hash-locked dependencies, and writes `docs/sbom/cprmv-api-<release>.cdx.json`, named after `serve_api/RELEASE`; without that file it refuses. The output is deterministic: no serial number or timestamp, and sorted, so the same requirements give the same bytes. The release is in the file name only: the document's root component is `cprmv` at the vocabulary version from `serve_api/pyproject.toml`, so a copy separated from its name does not say which release it describes. The requirements record no dependency graph, so the graph in the document is flat.

The job first runs the script's own tests. On a push to `main` the release must have its SBOM (`--verify-release`; drift is only a warning, because a promotion carries later commits); on the pull request that adds a release's SBOM it must match the requirements exactly (`--check`). It then uploads the document as an artifact kept 90 days; the committed copy is the durable one. It is not a required check. The development dependencies are not in the document; the daily dependency audit covers them. The image's own SBOM, with its Debian packages, is the attestation `publish` attaches in GHCR.

---

## Required checks

Two branch rulesets gate the branches: **acc supply-chain gate** on `acc` and **main promotion gate** on `main`. Both require `audit`, `scan`, `test` and `build`, require a pull request (with no approvals), allow merge commits only, block force pushes and deletion, and have no bypass actors. `publish` and `deploy` are not required: `deploy` fails while a VM is down, and that must not block a merge. Required checks match by job name, so renaming a job means updating the rulesets. `.github/rulesets/acc.json` and `main.json` record what the live rulesets hold; CI does not apply them.

---

## Pinning and Renovate

Nothing the pipeline fetches floats where a pin exists. Actions are pinned to commit hashes; the Python base image (`python:3.14-bookworm`), the Caddy image and the GitLab Pages image are pinned by digest; both requirements files are compiled with `--generate-hashes` on Linux and installed with `--require-hashes`. `SECURITY-PIPELINE.md` in the repository is the register of every pin and who moves it.

Renovate moves actions, images and Python packages after a 14-day minimum release age, without that wait for security fixes. Majors wait for approval in the Dependency Dashboard, and a PyPI `X.0.0` is never offered (ICTU recommendation 7). A Python minor moves the image, the `Makefile` copy of it and the workflows' `python-version` in one pull request, on approval. Lock-file maintenance runs on Monday mornings. A few tools are pinned by hand because Renovate cannot read them (Semgrep, pip-audit, pip-tools, the Renovate validator, `cyclonedx-bom`, and the SBOM workflow's `pytest`, which must equal the pin in `requirements-dev.txt`); shellcheck is whatever the runner ships.

---

## ReSpec publication

GitLab keeps one job. `.gitlab-ci.yml` holds `create-pages` (`node:26-alpine`, pinned by digest), which runs on a push of `main` and publishes the committed `html/public` to GitLab Pages at `https://standaarden.open-regels.nl/standards/cprmv/<version>/`. It builds nothing: the ReSpec is built locally with `npm run build` in `html/` (ReSpec, PlantUML class diagrams, a pandoc PDF) and committed, both to `html/public/<version>/` and to `serve_api/respec/`. `html/public/` has no index of its own, so the Pages root answers 404 and the versioned paths serve. `/bump-release` pushes `main` to the GitLab remote as a fixed step of every release, fast-forward only; that push starts the job ([Cutting a release](#cutting-a-release)).

---

## Releasing

### Two version numbers

CPRMV carries two version numbers, and they move independently.

| | Release | Vocabulary and API version |
|---|---|---|
| Example | `v2026.11.0` | `0.4.3` |
| Form | `vYYYY.MM.N`: `.0` is a month's first release, `.1` and `.2` follow in that month, and the count restarts each month; the `v` keeps it from reading as a vocabulary version | `MAJOR.MINOR.PATCH` |
| What it names | a release of production: whatever a release pull request took to `main`, such as dependency updates, fixes and pipeline changes | the CPRMV vocabulary, its specification, and the API's routes and namespaces |
| Kept in | `serve_api/RELEASE`, one line, written only by a release | `version` in `serve_api/pyproject.toml`, `version=` in `serve_api/src/serve.py`, the image's `org.opencontainers.image.version` label, `html/package.json`, the `rdf/<version>/` folder and the namespaces |
| Where it shows | `/health` `release`; the image tag `vYYYY.MM.N` on `main`; the SBOM's file name, `docs/sbom/cprmv-api-vYYYY.MM.N.cdx.json` | `/` and `/health` `version`; the image tag `<version>` on `main` and the image's version label; `rdf/<version>/`, the `/<version>/methods` route and the namespaces under `https://cprmv.open-regels.nl/<version>/`; the specification at `https://standaarden.open-regels.nl/standards/cprmv/<version>/`; the root component inside the SBOM; `CHANGELOG.md` |
| How it moves | at every release, by `/bump-release` | rarely, through its own pull request into `acc` with a `CHANGELOG.md` entry, merged before the release that carries it |

Production was released several times at 0.4.3 with different dependencies, so 0.4.3 alone does not say what runs; the release does. The release is built into the image on both tiers, so on acceptance `/health` reports the last release its code is at or after, and `build.sha` says exactly what runs. There are no git tags and no GitHub Releases. The site's [changelog](changelog-roadmap.md) lists the releases above the vocabulary and API versions.

The repository's README lists every file a vocabulary bump touches, with a `grep` to find them.

### Cutting a release

A release is cut with the repository's Claude Code command `/bump-release` (`.claude/commands/bump-release.md`), or `/bump-release vYYYY.MM.N` for an explicit number. It never pushes to `acc` or `main` and never merges a pull request; a maintainer merges both.

1. It lists the open pull requests, Renovate's and others, and asks which belong in the release; those are merged into `acc` first.
2. It computes the next number from `serve_api/RELEASE` on `acc` and `main` and today's date.
3. It asks whether the vocabulary version changes too. Usually it does not; if it does, that change is its own pull request, merged before the release, and the command does not make it.
4. On a branch `release/vYYYY.MM.N` from `acc` it writes `serve_api/RELEASE` and the release SBOM, and opens the pull request `Release vYYYY.MM.N` into `acc`. Its merge deploys acceptance.
5. It opens `Release vYYYY.MM.N` from `acc` into `main`. Its merge deploys production: `publish` tags the image `sha-<commit>`, `stable`, `<version>` and `vYYYY.MM.N`.
6. It checks that `cprmv.open-regels.nl` and `cprmv.open-rules.eu` report the release and the merge commit at `/health`, that GHCR has the tag, and that the Release SBOM run passed.
7. It pushes `main` to the GitLab remote, which publishes the specification. This is a fixed step of every release: fast-forward only, checked with `git merge-base --is-ancestor` first and `git ls-remote` after; if GitLab has diverged, it stops.
8. Housekeeping: the local branches are fast-forwarded and the release branch is deleted.

### The release SBOM

The SBOM is generated in the Python image from the `FROM` line of `serve_api/Dockerfile`, with the `cyclonedx-bom` version `sbom.yml` pins; both are read from the repository, so the command does not go stale when Renovate moves the image. `--check` must pass before the release pull request is opened, and the `release-sbom` job runs it again on that pull request. See [Release SBOM](#release-sbom-sbomyml).
