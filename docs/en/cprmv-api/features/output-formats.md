---
component: CPRMV
---

# Output Formats

The `format` query parameter on `/rules/{rule_id_path}` selects the serialisation of the response. Seven values are accepted; any other value falls back to `cprmv-json`. Every format is returned with the media type `text/plain; charset=utf-8`.

The response is always rooted at the `cprmv:RuleSet`. When a path to a specific rule is given, that rule becomes the rule set's only `cprmv:hasPart`, so the rule set's own properties (method, validity, provenance) travel with it.

---

## cprmv-json (default)

A custom recursive JSON format produced directly from rdflib's graph traversal, not from RDF serialisation. The response is a nested dictionary that mirrors the `cprmv:hasPart` tree, starting at the rule set; each `cprmv:hasPart` entry is keyed by the sub-rule's `cprmv:id`:

```json
{
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://standaarden.open-regels.nl/standards/cprmv/0.4.3#RuleSet",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.3#id": "BWBR0015703_2025-07-01_0",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.3#validFrom": "2025-07-01",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.3#hasMethod": "https://cprmv.open-regels.nl/0.4.3/methods/bwb",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.3#hasPart": {
        "Artikel 20": {
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://standaarden.open-regels.nl/standards/cprmv/0.4.3#Rule",
            "https://standaarden.open-regels.nl/standards/cprmv/0.4.3#id": "Artikel 20",
            "https://standaarden.open-regels.nl/standards/cprmv/0.4.3#hasPart": {
                "lid 1": { ... }
            }
        }
    }
}
```

(Abridged: the rule set also carries `cprmv:isOutputOf` — expanded into the service object, its identifier and the authority that provides it — and source-specific identifiers.) Objects other than the `cprmv:hasPart` lists are expanded the same way into nested objects. All sub-rules contained via `cprmv:hasPart` RDF lists are recursively included. Predicate URIs are used as keys.

!!! note
    `unformat` works with **any** output format, not only `cprmv-json`. The values extracted by the `parse` pattern are added as additional triples on the selected rule, so they also appear in the RDF serialisations (`turtle`, `n3`, `json-ld`, …). In `cprmv-json` they appear as extra keys on the rule object.

---

## RDF formats

For all non-`cprmv-json` formats, the API serialises the rule set node's triples and, recursively, those of the blank nodes it points to — in effect its [Concise Bounded Description (CBD)](https://www.w3.org/Submission/CBD/) — using rdflib's serialiser:

| `format` value | Serialisation | Notes |
|---|---|---|
| `json-ld` | JSON-LD | |
| `turtle` | Turtle | Standard Turtle |
| `ttl` | Turtle | Alias for `turtle` |
| `turtle2` | Turtle | rdflib's alternative Turtle serialiser |
| `n3` | Notation3 | |
| `xml` | RDF/XML | |

The description (built by `iterative_cbd`) includes all triples directly about the rule set node and follows blank nodes, so the `cprmv:hasPart` RDF lists and the blank-node rules they contain are included.

The API also adds the rule set's `cprmv:RuleMethod`: for each `cprmv:hasMethod` object it copies the method's `rdf:type` and `cprmv:id` from the Methods Knowledge Graph and asserts `rdf:type cprmv:RuleMethod`, so the output validates against the SHACL `RuleSetShape` and `RuleMethodShape`.

---

## Methods endpoint format

The `/methods` endpoint accepts the RDF format strings `json-ld` (default), `xml`, `turtle`, `ttl`, `n3` and `turtle2`, and serialises the entire Methods Knowledge Graph, loaded from `data/cprmvmethods.ttl` and `data/cprmv.ttl`. For any other value it returns `null`. With `method_name` it returns only the description of a node typed by that method (see [API Endpoints](../reference/api-endpoints.md#get-methods)).
