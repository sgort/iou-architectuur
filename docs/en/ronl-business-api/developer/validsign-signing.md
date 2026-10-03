---
component: RONL Business API
---

# ValidSign signing

A user signs the document of a BPMN user task without leaving the board they work on: a project leader signs a RIP phase-exit approval on the Infra-board, a gemachtigde ondertekenaar signs a besluit in the caseworker task inbox. The signed PDF and its evidence summary are archived in eDOCS, and the Operaton user task completes only once the signature has landed.

The feature is **opt-in from the process model**: it activates on a user task that carries `ronl:signatureRef`, and returns nothing for a task without it — which is every ordinary task.

!!! info "Verified against source"
    Read on `main` at `0625d48`, 3 October 2026 (v2026.10.0).

!!! success "Acceptance signs for real"
    Acceptance has been **live since 14 September 2026** — a real ceremony
    signed, callbacks accepted, and the evidence email received. The account
    below of what the callback accepts is written from that signing, not from
    the specification.

---

## How it activates

The Linked Data Explorer's [R2.1 bundle](../../linked-data-explorer/features/rip-phase1-bundle.md#the-phase-exit-approval-is-signed) sets one attribute on the task that closes the phase:

```xml
<bpmn:userTask id="Task_AccorderenProjectplan4"
               name="Accorderen Projectplan 4. Uitgangspunten VO-fase"
               ronl:signatureRef="rip-pdp">
```

*Besluitvorming onder gedelegeerde bevoegdheid* does the same on the task that signs the besluit:

```xml
<bpmn:userTask id="Task_Onderteken"
               name="Onderteken het besluit"
               camunda:formRef="besluit-gb-ondertekenen"
               ronl:signatureRef="besluit-gb-besluit"
               camunda:candidateGroups="besluit-ondertekenaar">
```

The backend resolves that attribute from a named BPMN user task to the document template deployed alongside the process. Where it is present, the task view renders the signing panel in place of the task's ordinary form — **every task view**: the Infra-board's project detail and the caseworker task inbox both ask `useTaskSignature` (`packages/frontend/src/components/signing/`) whether a task signs, and both render the same `SigningPanel`. Until the answer is in, the view shows *Ondertekening controleren…* rather than either the form or the panel, because the form would let a signature task be approved without signing. A failed lookup falls back to the form.

That is the whole switch. A single attribute in a model the LDE deploys turns on a feature implemented entirely here.

---

## Configuring a process for signing

Any process signs a task through ValidSign without code in the Business API:

1. **Give the user task `ronl:signatureRef="<document id>"`.** The LDE bundles that `.document` into the deployment.
2. **Give the document a `signOff` zone.** ValidSign's signature field is anchored at its first line; without it there is nothing to sign.
3. **Keep a `camunda:formRef` on the task as the fallback.** It is shown when the signing spec cannot be fetched, and it must set `approvalStatus` (`approved` / `rejected`) as signing does.
4. **Branch on `approvalStatus` after the task.** Signing completes the task server-side, writing `approvalStatus` and the `validsign*` variables.

**Signing state is per task.** The `validsign*` variables are process variables, so they outlive the task that created them. The package route therefore also records `validsignTaskId`, and a task reads another task's `validsign*` variables as status `none`. A process that loops back to a new signing task after a declined signature starts afresh there, while a second package for the **same** task is still refused with `409 VALIDSIGN_PACKAGE_EXISTS`. A package without a recorded task id is taken at face value.

**Archive names come from the template and the case.** The package route records the template's id and name (`validsignTemplateId`, `validsignTemplateName`), and the completion archives the signed PDF as `<templateId>-<businessKey>-signed.pdf` and the evidence summary as `<templateId>-<businessKey>-evidence.pdf`, titled `<businessKey> — <template name> (ondertekend) — getekend document` and `… — bewijsoverzicht`. A package without a recorded template falls back to `ondertekend-document` and *Ondertekend document*, and an instance without a business key to the package id. Both documents are uploaded to eDOCS as standalone documents under the department `EDOCS_DEPARTMENT`, not into a workspace.

---

## The three locks on live signing

The ValidSign licence is **production-only — there is no sandbox tenant, and the API key is account-wide.** A misconfigured environment must therefore not be able to fire a real signature request. `assertLiveAllowed()` checks three conditions before anything reaches the network:

```
1. stub mode is off          VALIDSIGN_STUB_MODE=false
2. an API key is present     VALIDSIGN_API_KEY
3. the tier is allowlisted   DEPLOYMENT_ENV ∈ VALIDSIGN_LIVE_TIERS
```

!!! danger "`VALIDSIGN_LIVE_TIERS` is empty by default"
    No tier may create real packages until one is explicitly named. This is an
    **allowlist, not a hardcoded exclusion of acceptance** — adding `acceptance`
    makes ACC sign for real exactly as production does. That is a deliberate
    choice: the environment that signs is a configuration decision, not
    something the code decides on your behalf.

    A blocked attempt throws `VALIDSIGN_LIVE_BLOCKED` naming the offending
    `DEPLOYMENT_ENV`; a live-mode start with no key throws
    `VALIDSIGN_LIVE_MISCONFIGURED`.

