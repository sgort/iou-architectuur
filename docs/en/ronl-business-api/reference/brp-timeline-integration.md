---
component: RONL Business API
---

# BRP Timeline Integration - Technical Architecture

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                      Browser (Citizen)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          Municipality Frontend (React)                   │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │  Timeline  │  │  BRP Service │  │ Historical State │  │  │
│  │  │ Component  │→ │   (brp.api)  │→ │   Calculation    │  │  │
│  │  └────────────┘  └──────────────┘  └──────────────────┘  │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │ JWT Token                          │
└───────────────────────────┼────────────────────────────────────┘
                            │ HTTPS
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                Business API (Node.js/Express)                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  POST /v1/brp/personen (Proxy Route)                    │  │
│  │  ┌──────────────┐  ┌────────────┐  ┌────────────────┐   │  │
│  │  │ JWT Validate │→ │ Audit Log  │→ │ Forward to BRP │   │  │
│  │  └──────────────┘  └────────────┘  └────────────────┘   │  │
│  └─────────────────────────┬───────────────────────────────┘  │
└────────────────────────────┼──────────────────────────────────┘
                             │ HTTPS
                             ↓
┌───────────────────────────────────────────────────────────────┐
│          BRP API (Haal Centraal - External Service)           │
│              https://brp-api-mock.open-regels.nl              │
└───────────────────────────────────────────────────────────────┘
```

---

## Component Structure

### Frontend Components

```
packages/frontend/src/
├── components/
│   ├── Timeline.tsx              # Interactive timeline UI
│   └── PersonalDataPanel.tsx     # Dynamic data display
├── services/
│   ├── brp.api.ts               # BRP API client (via proxy)
│   ├── brp.timeline.ts          # Timeline logic & state calculation
│   └── bsn.mapping.ts           # Test user BSN mapping
├── types/
│   └── brp.types.ts             # BRP data type definitions
└── pages/
    └── Dashboard.tsx            # Main page with timeline toggle
```

### Backend Routes

```
packages/backend/src/
└── routes/
    └── brp.routes.ts            # POST /v1/brp/personen proxy
```

---

## Data Flow

### 1. Timeline Initialization

```typescript
User clicks "Toon Tijdlijn"
    ↓
Dashboard.tsx triggers useEffect
    ↓
getUserBSN(user) → Maps username to BSN (test env)
    ↓
getPersonTimeline(bsn) called
    ↓
brpApi.getPersonByBSN(bsn)
    ↓
POST https://acc.api.open-regels.nl/v1/brp/personen
    ↓
Backend validates JWT, logs, forwards to BRP API
    ↓
BRP API returns current person data
    ↓
extractEvents() finds life events from data
    ↓
Timeline component renders with events
```

### 2. Date Selection & State Update

```typescript
User drags slider or clicks event button
    ↓
Timeline.onDateChange(newDate) triggered
    ↓
Dashboard updates selectedDate state
    ↓
calculateHistoricalState(currentState, targetDate)
    ↓
Filter partner: targetDate >= marriageDate?
Filter children: targetDate >= birthDate?
Update ages: Math.floor((targetDate - birthDate) / year)
    ↓
PersonalDataPanel re-renders with historical data
```

---

## Backend Proxy Implementation

### Why We Need a Proxy

**Problem:** Browser CORS policy blocks direct calls from `localhost:5173` to `brp-api-mock.open-regels.nl`

**Solution:** Route through our backend which:

1. Accepts authenticated frontend requests
2. Validates JWT tokens
3. Audits each lookup, while keeping the BSN out of the application log
4. Forwards to BRP API
5. Wraps the BRP answer in `{ success: true, data }`, and answers errors as RFC 9457 problem details

### Route Implementation

**File:** `packages/backend/src/routes/brp.routes.ts`

```typescript
import express, { Request, Response } from 'express';
import axios from 'axios';
import jwtMiddleware from '../auth/jwt.middleware';
import { auditLog } from '../middleware/audit.middleware';
import { createLogger } from '../utils/logger';
import { sendProblem } from '../utils/problem';

const router = express.Router();
const logger = createLogger('brp-routes');

const BRP_API_BASE_URL = 'https://brp-api-mock.open-regels.nl/haalcentraal/api/brp';

