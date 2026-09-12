---
component: RONL Business API
---

# Shared Package

`packages/shared` (`@ronl/shared`) carries the TypeScript types and constant data shared across the workspace — and, deliberately, no logic at all. It has no runtime dependencies and must be built before a consuming package can be built or type-checked.

It is consumed by the backend, the frontend and the PA-demo. The demo's imports are **type-only** and erased before the bundler sees them, so a shared-only change cannot alter its compiled output — but `packages/shared/**` still appears in the demo's CI path filter, so that a breaking type change fails there rather than surfacing later at an unrelated pull request.

!!! note "This is not the only workspace package"
    [`@ronl/pa-cockpit`](pa-cockpit-package.md) is the other one: the Public Affairs cockpit, imported by both the caseworker frontend and the public demo. Unlike `shared` it ships React components and carries a host contract.

---

## Build

```bash
npm run build --workspace=@ronl/shared
```

Output is written to `packages/shared/dist/`. Both `@ronl/backend` and `@ronl/frontend` reference `@ronl/shared: "*"` in their `package.json`, resolving to the `dist/index.js` and `dist/index.d.ts` files.

---

## Contents

The shared package exports the TypeScript types used across the system. Key interfaces include:

**`ApiResponse<T>`** — standard response envelope used by all backend endpoints:
```typescript
interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: { code: string; message: string; };
  timestamp: string;
}
```

**`TenantConfig`** — municipality tenant configuration shape:
```typescript
interface TenantConfig {
  id: string;
  name: string;
  displayName: string;
  municipalityCode: string;
  theme: TenantTheme;
  features: TenantFeatures;
  contact: TenantContact;
  enabled: boolean;
}
```

**`JwtClaims`** — decoded JWT payload type for `req.user`:
```typescript
interface JwtClaims {
  sub: string;
  municipality: string;
  roles: string[];
  loa: string;
  preferred_username: string;
  mandate?: string;
  bsn?: string;
}
```

---

## Kept declarations-only

`@ronl/shared` holds types and constant data, and nothing that executes. That is a checked property rather than a habit: `npm run check-shared` enforces it from the [`audit` job](cicd.md#audit-the-required-check), on every pull request.

**Why it needs a check at all.** The per-file 80% branch floor is enforced in the five workspaces that have a test runner. This package is not one of them, so a function placed here is not under-tested — it is outside the measurement entirely, and nothing signals that: no run fails and no number moves. v2026.09.4 moved a branching label helper back out of this package for exactly that reason, found by hand rather than by any check.

**Why the TypeScript compiler API rather than a pattern over text.** A regex cannot tell `(x: string) => void` inside an interface — a `FunctionType`, which is precisely what this package is for — from the same syntax assigned to a `const`, which is an `ArrowFunction` and is not. It would also miss a function expression assigned to a const. The parser knows the difference, and a check with false positives gets disabled. Flagged: function declarations and expressions, arrow functions, class declarations, method implementations, and the branching statements — `if`, `switch`, a ternary, the four loop forms, and `try`/`catch`. Not flagged: `FunctionType` and `MethodSignature`, and every type-level construct.

**Why the `audit` job rather than a workspace suite.** `audit` carries no paths filter and is the required check, so every pull request reaches it. A suite that only ran when `packages/shared/**` changed would not catch the pull request that adds the first function to a package that filter does not yet watch. Giving this package its own test runner was the other option, and it is worse today: with no executable lines to measure, the runner would report a green check over an empty set — the same false comfort the coverage floor exists to remove.

A passing run reads:

```
check-shared-declarations: 11 file(s) in packages/shared/src/ — declarations and constant data only.
```

A failure names the file, the line, and where the logic should live instead. If the package ever genuinely needs runtime logic, the documented path is to give it a Vitest runner with the same per-file floor and delete the script — a deliberate change, not a workaround.

---

## Development workflow

When you modify a type in `packages/shared/src/`, both the backend and frontend need to pick up the change:

```bash
# Rebuild shared
npm run build --workspace=@ronl/shared

# tsx watch (backend) and Vite HMR (frontend) pick up the rebuilt types automatically
# If they don't, restart npm run dev
```

The pre-push Husky hook runs `npm run type-check` across all workspaces, which catches type mismatches between shared types and their consumers before the push reaches CI.
