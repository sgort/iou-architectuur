# API Stability Contract — `/v1/norms`

This document is the binding stability contract for consumers of `/v1/norms`. It defines what consumers can rely on, how to detect change efficiently, and what kinds of changes warrant a major version bump.

## Audience

This contract is aimed at **G2G consumers** — other Dutch government services integrating `/v1/norms` to consume `cprmv:Rule` paths and norms. External consumers can build long-term integrations against this contract without fear of breakage within v1.

## The four versioning layers

`/v1/norms` carries four distinct version numbers, each describing a different layer of stability:

| Layer | Where | What it tracks | When it changes |
|-------|-------|----------------|-----------------|
| **API contract** | URL path `/v1/` | The schema and shape consumers code against | Breaking changes only (warrants `/v2/`) |
| **Dataset versions** | `data.dataset_versions` envelope map | Per-rulesetid publication snapshots | Each BWB ruleset on its own cadence; map carries the latest version per rulesetid present in the response |
| **CPRMV vocabulary** | `data.cprmv_version` envelope field | Which vocabulary the data uses | Vocabulary version bumps (usually additive) |
| **Backend service** | `API-Version` HTTP header | The deployed backend code | Each backend release (operational, not a contract signal) |

Only the first three are part of the consumer contract. The `API-Version` header is informational — useful for support tickets, not for cache invalidation or schema discrimination.

## Stability promise within v1

### Primary key semantics

The tuple `(rulesetid, applicable_date, rulesetid_index)` is the **immutable primary key** for any individual rule. Once published, this combination identifies a rule whose values never change.

- Corrections are published as new rows with a higher `rulesetid_index`
- Law amendments are published as new rows with a new `applicable_date`
- Old rows remain unchanged and queryable indefinitely

**Consumers can cache rows indexed by this tuple permanently. Cache invalidation is not required.**

### Logical identity across versions

The `rule_id_path_key` field provides a stable identifier for the *logical* rule across all its versions. To query "the current value of this rule":

1. Filter rules by `rule_id_path_key`
2. Pick the row with the latest `applicable_date`
3. Within that, pick the row with the highest `rulesetid_index`

The kind of change is **explanatory from the content** — a new `applicable_date` implies a law amendment; a same date with higher `rulesetid_index` implies a correction. No separate change-kind metadata is published.

### Additive evolution

Within v1, all changes are additive:

- New fields may appear in the response envelope or rule objects — consumers must ignore unknown fields gracefully
- New optional query parameters may be added — consumers may ignore them
- Existing fields, their names, types, and semantics will not change

### CPRMV vocabulary version

The `cprmv_version` envelope field surfaces which CPRMV vocabulary the response data uses (currently `"0.3.0"`). A bump within the `0.x` line is treated as additive vocabulary growth (new predicates, new optional fields). A major bump that changes predicate URIs the consumer sees would be released as `/v2/norms`.

## Per-rulesetid dataset versioning

Each BWB ruleset (BWBR0002471, BWBR0004044, …) is published as a distinct `cprmv:Dataset` resource in TriplyDB by the CPSV editor. **A single ruleset can have multiple Dataset records** — different applicable periods of the same law (e.g. the `2025-01-01` and `2026-01-01` editions of the Participatiewet) are *concurrent and equally authoritative*, not competing versions of each other. Both back rules that consumers may legitimately ask for. A single `/v1/norms` response can aggregate rules across N rulesets, each carrying M records.

### The `dataset_versions` map

The `data.dataset_versions` envelope field is keyed by `cprmv:rulesetId`; each value is a **list** of records:

```json
"dataset_versions": {
  "BWBR0015703": [
    {
      "version": "2026-01-01",
      "published_at": "2026-05-15T06:57:21Z",
      "title": "Participatiewet"
    },
    {
      "version": "2025-01-01",
      "published_at": "2026-05-15T07:45:36Z",
      "title": "Participatiewet"
    }
  ],
  "BWBR0044894": [
    { "version": null, "published_at": "2026-05-15T07:45:36Z", "title": null }
  ]
}
```

