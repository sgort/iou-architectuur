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

Every response carries a Content Security Policy restricting where scripts, styles, and images may be loaded from, and HTTP Strict Transport Security instructing browsers to only ever reach the platform over HTTPS. Both are set by Helmet, which `HELMET_ENABLED` can switch off and which is on by default.

Requests are rate-limited. One general limit applies to every request, authenticated or not, keyed per client IP; the ValidSign callback is exempt and has its own limiter. The limiter runs before any route authenticates the caller, so the per-tenant keying that `RATE_LIMIT_PER_TENANT` asks for never has a tenant to key on: in practice every bucket is per client IP. A separate, stricter limit — 10 requests per 15 minutes per IP — applies to the three public endpoints that accept a write without a login: submitting a use case, uploading a file for one, and sending feedback. The use-case and feedback submissions also require a solved ALTCHA proof-of-work challenge, which stands in for a login wall on a surface that deliberately has none; the check is skipped when no `ALTCHA_HMAC_KEY` is configured, and the file upload is not challenged.

Cross-origin access is governed by CORS, which is a browser control, not an access boundary. For a request from an origin that is not configured, the backend withholds the CORS response headers, so the browser does not hand the response to the calling page — but the request itself is still handled. Requests without an `Origin` header (server-to-server calls, `curl`, health probes) are allowed through. `/v1/openapi.json` is open to every origin, as the NL API Design Rules require for a published description.

---

## Authentication and authorization

Every protected endpoint requires a valid, signature-verified token before any request data is processed — see [Authentication & IAM](authentication-iam.md) for the full validation chain, the role checks a caller's token is subject to, and the tenant boundary that keeps one caller from reaching another tenant's resources.

---

## Secrets management

Credentials — database connection strings, the Operaton, eDOCS and ValidSign credentials, the Anthropic API key, and the like — are held as environment configuration on the hosting platform, not committed to the repository. Only template files documenting which variables are expected are version-controlled. The Business API's own Keycloak client, `ronl-business-api`, is a public client: it has no client secret to hold. In production the boot refuses a missing Anthropic API key and one still set to a placeholder value.

---

## Audit logging

Every authenticated request is recorded once it completes, capturing who made it (the caller's identity and tenant), what it was (the HTTP method and endpoint, and the resource type and id it addressed where the path identifies one), when it happened, the caller's IP address where that is configured to be captured, and the outcome (success, failure, or error, derived from the response status). Route handlers add their own entries for specific actions — a process start, a task completion, a refused start — with details of their own. Two paths are excluded: reading the audit log itself, and the AI assistant's chat turns. Audit logging can be disabled entirely by configuration, and IP capture can be disabled independently of the rest of the record.

Each entry is written to the audit database and also to the application log at `info` level.

The backend never deletes audit records. `AUDIT_LOG_RETENTION_DAYS` (default 2555, seven years) is parsed into configuration and read by no code: nothing purges audit records, and nothing applies a retention period to them.

---

## Data handling

The log level is set by `LOG_LEVEL` (default `info`) in every environment; nothing ties it to the deployment tier. Logs and audit records are not free of personal data:

- The BRP person lookup logs its whole request body at `info` level, citizen service number (BSN) included. This is an open issue on ronl-business-api (#241).
- The same lookup's audit entry stores the BSN it looked up, and audit entries are copied to the application log.

The frontend does not write a BSN to the browser console.

An unhandled error is answered with a generic message in production. Handled errors can carry upstream detail: a failed process start returns Operaton's own error message and the engine URL, and a BRP error returns the BRP response.

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

The delivery pipeline is itself a security surface, and is treated as one: every
GitHub Actions reference is pinned to an immutable commit digest, the pipeline
token is read-only unless a job demonstrably needs more, no git credential is
left in the workspace after checkout, and a blocking audit gate enforces all
three on every pull request. The backend reaches production through the same
pipeline: a promotion to `main` runs the production deploy workflow, which
authenticates to Azure over OIDC. Dependency updates are held for fourteen days
before adoption, except security advisories, which bypass the wait.

For what is enforced, what cannot be, and where the coverage stops, see
[Supply-chain gate](../../contributing/supply-chain.md).

---

## Related

- [ValidSign phase-approval signing](../developer/validsign-signing.md) — the signing feature, its environment locks and its unauthenticated routes
- [Supply-chain gate](../../contributing/supply-chain.md) — pipeline pinning, least privilege, and the audit gate
- [Authentication & IAM](authentication-iam.md) — the identity and tenancy checks this page's audit trail traces back to
- [API Design](api-design.md) — the response conventions error handling follows
- [Tasks](tasks.md) and [Processes](processes.md) — the actions an audit record most often describes