---

## The routes, across two routers

| Route | Router | Auth |
|---|---|---|
| `GET /v1/validsign/task/:taskId/spec` | main | JWT + tenant |
| `POST /v1/validsign/task/:taskId/package` | main | JWT + tenant |
| `GET /v1/validsign/task/:taskId/status` | main | JWT + tenant |
| `POST /v1/validsign/callback` | **pre-auth** | shared key, in any of five forms |
| `GET /v1/validsign/stub/ceremony/:packageId` | **pre-auth** | capability URL (stub only; `404` in live mode) |
| `POST /v1/validsign/stub/ceremony/:packageId/sign` | **pre-auth** | capability URL (stub only; `404` in live mode) |
| `GET /v1/validsign/ceremony/complete` | **pre-auth** | none |

The three task routes check the tenant before anything is looked up, sent or written: a task belongs to the organisation named by its process instance's `municipality` variable. The other four sit **outside** JWT middleware, and none is an oversight:

- **The callback** is posted by ValidSign's cloud, which holds no Keycloak token. It is verified against a shared key instead — see [What the callback accepts](#what-the-callback-accepts).
- **The stub ceremony** loads in an iframe, and an iframe cannot carry a bearer token.
- **The ceremony landing page** is a static confirmation the backend can serve after a ceremony. It is not the hand-over target — that is the Infra-board — and reveals nothing.

### The ceremony URL is a capability

Stub package ids were originally **sequential**. On any internet-reachable deployment, someone could enumerate a few values and approve a phase-exit that another person was in the middle of signing. They are now random UUIDs, which makes the URL itself the credential.

!!! warning "Do not run stub mode on acceptance from any commit before this fix"
    The change landed in v2026.08.36. Earlier commits carry the guessable ids.

The callback and the two stub ceremony routes share a rate limiter — 60 requests per minute — keyed on the **client IP**, not the secret header. The header is attacker-controlled, so keying on it would hand out a fresh budget per request. Keying on IP also means ValidSign's callbacks and a browser's ceremony traffic never land in the same bucket, so ceremony traffic cannot exhaust the budget the callbacks rely on.

---

## Completion: one path, two racing callers

A signature completes through a single idempotent path, reached from either direction:

```
ValidSign completes  ─┬─►  POST /callback   ─┐
                      │                       ├─►  archive signed PDF + evidence
   poller sweep       ─┘                      │    to eDOCS  →  complete the
                                              └─►  Operaton user task
```

**The poller is not belt-and-braces.** ValidSign's cloud cannot reach a developer's localhost, so during local work the callback never arrives at all. It sweeps process instances awaiting a signature on `VALIDSIGN_POLL_INTERVAL_MS` (default 15s) and drives completion through the same path the webhook uses.

### What the callback accepts

The route is registered with ValidSign under security type **Bearer token**.
What ValidSign actually sends is `Authorization: Basic <key>`, with the key raw
rather than base64-encoded. Both are accepted, along with three further forms,
all compared in constant time against `VALIDSIGN_CALLBACK_SECRET`:

| Credential | Logged as |
|---|---|
| `Authorization: Basic <key>` | `basic-raw` — **what ValidSign sends** |
| `Authorization: Basic base64(<key>)` | `basic-base64` |
| `Authorization: Basic base64(name:key)` | `basic-base64-pair` |
| `Authorization: Bearer <key>` | `bearer` |
| `x-validsign-secret: <key>` | `x-validsign-secret` |

The scheme is matched case-insensitively. A value that merely *contains* the
key, a wrong key in any form, and any other scheme such as `Digest` are all
still `401`.

`"ValidSign callback received"` records **which** form matched, so the check can
be narrowed to the one ValidSign genuinely uses once that has been observed long
enough. A rejection logs which credential forms arrived and never their values:
header names and the `Authorization` scheme only, with a scheme-less value
logged as `(no scheme)` because it could be the key itself. An accepted callback
always answers `200`, including for an event it does nothing with.

!!! note "This was found because a rejection says enough to diagnose it"
    Until v2026.09.8 the route read only `x-validsign-secret`, so **every real
    callback was a `401`** — invisibly, because the poller completes the
    signature anyway and the process looks healthy. The first live acceptance
    signing rejected all six callbacks for package `a2beacfa` and logged
    `authorization:Basic`; the poller finished seven seconds later. That one log
    line is what identified the scheme, and it is why the log names the form
    rather than the value.

    The tell, if this ever regresses: a completion with **no matching callback
    log line** means the webhook never landed and the poller did the work.
    Nothing is lost when a callback fails — signing still works, about fifteen
    seconds slower.

