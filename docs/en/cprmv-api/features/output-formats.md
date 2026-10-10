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
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#RuleSet",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#id": "BWBR0015703_2025-07-01_0",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#validFrom": "2025-07-01",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#hasMethod": "https://cprmv.open-regels.nl/0.4.2/methods/bwb",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#hasPart": {
        "Artikel 20": {
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#Rule",
            "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#id": "Artikel 20",
            "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#hasPart": {
                "lid 1": { ... }
            }
        }
    }
}
```

(Abridged: the rule set also carries `prov:wasDerivedFrom`, `cprmv:isOutputOf` and source-specific identifiers.) All sub-rules contained via `cprmv:hasPart` RDF lists are recursively included. Predicate URIs are used as keys.

!!! note
    `unformat` works with **any** output format, not only `cprmv-json`. The values extracted by the `parse` pattern are added as additional triples on the selected rule, so they also appear in the RDF serialisations (`turtle`, `n3`, `json-ld`, …). In `cprmv-json` they appear as extra keys on the rule object.

---

## RDF formats

For all non-`cprmv-json` formats, the API serialises the [Concise Bounded Description (CBD)](https://www.w3.org/Submission/CBD/) of the rule set node using rdflib's serialiser:

| `format` value | Serialisation | Notes |
|---|---|---|
| `json-ld` | JSON-LD | |
| `turtle` | Turtle | Standard Turtle |
| `ttl` | Turtle | Alias for `turtle` |
| `turtle2` | Turtle | rdflib's alternative Turtle serialiser |
| `n3` | Notation3 | |
| `xml` | RDF/XML | |

The CBD includes all triples directly about the rule set node and follows blank nodes, so the `cprmv:hasPart` RDF lists and the blank-node rules they contain are included.

The API also adds the rule set's `cprmv:RuleMethod`: for each `cprmv:hasMethod` object it copies the method's `rdf:type` and `cprmv:id` from the Methods Knowledge Graph and asserts `rdf:type cprmv:RuleMethod`, so the output validates against the SHACL `RuleSetShape` and `RuleMethodShape`.

---

## Methods endpoint format

The `/methods` endpoint accepts the RDF format strings `json-ld` (default), `xml`, `turtle`, `ttl`, `n3` and `turtle2`, and serialises the entire Methods Knowledge Graph, loaded from `data/cprmvmethods.ttl` and `data/cprmv.ttl`. For any other value it returns `null`.
