# Getting Started

The CPRMV API is available as a live service. No account or API key is required.

---

## Environments

| | URL |
|---|---|
| **Production** | [https://cprmv.open-regels.nl/docs](https://cprmv.open-regels.nl/docs) |
| **Acceptance** | [https://acc.cprmv.open-regels.nl/docs](https://acc.cprmv.open-regels.nl/docs) |

Both environments expose FastAPI's interactive Swagger UI at `/docs`, where every endpoint can be called directly in the browser.

---

## Exploring the API

Navigate to [https://acc.cprmv.open-regels.nl/docs](https://acc.cprmv.open-regels.nl/docs). The Swagger UI shows all available endpoints with their parameters and response schemas. Click **Try it out** on any endpoint to send a live request.

---

## Your first request

The simplest call fetches a complete article from Dutch national law. Use the `/rules/{rule_id_path}` endpoint:

```
GET https://acc.cprmv.open-regels.nl/rules/BWBR0015703_2025-07-01_0%2C%20Artikel%2020
```

`BWBR0015703_2025-07-01_0` is the rule set identifier (the Wet op de Zorgtoeslag, version from 1 July 2025, index 0). `Artikel 20` is the rule identifier within that set. The comma separator must be URL-encoded as `%2C`.

The default `format=cprmv-json` response returns the full article including all its nested paragraphs (`lid`) and sub-clauses (`onderdeel`).

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

Returns the Methods Knowledge Graph in Turtle format, listing all registered analysis methods, publication methods, and reference methods with their configuration properties.