---

## The signer's identity comes from the token

Package creation takes the signer's name and email entirely from the caller's Keycloak token. A real token carried **no email claim and no name claim at all**, so creation would have refused for every user — working exactly as designed, and useless.

Three protocol mappers are required on the client:

| Mapper | Claim |
|---|---|
| `email` | `email` |
| `given_name` | `given_name` |
| `family_name` | `family_name` |

`scripts/keycloak-add-token-claim-mappers.sh` adds them. It talks only to the Admin REST protocol-mappers endpoint — redirect URIs, web origins and the client secret appear in no request it builds — and is idempotent, so re-running reads state rather than changing it.

!!! note "Why not a realm import"
    A partial realm import cannot do this safely: `SKIP` policy skips an
    existing client entirely, and `OVERWRITE` replaces the whole client
    definition. The script was untracked until v2026.08.36 — a file that changes
    shared infrastructure for every environment is a worse candidate for
    privacy, not a better one.

---

## Documents: one representation, two renderings

A template deployed alongside the BPMN, plus the instance's process variables, is turned into a small **intermediate representation**. Markdown and PDF are emitted from it separately, so the archived human-readable copy and the signed artifact cannot drift apart.

`pdfkit` was chosen over `pdf-lib` because this generates a document from scratch and needs real text wrapping; `pdf-lib` is built for editing existing PDFs.

`rip-pdp` renders from its deployed template rather than the hardcoded switch the worker previously used — that switch restated, as TypeScript string literals, content the deployed templates already define. Only `rip-pdp` migrated: it is the document the signature touches, and converting the other two would have altered documents the feature does not need to alter.

!!! bug "The seal used to land on the body text"
    ValidSign places fields in **96-DPI pixels** while the PDF is authored in
    **72-DPI points**, so every coordinate and size arrived at three-quarter
    scale and the seal covered the body instead of the signature block.

---

## What live testing changed

Six claims in the design proved wrong once the feature ran against production ValidSign, live eDOCS and a real browser. They are worth recording, because each is the kind of thing a stub cannot surface:

| Symptom | Cause |
|---|---|
| The signing iframe showed the app's own landing page | In stub mode the backend returns a **relative** path, which the browser resolved against the board's origin rather than the API's |
| The browser refused to render the ceremony at all | `helmet`'s global defaults set `X-Frame-Options` and a `frame-ancestors` policy, and the board is a different origin from the API |
| A successful signature looked like a stalled one | The panel polled status but could never observe completion |
| The first real signature archived nothing | Status came back failed **and** the signed PDF never reached eDOCS — two separate defects |
| Archived documents would not open | The stub emitted 27-byte strings beginning with a PDF header; they uploaded perfectly and were unopenable |
| A second signature request could reach a real inbox | Package creation had no guard, so a second call put a second request in a person's inbox — which cannot be recalled — and left the process holding one of them |

A live signature request costs something against the licence, so the end-to-end guard now **refuses before a package is requested**, not after. It previously checked the ceremony URL, which only exists once the package has been created — stopping the signature but not the request.

---

## Testing it without filling twelve forms

Reaching the signature meant working an R2.1 instance through eleven user tasks by hand to get to the twelfth. A script now drives the process to the approval task in seconds, through the backend's own start endpoint rather than around it.

The panel's own tests mock the API module wholesale, so the three signing methods in the frontend client — and every one of their catch blocks — ran in no test at all. Those catch blocks are what turn a transport failure into something the panel can show a person, which makes the gap worse than the percentage suggested. They are covered directly now.

See [Testing](testing/overview.md) for the measured suite figures.

---

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `VALIDSIGN_BASE_URL` | `https://my.validsign.eu/api` | Platform endpoint |
| `VALIDSIGN_API_KEY` | *(empty)* | Account-wide; required in live mode |
| `VALIDSIGN_SENDER_EMAIL` | *(empty)* | Package sender |
| `VALIDSIGN_STUB_MODE` | `true` | Stub unless explicitly disabled |
| `VALIDSIGN_CALLBACK_SECRET` | *(empty)* | Verifies the webhook. Must equal the callback key **registered with ValidSign**, and is matched against all five credential forms above |
| `VALIDSIGN_LIVE_TIERS` | *(empty)* | Allowlist of tiers permitted to sign for real |
| `VALIDSIGN_POLL_INTERVAL_MS` | `15000` | Poller sweep interval |

---

## Related

- [RIP R2.1 Bundle](../../linked-data-explorer/features/rip-phase1-bundle.md) — where `ronl:signatureRef` is set
- [Infra-board](../user-guide/infra-board.md) and [Caseworker](../user-guide/caseworker.md) — the boards the panel appears on
- [Frontend Development](frontend-development.md) — how a task view chooses between the form and the panel
- [Security & Compliance](../features/security-compliance.md) — the wider posture
- [Testing](testing/overview.md) — measured suite figures