/**
 * POST /v1/brp/personen
 * Proxy to BRP API to avoid CORS issues in frontend
 */
router.post('/personen', jwtMiddleware, async (req: Request, res: Response) => {
  try {
    // Never log req.body or an upstream body: both carry BSNs (#241). The audit
    // log below records the subject on purpose; the application log must not.
    const query = req.body as { type?: string; burgerservicenummer?: unknown };
    logger.info('BRP personen request', {
      userId: req.user?.userId,
      tenantId: req.user?.tenantId,
      queryType: query?.type,
      bsnCount: Array.isArray(query?.burgerservicenummer) ? query.burgerservicenummer.length : 0,
    });

    // Forward request to BRP API - match curl headers exactly
    const response = await axios.post(`${BRP_API_BASE_URL}/personen`, req.body, {
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        Accept: 'application/json', // ✅ BE EXPLICIT
      },
      timeout: 10000,
      validateStatus: (status) => status < 500, // ✅ Don't throw on 4xx
    });

    // Check if response was successful
    if (response.status >= 400) {
      const upstreamCode = (response.data as { code?: unknown } | undefined)?.code;
      logger.error('BRP API returned error', {
        status: response.status,
        upstreamCode: typeof upstreamCode === 'string' ? upstreamCode : undefined,
      });

      return sendProblem(res, req, {
        status: response.status,
        code: 'BRP_API_ERROR',
        detail: 'BRP API returned an error',
        extensions: { details: response.data },
      });
    }

    // Log successful request
    auditLog(req, 'brp.personen.fetch', 'success', {
      bsn: req.body.burgerservicenummer?.[0],
    });

    res.json({
      success: true,
      data: response.data,
    });
  } catch (error) {
    logger.error('BRP API request failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
      userId: req.user?.userId,
      upstreamStatus: axios.isAxiosError(error) ? error.response?.status : undefined,
    });

    auditLog(req, 'brp.personen.fetch', 'error', {
      error: error instanceof Error ? error.message : 'Unknown error',
    });

    const statusCode = axios.isAxiosError(error) ? error.response?.status || 500 : 500;
    const message = axios.isAxiosError(error)
      ? error.response?.data?.message || error.message
      : 'BRP API request failed';

    sendProblem(res, req, { status: statusCode, code: 'BRP_API_ERROR', detail: message });
  }
});

