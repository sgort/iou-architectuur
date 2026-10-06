---
component: Linked Data Explorer
---

# API Stability Contract — `/v1/norms` and `/v2/norms`

This document is the binding stability contract for consumers of `/v1/norms` and `/v2/norms`. It defines what consumers can rely on, how to detect change efficiently, and what kinds of changes warrant a major version bump.

!!! warning "`/v1/norms` is deprecated — use `/v2/norms`"
    `/v1/norms` is deprecated from **1 November 2026** and will be removed on
    **1 November 2028** (24 months, per the [deprecation policy](#deprecation-policy)).
    Every v1 response carries `Deprecation: @1793491200`,
    `Sunset: Wed, 01 Nov 2028 00:00:00 GMT` and
    `Link: </v2/norms>; rel="successor-version"`. Until the sunset, v1 behaves
    exactly as described below.

## `/v2/norms`

`/v2/norms` answers the question consumers actually ask: _which norms are in
force on this date?_

|                         | `/v1/norms`                                                 | `/v2/norms`                                        |
| ----------------------- | ----------------------------------------------------------- | -------------------------------------------------- |
| Default `cprmv_version` | `0.3.0`                                                     | `0.4.1`                                            |
| Date parameter          | `applicable_date`: exact match on a period's **start** date | `valid_on`: the norms **in force** on that date    |
| Date omitted            | every period of every ruleset                               | in force **today** (Europe/Amsterdam)              |
| `dataset_versions`      | every record of each ruleset in the response                | the records of the period in force                 |
| Envelope                | —                                                           | adds `valid_on`, the date the response answers for |

**Selection.** For each ruleset, `/v2/norms` returns the rules of the latest
period whose start date (`applicable_date`) is on or before `valid_on`. A
period stays in force until the same ruleset publishes a later one. Rulesets
whose periods all start after `valid_on` are absent. A response therefore
mixes periods: on 2026-08-15 it holds BWBR0002471 from 2026-02-21,
BWBR0015711 from 2026-01-01 and the rulesets whose period starts on
2026-07-01.

**Parameters.** `valid_on` must be a real calendar date (`2026-02-30` is
rejected). `applicable_date` is refused with a 400 that points to `valid_on`.
`rulesetid`, `cprmv_version` and `endpoint` behave as on v1; on both versions a
`rulesetid` or `cprmv_version` sent as an array (`?rulesetid[]=X`) is answered
with `400 INVALID_PARAM`.

**Dataset versions.** For 0.3.x rulesets whose records carry no version,
`dataset_versions` lists the version-less records, and `[0]` is the most
recently published of them, not necessarily the record of the period in force.

**Caching.** The ETag is strong and covers the dataset metadata of the
selected periods, the request parameters (`endpoint`, `rulesetid`,
`cprmv_version` and the resolved `valid_on`, plus a marker that keeps v2 ETags
apart from v1 ones), and a digest of the content of the selected rules. A correction within a period (a higher `rulesetid_index`)
therefore changes the ETag, and so does midnight, even when nothing was
republished, because a new period may have come into force. `Last-Modified` is
omitted when it would be later than the response (a period not yet started),
so consumers should revalidate with `If-None-Match`; when it is sent,
`If-Modified-Since` is ignored (RFC 9110 §13.2.2). There is no pre-query 304 for `rulesetid`
requests on v2: the 304 check runs after the rules query, because the digest
needs the rules. Without `valid_on`, `max-age` never reaches past the next
midnight in Europe/Amsterdam.

**Stability.** Within v2, the default (`0.4.1`) response shape, its
predicate URIs and the `valid_on` semantics do not change; the v2 default
version changes only with a `/v3/norms`. `0.3.0` and `0.3.2` remain
selectable on v2 without that guarantee. The primary key
`(rulesetid, applicable_date, rulesetid_index)` and the additive-evolution
rules below hold for v2 as for v1. The OpenAPI description is at
`/v2/openapi.json`.

## Audience

This contract is aimed at **G2G consumers** — other Dutch government services integrating `/v1/norms` or `/v2/norms` to consume `cprmv:Rule` paths and norms. External consumers can build long-term integrations against this contract without fear of breakage within a major version.

## The four versioning layers

Each `/vN/norms` carries four distinct version numbers, each describing a different layer of stability:

| Layer | Where | What it tracks | When it changes |
|-------|-------|----------------|-----------------|
| **API contract** | URL path `/v1/`, `/v2/` | The schema and shape consumers code against | Breaking changes only (warrants a new major path) |
| **Dataset versions** | `data.dataset_versions` envelope map | Per-rulesetid publication snapshots | Each BWB ruleset on its own cadence; map carries the latest version per rulesetid present in the response |
| **CPRMV vocabulary** | `?cprmv_version=` request param ↔ `data.cprmv_version` envelope field | Which CPRMV vocabulary version the response is requested in and emitted as | **Consumer-selected** per request (`0.3.0`, `0.3.2`, `0.4.1`; default `0.3.0` on v1, `0.4.1` on v2); the namespace of the data follows the selection |
| **Backend service** | `API-Version` HTTP header | The deployed backend code | Each backend release (operational, not a contract signal) |

Only the first three are part of the consumer contract. The `API-Version` header is informational — useful for support tickets, not for cache invalidation or schema discrimination.

!!! note "`cprmv_version` is now a request input"
    As of backend v1.9.10, `cprmv_version` is a **negotiable** layer: consumers choose the
    vocabulary version via the optional `?cprmv_version=` parameter (default `0.3.0`), and the
    envelope `cprmv_version` echoes the choice. It previously surfaced only "what the backend
    speaks". Omitting the parameter keeps the exact prior behaviour, so this is an additive
    change within v1.

## Stability promise within v1

!!! note "Scope"
    This section and the ones that follow describe the deprecated `/v1/norms`. `/v2/norms` is covered by the [`/v2/norms`](#v2norms) section above.

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

The `cprmv_version` envelope field echoes the version requested via `?cprmv_version=` (one of `0.3.0`, `0.3.2`, `0.4.1`; default `0.3.0`). The **fully-qualified rule keys** (`type`, `id`, `definition`, `contains`) carry that version's namespace, so the predicate URIs a consumer sees are a function of the version they *ask for*:

- `0.3.0` / `0.3.2` → `https://cprmv.open-regels.nl/<version>/…`
- `0.4.1` → `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#…`

Stability within v1: **the default (`0.3.0`) response shape and its predicate URIs do not change.** Requesting a different `cprmv_version` is an explicit opt-in to that namespace — not a breaking change to the default contract. A consumer that never sends the parameter is unaffected by new versions being added to the supported set. A change to the **default** version, or to the predicate URIs of the **default** version, needs a new major path: that is `/v2/norms`, whose default is `0.4.1`.

!!! warning "Experimental versions — `0.3.2` and `0.4.1` are not part of the v1 guarantee"
    On `/v1/norms`, only the default **`0.3.0`** is covered by this stability contract.
    **`0.3.2` and `0.4.1` are experimental / preview on v1:** their response shape,
    predicate URIs, `dataset_versions` semantics (e.g. the 0.4.1 `cprmv:RuleSet`/`validFrom`
    model and its [cache caveat](#detecting-publications)) and even their availability on
    v1 may change — or be withdrawn — **without** a new major path and outside the
    additive-evolution promise above. This applies to v1 only: on `/v2/norms`, `0.4.1` is
    the contract default (see [`/v2/norms`](#v2norms)). Build long-term G2G integrations
    against `/v2/norms`.

## Per-rulesetid dataset versioning

Each BWB ruleset (BWBR0002471, BWBR0004044, …) carries per-ruleset version metadata published by the CPSV editor. **Where that metadata lives depends on the requested `cprmv_version`:** `0.3.0`/`0.3.2` use a distinct `cprmv:Dataset` resource per ruleset; `0.4.1` has no `cprmv:Dataset` and the metadata is read from the `cprmv:RuleSet` (`cprmv:validFrom`). Either way the envelope shape below is identical. **A single ruleset can have multiple records** — different applicable periods of the same law (e.g. the `2025-01-01` and `2026-01-01` editions of the Participatiewet) are *concurrent and equally authoritative*, not competing versions of each other. Both back rules that consumers may legitimately ask for. A single `/v1/norms` response can aggregate rules across N rulesets, each carrying M records.

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

The list is **pre-sorted**: `version` descending with nulls at the end, ties broken by `published_at` descending. Element `[0]` is the most-recent applicable version of that ruleset.

The map contains entries only for rulesetids that have at least one version record (a `cprmv:Dataset` for 0.3.x, a `cprmv:RuleSet` for 0.4.1). Rulesetids without one are silently absent (a transitional state for legacy 0.3.x data; 0.4.1 always has a RuleSet per ruleset).

Three per-entry fields:

| Field          | Source (0.3.x / 0.4.1)             | Notes                                                                                          |
| -------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------- |
| `version`      | `dcat:version` / `cprmv:validFrom` | **Present for every ruleset since CPSV editor v1.10.5** — the editor derives each ruleset's version from the BWB date its own rules carry (their `ruleIdPath`), so non-primary rulesets are versioned too. `null` only survives for legacy data published before that change; consumers must still tolerate it. |
| `published_at` | `dct:issued` / `cprmv:validFrom`   | **0.3.x:** the publication timestamp — updates on every (re-)publication, the change-detection signal. **0.4.1:** there is no `dct:issued`, so `cprmv:validFrom` serves as `published_at` (see the [0.4.1 cache caveat](#detecting-publications)). |
| `title`        | `dct:title`                        | **Primary ruleset only.** The editor only knows the human title of the service's `legalResource.bwbId`. `null` for non-primary rulesets. |

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

ETag and `Last-Modified` are computed from `published_at`, not `version`; the `version` field is informational metadata for human and UI consumption. For `0.3.0`/`0.3.2`, `published_at` is `dct:issued`, which updates on every publication event and is therefore a reliable change signal (a legacy `null` `version` does not make the data uncacheable).

!!! warning "0.4.1 cache caveat"
    On `/v1/norms` with `cprmv_version=0.4.1`, `published_at` equals `cprmv:validFrom` (the applicable date),
    because the 0.4.1 RuleSet has no `dct:issued`. A re-publish that **keeps the same
    `validFrom`** but corrects rule values does **not** change ETag/`Last-Modified`, so a
    cached response keeps being revalidated as unchanged on **`/v1/norms`**: the ETag does not
    change until a later period is published. Consumers needing correction-level freshness on
    `0.4.1` should use [`/v2/norms`](#v2norms), whose ETag also covers the content of the
    selected rules, so a correction within a period changes it. `0.3.x` is unaffected
    (`dct:issued` advances on every publish).

#### Partial-coverage behaviour

When **any** rulesetid in the response lacks a version record (a `cprmv:Dataset` for 0.3.x, a `cprmv:RuleSet` for 0.4.1), the response degrades to:

- `dataset_versions` map omits the unversioned rulesetid(s)
- `ETag` and `Last-Modified` headers are not set
- `Cache-Control: no-cache`

Rationale: we cannot reliably detect a change in an unversioned ruleset. Returning a 304 in that case would risk serving stale data, so we tell consumers to always refetch. As more BWB rulesets are published with version metadata, caching kicks in progressively for queries that span only versioned rulesets.

## What warrants `/v3/norms`

The following would break the v2 contract and would be released as `/v3/norms`, with `/v2/norms` kept alive for a deprecation window. The same rules are why the v1 default (`0.3.0`) could not change in place and `/v2/norms` was introduced instead:

- Removing or renaming an existing field
- Changing the type or semantics of an existing field
- Changing the PK semantics of `(rulesetid, applicable_date, rulesetid_index)` (e.g., allowing in-place mutation)
- CPRMV major version bump that changes predicate URIs the consumer sees

## Deprecation policy

With the introduction of `/v2/norms`:

- `/v1/norms` remains available for **at least 24 months** after `/v2/norms` is published
- During deprecation, `/v1/norms` responses include `Deprecation: @1793491200` (1 November 2026) and `Sunset: Wed, 01 Nov 2028 00:00:00 GMT` headers (`Deprecation` per RFC 9745, `Sunset` per RFC 8594), and a `Link: </v2/norms>; rel="successor-version"` header
- Active consumers will be notified via the IOU Architecture documentation site and the changelog

## Quick reference for consumers

| Question | Answer |
|----------|--------|
| Can I cache a rule's values indefinitely? | Yes, keyed by `(rulesetid, applicable_date, rulesetid_index)` |
| How do I detect new publications efficiently? | Use `If-None-Match` with the previous `ETag` — `304` means nothing changed (on `/v1/norms` with `cprmv_version=0.4.1`, a correction within a period is not detected; use `/v2/norms`) |
| Which `cprmv_version` should I request? | On `/v2/norms`, omit it for the stable default (`0.4.1`). On the deprecated `/v1/norms`, the default is `0.3.0`, where the editor no longer publishes new periods. |
| How do I get the norms in force on a date? | `GET /v2/norms?valid_on=YYYY-MM-DD`; omit `valid_on` for today. |
| What if a rulesetid is missing from `dataset_versions`? | That ruleset has no version record yet (a `cprmv:Dataset` for 0.3.x / a `cprmv:RuleSet` for 0.4.1); do not cache |
| What does `Cache-Control: no-cache` mean here? | At least one rulesetid in your query is unversioned — refetch every time |
| What does `version: null` mean? | Legacy data published before CPSV editor v1.10.5 — its non-primary version was unknown. Current data versions **every** ruleset, so `null` is rare. `published_at` remains authoritative for change detection (with the [0.4.1 caveat](#detecting-publications)). |
| Is `published_at` always a publication timestamp? | For `0.3.x`, yes (`dct:issued`). For `0.4.1` it is `cprmv:validFrom` (the applicable date) — a same-date re-publish won't bump it; see the 0.4.1 cache caveat. |
| Why does a single rulesetid have multiple Dataset records? | Different applicable periods of the same law are concurrent and equally authoritative. The `2025-01-01` and `2026-01-01` editions of Participatiewet both back current rules; both are listed. |
| How do I find which Dataset record backs a specific rule? | Look up `dataset_versions[<rule.rulesetid>]`, find the entry whose `version` matches `<rule.applicable_date>`; fall through to the latest by `published_at` when `version` is null. |
| How do I find the current value of a rule? | Filter by `rule_id_path_key`, sort by `applicable_date` desc then `rulesetid_index` desc, take first |
| Will new fields appear in responses? | Yes — additively, never as a breaking change. Ignore unknown fields |
| Are all BWB rulesets on the same publication cycle? | No — each ruleset has its own cadence; check `dataset_versions[<id>][0].published_at` individually |