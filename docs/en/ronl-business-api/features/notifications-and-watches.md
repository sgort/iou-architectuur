---
component: RONL Business API
---

# Notifications & Watches

A **watch** is a standing instruction to be told when something new matches a person's interest, rather than requiring them to keep checking for it. New entries are matched against every active watch as they arrive, and a match becomes a notification for the person who set the watch.

---

## What can be watched

A watch can be built two ways. It can be a set of **criteria** — search terms an incoming entry's title and description are matched against — so anything arriving later that matches those terms produces a notification. Or it can target a **single item** directly: watching an item this way matches everything that later arrives for that item, with no criteria of its own to satisfy.

---

## What a watch produces

A match becomes a notification for the person the watch belongs to. Watches are matched independently, but their results are not: if the same entry matches more than one of a person's watches at once, it still produces a single notification, listing every watch that matched rather than one notification per match. A notification is also delivered at most once — an entry already notified to a person does not resurface on a later matching pass.

---

## Scoping a watch

A watch belongs to the person who set it, and only they are notified by it. Criteria can also be defined once and shared across a team rather than owned by any one person; watching a shared set of criteria does not notify the whole team — it creates a personal, derivative watch for the individual who turned it on, and it is that derivative watch, not the shared original, that is actually matched and delivered.

---

## When notifications are computed

Matching does not wait solely for a periodic cycle to run. Turning a watch on, and an entry becoming eligible to match in the first place, both trigger an immediate matching pass — so a match that was already possible surfaces right away instead of sitting undelivered until some later, unrelated event forces a full rescan.

---

## Delivery

A notification appears in an in-app list, with a count shown wherever the caller is signed in. Because not every consumer of a notification can carry a signed-in session, a personal feed is also available, authenticated by a per-person token carried in the feed's own URL rather than a bearer token in a header — the pattern a feed reader needs, since it cannot attach one.

---

## Related

- [Authentication & IAM](authentication-iam.md) — how a person's identity scopes a watch to them
- [Timeline Navigation](timeline-navigation.md) — another way accumulated case data is presented back to a person
- [Security & Compliance](security-compliance.md) — the audit and rate-limiting posture notification endpoints share with the rest of the platform
