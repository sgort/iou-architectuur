#!/usr/bin/env python3
"""
shacl_to_graphml.py

Converts a SHACL shapes file (Turtle) to GraphML for visualization in yEd.

Pipeline:
  .ttl  →[rdflib]→  RDF/XML  →[saxonche + rdf2graphml.xsl]→  .graphml

The XSL transform (rdf2graphml.xsl) is expected in the same directory as this
script, or can be specified with --xsl.

Usage:
    python shacl_to_graphml.py <input.ttl> [output.graphml] [--xsl path/to/rdf2graphml.xsl]

Examples:
    python shacl_to_graphml.py ../linked-data-explorer/packages/backend/shapes/cprmv/0.4.1/cprmv.shacl.ttl
    python shacl_to_graphml.py ../linked-data-explorer/packages/backend/shapes/cpsv-ap/3.2.0/cpsv-ap-SHACL.ttl docs/assets/diagrams/cpsv-ap.graphml
"""

import sys
import argparse
import tempfile
from pathlib import Path

import rdflib
from rdflib.namespace import RDF, SH
import saxonche

# Namespaces that are commonly used by full URI in SHACL files but lack @prefix
# declarations — bind them so qname() produces readable prefixed names.
_WELL_KNOWN_PREFIXES: dict[str, str] = {
    "dc":    "http://purl.org/dc/terms/",    # rdflib prefers dcterms: → dc1: without this
    "cpsv":  "http://purl.org/vocab/cpsv#",
    "clv":   "http://data.europa.eu/m8g/",
    "eli":   "http://data.europa.eu/eli/ontology#",
    "locn":  "http://www.w3.org/ns/locn#",
    "time":  "http://www.w3.org/2006/time#",
    "a4g":   "http://data.europa.eu/a4g/ontology#",
}


def _try_qname(g: rdflib.Graph, uri: rdflib.URIRef) -> str | None:
    """Return a prefixed name for uri, or None.

    Checks _WELL_KNOWN_PREFIXES first so we never get rdflib's auto-generated
    variants like dc1: or ns2: for namespaces in that table.
    """
    uri_str = str(uri)
    for prefix, ns_uri in _WELL_KNOWN_PREFIXES.items():
        if uri_str.startswith(ns_uri):
            local = uri_str[len(ns_uri):]
            if local and "/" not in local and "#" not in local:
                return f"{prefix}:{local}"
    try:
        qn = g.namespace_manager.qname(uri_str)
        return qn if ":" in qn else None
    except Exception:
        return None


def add_prefixed_labels(g: rdflib.Graph) -> None:
    """Enrich the graph with sh:name literals derived from prefixed URIs.

    - NodeShapes without sh:name get one from sh:targetClass (e.g. "cpsv:PublicService")
    - Property shapes without sh:name get one from sh:path  (e.g. "dct:description")

    The XSL's label template already prefers sh:name, so this is all that's needed.
    """
    for shape in g.subjects(RDF.type, SH.NodeShape):
        if (shape, SH.name, None) in g:
            continue
        target = g.value(shape, SH.targetClass)
        if target:
            qn = _try_qname(g, target)
            if qn:
                g.add((shape, SH.name, rdflib.Literal(qn)))

    for prop_shape, _, path in g.triples((None, SH.path, None)):
        if (prop_shape, SH.name, None) in g:
            continue
        if isinstance(path, rdflib.URIRef):
            qn = _try_qname(g, path)
            if qn:
                g.add((prop_shape, SH.name, rdflib.Literal(qn)))


def ttl_to_rdfxml(ttl_path: Path) -> str:
    g = rdflib.Graph()
    g.parse(str(ttl_path), format="turtle")
    # Bind well-known prefixes that SHACL files often omit so qname() stays readable.
    for prefix, uri in _WELL_KNOWN_PREFIXES.items():
        g.namespace_manager.bind(prefix, rdflib.Namespace(uri), override=True)
    add_prefixed_labels(g)
    return g.serialize(format="xml")


def wrap_in_root(rdfxml: str) -> str:
    # rdf2graphml.xsl matches /ROOT/rdf:RDF — wrap accordingly.
    # Strip the XML declaration so it doesn't end up inside <ROOT>.
    body = "\n".join(
        line for line in rdfxml.splitlines()
        if not line.startswith("<?xml")
    )
    return f"<ROOT>\n{body}\n</ROOT>"


def convert(ttl_path: Path, xsl_path: Path, out_path: Path) -> None:
    print(f"Reading  : {ttl_path}")
    rdfxml = ttl_to_rdfxml(ttl_path)
    wrapped = wrap_in_root(rdfxml)

    # Saxon needs a real file path; write a temp file then delete after transform.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".xml", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(wrapped)
        tmp_path = Path(tmp.name)

    try:
        print(f"Applying : {xsl_path.name}")
        with saxonche.PySaxonProcessor(license=False) as proc:
            xslt = proc.new_xslt30_processor()
            exe = xslt.compile_stylesheet(stylesheet_file=str(xsl_path.resolve()))
            exe.transform_to_file(
                source_file=str(tmp_path),
                output_file=str(out_path.resolve()),
            )
    finally:
        tmp_path.unlink(missing_ok=True)

    print(f"Written  : {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert a SHACL Turtle file to GraphML (yEd format)"
    )
    parser.add_argument("input", type=Path, help="Input .ttl file")
    parser.add_argument("output", nargs="?", type=Path, help="Output .graphml file (default: input with .graphml extension)")
    parser.add_argument("--xsl", type=Path, help="Path to rdf2graphml.xsl (default: same dir as this script)")
    args = parser.parse_args()

    ttl_path: Path = args.input
    if not ttl_path.exists():
        print(f"Error: input file not found: {ttl_path}", file=sys.stderr)
        sys.exit(1)

    xsl_path: Path = args.xsl or Path(__file__).parent / "rdf2graphml.xsl"
    if not xsl_path.exists():
        print(f"Error: XSL not found: {xsl_path}", file=sys.stderr)
        print("Pass --xsl <path> or place rdf2graphml.xsl next to this script.", file=sys.stderr)
        sys.exit(1)

    out_path: Path = args.output or ttl_path.with_suffix(".graphml")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    convert(ttl_path, xsl_path, out_path)


if __name__ == "__main__":
    main()
