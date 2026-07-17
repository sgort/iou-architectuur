# Doccle — Live Testing

This page will track live testing of the `/v1/doccle/*` surface against the
real Doccle sender API, following the same format as
[eDOCS — Live Testing](edocs-live-testing.md) — a summary table up top, details
below.

!!! info "Not yet live-tested"
    Every smoke run so far has had `DOCCLE_STUB_MODE=true`. No row below has
    been exercised against the real Doccle staging API yet.
    `scripts/test-doccle-live.sh` in `ronl-business-api` is written and ready —
    run it with `DOCCLE_STUB_MODE=false` and a confirmed `DOCCLE_SENDERNAME`
    to start filling this page in.

---

## Summary

| Request | Live-tested | Result |
| --- | :---: | --- |
| `GET /v1/doccle/status` | ✗ | not yet |
| `PUT /v1/doccle/senders/:senderName/receivers/:externalReference` | ✗ | not yet — receiver upsert |
| `POST /v1/doccle/senders/:senderName/receivers/:externalReferenceId/documents/:documentId` | ✗ | not yet — document upload |
| `POST /v1/doccle/senders/:senderName/receivers/:externalReferenceId/documents/:documentId/paid` | ✗ | not yet — mark document paid |

---

## Running it

```bash
CLIENT_SECRET=<secret> bash scripts/test-doccle-live.sh
```

A Keycloak-free pre-flight runs first — it probes Doccle reachability
in-process and aborts before the token dance / any mutation if Doccle is
unreachable or still in stub mode. Unlike eDOCS, this API has no
side-effect-free endpoint, so the pre-flight cannot verify
`DOCCLE_USERNAME`/`DOCCLE_PASSWORD` — that only happens once the mutating
steps run. For just the reachability answer: `npm run doccle:health` from
`packages/backend`.

A successful run creates a real receiver and document on Doccle staging — the
service exposes no delete, so `RECEIVER_REF`/`DOCUMENT_ID` default to
timestamps so runs never collide, and manual cleanup is needed if the sender
account requires it.

---

## Details

_To be filled in once live testing starts — see [eDOCS — Live Testing](edocs-live-testing.md)
for the format this section will follow: one subsection per confirmed finding,
linked from the summary table above._