export default router;
```

**Registration in `packages/backend/src/routes/registry.ts`:** `index.ts` mounts every entry of `routeRegistry`, in array order.

```typescript
{ mount: '/v1/brp', router: brpRoutes, advertiseAs: 'brp', summary: 'Personal records lookup' },
```

---

## Historical State Calculation

### Algorithm

The timeline doesn't store historical snapshots. Instead, it **derives** historical state from:
1. Current BRP data (source of truth)
2. Event dates (marriage, births)
3. Selected target date

### Implementation

**File:** `packages/frontend/src/services/brp.timeline.ts`

```typescript
export function calculateHistoricalState(
  currentState: PersonState,
  targetDate: Date
): PersonState | null {
  const birthDate = new Date(currentState.geboorte.datum.datum);
  
  // Person not born yet
  if (targetDate < birthDate) {
    return null;
  }

  // Calculate age at target date
  const age = Math.floor(
    (targetDate.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25)
  );

  // Start with basic person data
  const historicalState: PersonState = {
    ...currentState,
    leeftijd: age,
  };

  // Filter partners based on marriage date
  if (currentState.partners && currentState.partners.length > 0) {
    historicalState.partners = currentState.partners.filter((partner) => {
      const marriageDate = new Date(partner.aangaanHuwelijkPartnerschap.datum.datum);
      return targetDate >= marriageDate;
    });

    if (historicalState.partners.length === 0) {
      delete historicalState.partners; // Hide section if no partners at this date
    }
  }

  // Filter children and update ages
  if (currentState.kinderen && currentState.kinderen.length > 0) {
    historicalState.kinderen = currentState.kinderen
      .filter((kind) => {
        const childBirthDate = new Date(kind.geboorte.datum.datum);
        return targetDate >= childBirthDate;
      })
      .map((kind) => {
        const childBirthDate = new Date(kind.geboorte.datum.datum);
        const childAge = Math.floor(
          (targetDate.getTime() - childBirthDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25)
        );
        return {
          ...kind,
          leeftijd: childAge >= 0 ? childAge : undefined,
        };
      });

    if (historicalState.kinderen.length === 0) {
      delete historicalState.kinderen; // Hide section if no children at this date
    }
  }

  return historicalState;
}
```

### Event Extraction

```typescript
export function extractEvents(personState: PersonState): BRPEvent[] {
  const events: BRPEvent[] = [];

  // Birth event
  events.push({
    id: 'birth',
    type: 'birth',
    date: new Date(personState.geboorte.datum.datum),
    label: 'Geboren',
    description: `Geboorte ${personState.naam.volledigeNaam}`,
  });

  // Marriage events
  if (personState.partners) {
    personState.partners.forEach((partner, idx) => {
      events.push({
        id: `marriage-${idx}`,
        type: 'marriage',
        date: new Date(partner.aangaanHuwelijkPartnerschap.datum.datum),
        label: 'Getrouwd',
        description: `Huwelijk met ${partner.naam.voornamen} ${partner.naam.geslachtsnaam}`,
      });
    });
  }

  // Children birth events (grouped by date for twins/triplets)
  if (personState.kinderen) {
    const childrenByDate = new Map<string, typeof personState.kinderen>();
    
    personState.kinderen.forEach((kind) => {
      const dateKey = kind.geboorte.datum.datum;
      if (!childrenByDate.has(dateKey)) {
        childrenByDate.set(dateKey, []);
      }
      childrenByDate.get(dateKey)!.push(kind);
    });

    childrenByDate.forEach((children, dateKey) => {
      const birthDate = new Date(dateKey);
      
      if (children.length === 1) {
        events.push({
          id: `child-birth-${children[0].burgerservicenummer}`,
          type: 'birth',
          date: birthDate,
          label: 'Kind geboren',
          description: `Geboorte ${children[0].naam.voornamen}`,
        });
      } else {
        const count = children.length === 2 ? 'tweeling' : children.length === 3 ? 'drieling' : `${children.length}-ling`;
        events.push({
          id: `child-birth-${dateKey}`,
          type: 'birth',
          date: birthDate,
          label: `Kinderen geboren (${count})`,
          description: `Geboorte ${children.map((k) => k.naam.voornamen).join(', ')}`,
        });
      }
    });
  }

  return events.sort((a, b) => a.date.getTime() - b.date.getTime());
}
```

---

## BSN Mapping for Test Environment

In production, BSN comes from DigiD via Keycloak. For testing, we map usernames to BSNs.

**File:** `packages/frontend/src/services/bsn.mapping.ts`

```typescript
/**
 * Maps Keycloak test usernames to BSN numbers for BRP API demo
 * In production, BSN should come from DigiD via Keycloak user attributes
 */

export const testUserBSNMapping: Record<string, string> = {
  'test-citizen-utrecht': '999992235', // Wessel Kooyman
  'test-caseworker-utrecht': '999992235', // Same person for demo
  'test-citizen-amsterdam': '999992235', // For now, same test data
  'test-citizen-rotterdam': '999992235', // For now, same test data
  'test-citizen-denhaag': '999992235', // For now, same test data
  'test-citizen-flevoland': '999992235', // For now, same test data
};

/**
 * Get BSN for current user
 * First tries user.bsn attribute from JWT
 * Falls back to username mapping for test users
 */
