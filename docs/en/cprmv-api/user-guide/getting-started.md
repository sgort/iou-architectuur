---
component: CPRMV
---

# Getting Started

The CPRMV API is available as a live service. No account or API key is required.

---

## Environments

| | URL |
|---|---|
| **Production** | [https://cprmv.open-regels.nl/docs](https://cprmv.open-regels.nl/docs) (also [https://cprmv.open-rules.eu/docs](https://cprmv.open-rules.eu/docs)) |
| **Acceptance** | [https://acc.cprmv.open-regels.nl/docs](https://acc.cprmv.open-regels.nl/docs) |

Every environment exposes FastAPI's interactive Swagger UI at `/docs`, where every endpoint can be called directly in the browser. `GET /` returns the running version, for example `{"CPRMV Rules Serve API": "0.4.2"}`.

---

## Exploring the API

Navigate to [https://acc.cprmv.open-regels.nl/docs](https://acc.cprmv.open-regels.nl/docs). The Swagger UI shows all available endpoints with their parameters and response schemas. Click **Try it out** on any endpoint to send a live request.

---

## Your first request

The simplest call fetches a complete article from Dutch national law. Use the `/rules/{rule_id_path}` endpoint:

```
GET https://acc.cprmv.open-regels.nl/rules/BWBR0015703_2025-07-01_0%2C%20Artikel%2020
```

`BWBR0015703_2025-07-01_0` is the rule set identifier (the Participatiewet, originally the Wet werk en bijstand, in the version valid from 1 July 2025, index 0). `Artikel 20` is the rule identifier within that set. The comma separator must be URL-encoded as `%2C`.

The default `format=cprmv-json` response returns the rule set with the full article as its part, including all its nested paragraphs (`lid`) and sub-clauses (`onderdeel`).

---

## Fetching the current version of a law

You do not need to know the publication date and index. Use a bare BWB identifier to get the version valid today:

```
GET https://acc.cprmv.open-regels.nl/rules/BWBR0015703
```

Or specify a date for which you want the valid version:

```
GET https://acc.cprmv.open-regels.nl/rules/BWBR0015703_2025-07-02_latest
```

The `cprmv:id` of the returned rule set shows which publication was found (for example `BWBR0015703_2025-07-01_0`).

---

## Checking the CPRMV specification

The CPRMV specification in ReSpec format is served at:

```
https://acc.cprmv.open-regels.nl/respec/
```

This describes the full vocabulary — classes, properties, and cardinality constraints — that the API's output conforms to.

---

## Checking supported methods

```
GET https://acc.cprmv.open-regels.nl/methods?format=turtle
```

Returns the Methods Knowledge Graph in Turtle format: the acknowledged method lists (`cprmvmethods:rulemethods`, `publicationmethods`, `referencemethods`, `analysismethods`, …) and the definition of each method with its configuration properties. The graph is loaded from `serve_api/data/cprmvmethods.ttl`, which currently lags behind the method definitions in `rdf/0.4.2/methods/` ([standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31)).
