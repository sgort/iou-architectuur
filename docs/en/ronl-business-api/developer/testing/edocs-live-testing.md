# eDOCS — Live Testing

This page tracks live testing of the `/v1/edocs/*` surface against a real
OpenText eDOCS DM server — what's been verified, what's broken, and why. For
the OAuth/Copilot Studio integration itself, see
[Copilot Studio — eDOCS](../copilot-studio-edocs.md). For the general endpoint
shapes, see [API Endpoints](../../reference/api-endpoints.md#edocs).

!!! warning "Test account has restricted rights"
    All results below were captured against `infocenter-test.flevoland.nl`
    (library `sqldocuvitt`) using a service account (`IOUTEST`) with limited
    permissions — it cannot delete documents, for example. A replacement test
    account with full rights is planned. Several "broken" rows below may turn
    out to be account-permission issues rather than integration bugs once
    retested with that account — each row links to the detail that explains
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

Five environment variables, read by `config.ts`:

| Variable | Meaning | Default |
| --- | --- | --- |
| `EDOCS_STUB_MODE` | `false` to go live | `true` |
| `EDOCS_BASE_URL` | DM REST API **root** — not the login endpoint | _(empty)_ |
| `EDOCS_USER_ID` | service account user id | _(empty)_ |
| `EDOCS_PASSWORD` | service account password | _(empty)_ |
| `EDOCS_LIBRARY` | eDOCS library / docbase | `DOCUVITT` |

!!! note "EDOCS_BASE_URL must be the API root"
    The client appends `connect`, `workspaces`, `documents`, and `libraries` to
    the base URL. Use `https://<host>:<port>/edocsapi/v1.0` — **not**
    `.../v1.0/connect`. A trailing `/connect` makes every call resolve to
    `.../connect/<endpoint>` and 404.

In stub mode (the default) every method on `EdocsService` returns realistic
fake data; the switch to live is a config change only, transparent to routes,
the BPMN worker, and the frontend — see
[`edocs.service.ts`](https://github.com/sgort/ronl-business-api/blob/acc/packages/backend/src/services/edocs.service.ts).

---

## Running the live smoke test

```bash
# Local backend → live eDOCS (default target — CLIENT_SECRET auto-loads from
# packages/backend/.env.<NODE_ENV>):
bash scripts/test-edocs-live.sh

# Against ACC — always needs an explicit ACC CLIENT_SECRET:
TARGET=acc CLIENT_SECRET=<acc-m2m-secret> bash scripts/test-edocs-live.sh

# Fast reach/login check only — no Keycloak, no running backend:
cd packages/backend && npm run edocs:health
```

The script runs, in order: status gate → list workspaces → ensure workspace →
upload a document standalone → list workspace content → document profile →
document versions → download + verify round-trip (sha256) → pause for a
`y/N` confirmation before deleting anything it created. Non-interactive runs
skip cleanup by default (`AUTO_CONFIRM_CLEANUP=1` to delete without
prompting).

Because the workspace-**create** path is broken (see below), point
`PROJECT_NUMBER` at a workspace that already exists (created by hand in
InfoCenter) to skip past it — the search branch works, and everything after
it (including upload, which no longer depends on a workspace at all) runs
regardless.

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
authorized to perform the requested operation"). The `IOUTEST` service
account likely lacks delete rights (consistent with the "Restricted"
permission shown in InfoCenter's Create Profile dialog) — this is the
leading candidate to re-test once the full-rights replacement account is
available.

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

!!! danger "Lockout risk"
    Repeated failed logins can lock the service account. `healthCheck()`
    throttles the login probe (reuses a live session; caches a failed probe
    for 30s) so `/status` polling alone cannot lock the account — but a wrong
    password in config will still lock it via real login attempts. Verify the
    password before retrying, and have an eDOCS admin unlock the account after
    a lockout.

---

## Rollback

Set `EDOCS_STUB_MODE=true` and restart the backend. No code change, no
deploy — every caller transparently returns stub data again.
