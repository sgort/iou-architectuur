# Frontend Development

The frontend is `packages/frontend` (`@ronl/frontend`) — a React 18 + TypeScript SPA built with Vite.

## Project structure

```
packages/frontend/src/
├── App.tsx                     # Root component, environment detection, layout
├── main.tsx                    # React entry point, StrictMode
├── index.css                   # Global CSS (Tailwind base + custom properties)
├── components/                 # UI components
├── contexts/                   # React contexts (auth, tenant)
├── hooks/                      # Custom React hooks
├── services/
│   ├── keycloak.ts             # Keycloak JS adapter initialisation
│   ├── api.ts                  # Business API HTTP client (Axios)
│   └── tenant.ts               # Tenant config loading and theme application
└── themes/                     # Per-municipality theme tokens
packages/frontend/public/
└── tenants.json                # Municipality configurations (loaded at runtime)
```

## Authentication with Keycloak JS

`services/keycloak.ts` initialises the Keycloak JS adapter on app start:

```typescript
const keycloak = new Keycloak({
  url: import.meta.env.VITE_KEYCLOAK_URL,
  realm: 'ronl',
  clientId: 'ronl-business-api',
});
```

The adapter checks for an existing session token. If none is found, it redirects the user to Keycloak automatically. On successful authentication, `keycloak.token` holds the JWT access token, which is included in all subsequent API calls.

Token refresh is handled automatically by the adapter before the 15-minute expiry.

## Multi-tenant theming

On successful login, `services/tenant.ts` reads the `municipality` claim from the decoded JWT and applies the corresponding theme:

```typescript
await initializeTenantTheme(keycloak.tokenParsed.municipality);
```

`initializeTenantTheme` loads `public/tenants.json`, finds the matching entry, and calls `applyTenantTheme`, which sets CSS custom properties on `document.documentElement`:

```typescript
root.style.setProperty('--color-primary', theme.primary);
root.style.setProperty('--color-primary-dark', theme.primaryDark);
// ...
```

All Tailwind utility classes and component styles reference these custom properties, so the entire UI re-themes without a page reload.

## API client

`services/api.ts` wraps Axios and adds the JWT bearer token to every request:

```typescript
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

client.interceptors.request.use((config) => {
  config.headers.Authorization = `Bearer ${keycloak.token}`;
  return config;
});
```

If a request returns HTTP 401 (token expired between refresh cycles), the interceptor triggers a silent Keycloak refresh and retries.

## Environment variables

| Variable | Description | Example |
|---|---|---|
| `VITE_API_URL` | Business API base URL | `http://localhost:3002/v1` |
| `VITE_KEYCLOAK_URL` | Keycloak base URL | `http://localhost:8080` |

Three `.env` files are used for different deployments:
- `.env` — local development
- `.env.acceptance` — ACC deployment
- `.env.production` — production deployment

The Vite build command specifies which file to use: `vite build --mode acceptance`.

## Development commands

```bash
npm run dev           # Vite dev server with HMR on http://localhost:5173
npm run build         # Production build → dist/
npm run build:acc     # Acceptance build (uses .env.acceptance)
npm run build:prod    # Production build (uses .env.production)
npm run lint          # ESLint
npm run lint:fix      # ESLint with auto-fix
npm run type-check    # tsc --noEmit
```

## Adding a new page

1. Create a component in `src/components/`
2. Add a route in `App.tsx`
3. If the page requires authentication, wrap it with the auth context guard
4. Apply Tailwind classes using `var(--color-primary)` for municipality-branded colours

## Adding a feature flag check

```typescript
import { useTenant } from '../contexts/TenantContext';

const { features } = useTenant();

if (!features.zorgtoeslag) {
  return <p>Deze dienst is niet beschikbaar voor uw gemeente.</p>;
}
```
