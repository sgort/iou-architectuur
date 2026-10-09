---
component: RONL Business API
---

# eDOCS — Live Testing

This page tracks live testing of the `/v1/edocs/*` surface against a real
OpenText eDOCS DM server — what's been verified, what's broken, and why. For
the OAuth/Copilot Studio integration itself, see
[Copilot Studio — eDOCS](../copilot-studio-edocs.md). For the general endpoint
shapes, see [API Specification](../../reference/api-specification.md), under **Documents**.

!!! warning "The service account has restricted rights"
    The results below were captured against `infocenter-test.flevoland.nl`
    (library `sqldocuvitt`) as the eDOCS service account. The service account
    is `testuser001` ("TestUser001 (voor iou)"); it cannot delete documents,
    for example. Several "broken" rows below may be account-permission issues
    rather than integration bugs — each row links to the detail that explains
    which is which.

---

## Summary

| Request | Live-tested | Result |
| --- | :---: | --- |
| `GET /v1/edocs/status` | ✓ | Works — `reachable` and `authenticated` both confirmed |
| `GET /v1/edocs/workspaces` | ✓ | Works — `200`, list returned |
| `POST /v1/edocs/workspaces/ensure` — search branch | ✓ | Works — finds an existing workspace by `DOCNAME` filter |
| `POST /v1/edocs/workspaces/ensure` — create branch | ✓ | **Broken** — server-side `500`, see [Workspace create fails](#workspace-create-fails) |
| `POST /v1/edocs/documents` — standalone (no `workspaceId`) | ✓ | Works — see [Document upload fix](#document-upload-fix) |
| `POST /v1/edocs/documents` — workspace-ref (`workspaceId` set) | ✓ | **Broken** — two different errors tried, neither works, see [Workspace-ref upload](#workspace-ref-upload-still-broken) |
| `GET /v1/edocs/workspaces/:id/documents` | ✓ | Works (empty-list case) — see [Workspace-documents endpoint](#workspace-documents-endpoint-didnt-exist) — non-empty case not yet verified |
| `GET /v1/edocs/documents/:id/profile` | ✓ | Works — `200` |
| `GET /v1/edocs/documents/:id/versions` | ✓ | Works — see [Versions list parsing](#versions-list-parsing-was-wrong) |
| `GET /v1/edocs/documents/:id/versions/:version` | ✓ | Works — only with the literal value `0`, see [Download](#download-wrong-shape-and-wrong-version-id) |
| `DELETE /v1/edocs/documents/:id` | ✓ | **Blocked** — account lacks delete rights, see [Delete permission](#delete-blocked-by-account-permissions) |
| `DELETE /v1/edocs/workspaces/:id` | ✓ | Works — `200` |
| `POST /connect`, `GET /libraries` | ✓ | Underpin `healthCheck()` — reachable vs. authenticated, see below |

---

## Configuration

The variables `config.ts` reads for eDOCS (the full list, with `EDOCS_DEPARTMENT` and the AI assistant's eDOCS settings, is in [Environment Variables](../../reference/environment-variables.md#edocs)):

| Variable | Meaning | Default |
| --- | --- | --- |
| `EDOCS_STUB_MODE` | `false` to go live | `true` |
| `EDOCS_BASE_URL` | DM REST API **root** — not the login endpoint | _(empty)_ |
| `EDOCS_USER_ID` | service account user id (`testuser001`) | _(empty)_ |
| `EDOCS_PASSWORD` | service account password | _(empty)_ |
| `EDOCS_LIBRARY` | eDOCS library / docbase | `DOCUVITT` |
| `ENTRA_TENANT_ID` | Flevoland's Entra tenant, for refreshing a person's ID token | _(empty)_ |
| `ENTRA_CLIENT_ID` | the IOU-demonstrator app registration (the one Keycloak brokers) | _(empty)_ |
| `ENTRA_CLIENT_SECRET` | its client secret — the same value Keycloak's `entra-flevoland` holds | _(empty)_ |
| `EDOCS_ALLOW_SERVICE_FALLBACK` | a person without an Entra token may act as the service account, visibly | `false`; refused on `DEPLOYMENT_ENV=production` |
| `EDOCS_ALLOWED_CLIENTS` | machine clients (token `azp`) allowed on `/v1/edocs` | `edocs-mcp-client,copilot-studio-edocs,operaton-mcp-client` |

With `EDOCS_STUB_MODE=false` the backend **refuses to start** unless
`EDOCS_USER_ID`, `EDOCS_PASSWORD` and the three `ENTRA_*` settings are set.

!!! note "EDOCS_BASE_URL must be the API root"
    The client appends `connect`, `workspaces`, `documents`, and `libraries` to
    the base URL. Use `https://<host>:<port>/edocsapi/v1.0` — **not**
    `.../v1.0/connect`. A trailing `/connect` makes every call resolve to
    `.../connect/<endpoint>` and 404.

In stub mode (the default) every method on `EdocsService` returns realistic
fake data; the switch to live is a config change only, transparent to routes,
the BPMN worker, and the frontend — see
[`edocs.service.ts`](https://github.com/sgort/ronl-business-api/blob/acc/packages/backend/src/services/edocs.service.ts).
In stub mode a person's call is served by the stub service client as well
(`actingAs: "service"`); nobody talks to eDOCS.

---

## People and the service account

Two identities reach eDOCS:

- **A person** — a caseworker or admin signed in with the
  **Inloggen met uw Flevoland-account** button — opens an eDOCS session **as
  themselves**. The backend reads the Entra ID token Keycloak stored at their
  login from Keycloak's broker endpoint, with the person's own Keycloak token,
  and sends it in the `X-DM-AUTH` header on `/connect`. No password is
  involved; eDOCS enforces and records that person's rights. When the stored
  ID token has expired, the backend refreshes it at Entra itself with the
  `ENTRA_*` settings.
- **The service account** (`EDOCS_USER_ID`, `testuser001`) serves machine
  clients on `EDOCS_ALLOWED_CLIENTS` and background archiving (the Operaton
  worker and ValidSign). It records the employee who caused a write at the end
  of the document title, as "— namens <naam> (<e-mail>)".

The backend keeps one eDOCS session per identity. For a person, a `401` from
eDOCS fetches a fresh ID token and retries once; a `403` is eDOCS refusing
that person, not an expired session, and is not retried.

Every `/v1/edocs` data response says which one acted, in a top-level
`actingAs` member: `"user"` or `"service"`. `GET /v1/edocs/status` adds, for a
person, `data.user`: whether an eDOCS session can be opened as them
(`available`, `authenticated`, their eDOCS `edocsUserId`, or a `problem` code
such as `EDOCS_USER_TOKEN_UNAVAILABLE`, `STUB_MODE` or
`EDOCS_USER_LOOKUP_FAILED`). Refusals are problem details, with the code in
the `code` member:

| Code | Status | Meaning |
| --- | --- | --- |
| `EDOCS_USER_TOKEN_UNAVAILABLE` | 403 | The person has no stored Entra token — a Keycloak account, or signed in before Keycloak stored tokens. Sign in with the Flevoland button |
| `EDOCS_REAUTH_REQUIRED` | 401 | Entra no longer refreshes the person's session — sign in again |
| `EDOCS_ACCESS_DENIED` | 403 | eDOCS refused the person: no rights on the item, or not a user of the library / account disabled (`0X8004020C`) |
| `EDOCS_CLIENT_NOT_ALLOWED` | 403 | A machine client not on `EDOCS_ALLOWED_CLIENTS` |
| `FORBIDDEN` | 403 | A person without the `caseworker` or `admin` role |

A person is never silently turned into the service account. Only with
`EDOCS_ALLOW_SERVICE_FALLBACK=true` — refused on production — does a person
without a stored Entra token act as the service account, visibly
(`actingAs: "service"`) and with an audit entry. When Keycloak or Entra cannot
be asked at all (an outage, not a fact about the person), the request fails
rather than falling back.

**Keycloak prerequisite**, per environment: run
`scripts/keycloak-add-entra-idp.sh` (see [Entra ID](../deployment/entra-id.md)).
It makes `entra-flevoland` store the tokens (`offline_access`), adds the
`broker` client's `read-token` role to `default-roles-ronl`, and puts the
broker roles in `ronl-business-api`'s access token (`broker-roles` mapper).
Afterwards **each person signs in once more** for Keycloak to hold their
tokens. Until then they get `EDOCS_USER_TOKEN_UNAVAILABLE` — not the service
account — unless the fallback is on.

---

## Running the live smoke test

```bash
# Local backend → live eDOCS (default target — CLIENT_SECRET auto-loads from
# packages/backend/.env.<NODE_ENV>):
bash scripts/test-edocs-live.sh
#   1b checks a Keycloak person without an Entra token is refused;
#   1c (PERSON_TOKEN=<a Flevoland-signed-in person's Keycloak token>) checks
#   eDOCS knows that person and answers actingAs "user"

# The same, with the person's token taken from the clipboard (copy any /v1
# request as cURL in DevTools first). Never prints the token; stops on an
# expired one or one from another environment:
bash scripts/test-edocs-person.sh live          # test-edocs-live.sh, 1c included
bash scripts/test-edocs-person.sh smoke acc     # test-smoke-live.sh, Tier 2c included
bash scripts/test-edocs-person.sh diag acc      # only: broker endpoint + /v1/edocs as the person

# Against ACC — always needs an explicit ACC CLIENT_SECRET:
TARGET=acc CLIENT_SECRET=<acc-m2m-secret> bash scripts/test-edocs-live.sh

# Fast reach/login check only — no Keycloak, no running backend:
cd packages/backend && npm run edocs:health
```

`test-edocs-live.sh` runs, in order: a liveness gate and an in-process
pre-flight (is eDOCS reachable, can the service account log in) → token →
status gate (must be live, not stub) → **1b**, a Keycloak person without an
Entra token (`test-caseworker-flevoland` by default), who must be refused with
`EDOCS_USER_TOKEN_UNAVAILABLE` (or, with `EXPECT_FALLBACK=true`, act as the
service) → **1c**, when `PERSON_TOKEN` is set, a person signed in with the
Flevoland button: eDOCS must know them, answer `actingAs: "user"`, and record
them as `AUTHOR_ID` of a document they upload → list workspaces (read-only) →
upload a document standalone → document profile → document versions →
download + verify the round-trip (sha256). Locally, with
`PYTHON_MCP_POC_ENABLED=true`, a second route repeats the reads and an upload
through the Python MCP proof of concept.

The script creates and deletes no workspaces, and does not clean up the
service account's documents: that account cannot delete them (see
[Delete blocked](#delete-blocked-by-account-permissions)), so every run
leaves its uploaded documents behind, named with a timestamped
`PROJECT_NUMBER`. Section 1c tries to delete the person's own test document
and, when eDOCS refuses, says to remove it in InfoCenter.

`test-edocs-person.sh` reads the token from the clipboard: sign in with
**Inloggen met uw Flevoland-account**, then in DevTools copy any request to
the API's `/v1` as cURL, and run the script within the token's 15-minute
lifetime. On ACC, which cannot reach the on-premises eDOCS and runs in stub
mode, `diag` is the useful mode: it shows whether Keycloak's broker endpoint
holds the person's Entra token.

The workspace-**create** path is broken (see below); a workspace needed by
hand-run calls is created once in InfoCenter, and upload does not depend on a
workspace at all.

---

## Details

### Workspace create fails

`POST /v1/edocs/workspaces/ensure` — its **create** branch, specifically.
Workspace **search** (`GET workspaces?filter=...`) works fine; workspace
**create** (`POST workspaces`) reliably returns:

```
HTTP 500, Content-Length: 0, Content-Type: application/json
(empty body)
```

Reproduced directly against the DM server (bypassing the backend) with two
different project numbers — not a collision, not a payload validation issue.
Unlike a malformed-request rejection (this server returns those as a
structured `400` with an `ERROR.message`/`rapi_details` body), a bare `500`
with no body looks like an unhandled exception **on the server side**. Needs
investigation by whoever administers the DM server, not a client-side fix.

**Workaround**: create the workspace once by hand in InfoCenter, then point
`PROJECT_NUMBER` at its name — the search branch finds it and `ensureWorkspace()`
never calls the broken create path.

A related, now-fixed bug surfaced while testing this workaround: the search
branch's *parsing* crashed on every real match (`existing.data.DOCNAME` — but
a real match's fields are flat, `existing.DOCNAME`, no nested `data`). Fixed.
The still-unverified create-response parsing was given a matching flat-shape
fallback for whenever the `500` is resolved.

### Document upload fix

`POST /v1/edocs/documents` was fixed after live testing (via a standalone
upload, bypassing the broken workspace create above) showed three things the
original implementation got wrong:

1. **Real multipart/form-data is required.** The DM server rejects a JSON body
   with an inline base64 `file` field (`400: "No JSON data for document copy
   request"` — it's interpreted as a *copy* operation needing a source that
   was never supplied). The service now sends an actual multipart body (`data`
   part as JSON text, `file` part as raw bytes).
2. **`APP_ID` must be `"DEFAULT"`.** The previous default, `"INFRA"`, is
   rejected as an unrecognized linked application.
3. **`UV_AFD_NAAM`** ("Behandelgroep" in InfoCenter) is a **mandatory**
   profile field with no default — it's now a required `department` field on
   the upload payload, same as the document name.

A validation failure on this endpoint comes back as **`HTTP 206`** (not a
4xx/5xx) with an `error_list` in the body — a naive `axios` caller treats 206
as success, so the service explicitly checks `error_list` and throws if
non-empty.

Verified live with a standalone multipart upload (`APP_ID: "DEFAULT"`,
`UV_AFD_NAAM: "IVR"`) → `HTTP 200`, document created and visible in
InfoCenter. **Given the workspace-ref path below doesn't work, standalone
upload (`workspaceId: null`) is now the primary, only-proven-working path.**

### Workspace-ref upload still broken

Once a real workspace was reachable, the **workspace-ref** upload path
(passing a `workspaceId`) was tried and failed — twice, two different errors:

1. Without a form name: `HTTP 206`, `error_list` message *"Kan klasse-id niet
   vinden voor dit objecttype... :%OBJECT_TYPE_ID = DEFAULT"* ("cannot find a
   class-id for this object type").
2. With the form that worked for standalone upload (`D_INTERN_NIEUW`) added
   alongside the workspace ref: `HTTP 206`, `error_list` code `15`, no message
   text.

Neither combination succeeds when a workspace `ref` is present — suggests
items added *into* a workspace may need a different form/profile/object-type
than a top-level document create. Needs eDOCS admin/vendor input on what's
valid for workspace-contained documents.

The workspace-ref path is kept in the code (not removed) for when this is
resolved, but does not currently work. The BPMN worker
(`externalTaskWorker.service.ts`, `rip-edocs-document` topic) still uses this
path — it's blocked until this is fixed. In practice the preceding
`rip-edocs-workspace` task already fails first for any project needing a
genuinely new workspace, since it hits the same `500` above — the process
never reaches the document task in that case.

### Workspace-documents endpoint didn't exist

`GET /v1/edocs/workspaces/:id/documents` failed with `400: "Unknown component
\"documents\""` once a real workspace existed to test against. There is no
such sub-resource in the API — workspace content is retrieved from the
workspace resource itself, `GET /workspaces/{id}`. Fixed, along with the same
flat-list-item parsing fix as the workspace-search bug above.

Only the empty-list case has been confirmed live (no document has
successfully landed *inside* a workspace, since the ref-upload path above
doesn't work) — the non-empty shape is inferred from the same confirmed flat
pattern used elsewhere, not yet directly observed.

### Versions list parsing was wrong

`GET /v1/edocs/documents/:id/versions` returned `200` with an empty list on
the first end-to-end run — this wasn't a data question, the parsing was wrong.
A real response (confirmed via a manual call against a document with 2
versions) has **flat** list items with **no `id` field at all** and no nested
`.data`: `{ VERSION_ID: "4171013", VERSION: "1", DOCNUMBER, ... }`. `VERSION`
is the human-facing label (`"1"`, `"2"`); `VERSION_ID` looked like the obvious
"real identifier" — **this turned out to be wrong**, see the download section
below. Fixed.

Whether a single-version document returns an empty list or a one-item list is
still unconfirmed.

### Download — wrong shape and wrong version id

`GET /v1/edocs/documents/:id/versions/:version` needed two fixes:

- **Neither `VERSION` nor `VERSION_ID` from the versions list works** as the
  `:version` path segment — both throw `400`: *"Kan documentversie niet vinden
  met opgegeven versie-id"*. The value that actually works, found by trial:
  the literal string **`"0"`** — apparently a "current version" sentinel,
  unrelated to the versions list entirely.
- **The response is raw file bytes, not JSON.** Confirmed via `curl`, which
  printed the exact uploaded PDF content directly — no envelope, no base64
  field. The service now requests `responseType: 'arraybuffer'` (the default
  JSON/string decoding would corrupt real binary content) and base64-encodes
  the raw bytes.

Verified live end-to-end: uploaded a PDF, downloaded it back via
`.../versions/0`, bytes matched the upload exactly (marker text included) —
the first fully round-tripped live confirmation of upload → download.

### Delete blocked by account permissions

`DELETE /v1/edocs/documents/:id` failed with `400`, not a server error:
*"U bent niet gemachtigd de gevraagde bewerking uit te voeren"* ("not
authorized to perform the requested operation"). The service account has no
delete-document right in the live DM server (consistent with the
"Restricted" permission shown in InfoCenter's Create Profile dialog); through
the backend the refusal surfaces as `502 EDOCS_ERROR`.

`DELETE /v1/edocs/workspaces/:id`, by contrast, succeeded (`200`) with the
same account — so the restriction is specific to document delete, not a
blanket delete restriction.

### Possible workspace-search filter issue (unconfirmed)

In one run, `PROJECT_NUMBER` was left at its default (a fresh
`SMOKE-<timestamp>`, not any workspace used before), yet
`ensureWorkspace()`'s search still returned `created: false` for an unrelated,
differently-named workspace. A `DOCNAME like 'SMOKE-<timestamp>%'` filter
should not match a `DOCNAME` that doesn't start with that prefix. Not yet
root-caused — could be the DM server not honoring/parsing the `filter` query
param, or something in how the client builds/encodes it. Worth checking
before relying on `ensureWorkspace()`'s "found existing" result for anything
that matters.

---

## Reading a status failure

```json
{
  "status": 400,
  "upstream": {
    "ERROR": {
      "message": "The referenced account is currently locked out …",
      "rapi_code": "0X80070775"
    }
  }
}
```

| Symptom (`/status`) | Likely cause |
| --- | --- |
| `stubMode: true` | `EDOCS_STUB_MODE` still `true`, or backend not restarted |
| `reachable: false` | Wrong `EDOCS_BASE_URL`, network/TLS, or server down |
| `reachable: true`, `authenticated: false` | Login rejected — bad credentials, or **account locked out** |
| `data.user.available: false`, `problem: EDOCS_USER_TOKEN_UNAVAILABLE` | The person signed in with a Keycloak account, or before Keycloak stored tokens — sign in with the Flevoland button |
| `data.user.problem: EDOCS_USER_LOOKUP_FAILED` | Keycloak's broker endpoint or Entra could not be asked; `data.user.error` has the reason |

!!! danger "Lockout risk"
    Repeated failed logins can lock the service account. `healthCheck()`
    throttles the login probe (reuses a live session; caches a failed probe
    for 30s) so `/status` polling alone cannot lock the account — but a wrong
    password in config will still lock it via real login attempts. Verify the
    password before retrying, and have an eDOCS admin unlock the account after
    a lockout.

    The service account is the only password login: a person connects with
    their Entra ID token and cannot be locked out this way. A failed
    `data.user` probe for a person is likewise remembered for 30 s, per
    person, so a polling dashboard does not reconnect on every load while that
    person cannot connect.

---

## Rollback

Set `EDOCS_STUB_MODE=true` and restart the backend. No code change, no
deploy — every caller transparently returns stub data again.
