---
component: RONL Business API
---

# Timeline Navigation

**Timeline navigation** presents a person's own record along a time axis rather than as a single, present-day snapshot: a point in time is selected, and the data shown updates to reflect what the record looked like — or would look like — as of that date.

---

## What a timeline presents

A timeline draws on a personal-records source — currently the BRP (Basisregistratie Personen), the municipal register of personal data — and presents the caller's own information, partner, and any children as of the selected date. Nothing about this view is stored separately per date: each time the selected date changes, the displayed state is derived again from the underlying record and its own dated fields, such as a marriage date or a date of birth, rather than read from a saved historical copy.

---

## Selecting a point in time

A point in time can be reached by moving continuously along the timeline or by jumping directly to a marker. The range is not limited to the present or the past: a date can also be selected ahead of today, within a bounded window, to see how the record would present if nothing about it changes before then.

---

## Event markers

A timeline surfaces markers for the dates on which something in the record changed — a birth, a marriage — detected automatically from the record's own dated fields rather than entered separately. Selecting a marker jumps straight to that date.

---

## What changes when the date changes

Moving the selected date can add or remove sections from view and recompute the values within them: a partner appears only once the record's marriage date has passed; a child appears only once their birth date has passed; an age is computed relative to the selected date rather than to today. The mechanism is the same as ordinary filtering and derivation — nothing is precomputed or cached per date.

---

## Access and privacy

Viewing a timeline requires authentication, and a caller can only view their own record — never another person's. Reaching this level of assurance is required the same way described in [Authentication & IAM](authentication-iam.md). Every access to timeline data is logged, consistent with the audit trail described in [Security & Compliance](security-compliance.md).

---

## Related

- [Authentication & IAM](authentication-iam.md) — the assurance level required to reach a personal record
- [Security & Compliance](security-compliance.md) — the audit trail timeline access is recorded in
- [Documents](documents.md) — the other way a case's accumulated data is presented
