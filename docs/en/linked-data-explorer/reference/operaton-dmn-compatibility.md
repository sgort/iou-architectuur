# Operaton DMN Compatibility Checklist

A practical checklist for authoring DMN files that deploy and execute correctly in Operaton (the open-source Camunda 7 CE fork). Work through this list when a DMN fails to deploy or produces unexpected results.

---

## 1) Namespace and DMN version

- ✅ Use DMN 1.3 namespace: `xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/"`
- ✅ Avoid DMN 1.1 namespace — Operaton supports 1.1 but behaviour may differ for newer features
- ✅ Verify `<definitions>` has a valid `namespace` attribute and a unique `id`

---

## 2) Decision IDs and references

- ✅ Every `<decision>` element must have a unique `id` attribute
- ✅ `<requiredDecision href="#...">` must reference the `id` of another `<decision>` in the same `<definitions>`, not its `name`
- ✅ `<informationRequirement>` elements need their own unique `id` attribute
- ✅ Avoid duplicate `id` values anywhere in the document — even across `<dmndi:DMNDI>` elements

---

## 3) FEEL expressions

- ✅ Use `not(x)` — **not** `not x` (the latter is a unary test, not a negation function)
- ✅ Unary test intervals: `[a..b)`, `(a..b]`, `[a..b]` — parentheses for exclusive bounds
- ✅ `and` / `or` in unary tests refer to multiple unary conditions on the same input — do not use them as Boolean operators in FEEL expressions
- ✅ String literals must use double quotes: `"active"`, not `'active'`
- ✅ Date literals: `date("2026-01-01")`, not bare strings
- ✅ Test FEEL expressions in isolation with the Operaton REST API `evaluate` endpoint before deploying a full DRD

---

## 4) Variable naming and types

- ✅ Use simple variable names (letters, digits, underscore). Avoid spaces and punctuation in variable names referenced by FEEL.
- ✅ In FEEL, reference **runtime variables** (the `<variable name="...">`) rather than element IDs
- ✅ Keep numeric types consistent — `Integer` vs `Double` differences between request and DMN declaration cause runtime type errors

---

## 5) Null / missing inputs

If a required input may be absent, Operaton may throw a runtime error rather than producing a null output.

- ✅ Use null-safe FEEL where inputs may be missing: `x = false` is safer than `not(x)` when `x` can be null
- ✅ Use `if x = null then … else …` for optional inputs
- ✅ For optional inputs, provide defaults in FEEL expressions: `if medischeVerklaring = true then true else missendeMaand = false`

---

## 6) DMNDI (diagram section)

The engine ignores the `<dmndi:DMNDI>` block for execution, but the Operaton Modeler and UI use it for rendering.

- ✅ Avoid multiple DI elements referencing the same `dmnElementRef`
- ✅ `<dmndi:DMNEdge>` `dmnElementRef` must reference an `<informationRequirement>` ID, not a `<decision>` ID
- ✅ If deployment fails and you cannot isolate the cause, temporarily remove the entire `<dmndi:DMNDI>…</dmndi:DMNDI>` block, deploy without it, and re-add once the execution logic is confirmed working

---

## 7) Operaton-specific extensions

- ✅ If Operaton enforces history cleanup TTL, set `camunda:historyTimeToLive="..."` on `<decision>` elements (or configure a global default in the engine)
- ✅ Keep extension namespaces consistent: `xmlns:camunda="http://camunda.org/schema/1.0/dmn"`

---

## 8) Deployment debugging workflow

If you see `ENGINE-22004 Unable to transform DMN resource …`:

1. Verify DMN namespace and version (DMN 1.1 vs 1.3)
2. Check for broken `href="#..."` references — the target `id` must exist
3. Check FEEL parsing: `not x` vs `not(x)`, unary test `and/or` vs Boolean `and/or`
4. Temporarily remove `<dmndi:DMNDI>` to rule it out
5. Inspect Operaton server logs immediately after `ENGINE-22004` for the underlying parse error — the 22004 message is a wrapper; the actual cause is one line below it

---

## 9) Testing strategy

- ✅ Test leaf decisions first (single-input literal expressions) before testing a full DRD
- ✅ When testing a decision that depends on others, provide the full upstream input set — unless you have made all inputs null-safe
- ✅ Maintain one "superset" JSON payload covering all possible inputs for the chain, usable for quick regression testing across DMN versions