The list is **pre-sorted**: `version` descending with nulls at the end, ties broken by `published_at` descending. Element `[0]` is the most-recent applicable version of that ruleset. Non-primary rulesets (where the editor doesn't know `dcat:version`) fall through to pure `published_at` desc ordering.

The map contains entries only for rulesetids that have at least one `cprmv:Dataset` record. Rulesetids without one are silently absent (transitional state during rollout).

Three per-entry fields, with two of them nullable:

| Field          | Source         | Always present?                                                                                              |
| -------------- | -------------- | ------------------------------------------------------------------------------------------------------------ |
| `version`      | `dcat:version` | **Primary ruleset only.** The CPSV editor only knows the version of the service's `legalResource.bwbId` — the law explicitly entered in the Legal tab. For other rulesets that enter the service via `cprmv:Rule` references, the version is unknown and emitted as `null`. |
| `published_at` | `dct:issued`   | **Always present.** Timestamp of when this `cprmv:Dataset` record was published. This is the meaningful signal for change detection — it updates on every (re-)publication regardless of whether the BWB's own version is known. |
| `title`        | `dct:title`    | **Primary ruleset only.** `null` for non-primary rulesets, for the same reason as `version`. |

### Matching rules to Dataset records

A rule with `applicable_date: "2025-07-01"` is backed by the Dataset record whose `version` covers that period. The mapping is convention-based, not enforced by the API: the editor publishes Dataset records for the same applicable periods as the rules it generates. Consumers wanting "the Dataset record that backs this rule" can:

1. Look up `dataset_versions[<rule.rulesetid>]`
2. Find the entry whose `version` matches `<rule.applicable_date>` (when version is known)
3. Fall through to the latest entry by `published_at` when version is null

### Detecting publications

#### HTTP cache headers

When **every** rulesetid in the response has at least one `dataset_versions` entry, the response carries:

| Header | Example | Meaning |
|--------|---------|---------|
| `ETag` | `"3c899856"` | Opaque strong validator over every `(version, published_at)` pair plus filter params. `title` is intentionally excluded — informational only. |
| `Last-Modified` | `Fri, 15 May 2026 07:45:36 GMT` | Maximum `published_at` across **all records** in the response |
| `Cache-Control` | `public, max-age=3600` | Biannual data tolerates generous caching |

Consumers should use conditional requests for efficiency:

```http
GET /v1/norms HTTP/1.1
Host: backend.linkeddata.open-regels.nl
If-None-Match: "3c899856"
```

The server returns `304 Not Modified` with no body when nothing in the response has been republished since the last fetch. For single-rulesetid queries (`?rulesetid=<id>`), the 304 check happens before the expensive rules SPARQL query — only the cheap (cached) metadata lookup runs.

#### Why `published_at` (not `version`) drives cache validity

A null `version` field doesn't mean the data is uncacheable — it just means the BWB's own version label is unknown. The actual change signal is `published_at` (`dct:issued`), which is always present and updates on every publication event. ETag and Last-Modified rely on `published_at`; the `version` field is informational metadata for human and UI consumption.

#### Partial-coverage behaviour

When **any** rulesetid in the response lacks a `cprmv:Dataset` record (an unversioned ruleset), the response degrades to:

- `dataset_versions` map omits the unversioned rulesetid(s)
- `ETag` and `Last-Modified` headers are not set
- `Cache-Control: no-cache`

Rationale: we cannot reliably detect a change in an unversioned ruleset. Returning a 304 in that case would risk serving stale data, so we tell consumers to always refetch. As more BWB rulesets are published with `cprmv:Dataset` metadata, caching kicks in progressively for queries that span only versioned rulesets.

## What warrants `/v2/norms`

The following would break the v1 contract and would be released as `/v2/norms`, with `/v1/norms` kept alive for a deprecation window:

- Removing or renaming an existing field
- Changing the type or semantics of an existing field
- Changing the PK semantics of `(rulesetid, applicable_date, rulesetid_index)` (e.g., allowing in-place mutation)
- CPRMV major version bump that changes predicate URIs the consumer sees

## Deprecation policy

When `/v2/norms` is eventually introduced:

- `/v1/norms` remains available for **at least 24 months** after `/v2/norms` is published
- During deprecation, `/v1/norms` responses include `Deprecation: <date>` and `Sunset: <date>` headers per RFC 8594
- Active consumers will be notified via the IOU Architecture documentation site and the changelog

## Quick reference for consumers

| Question | Answer |
|----------|--------|
| Can I cache a rule's values indefinitely? | Yes, keyed by `(rulesetid, applicable_date, rulesetid_index)` |
| How do I detect new publications efficiently? | Use `If-None-Match` with the previous `ETag` — `304` means nothing changed |
| What if a rulesetid is missing from `dataset_versions`? | That ruleset has no `cprmv:Dataset` record yet; do not cache |
| What does `Cache-Control: no-cache` mean here? | At least one rulesetid in your query is unversioned — refetch every time |
| What does `version: null` mean? | The BWB's own version is unknown (this ruleset isn't the primary law of any service that publishes it). `published_at` is still authoritative for change detection. |
| Why does a single rulesetid have multiple Dataset records? | Different applicable periods of the same law are concurrent and equally authoritative. The `2025-01-01` and `2026-01-01` editions of Participatiewet both back current rules; both are listed. |
| How do I find which Dataset record backs a specific rule? | Look up `dataset_versions[<rule.rulesetid>]`, find the entry whose `version` matches `<rule.applicable_date>`; fall through to the latest by `published_at` when `version` is null. |
| How do I find the current value of a rule? | Filter by `rule_id_path_key`, sort by `applicable_date` desc then `rulesetid_index` desc, take first |
| Will new fields appear in responses? | Yes — additively, never as a breaking change. Ignore unknown fields |
| Are all BWB rulesets on the same publication cycle? | No — each ruleset has its own cadence; check `dataset_versions[<id>][0].published_at` individually |