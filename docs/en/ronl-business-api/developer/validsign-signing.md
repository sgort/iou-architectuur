---
component: RONL Business API
---

# ValidSign phase-approval signing

A project leader signs a RIP phase-exit approval without leaving the Infra-board. The signed PDF and its evidence summary are archived into the project's eDOCS workspace, and the Operaton user task completes only once the signature has landed.

The feature is **opt-in from the process model**: it activates on a user task that carries `ronl:signatureRef`, and returns nothing for a task without it — which is every ordinary task.

!!! info "Verified against source"
    Measured and read on `acc` at `15dfbf9`, 30 August 2026 (v2026.08.36).

---

## How it activates

The Linked Data Explorer's [R2.1 bundle](../../linked-data-explorer/features/rip-phase1-bundle.md#the-phase-exit-approval-is-signed) sets one attribute on the task that closes the phase:

```xml
<bpmn:userTask id="Task_AccorderenProjectplan4"
               name="Accorderen Projectplan 4. Uitgangspunten VO-fase"
               ronl:signatureRef="rip-pdp">
```

The backend resolves that attribute from a named BPMN user task to the document template deployed alongside the process. Where it is present, the Infra-board renders the signing panel in place of the task's ordinary form.

That is the whole switch. A single attribute in a model the LDE deploys turns on a feature implemented entirely here.

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

## The five routes, across two routers

| Route | Router | Auth |
|---|---|---|
| `GET /v1/validsign/task/:taskId/spec` | main | JWT |
| `POST /v1/validsign/task/:taskId/package` | main | JWT |
| `GET /v1/validsign/task/:taskId/status` | main | JWT |
| `POST /v1/validsign/callback` | **pre-auth** | shared secret |
| `GET`+`POST /v1/validsign/stub/ceremony/:packageId` | **pre-auth** | capability URL (stub only) |

Two of the five sit **outside** JWT middleware, and neither is an oversight:

- **The callback** is posted by ValidSign's cloud, which has no bearer token. It is verified by a shared secret header instead.
- **The stub ceremony** loads in an iframe, and an iframe cannot carry a bearer token.

### The ceremony URL is a capability

Stub package ids were originally **sequential**. On any internet-reachable deployment, someone could enumerate a few values and approve a phase-exit that another person was in the middle of signing. They are now random UUIDs, which makes the URL itself the credential.

!!! warning "Do not run stub mode on acceptance from any commit before this fix"
    The change landed in v2026.08.36. Earlier commits carry the guessable ids.

Both pre-auth routes share a rate limiter — 60 requests per minute — keyed on the **client IP**, not the secret header. The header is attacker-controlled, so keying on it would hand out a fresh budget per request. Keying on IP also means ValidSign's callbacks and a browser's ceremony traffic never land in the same bucket, so ceremony traffic cannot exhaust the budget the callbacks rely on.

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

!!! warning "The callback header name is not confirmed with ValidSign"
    The route expects **`x-validsign-secret`**. OneSpan-derived platforms — and
    ValidSign is the EU-branded OneSpan Sign — conventionally use a different
    header. If it is the latter, **every callback 401s silently**, because the
    poller completes the task anyway and the process looks healthy.

    The tell: a completion with no matching callback log line means the webhook
    never landed and the poller did the work. Worth checking before assuming the
    webhook is wired.

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
| `VALIDSIGN_CALLBACK_SECRET` | *(empty)* | Verifies the webhook |
| `VALIDSIGN_LIVE_TIERS` | *(empty)* | Allowlist of tiers permitted to sign for real |
| `VALIDSIGN_POLL_INTERVAL_MS` | `15000` | Poller sweep interval |

---

## Related

- [RIP R2.1 Bundle](../../linked-data-explorer/features/rip-phase1-bundle.md) — where `ronl:signatureRef` is set
- [Infra-board](../user-guide/infra-board.md) — the board the panel appears on
- [Security & Compliance](../features/security-compliance.md) — the wider posture
- [Testing](testing/overview.md) — measured suite figures