export function getUserBSN(user: {
  sub: string;
  preferred_username?: string;
  bsn?: string;
}): string | null {
  // If BSN is in the JWT (production with DigiD), use it
  if (user.bsn) {
    return user.bsn;
  }

  // For test users, map username to BSN
  if (user.preferred_username && user.preferred_username in testUserBSNMapping) {
    return testUserBSNMapping[user.preferred_username];
  }

  // No BSN available. Logs the username only, not the whole claims object:
  // this branch cannot carry a BSN (it is the one where there isn't one), but
  // `user` also holds `sub` and whatever else the token brought, and none of
  // that is needed to explain the warning.
  console.warn('No BSN found for user', user.preferred_username ?? '(no username)');
  return null;
}
```

---

## Security Considerations

### Authentication & Authorization

1. **JWT Validation** - All `/v1/brp/personen` requests require valid JWT token
2. **User Context** - The frontend derives the BSN from the authenticated user. The backend does not check it: the route answers for any BSN in the request body
3. **Audit Logging** - Each lookup is audited as `brp.personen.fetch`, with the queried BSN; the application log carries neither the request body nor the upstream body
4. **Rate Limiting** - The Business API's global limiter applies

### Privacy

- **No Data Storage** - Timeline calculations done client-side, no persistence
- **Encrypted Transit** - All communication over HTTPS
- **Audit Trail** - No retention period is applied; nothing purges audit records

### DigiD Integration

For production with real DigiD:

1. **LoA Requirement** - Timeline requires DigiD LoA "hoog" (substantial assurance)
2. **BSN in Token** - DigiD provides BSN via SAML → Keycloak → JWT
3. **Session Management** - Keycloak handles DigiD session timeout
4. **Mandate Support** - (Future) Representatives can view citizen timelines with proper mandate

---

## Performance Considerations

### Caching Strategy

**Current:** No caching (real-time BRP data)

**Future Optimization:**

- Cache BRP responses for 5 minutes (Redis)
- Invalidate on known events (marriage registration, birth)
- Cache key: `brp:person:${bsn}`

### Load Times

Typical timeline load:

1. BRP API call: ~500-1000ms
2. Event extraction: <10ms
3. Historical state calculation: <5ms per date change
4. Total initial load: ~1-1.5 seconds

### Scalability

- **Backend Proxy** - Stateless, horizontally scalable
- **BRP API** - External service, rate limits apply
- **Client Calculation** - No server load for date changes

---

## Error Handling

### Frontend

```typescript
try {
  const data = await getPersonTimeline(bsn);
  setTimelineData(data);
} catch (error) {
  console.error('Failed to load timeline:', error);
  // Show user-friendly error message
  setIsLoadingTimeline(false);
}
```

### Backend

A BRP answer of 4xx is passed on with its own status, code `BRP_API_ERROR` and the upstream body in a `details` extension member. A thrown error — a 5xx, a timeout, no connection — ends in the `catch`, which answers with the upstream status (or `500`) and the message as `detail`:

```typescript
const statusCode = axios.isAxiosError(error) ? error.response?.status || 500 : 500;
const message = axios.isAxiosError(error)
  ? error.response?.data?.message || error.message
  : 'BRP API request failed';

sendProblem(res, req, { status: statusCode, code: 'BRP_API_ERROR', detail: message });
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 406 Not Acceptable | Missing Accept header | Added explicit `Accept: application/json` |
| 401 Unauthorized | Invalid/expired JWT | User must re-login |
| 404 Not Found | BSN not in BRP | Verify BSN mapping |
| 500 Server Error | BRP API down | Retry or show maintenance message |
| Network Error | CORS or connectivity | Check proxy configuration |

---

## Configuration Changes Required

### 1. Keycloak Protocol Mapper

**Add `preferred_username` to JWT token:**

1. Keycloak Admin Console → Realms → `ronl`
2. Clients → `ronl-business-api`
3. Client scopes → `ronl-business-api-dedicated`
4. Mappers → Add mapper → By configuration → User Property
5. Configure:
   - **Name**: `username`
   - **Property**: `username`
   - **Token Claim Name**: `preferred_username`
   - **Claim JSON Type**: `String`
   - **Add to ID token**: ON
   - **Add to access token**: ON
   - **Add to userinfo**: ON
6. Save

**Why:** Frontend needs `preferred_username` to map test users to BSN numbers.

### 2. Backend TypeScript Configuration

**Remove `composite: true` from `packages/backend/tsconfig.json`:**

```json
{
  "compilerOptions": {
    // ... all existing settings ...
    // ❌ REMOVE THIS LINE:
    // "composite": true
  },
  "include": ["src/**/*", "package.json"],
  "exclude": ["node_modules", "dist", "tests"]
  // ❌ REMOVE THIS LINE:
  // "references": [{ "path": "../shared" }]
}
```

**Why:** Project references caused type-checking errors. The path alias `"@ronl/shared": ["../shared/src"]` was removed, and imports now resolve via npm workspaces to the compiled `dist` folder.

