---
component: CPRMV
---

# VM Deployment

The CPRMV API runs on two Azure VMs, one per tier, that keep themselves current. Nothing connects to a VM to deploy it: every two minutes each VM reads the head of its branch on GitHub, pulls the image CI built for that commit, starts it with Docker Compose, checks it, and reports what runs. A merge into `acc` or `main` is therefore a deploy, and the branch rulesets are what stand between a pull request and a VM ([CI/CD](ci-cd.md#required-checks)).

The VM *pulls*; nothing pushes to it. A push from a GitHub-hosted runner would need SSH open to GitHub's address ranges, and a self-hosted runner on a public repository could be handed to a fork by one mistake in its triggers. Pulling needs no inbound access beyond the web ports and no credentials, and what runs becomes something the VM reports rather than something a deploy asserts. The source of everything on this page is `deployment/vm/` in [open-regels/cprmv](https://github.com/open-regels/cprmv/tree/main/deployment/vm), with the operator's runbook in its `README.md`.

---

## The two tiers

| Tier | Branch | Host | VM | Deployment description |
|---|---|---|---|---|
| `acc` | `acc` | `acc.cprmv.open-regels.nl` | `vm-cprmv-acc` | `deployment/vm/acc/` |
| `stable` | `main` | `cprmv.open-regels.nl`, alias `cprmv.open-rules.eu` | `vm-cprmv-stable` | `deployment/vm/stable/` |

`stable` is the released version; the API reports it as environment `stable`, and acceptance as `acceptance`. Each VM serves one tier and runs nothing else: two tiers on one VM would both need ports 80 and 443.

Each tier's directory holds a `compose.yml` and a `Caddyfile`, and the Compose project is named `cprmv-<tier>`. It runs two services:

- **`cprmv-api`** runs the image by digest (`${CPRMV_IMAGE}`, which the reconciler writes as `ghcr.io/open-regels/cprmv-api@sha256:…`), with `CPRMV_IMAGE_DIGEST` set to that digest and `CPRMV_ENVIRONMENT` set to `acceptance` or `stable`. It publishes port 8000 on `127.0.0.1` only. Its health check requests `/health` every 30 seconds, with a 60-second start period (probing every 2 seconds during it) and 3 retries.
- **`caddy`** (`caddy:2.11.9-alpine`, pinned by digest) starts only once the API reports healthy. It listens on ports 80 and 443, obtains a Let's Encrypt certificate for each host name, proxies to the API, and sets `Strict-Transport-Security` (with `preload`), `X-Content-Type-Options`, `X-Frame-Options: DENY`, `X-XSS-Protection` and a `Permissions-Policy` that switches off device features. It serves the reconciler's status file at `/deploy-status.json`, with `Cache-Control: no-store`, from a read-only mount of `/opt/cprmv/<tier>/www`. A plain-HTTP site on port 80 answers requests made by IP address, without redirecting, so a new VM can be checked before DNS points at it. Its certificates live in named volumes, so they survive each release.

Both services restart unless stopped and keep at most three 10 MB log files. The stable Caddyfile lists `cprmv.open-rules.eu` beside `cprmv.open-regels.nl`, each with its own certificate; otherwise the two tiers' files differ only in the tier name, the status path and the host names.

---

## From merge to running

1. A pull request merges into `acc` (or `main`).
2. CI tests and builds the commit, pushes `ghcr.io/open-regels/cprmv-api:sha-<commit>`, checks the pushed image's `/health`, and attests its provenance ([CI/CD](ci-cd.md#ci-ciyml)). On `main` the image is built again from the merge commit, not copied from acceptance, so that it reports the commit the VM deploys.
3. Within two minutes of the image appearing, the tier's VM sees the new head, pulls `sha-<commit>` and brings the release up.
4. CI's `deploy` job waits until `deploy-status.json` reports the commit running and `/health` reports the same `build.sha`.

On this page, as in the reconciler, a *release* is what the reconciler deploys: one commit's deployment directory. The release *number* (`v2026.11.1`) that `/health` reports is a different thing; see [Two version numbers](ci-cd.md#two-version-numbers).

Release pull request [#45](https://github.com/open-regels/cprmv/pull/45), release v2026.11.1, merged into `main` at 17:17 UTC on 27 November 2026. CI [run 50](https://github.com/open-regels/cprmv/actions/runs/46040683051) had published `0c4d236` by 17:21, the stable VM reported it running at 17:22:38, and `deploy` passed at 17:23:08, 88 seconds after that job started.

---

## The reconciler

`deployment/vm/reconciler/reconcile.sh <tier>` is a POSIX shell script that needs git, jq, curl, `flock` and the Docker CLI with its Compose plugin. It runs as the `cprmv` system user, started by the systemd timer `cprmv-reconcile@<tier>.timer` one minute after boot and two minutes after each run ends; the service is a oneshot with a 15-minute limit. The stable tier follows `main` through `CPRMV_BRANCH=main` in `/etc/cprmv/stable.env`, which the unit reads when it exists; acceptance needs none, because its branch has its tier's name. Runs never overlap: a run that finds the lock held exits at once.

On the VM, for a tier:

| Path | What |
|---|---|
| `/usr/local/lib/cprmv/reconcile.sh` | the reconciler, installed once, never self-updating |
| `/etc/systemd/system/cprmv-reconcile@.service`, `.timer` | its units, instantiated as `@acc` or `@stable` |
| `/etc/cprmv/stable.env` | stable only: `CPRMV_BRANCH=main` |
| `/opt/cprmv/<tier>/repo/` | a bare repository the reconciler creates and fetches into |
| `/opt/cprmv/<tier>/releases/<sha>/` | `deployment/vm/<tier>/` at that commit, plus an `.env` with the image digest |
| `/opt/cprmv/<tier>/current` | a symlink to the release that runs |
| `/opt/cprmv/<tier>/state.json` | running and previous release, failed commits, what it waits for |
| `/opt/cprmv/<tier>/www/deploy-status.json` | the status Caddy serves |

### One run

1. **Fetch** the branch head from `https://github.com/open-regels/cprmv.git`, anonymously, within two minutes. If the fetch fails, nothing changes and the status carries a warning.
2. **Check Docker.** Without a reachable daemon nothing can be judged: nothing changes, with a warning.
3. **Nothing to do** when the head already runs and Compose reports its API healthy. If it runs but is unhealthy, it is re-applied (step 7).
4. **A failed commit is not retried.** If the head is on the list of failed commits (the last 50 are kept), the reconciler only keeps the running release healthy; the fix is a new commit.
5. **Wait for the image.** If `sha-<head>` is not on GHCR yet, or cannot be pulled, the state is `waiting`, and after 30 minutes on the same head `stalled`. What ran before keeps running, and is re-applied if Compose reports it unhealthy.
6. **Prepare** the release: resolve the image's registry digest, export `deployment/vm/<tier>/` from that commit with `git archive` (refusing a `compose.yml` that is missing or a symlink), and write `.env` with the image pinned as `ghcr.io/open-regels/cprmv-api@sha256:…`.
7. **Apply and verify:** `docker compose up -d --wait --remove-orphans`, allowing 120 seconds to become healthy, then `GET http://127.0.0.1:8000/health` must report `build.sha` equal to the commit.
8. **Record** the release as running and the one before it as previous, repoint `current` in a single rename, and **prune** every other release directory and its image tag.
9. **Write** `deploy-status.json`, through a temporary file and a rename, so a reader never sees half a file.

The deployment description comes from the deployed commit itself, so a change to `compose.yml` or the Caddyfile deploys with the image, through the same pull request. The API's data comes only from the image: nothing is mounted over `/app/data`. The run exits 0 also when a deploy fails, because the status says so; it exits non-zero only on an error of its own.

### When a deploy fails

If the new release does not come up healthy within the time limit, or `/health` reports another commit, the commit is marked failed and the reconciler brings back the release that ran before it: the state is `failed` and `last_attempt.result` is `restored`. If there was no earlier release, nothing runs and the state is `failed`. Only if the restore fails too is the state **`broken`**: nothing reliable runs, and it is the one state that needs a person. While a newer head waits or has failed, a running release that Compose reports unhealthy is re-applied; that is reported as a warning and changes neither the state nor the last attempt.

| Situation | What runs | `state` | CI `deploy` |
|---|---|---|---|
| Image not built (yet) | the previous release | `waiting`, after 30 minutes `stalled` | waits; times out after 15 minutes |
| New release unhealthy, or another `build.sha` | the previous release, restored | `failed` | fails |
| Restore fails as well | nothing reliable | `broken` | fails |
| VM or timer down | unknown | stale `checked_at`, or no answer | times out |
| Two merges in quick succession | the newer | the newer as target | the older passes as *superseded* |

### Reading `deploy-status.json`

`https://<host>/deploy-status.json` (or `http://<ip>/deploy-status.json` before DNS moves) reports:

| Field | Meaning |
|---|---|
| `tier` | `acc` or `stable` |
| `checked_at` | the last run; a stale value means the VM or its timer is down |
| `state` | `running`, `waiting`, `stalled`, `failed` or `broken` |
| `target.sha` | the head of the branch the reconciler works towards |
| `running` | the commit, image digest and start time of what runs now |
| `last_attempt` | the last deploy: `deployed`, `failed` or `restored`, with the error output |
| `reconciler.matches_repo` | whether the installed `reconcile.sh` equals the one in the target commit |
| `warning` | something to look at that did not change the state |

| State | Meaning | Do |
|---|---|---|
| `running` | The target runs and is healthy. | Nothing. |
| `waiting` | The target's image is not on GHCR yet, usually because CI is still building it. | Nothing; it resolves itself. |
| `stalled` | Still no image for the target after 30 minutes. | Look at that commit's `build` or `publish` job. A new commit unblocks it. |
| `failed` | The target did not come up; the previous release was restored, or nothing ran before. | Read `last_attempt.error`, fix, merge a new commit. |
| `broken` | The target failed and the restore failed. | SSH in, read the reconciler's journal and `state.json`, and bring a release up by hand. |

On 28 November 2026 both stable host names reported `running` `0c4d236`, and acceptance `running` `ebf7def`, each with `matches_repo: true` and no warning.

### Changing the reconciler

The reconciler never updates itself, so that a bad merge cannot replace what would roll it back. `reconciler.matches_repo` reads `false` after a pull request changes `reconcile.sh`, until someone installs the new copy over SSH from the one allowed address. It compares only `reconcile.sh`: a changed systemd unit shows no such sign, and is installed the same way, followed by a `systemctl daemon-reload`. The alternative is to reprovision the VM. A run by hand must change nothing the second time.

---

## What `/health` proves

`GET /health` answers `status`, `version`, `environment`, `release`, `build.sha`, `build.run` and `image.digest` ([API Endpoints](../reference/api-endpoints.md#get-health)). The release number, the commit and the run are baked into the image by CI as build arguments; the digest and the environment are set by the tier's Compose file. Only `build.sha` is checked; `release` says which release the code belongs to, and on acceptance it is the last release the code is at or after. Four checks compare `build.sha` with the commit they expect:

| Where | Against |
|---|---|
| CI `build` | the image just built, started locally |
| CI `publish` | the image pulled back from GHCR by digest |
| the reconciler | the release it has just started, before recording it |
| CI `deploy` | the public host, once `deploy-status.json` reports the commit |

A host that reports a commit therefore runs an image built from that commit, and `deploy-status.json` names the registry digest the VM pinned. `/health` does not load a method; it proves which build runs, not that every source answers.

On 28 November 2026 `cprmv.open-regels.nl` and `cprmv.open-rules.eu` reported `stable`, release `v2026.11.1`, `0c4d236` (run 50), and `acc.cprmv.open-regels.nl` reported `acceptance`, release `v2026.11.1`, `ebf7def` (run 56). Acceptance runs two pull requests more, merged into `acc` after the release: the development requirements compiled against the shipped ones ([#46](https://github.com/open-regels/cprmv/pull/46)) and a Renovate update of `fastapi-cli` to 0.0.34 ([#43](https://github.com/open-regels/cprmv/pull/43)).

---

## Provisioning a VM

Everything that writes to Azure is run by a maintainer with the `az` CLI. `deployment/vm/provision.sh` creates one tier's VM: `TIER=acc` (the default) or `TIER=stable`. The subscription and the one address allowed to reach SSH are passed in the environment and never written to a file, because the repository is public. The script is idempotent: it creates only what is missing, and corrects an SSH rule whose source differs.

Per tier it creates a resource group `rg-cprmv-<tier>`, a virtual network and subnet, a network security group that allows 80 and 443 from anywhere and 22 from that one address, a static public IP, and the VM `vm-cprmv-<tier>`: `westeurope`, `Standard_B2ms`, Ubuntu 24.04 LTS on x86-64 (the image is built for `linux/amd64` only), SSH key only. Every default can be overridden by an environment variable of the same name.

The VM is set up by **cloud-init** on first boot. `provision.sh` renders `deployment/vm/cloud-init.yaml` for the tier with the reconciler and its two units embedded from the local checkout, so the VM gets exactly the reviewed files and fetches no code at boot. cloud-init installs Docker Engine and its Compose plugin from Docker's repository after checking its signing key's fingerprint, with git, jq, curl and util-linux (`flock`); creates the `cprmv` system user, without a login shell and in the `docker` group; writes `/etc/cprmv/stable.env` for the stable tier; and enables the tier's timer. The reconciler then creates its own repository and deploys the head of the branch. The VM is tagged with the hash of its cloud-init, so a later run says when the template has changed (cloud-init runs only on first boot); `--render <file>` writes the rendered cloud-init without touching Azure.

Outbound HTTPS is open, as on an Azure VM by default. The VM needs GitHub, GHCR and its layer storage, Let's Encrypt, Docker Hub for the Caddy image, Docker's apt repository at provisioning, and every external source the API calls.

---

## Moving DNS

`deployment/vm/cutover-dns.sh` points a tier's host name at its VM. A day ahead, `--lower-ttl` sets the record's TTL to 300 seconds. The cutover itself refuses unless the new VM reports, over its own IP, that it runs this tier with state `running`. It adds the new address before removing the others, so the record set is never empty, checks that the set holds exactly that address with TTL 300, and prints the old and new values. For the stable tier it then deletes the TLSA record `_443._tcp.<record>`, if there is one: such a record pins a server's key, and Caddy's key can change at renewal. `cprmv.open-rules.eu` was moved the same way, with the zone and record overridden. Caddy obtains each certificate once the name points at the VM.

---

## What the tests verify

The scripts are shellchecked and tested with bats in CI's `test` job: 69 tests in six files, all passing in CI run 50 on 27 November 2026.

| File | Tests | What they pin down |
|---|---|---|
| `deployment/vm/reconciler/test/reconcile.bats` | 24 | a first deploy; a second run changes nothing; waiting, then stalled; a failed deploy restores the previous release; a wrong `build.sha` counts as failure; a failed commit is not retried, a newer one is; a failing restore is `broken`; a first deploy that fails has nothing to restore; an unhealthy release is re-applied, and a failed re-apply restores the previous one; a failed fetch or an unreachable Docker daemon changes nothing; a failed or waiting target keeps the running release healthy; a pull failure waits; a missing digest or tier directory fails and restores; pruning keeps the running and previous releases; `matches_repo`; a held lock skips the run; an existing clone is reused; the stable tier follows `CPRMV_BRANCH` |
| `scripts/test/wait-for-deploy.bats` | 11 | passes only when the status and `/health` agree; fails on `broken`, even when the commit matches, and on this commit failed, but not on an older failed commit; superseded; an unreachable status polls until the time-out; a status value cannot start a workflow command; usage |
| `scripts/test/smoke-health.bats` | 5 | matching, mismatching and null `build.sha`; no answer within the deadline; usage |
| `scripts/test/read-release.bats` | 15 | the release number CI builds into the image: a valid release is printed, with or without a trailing newline; an absent file gives an empty release; the default path; a missing `v`, month 13, month 00 or an unpadded month, more than one line, trailing text, a CRLF ending, an empty file, a NUL byte, two trailing newlines and a leading space all fail without printing a release; usage |
| `scripts/test/ci-tier.bats` | 5 | `acc` and `main` map to their tiers; other branches, tags and no argument fail |
| `scripts/test/audit-requirements.bats` | 9 | the [dependency audit](ci-cd.md#dependency-audit-dependency-audityml): shipped findings fail, development-only findings do not, accepted ids are ignored, a clean file is clean, tool errors and skipped shipped packages are failures |

The reconciler's tests run in temporary git repositories against stubbed `docker` and `curl`; they start no real containers. Nothing tests `provision.sh`, `cloud-init.yaml` or `cutover-dns.sh` beyond shellcheck.

---

## A template for other VMs

This deployment is the first implementation of the approach decided in [ronl-business-api#196](https://github.com/sgort/ronl-business-api/issues/196) for IOU's VMs: the VM reconciles itself from its repository, with no inbound access for a deploy. Its design is meant as the template for the other IOU VM deployments, with the parts that are not CPRMV-specific kept recognisable:

- **Generic:** the reconciler takes the tier as its argument and the branch from `CPRMV_BRANCH`; the systemd units are templates on the tier; each repository carries its own `deployment/vm/<tier>/`, so a release stays one pull request in one repository; the status file and the `build.sha` check on `/health`; the failure handling; the provisioning and DNS scripts that take `TIER`.
- **CPRMV-specific:** one application image, whose commit `/health` reports; a public repository and a public package, so the VM needs no credentials at all; data only from the image; and one tier per VM, on a VM that runs nothing else.

Lifting the reconciler into a form other repositories can share is a follow-up for when a second repository uses it.

---

## Limits

- **The image is trusted by its tag.** CI attests each image's provenance, but the VM does not yet check that attestation before it applies an image; anyone with write access to the package could push a `sha-` tag. Verifying it on the VM is the design's first follow-up.
- **The `cprmv` user is in the `docker` group**, which is root-equivalent. It is a system account without a login shell, on a VM that runs nothing else.
- **Caddy restarts on every deploy**, because each release has its own directory and so its own Caddyfile mount: a brief connection drop per deploy.
- **A changed reconciler or unit is installed by hand**, over SSH or by reprovisioning; `matches_repo` shows only the former.
- **No image scan** yet; it is a follow-up in the design. Each release has an SBOM, and each pushed image an SBOM attestation ([Release SBOM](ci-cd.md#release-sbom-sbomyml)).
