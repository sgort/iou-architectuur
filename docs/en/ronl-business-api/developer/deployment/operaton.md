---
component: RONL Business API
---

# Operaton Deployment (VM)

Operaton is the BPMN/DMN execution engine. It runs as a single Docker container on the VM, shared between ACC and PROD (process definition version tags differentiate environments), behind the [Caddy](caddy.md) reverse proxy.

Since v2026.11.1 the engine's REST API **requires a login**. Reading the rules and evaluating a decision stay public; everything else — cases, tasks, history, deploying — needs credentials of the caller's own ([#415](https://github.com/sgort/ronl-business-api/issues/415)).

---

## Repository structure

The repository holds a copy of what the VM runs, kept in step by hand: the VM is not under action control yet ([#196](https://github.com/sgort/ronl-business-api/issues/196)).

```
deployment/vm/operaton/
├── README.md                 # What is configured, the accounts, and the rollout runbook
├── prod/docker-compose.yml   # The engine as it runs on the VM
├── provision-accounts.sh     # Creates the service accounts and the read-only account
└── test/                     # A harness running the same engine and proxy locally
    ├── docker-compose.yml
    ├── Caddyfile
    ├── check-engine.sh       # 22 checks on the engine's permissions
    ├── check-allowlist.sh    # 57 checks on the proxy's public paths
    └── fixtures/             # One case process and one public decision
deployment/vm/caddy/
└── operaton-engine-rest.caddy  # The proxy rules for the engine's REST API
```

The engine's `.env` stays out of the repository through the `deployment/vm/**/.env` ignore rule.

---

## The engine

`prod/docker-compose.yml` names the image **`operaton/operaton:1.0.0`** — the version the VM runs, which a once-pulled `latest` turned out to be. Since v2026.11.2 it is pinned by digest as well — `operaton/operaton:1.0.0@sha256:74659f07…` — so a re-pull cannot move it. Upgrading it to the 2.x line the local stack uses is [#423](https://github.com/sgort/ronl-business-api/issues/423); Renovate's pull requests for 1.1.5 and 2.2.0 were closed in its favour. The engine stores its data in H2 on a volume, and `JAVA_OPTS` switches on three settings:

| Setting | Effect |
|---|---|
| `-Doperaton.bpm.run.auth.enabled=true` | The REST API answers `401` without credentials (basic auth) |
| `-Doperaton.bpm.authorization.enabled=true` | The engine checks each account's permissions |
| `-Doperaton.bpm.run.cors.enabled=false` | The engine sends no CORS headers; the proxy answers CORS for the public paths only |

The tenant check stays on, its default: decisions are deployed without a tenant, so a tenant-scoped process can still reach them.

---

## Accounts

`provision-accounts.sh` creates the accounts, idempotently: it adds only what is missing and never changes an existing password. It needs only POSIX `sh` and `curl`, and takes everything from the environment, so nothing secret or personal is in the file.

- **A service account per backend and tier**, in the engine's `operaton-admin` group. The RONL Business API and the Linked Data Explorer each call the engine as their own account.
- **Existing users** are added to `operaton-admin` by ID, given at run time.
- **`publicReader`**, a read-only account: `READ` on process, decision and decision-requirements definitions and on deployments, plus `CREATE_INSTANCE` on decision definitions, which is what evaluating a decision needs. It sees no cases and changes nothing.

Account IDs are camelCase because Operaton rejects dashes in them.

---

## What is public

The proxy rules in `operaton-engine-rest.caddy` decide what reaches the engine without credentials:

- **Reading the rules** — process, decision and decision-requirements definitions and their XML, deployments and their resources — and **evaluating a decision** are forwarded as `publicReader` when the request carries no credentials. Sub-resources that return instance data, such as statistics, are not public.
- **Every other request** is forwarded unchanged, so the engine answers `401` unless the caller sends its own credentials. A caller's own credentials are never replaced.
- **CORS** — `Access-Control-Allow-Origin: *`, without credentials — only on the public paths. The proxy removes any CORS header the engine sends, so a browser never sees the header twice.

See [Caddy](caddy.md#operaton) for how the rules are loaded.

---

## Integration with the Business API

The backend connects to the engine with:

```bash
OPERATON_BASE_URL=<the engine's engine-rest URL>
OPERATON_USERNAME=<the backend's service account>
OPERATON_PASSWORD=<its password>
OPERATON_TIMEOUT=30000
```

On ACC and PROD `validateConfig` refuses to start without `OPERATON_USERNAME` and `OPERATON_PASSWORD`, so a missing credential stops the deploy instead of failing later in the background. Every engine call carries them: `OperatonService` (`packages/backend/src/services/operaton.service.ts`), the external-task worker, and the assistant's Operaton tools. Every value the service places in an engine URL path goes through `engineSegment()` (`packages/backend/src/utils/engine-segment.ts`), which encodes it and refuses `.` and `..`, because the backend's account has administrative rights.

---

## Deploying BPMN/DMN process definitions

Deploying is not public. Process and decision bundles are deployed from the Linked Data Explorer, which calls the engine as its own service account, or by an operator with an `operaton-admin` account.

---

## Changing the engine

1. Make the change in `deployment/vm/operaton/` and prove it with the harness in `test/` (`check-engine.sh`, `check-allowlist.sh`), which runs the same engine version and proxy.
2. Apply it on the VM by hand, following the README's runbook.
3. Check from outside, without credentials, that case data answers `401` and the rules still answer.

Check the Operaton release notes before upgrading — BPMN/DMN deployment compatibility should be verified in the ACC environment first.