### 3. Shared Package TypeScript Configuration

**`packages/shared/tsconfig.json` - Keep simple:**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
    // ❌ NO composite: true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**Why:** The `composite: true` setting was preventing proper `.d.ts` file generation.

---

## Deployment Notes

### Manual Backend Deployment

```bash
# 1. Rebuild shared package (important after type changes)
cd packages/shared
npm run build

# 2. Build backend
cd ../backend
npm run build

# 3. Prepare deployment package
mkdir -p deploy
cp -r dist deploy/
cp package.json deploy/
mkdir -p deploy/node_modules/@ronl
cp -r ../shared/dist deploy/node_modules/@ronl/shared
cp ../shared/package.json deploy/node_modules/@ronl/shared/

# 4. Install production dependencies
cd deploy && npm install --production --omit=dev && cd ..

# 5. Create zip and deploy
cd deploy
zip -r ../deployment-acc.zip .
cd ..

az webapp deploy \
  --name ronl-business-api-acc \
  --resource-group rg-ronl-acc \
  --src-path deployment-acc.zip \
  --type zip

# 6. Cleanup
rm -rf deploy deployment-acc.zip
```

### Frontend Deployment Workflow

**Update `.github/workflows/azure-frontend-acc.yml`:**

```yaml
- name: Update API URLs for ACC
  working-directory: packages/frontend
  run: |
    sed -i "s|http://localhost:3002/v1|https://acc.api.open-regels.nl/v1|g" src/services/api.ts
    sed -i "s|http://localhost:3002/v1|https://acc.api.open-regels.nl/v1|g" src/services/brp.api.ts
    sed -i "s|http://localhost:8080|https://acc.keycloak.open-regels.nl|g" src/services/keycloak.ts
```

**Why:** The new `brp.api.ts` file also contains `localhost:3002` URLs that need to be replaced.

---

## Testing

### Local Testing

```bash
# 1. Start backend (with BRP routes registered)
cd packages/backend
npm run dev

# 2. Start frontend
cd packages/frontend
npm run dev

# 3. Login as test-citizen-utrecht
# 4. Click "Toon Tijdlijn"
# 5. Verify timeline loads with 3 events
# 6. Drag slider and verify data updates
```

### ACC Testing

```bash
# Test BRP proxy endpoint
curl -X POST https://acc.api.open-regels.nl/v1/brp/personen \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "RaadpleegMetBurgerservicenummer",
    "burgerservicenummer": ["999992235"],
    "fields": ["burgerservicenummer","naam","geboorte","partners","kinderen","leeftijd"]
  }'
```

---

## Future Enhancements

### 1. Verblijfplaatshistorie Integration

Add address history to timeline:

```typescript
// New endpoint: POST /v1/brp/verblijfplaatshistorie
router.post('/verblijfplaatshistorie', jwtMiddleware, async (req, res) => {
  // Forward to BRP verblijfplaatshistorie API
});

// Extract address events
function extractAddressEvents(verblijfplaatshistorie): BRPEvent[] {
  return verblijfplaatshistorie.map(vp => ({
    type: 'address_change',
    date: new Date(vp.datumVan.datum),
    label: 'Verhuizing',
    description: `Verhuisd naar ${vp.verblijfadres.straat}`,
  }));
}
```

### 2. Cached BRP Data

Implement Redis caching:

```typescript
// Cache BRP responses for 5 minutes
const cacheKey = `brp:person:${bsn}`;
const cached = await redis.get(cacheKey);

if (cached) {
  return JSON.parse(cached);
}

const data = await brpApi.getPersonByBSN(bsn);
await redis.setex(cacheKey, 300, JSON.stringify(data)); // 5 min TTL
return data;
```

### 3. Historical Application Data

Store zorgtoeslag calculations:

```typescript
// Link timeline to historical applications
interface HistoricalApplication {
  date: Date;
  type: 'zorgtoeslag' | 'kinderbijslag';
  amount: number;
  status: 'approved' | 'denied';
}

// Show on timeline as events
```

---

## Related Documentation

- [Feature Overview](../features/timeline-navigation.md)
- [Developer Guide](../developer/implementing-timeline.md)
- [API Reference](../reference/brp-api-endpoints.md)
