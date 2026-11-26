---
component: CPRMV
---

# CI/CD

CPRMV is developed on GitHub, in [open-regels/cprmv](https://github.com/open-regels/cprmv), and its pipeline runs on GitHub Actions. Four workflows check every pull request and every push to `acc` and `main`; a push to either branch also publishes the API image and waits until the tier's VM runs it. GitLab keeps one job: it publishes the ReSpec specification.

---

## Branches and tiers

Two long-lived branches each drive a tier. `acc` is the default and integration branch and runs on acceptance; `main` is the stable release. Feature branches start from `acc`; only release pull requests go from `acc` into `main`. Nothing reaches either branch except through a pull request.

| Tier | Branch | Host | Image tags | GitHub environment |
|---|---|---|---|---|
| acceptance | `acc` | `acc.cprmv.open-regels.nl` | `sha-<commit>`, `acc` | `acceptance` |
| stable | `main` | `cprmv.open-regels.nl`, alias `cprmv.open-rules.eu` | `sha-<commit>`, `stable`, `<version>` | `stable` |

`scripts/ci-tier.sh` maps the branch to the tier, host, environment and branch name; any other ref, a tag included, has no tier and fails. A merge into `acc` or `main` is therefore a deploy: see [VM Deployment](vm-deployment.md).

---

## The workflows

| Workflow | File | Runs on | Jobs |
|---|---|---|---|
| CI | `ci.yml` | pull requests into `acc` or `main`; pushes to `acc` and `main`; by hand | `test`, `build`, `publish`, `deploy` |
| Supply-chain audit | `zizmor.yml` | every pull request; pushes to `acc` and `main` | `audit` |
| Semgrep | `semgrep.yml` | every pull request; pushes to `acc` and `main` | `scan` |
| Dependency audit | `dependency-audit.yml` | daily at 05:17 UTC; by hand; pull requests that change the audit itself | `dependency-audit` |

`audit` and `scan` have no branch or path filter on pull requests, so a pull request cannot avoid a required check by its base branch or the files it touches. CI has no path filter on pushes either: the VM maps every commit of its branch to one image, and a commit without an image would stall it. The Actions layer cache keeps a documentation-only rebuild cheap.

Every job runs on `ubuntu-24.04` with a read-only token, except `publish` (packages, attestations and the OIDC token for signing) and the dependency audit (issues). Pull-request runs of CI and Semgrep are cancelled when a newer commit arrives; pushes queue, so a commit being published is never cancelled half way.

### CI (`ci.yml`)

**`test`** installs `serve_api/requirements-dev.txt` with `--require-hashes` on Python 3.14, compiles and imports the API (`py_compile src/serve.py`, `from src.serve import app`), runs `pytest` from `serve_api/`, runs shellcheck over every tracked `*.sh` outside `rdf/` and over the reconciler's test stubs, and runs the bats suites in `scripts/test` and `deployment/vm/reconciler/test` (bats-core v1.14.0, checked out by commit). See [Testing](testing.md).

**`build`** builds the image from `serve_api/` with the commit and run number as build arguments, loads it locally and runs `scripts/smoke-health.sh`: it starts the container, waits up to 60 seconds for `GET /health`, and fails unless `build.sha` equals the commit. The layer cache is read on every run and written only by pushes, so a pull request cannot poison it.

**`publish`** runs only on a push to `acc` or `main`, and is the only job with write permissions. It resolves the tier and pushes the image to `ghcr.io/open-regels/cprmv-api` as `sha-<commit>` and the tier tag (`acc` or `stable`) and, on `main`, as the version from `serve_api/pyproject.toml`, refused unless it is `MAJOR.MINOR.PATCH`. It then pulls what the registry holds, by digest, runs the same smoke test on it, and attests build provenance for that digest.

**`deploy`** runs after `publish`, in the tier's GitHub environment, and pushes nothing. `scripts/wait-for-deploy.sh` polls the tier's `https://<host>/deploy-status.json` every 20 seconds for up to 15 minutes. It passes when the VM reports `running.sha` equal to the commit **and** `https://<host>/health` reports the same `build.sha`; it fails at once when the VM reports state `broken`, or reports this commit as `failed` or `restored`; and it passes as *superseded* when the branch has already moved to a newer commit, which the VM will deploy instead. Anything it cannot fetch or parse is not a verdict: it keeps polling until the time-out.

### Supply-chain audit (`zizmor.yml`)

One job, **`audit`**, checks the supply-chain policy and reports on every part even when one fails: zizmor 1.29.0 over the workflows (every action reference must be a commit hash, first-party actions included, as `.github/zizmor.yml` records); the Renovate configuration, with `renovate-config-validator --strict`; that `requirements.txt` and `requirements-dev.txt` are exactly what `pip-compile.sh` produces from `pyproject.toml` on the runner; and that every requirement carries a hash.

### Semgrep (`semgrep.yml`)

**`scan`** runs `semgrep ci` (Semgrep 1.176.1, Code and Supply Chain) on the full history, so the scan is diff-aware. It fails on findings the Semgrep policy marks as blocking, and on a scanner that cannot run. A pull request from a fork gets no `SEMGREP_APP_TOKEN`, so `scan` fails for it ([open-regels/cprmv#4](https://github.com/open-regels/cprmv/issues/4)); contributors push a branch to the repository instead.

### Dependency audit (`dependency-audit.yml`)

Every day the audit runs `pip-audit` 2.10.1 over the pinned requirements of both `acc` and `main` (`scripts/audit-requirements.sh`). Any known advisory in a shipped dependency (`serve_api/requirements.txt`) fails it; pip-audit grades no severity. Advisories in development-only dependencies are listed and do not fail it. An audit that cannot run counts as a failure, never as clean. Outside pull requests it opens, updates and closes one tracking issue, labelled `security` and `ci`. Accepted advisories would be listed in `scripts/pip-audit-accepted.txt`; there are none. It is not a merge check.

---

## Required checks

Two branch rulesets gate the branches: **acc supply-chain gate** on `acc` and **main promotion gate** on `main`. Both require `audit`, `scan`, `test` and `build`, require a pull request (with no approvals), allow merge commits only, block force pushes and deletion, and have no bypass actors. `publish` and `deploy` are not required: `deploy` fails while a VM is down, and that must not block a merge. Required checks match by job name, so renaming a job means updating the rulesets. `.github/rulesets/acc.json` and `main.json` record what the live rulesets hold; CI does not apply them.

---

## Pinning and Renovate

Nothing the pipeline fetches floats where a pin exists. Actions are pinned to commit hashes; the Python base image (`python:3.14-bookworm`), the Caddy image and the GitLab Pages image are pinned by digest; both requirements files are compiled with `--generate-hashes` on Linux and installed with `--require-hashes`. `SECURITY-PIPELINE.md` in the repository is the register of every pin and who moves it.

Renovate moves actions, images and Python packages after a 14-day minimum release age, without that wait for security fixes. Majors wait for approval in the Dependency Dashboard, and a PyPI `X.0.0` is never offered (ICTU recommendation 7). A Python minor moves the image, the `Makefile` copy of it and the workflows' `python-version` in one pull request, on approval. Lock-file maintenance runs on Monday mornings. A few tools are pinned by hand because Renovate cannot read them (Semgrep, pip-audit, pip-tools, the Renovate validator); shellcheck is whatever the runner ships.

---

## ReSpec publication

GitLab keeps one job. `.gitlab-ci.yml` holds `create-pages` (`node:26-alpine`, pinned by digest), which runs on a push of `main` and publishes the committed `html/public` to GitLab Pages at `https://standaarden.open-regels.nl/standards/cprmv/<version>/`. It builds nothing: the ReSpec is built locally with `npm run build` in `html/` (ReSpec, PlantUML class diagrams, a pandoc PDF) and committed, both to `html/public/<version>/` and to `serve_api/respec/`. `html/public/` has no index of its own, so the Pages root answers 404 and the versioned paths serve. A maintainer pushes `main` to the GitLab remote by hand at a release, fast-forward; that push starts the job.

---

## Releasing

1. On `acc`, through a pull request, raise the version everywhere it is written and add the `CHANGELOG.md` entry: for the API and image, `version` in `serve_api/pyproject.toml` (the `<version>` tag is read from it), `version=` in `serve_api/src/serve.py` and the image's version label in `serve_api/Dockerfile`; for the vocabulary, `html/package.json`, the `rdf/<version>/` folder and the other hard-coded occurrences.
2. Open a pull request from `acc` into `main`, named `Release <version>`. `audit`, `scan`, `test` and `build` run on it.
3. Merge it. `publish` tags the image `stable` and `<version>`, the stable VM deploys it within minutes, and `deploy` turns green.
4. Push `main` fast-forward to GitLab, which publishes the ReSpec.
