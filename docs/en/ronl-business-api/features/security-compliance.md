---
component: RONL Business API
---

# Security & Compliance

Security is enforced at several layers: transport, request handling, identity, and — after a request completes — an audit record of what happened. None of these depend on which process, decision, or form a given request touches; they apply to every request the same way.

---

## Transport

Traffic to the platform's own services is encrypted end to end. TLS certificates are provisioned and renewed automatically for the components behind the reverse proxy, and the managed hosting environment for the API itself handles its own certificate lifecycle.

---

## Request-level protections

Every response carries a Content Security Policy restricting where scripts, styles, and images may be loaded from, and HTTP Strict Transport Security instructing browsers to only ever reach the platform over HTTPS.

Requests are rate-limited: a general limit applies across the authenticated API, keyed per caller IP (or per tenant and IP, where that stricter keying is enabled) so that one tenant's traffic cannot exhaust the limit for another. A separate, stricter limit applies to the public, unauthenticated endpoints that accept a write — submitting content without being signed in — and those endpoints additionally require passing a proof-of-work challenge before the write is accepted, which is what stands in for a login wall on a surface that deliberately has none.

Only requests from explicitly configured origins are accepted; anything else is rejected before it reaches a route handler.

---

## Authentication and authorization

Every protected endpoint requires a valid, signature-verified token before any request data is processed — see [Authentication & IAM](authentication-iam.md) for the full validation chain, the role checks a caller's token is subject to, and the tenant boundary that keeps one caller from reaching another tenant's resources.

---

## Secrets management

Credentials — Keycloak client secrets, database connection strings, and the like — are held as environment configuration on the hosting platform, not committed to the repository. Only template files documenting which variables are expected are version-controlled.

---

## Audit logging

A request that results in a process action is recorded once it completes, capturing who made it (the caller's identity and tenant), what it was (the HTTP method and endpoint, and the resource type and id it addressed where the path identifies one), when it happened, the caller's IP address where that is configured to be captured, and the outcome (success, failure, or error, derived from the response status). Audit logging can be disabled entirely by configuration, and IP capture can be disabled independently of the rest of the record. High-frequency, read-only traffic that would otherwise flood the log is deliberately excluded.

Audit records carry a configured retention target — long enough to satisfy a government archiving expectation measured in years rather than months — though retention is a configuration value the platform is set up to honour, not an automated purge the platform runs on a schedule.

---

## Data handling

Log output at debug verbosity is disabled outside development, so operational logs do not carry the level of request detail a developer would use while debugging. Error responses do not leak process variables or other request payload content beyond what the error itself needs to describe.

---

## Electronic signatures

Phase-exit approvals on the Infra-board can be signed electronically rather than
merely approved. The signing platform is ValidSign, the EU-branded OneSpan Sign.

Three properties matter for this page:

- **Signing is opt-in from the process model**, activated by an attribute on a
  single user task. A task without it behaves exactly as before, which is every
  ordinary task.
- **Live signing is gated by an allowlist that is empty by default.** The licence
  is production-only with an account-wide key and no sandbox tenant, so a
  misconfigured environment cannot fire a real signature request: stub mode must
  be off, a key present, and the deployment tier explicitly named.
- **The signed document and its evidence summary are archived** into the
  project's document workspace, and the process task completes only once the
  signature has landed — through the platform's callback or a periodic sweep,
  whichever arrives first, on one idempotent path.

The ceremony URL is a capability: package identifiers are random UUIDs, and the
two unauthenticated routes it needs are rate-limited per client IP. Full detail,
including a callback-header caveat that is not yet confirmed with the vendor, is
on [ValidSign phase-approval signing](../developer/validsign-signing.md).

---

## Build and pipeline integrity

The delivery pipeline is itself a security surface, and is treated as one on the
`acc` branch: every GitHub Actions reference is pinned to an immutable commit
digest, the pipeline token is read-only unless a job demonstrably needs more, no
git credential is left in the workspace after checkout, and a blocking audit
gate enforces all three on every pull request. Dependency updates are held for
fourteen days before adoption, except security advisories, which bypass the wait.

Two limits are worth stating plainly. The gate does **not** cover the backend's
path to production, which runs from a developer machine rather than CI. And the
`main` branch does not yet carry any of this.

For what is enforced, what cannot be, and where the coverage stops, see
[Supply-chain gate](../../contributing/supply-chain.md).

---

## Related

- [ValidSign phase-approval signing](../developer/validsign-signing.md) — the signing feature, its environment locks and its unauthenticated routes
- [Supply-chain gate](../../contributing/supply-chain.md) — pipeline pinning, least privilege, and the audit gate
- [Authentication & IAM](authentication-iam.md) — the identity and tenancy checks this page's audit trail traces back to
- [API Design](api-design.md) — the response conventions error handling follows
- [Tasks](tasks.md) and [Processes](processes.md) — the actions an audit record most often describes
