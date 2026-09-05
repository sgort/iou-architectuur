#!/usr/bin/env node
/**
 * ts-changelog.js — read a TypeScript changelog module without parsing it as JSON.
 *
 * RONL Business API keeps its changelog in
 * `packages/frontend/src/pages/changelog-data.ts`, which `version-gap.py` cannot
 * read: unquoted keys, single quotes, trailing commas and a union type mixed
 * into `items` arrays all defeat `json.loads`. The skill previously said to read
 * that file by hand, because the obvious fix — regexing `key:` into `"key":` —
 * mangles any colon appearing inside changelog prose, and this changelog is
 * mostly prose.
 *
 * The observation that makes it easy: the file's *data* is a plain JavaScript
 * object literal. Everything TypeScript-specific is in the interfaces above it.
 * So slice off everything before the assignment, evaluate the literal as an
 * expression in a throwaway context, and hand back a real structure. No regex
 * touches the content.
 *
 * Usage:
 *   node ts-changelog.js <file.ts>                  # one line per version
 *   node ts-changelog.js <file.ts> --json           # the whole object
 *   node ts-changelog.js <file.ts> --gap 2026.08.36 # entries newer than this
 *   node ts-changelog.js <file.ts> --latest         # newest version string only
 *
 * Read the file from a ref, not the working tree:
 *   git -C ../ronl-business-api show origin/acc:packages/frontend/src/pages/changelog-data.ts > /tmp/cl.ts
 *
 * Exits non-zero if the file cannot be located or the literal cannot be
 * evaluated, rather than returning something plausible and empty.
 */

const fs = require("node:fs");
const vm = require("node:vm");

const args = process.argv.slice(2);
const path = args[0];
if (!path) {
  console.error(
    "usage: ts-changelog.js <file.ts> [--json|--latest|--gap <version>]",
  );
  process.exit(2);
}

const src = fs.readFileSync(path, "utf8");

const marker = src.indexOf("export const changelog");
if (marker === -1) {
  console.error(
    `no \`export const changelog\` in ${path} — is this the right file?`,
  );
  process.exit(1);
}
const eq = src.indexOf("=", marker);
if (eq === -1) {
  console.error("no assignment found after `export const changelog`");
  process.exit(1);
}

// Everything after the '=' is the literal, optionally followed by a semicolon
// and further exports; wrapping in parentheses makes it an expression, and the
// parser stops at the end of the literal.
let body = src.slice(eq + 1).trim();
if (body.endsWith(";")) body = body.slice(0, -1);

let changelog;
try {
  changelog = vm.runInNewContext(`(${body})`, Object.create(null), {
    timeout: 5000,
  });
} catch (err) {
  console.error(`could not evaluate the changelog literal: ${err.message}`);
  console.error(
    "If this file has grown a real TypeScript construct in its data " +
      "(a type assertion, an enum reference, a template literal with an " +
      "expression), this shim no longer applies — say so rather than " +
      "working around it.",
  );
  process.exit(1);
}

const versions = changelog?.versions;
if (!Array.isArray(versions) || versions.length === 0) {
  console.error(
    "parsed, but `versions` is missing or empty — refusing to report a gap",
  );
  process.exit(1);
}

const key = (v) =>
  String(v)
    .replace(/^v/i, "")
    .split(".")
    .map((n) => parseInt(n, 10) || 0);
const cmp = (a, b) => {
  const x = key(a);
  const y = key(b);
  for (let i = 0; i < Math.max(x.length, y.length); i++) {
    if ((x[i] ?? 0) !== (y[i] ?? 0)) return (x[i] ?? 0) - (y[i] ?? 0);
  }
  return 0;
};

if (args.includes("--json")) {
  process.stdout.write(JSON.stringify(changelog, null, 2));
  process.exit(0);
}

if (args.includes("--latest")) {
  console.log(versions[0].version);
  process.exit(0);
}

const gapIdx = args.indexOf("--gap");
if (gapIdx !== -1) {
  const from = args[gapIdx + 1];
  if (!from) {
    console.error("--gap needs a version, e.g. --gap 2026.08.36");
    process.exit(2);
  }
  const gap = versions.filter((v) => cmp(v.version, from) > 0).reverse();
  if (gap.length === 0) {
    console.log(`in sync — nothing newer than ${from}`);
    process.exit(0);
  }
  for (const v of gap) {
    const scope = Array.isArray(v.scope)
      ? v.scope.join(", ")
      : (v.scope ?? "-");
    const entries = v.commits ?? v.sections ?? [];
    const types = {};
    for (const c of entries) types[c.type] = (types[c.type] ?? 0) + 1;
    console.log(`\n${"=".repeat(78)}`);
    console.log(`## ${v.version} — ${v.date} (${v.status})  scope: ${scope}`);
    console.log(
      `   ${entries.length} entries — ` +
        Object.entries(types)
          .sort((a, b) => b[1] - a[1])
          .map(([t, n]) => `${t}=${n}`)
          .join(" "),
    );
    console.log("=".repeat(78));
    for (const c of entries) {
      console.log(
        `\n### ${c.sha ?? ""} [${c.type ?? "?"}] ${c.subject ?? c.title ?? ""}`,
      );
      for (const d of c.details ?? c.items ?? []) {
        console.log(`  - ${typeof d === "string" ? d : JSON.stringify(d)}`);
      }
    }
  }
  process.exit(0);
}

for (const v of versions) {
  const scope = Array.isArray(v.scope) ? v.scope.join("+") : (v.scope ?? "-");
  const n = (v.commits ?? v.sections ?? []).length;
  console.log(
    `${String(v.version).padEnd(12)} ${String(v.date).padEnd(14)} ` +
      `${String(v.status).padEnd(10)} scope=${scope.padEnd(28)} ${n} entries`,
  );
}
