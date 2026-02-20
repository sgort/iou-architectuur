# Shared Package

`packages/shared` (`@ronl/shared`) contains TypeScript types and utilities shared between the backend and frontend packages. It has no runtime dependencies and must be built before either package can consume it.

## Build

```bash
npm run build --workspace=@ronl/shared
```

Output is written to `packages/shared/dist/`. Both `@ronl/backend` and `@ronl/frontend` reference `@ronl/shared: "*"` in their `package.json`, resolving to the `dist/index.js` and `dist/index.d.ts` files.

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

## Development workflow

When you modify a type in `packages/shared/src/`, both the backend and frontend need to pick up the change:

```bash
# Rebuild shared
npm run build --workspace=@ronl/shared

# tsx watch (backend) and Vite HMR (frontend) pick up the rebuilt types automatically
# If they don't, restart npm run dev
```

The pre-push Husky hook runs `npm run type-check` across all workspaces, which catches type mismatches between shared types and their consumers before the push reaches CI.
