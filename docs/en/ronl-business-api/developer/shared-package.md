---
component: RONL Business API
---

# Shared Package

`packages/shared` (`@ronl/shared`) contains TypeScript types and utilities shared across the workspace. It has no runtime dependencies and must be built before a consuming package can be built or type-checked.

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

## Development workflow

When you modify a type in `packages/shared/src/`, both the backend and frontend need to pick up the change:

```bash
# Rebuild shared
npm run build --workspace=@ronl/shared

# tsx watch (backend) and Vite HMR (frontend) pick up the rebuilt types automatically
# If they don't, restart npm run dev
```

The pre-push Husky hook runs `npm run type-check` across all workspaces, which catches type mismatches between shared types and their consumers before the push reaches CI.
