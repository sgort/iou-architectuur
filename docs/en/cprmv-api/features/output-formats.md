# Output Formats

The `format` query parameter on `/rules/{rule_id_path}` selects the serialisation of the response. Seven values are accepted.

---

## cprmv-json (default)

A custom recursive JSON format produced directly from rdflib's graph traversal, not from RDF serialisation. The response is a nested dictionary that mirrors the `cprmv:hasPart` tree of the rule:

```json
{
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.1#id": "Artikel 20",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.1#definition": "...",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.1#hasPart": {
        "lid 1": {
            "https://standaarden.open-regels.nl/standards/cprmv/0.4.1#id": "lid 1",
            "https://standaarden.open-regels.nl/standards/cprmv/0.4.1#definition": "...",
            "https://standaarden.open-regels.nl/standards/cprmv/0.4.1#hasPart": {
                "onderdeel a": { ... }
            }
        }
    }
}
```

All sub-rules contained via `cprmv:hasPart` RDF lists are recursively included. Predicate URIs are used as keys.

!!! note
    As of v0.4.1, `unformat` works with **any** output format, not only `cprmv-json`. The values extracted by the `parse` pattern are added as additional triples on the selected rule, so they also appear in the RDF serialisations (`turtle`, `n3`, `json-ld`, …). In `cprmv-json` the extracted fields are merged into the rule object.

---

## RDF formats

For all non-`cprmv-json` formats, the API serialises the [Concise Bounded Description (CBD)](https://www.w3.org/Submission/CBD/) of the matched rule node using rdflib's serialiser:

| `format` value | Media type | Notes |
|---|---|---|
| `json-ld` | `application/ld+json` | JSON-LD 1.1 |
| `turtle` | `text/turtle` | Standard Turtle |
| `ttl` | `text/turtle` | Alias for `turtle` |
| `turtle2` | `text/turtle` | rdflib's alternative Turtle serialiser |
| `n3` | `text/n3` | Notation3 |
| `xml` | `application/rdf+xml` | RDF/XML |

The CBD includes all triples directly about the matched rule node. Nested sub-rules referenced via `cprmv:hasPart` RDF lists are included because the list blank nodes form part of the CBD.

---

## Methods endpoint format

The `/methods` endpoint accepts the same set of RDF format strings (`json-ld`, `xml`, `turtle`, `ttl`, `n3`, `turtle2`) and serialises the entire Methods Knowledge Graph, which contains both `cprmv.ttl` and `cprmvmethods.ttl`.
