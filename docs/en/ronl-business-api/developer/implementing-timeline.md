# Timeline Implementation - Developer Guide

## Table of Contents

1. [Adding New Test Personas](#adding-new-test-personas)
2. [Extending Timeline with New Event Types](#extending-timeline-with-new-event-types)
3. [Adding Address History](#adding-address-history-verblijfplaatshistorie)
4. [Customizing Timeline Appearance](#customizing-timeline-appearance)
5. [Testing Timeline Features](#testing-timeline-features)

---

## Adding New Test Personas

Currently, all test users map to Wessel Kooyman (BSN: 999992235). To add more diverse personas:

### Step 1: Add Test Data to BRP API Mock

If you control the BRP API mock, add new persona data. Otherwise, you'll need to use different BSN numbers that exist in the mock.

**Example personas to add:**
- Single person without partner/children
- Divorced person with children
- Person with multiple marriages
- Person with address changes

### Step 2: Update BSN Mapping

**File:** `packages/frontend/src/services/bsn.mapping.ts`

```typescript
const testUserBSNMapping: Record<string, string> = {
  // Existing
  'test-citizen-utrecht': '999992235',        // Wessel Kooyman (married, 3 children)
  
  // Add new personas
  'test-citizen-single': '999991111',         // Single person, no partner/children
  'test-citizen-divorced': '999992222',       // Divorced, 2 children
  'test-citizen-remarried': '999993333',      // Multiple marriages
  'test-citizen-young': '999994444',          // Born 2000, no major events yet
};
```

### Step 3: Create Keycloak Test Users

1. **Keycloak Admin Console** → Realms → `ronl`
2. **Users** → **Add user**
3. Configure:
   - **Username**: `test-citizen-single`
   - **Email**: `single@test.nl`
   - **First Name**: `Jan`
   - **Last Name**: `Jansen`
4. **Credentials** tab → Set password: `test123` (temporary: OFF)
5. **Attributes** tab → Add:
   - `municipality`: `utrecht`
   - `assurance_level`: `hoog`
6. **Role Mappings** tab → Assign role: `citizen`
7. Save

### Step 4: Test New Persona

```bash
# Login as new user
# Navigate to timeline
# Verify correct data appears
```

---

## Extending Timeline with New Event Types

### Supported Event Types (Current)

```typescript
type BRPEventType = 'birth' | 'marriage' | 'divorce';
```

### Adding New Event Type: Divorce

#### Step 1: Update Type Definition

**File:** `packages/frontend/src/types/brp.types.ts`

```typescript
export type BRPEventType = 
  | 'birth' 
  | 'marriage' 
  | 'divorce'      // ✅ Add this
  | 'address_change';  // ✅ Future

export interface BRPEvent {
  id: string;
  type: BRPEventType;
  date: Date;
  label: string;
  description: string;
  icon?: string;     // ✅ Add optional icon
  color?: string;    // ✅ Add optional color
}
```

#### Step 2: Extract Divorce Events

**File:** `packages/frontend/src/services/brp.timeline.ts`

Add to `extractEvents()` function:

```typescript
export function extractEvents(personState: PersonState): BRPEvent[] {
  const events: BRPEvent[] = [];

  // ... existing birth and marriage events ...

  // ✅ Add: Divorce/separation events
  if (personState.partners) {
    personState.partners.forEach((partner, idx) => {
      // Check if partnership ended
      if (partner.ontbindingHuwelijkPartnerschap?.datum?.datum) {
        events.push({
          id: `divorce-${idx}`,
          type: 'divorce',
          date: new Date(partner.ontbindingHuwelijkPartnerschap.datum.datum),
          label: 'Scheiding',
          description: `Einde huwelijk met ${partner.naam.voornamen} ${partner.naam.geslachtsnaam}`,
          icon: '💔',
          color: '#DC2626', // Red color
        });
      }
    });
  }

  return events.sort((a, b) => a.date.getTime() - b.date.getTime());
}
```

#### Step 3: Update Historical State Calculation

**File:** `packages/frontend/src/services/brp.timeline.ts`

Modify `calculateHistoricalState()`:

```typescript
// Filter partners based on marriage AND divorce dates
if (currentState.partners && currentState.partners.length > 0) {
  historicalState.partners = currentState.partners.filter((partner) => {
    const marriageDate = new Date(partner.aangaanHuwelijkPartnerschap.datum.datum);
    
    // Check if partnership ended
    const divorceDate = partner.ontbindingHuwelijkPartnerschap?.datum?.datum
      ? new Date(partner.ontbindingHuwelijkPartnerschap.datum.datum)
      : null;
    
    // Show partner only between marriage and divorce (or now if still married)
    return targetDate >= marriageDate && (!divorceDate || targetDate < divorceDate);
  });

  if (historicalState.partners.length === 0) {
    delete historicalState.partners;
  }
}
```

#### Step 4: Update Timeline Component

**File:** `packages/frontend/src/components/Timeline.tsx`

Add visual styling for divorce events:

```typescript
{/* Event markers on timeline */}
{events.map((event) => {
  const position = dateToPercentage(event.date);
  
  // ✅ Add: Different colors per event type
  const eventColor = event.color || 
    (event.type === 'birth' ? 'var(--color-primary)' : 
     event.type === 'marriage' ? '#10B981' : 
     event.type === 'divorce' ? '#DC2626' : 
     'var(--color-accent)');
  
  return (
    <div
      key={event.id}
      className="absolute top-1/2 transform -translate-x-1/2 -translate-y-1/2 cursor-pointer z-10"
      style={{ left: `${position}%` }}
      onClick={() => onDateChange(event.date)}
      title={event.description}
    >
      <div
        className="w-4 h-4 rounded-full border-2 border-white"
        style={{ backgroundColor: eventColor }}
      />
      {event.icon && (
        <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 text-lg">
          {event.icon}
        </div>
      )}
    </div>
  );
})}
```

### Adding Event Type: Death

**⚠️ Sensitive Implementation Note:** Handle with care for UX.

```typescript
// In extractEvents()
if (personState.overlijden?.datum?.datum) {
  events.push({
    id: 'death',
    type: 'death',
    date: new Date(personState.overlijden.datum.datum),
    label: 'Overleden',
    description: 'Overlijden',
    icon: '🕊️',
    color: '#6B7280', // Gray
  });
}

// In calculateHistoricalState()
// If target date is after death, show memorial state
const deathDate = currentState.overlijden?.datum?.datum
  ? new Date(currentState.overlijden.datum.datum)
  : null;

if (deathDate && targetDate >= deathDate) {
  // Show "In Memoriam" or special state
  return {
    ...historicalState,
    _memorial: true, // Custom flag
  };
}
```

---

## Adding Address History (Verblijfplaatshistorie)

### Step 1: Add Backend Route

**File:** `packages/backend/src/routes/brp.routes.ts`

```typescript
/**
 * POST /v1/brp/verblijfplaatshistorie
 * Fetch address history for a person
 */
router.post('/verblijfplaatshistorie', jwtMiddleware, async (req: Request, res: Response) => {
  try {
    logger.info('BRP verblijfplaatshistorie request', {
      userId: req.user?.userId,
      requestBody: req.body,
    });

    // Forward to BRP verblijfplaatshistorie API
    const response = await axios.post(
      `${BRP_API_BASE_URL}/verblijfplaatshistorie`,
      req.body,
      {
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Accept': 'application/json',
        },
        timeout: 10000,
        validateStatus: (status) => status < 500,
      }
    );

    if (response.status >= 400) {
      logger.error('BRP API returned error', {
        status: response.status,
        data: response.data,
      });
      
      return res.status(response.status).json({
        success: false,
        error: {
          code: 'BRP_API_ERROR',
          message: 'BRP API returned an error',
          details: response.data,
        },
      });
    }

    auditLog(req, 'brp.verblijfplaatshistorie.fetch', 'success', {
      bsn: req.body.burgerservicenummer?.[0],
    });

    res.json({
      success: true,
      data: response.data,
    });
  } catch (error) {
    logger.error('BRP verblijfplaatshistorie request failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
    });

    res.status(500).json({
      success: false,
      error: {
        code: 'BRP_API_ERROR',
        message: 'Verblijfplaatshistorie request failed',
      },
    });
  }
});
```

### Step 2: Add Frontend Service

**File:** `packages/frontend/src/services/brp.api.ts`

```typescript
/**
 * Fetch address history by BSN
 */
async getVerblijfplaatshistorie(
  bsn: string,
  datumVan?: string,
  datumTot?: string
): Promise<VerblijfplaatsHistorie[] | null> {
  try {
    const response = await this.client.post<{
      success: boolean;
      data: { verblijfplaatshistorie: VerblijfplaatsHistorie[] };
    }>('/brp/verblijfplaatshistorie', {
      type: 'RaadpleegMetPeriode',
      burgerservicenummer: [bsn],
      datumVan: datumVan || undefined,
      datumTot: datumTot || undefined,
    });

    if (
      response.data.success &&
      response.data.data.verblijfplaatshistorie
    ) {
      return response.data.data.verblijfplaatshistorie;
    }

    return null;
  } catch (error) {
    console.error(`Failed to fetch verblijfplaatshistorie for BSN ${bsn}:`, error);
    throw error;
  }
}
```

### Step 3: Add TypeScript Types

**File:** `packages/frontend/src/types/brp.types.ts`

```typescript
export interface VerblijfplaatsHistorie {
  datumVan: {
    datum: string;
    langFormaat: string;
  };
  datumTot?: {
    datum: string;
    langFormaat: string;
  };
  verblijfadres: {
    straat: string;
    huisnummer: number;
    huisletter?: string;
    huisnummertoevoeging?: string;
    postcode: string;
    woonplaats: string;
  };
  gemeenteVanInschrijving: {
    code: string;
    omschrijving: string;
  };
}
```

### Step 4: Extract Address Events

**File:** `packages/frontend/src/services/brp.timeline.ts`

```typescript
export function extractAddressEvents(
  verblijfplaatshistorie: VerblijfplaatsHistorie[]
): BRPEvent[] {
  return verblijfplaatshistorie.map((vph, idx) => ({
    id: `address-${idx}`,
    type: 'address_change',
    date: new Date(vph.datumVan.datum),
    label: 'Verhuizing',
    description: `Verhuisd naar ${vph.verblijfadres.straat} ${vph.verblijfadres.huisnummer}, ${vph.verblijfadres.woonplaats}`,
    icon: '🏠',
    color: '#F59E0B', // Orange
  }));
}

// Update getPersonTimeline to fetch address history too
export async function getPersonTimeline(bsn: string): Promise<BRPPersonHistoricalData | null> {
  try {
    const currentState = await brpApi.getPersonByBSN(bsn);
    if (!currentState) return null;

    // ✅ Add: Fetch address history
    const addressHistory = await brpApi.getVerblijfplaatshistorie(bsn);

    const personEvents = extractEvents(currentState);
    const addressEvents = addressHistory ? extractAddressEvents(addressHistory) : [];
    
    // Combine and sort all events
    const events = [...personEvents, ...addressEvents].sort(
      (a, b) => a.date.getTime() - b.date.getTime()
    );

    const birthDate = new Date(currentState.geboorte.datum.datum);
    const earliestDate = new Date(birthDate);
    earliestDate.setFullYear(earliestDate.getFullYear() - 2);
    
    const futureDate = new Date();
    futureDate.setFullYear(futureDate.getFullYear() + 10);

    return {
      bsn,
      events,
      earliestDate,
      latestDate: futureDate,
      currentState,
      addressHistory, // ✅ Include in response
    };
  } catch (error) {
    console.error('Failed to generate person timeline:', error);
    return null;
  }
}
```

### Step 5: Display Address in Timeline

**File:** `packages/frontend/src/components/PersonalDataPanel.tsx`

Add address section:

```typescript
{/* ✅ Add: Address section */}
{addressAtDate && (
  <div className="bg-white rounded-lg shadow-md p-6 mb-4">
    <h2 className="text-xl font-semibold mb-4 flex items-center">
      <span className="mr-2">🏠</span>
      Adres
    </h2>
    <div className="space-y-2">
      <div>
        <span className="text-gray-600">Straat:</span>{' '}
        <span className="font-medium">
          {addressAtDate.verblijfadres.straat} {addressAtDate.verblijfadres.huisnummer}
        </span>
      </div>
      <div>
        <span className="text-gray-600">Postcode:</span>{' '}
        <span className="font-medium">{addressAtDate.verblijfadres.postcode}</span>
      </div>
      <div>
        <span className="text-gray-600">Woonplaats:</span>{' '}
        <span className="font-medium">{addressAtDate.verblijfadres.woonplaats}</span>
      </div>
      <div>
        <span className="text-gray-600">Gemeente:</span>{' '}
        <span className="font-medium">
          {addressAtDate.gemeenteVanInschrijving.omschrijving}
        </span>
      </div>
    </div>
  </div>
)}
```

---

## Customizing Timeline Appearance

### Changing Theme Colors

Timeline uses CSS custom properties for theming:

**File:** `packages/frontend/src/services/tenant.ts`

Colors are set per municipality:

```typescript
const tenantConfigs: Record<string, TenantConfig> = {
  utrecht: {
    theme: {
      primary: '#C41E3A',      // Timeline marker color
      primaryDark: '#9B1830',   // Hover states
      primaryLight: '#E85770',  // Light accents
      secondary: '#2C5F2D',     // Secondary buttons
      accent: '#FF6B00',        // Event markers
    },
  },
};
```

### Customizing Timeline Range

**File:** `packages/frontend/src/services/brp.timeline.ts`

```typescript
// Adjust padding before birth
const earliestDate = new Date(birthDate);
earliestDate.setFullYear(earliestDate.getFullYear() - 2); // ← Change this

// Adjust future range
const futureDate = new Date(today);
futureDate.setFullYear(futureDate.getFullYear() + 10); // ← Change this
```

### Adjusting Year Marker Intervals

**File:** `packages/frontend/src/components/Timeline.tsx`

```typescript
const generateYearMarkers = () => {
  const roundedStartYear = Math.floor(startYear / 5) * 5; // ← Change interval
  
  for (let year = roundedStartYear; year <= endYear; year += 5) { // ← Change step
    // ...
  }
};
```

### Custom Event Icons

Add custom icons per event type:

```typescript
const eventIcons: Record<BRPEventType, string> = {
  birth: '👶',
  marriage: '💍',
  divorce: '💔',
  address_change: '🏠',
  death: '🕊️',
};

// In Timeline.tsx
{events.map((event) => (
  <div>
    <span>{eventIcons[event.type]}</span>
    {/* ... */}
  </div>
))}
```

---

## Testing Timeline Features

### Unit Testing Historical State Calculation

**File:** `packages/frontend/src/services/__tests__/brp.timeline.test.ts`

```typescript
import { calculateHistoricalState } from '../brp.timeline';
import type { PersonState } from '../../types/brp.types';

describe('calculateHistoricalState', () => {
  const mockPersonState: PersonState = {
    burgerservicenummer: '999992235',
    leeftijd: 45,
    naam: {
      volledigeNaam: 'Wessel Kooyman',
      voornamen: 'Wessel',
      geslachtsnaam: 'Kooyman',
    },
    geboorte: {
      datum: { datum: '1980-12-12', langFormaat: '12 december 1980' },
      plaats: { omschrijving: 'Leerdam' },
    },
    partners: [{
      naam: {
        voornamen: 'Catootje',
        geslachtsnaam: 'Altena',
      },
      aangaanHuwelijkPartnerschap: {
        datum: { datum: '2002-02-02', langFormaat: '2 februari 2002' },
      },
    }],
    kinderen: [{
      burgerservicenummer: '999991231',
      naam: {
        voornamen: 'Stefano',
        geslachtsnaam: 'Kooyman',
      },
      geboorte: {
        datum: { datum: '2003-03-03', langFormaat: '3 maart 2003' },
      },
    }],
  };

  test('before marriage - no partner visible', () => {
    const targetDate = new Date('2001-01-01');
    const result = calculateHistoricalState(mockPersonState, targetDate);
    
    expect(result).not.toBeNull();
    expect(result?.partners).toBeUndefined();
    expect(result?.leeftijd).toBe(20); // Age in 2001
  });

  test('after marriage - partner visible', () => {
    const targetDate = new Date('2002-06-01');
    const result = calculateHistoricalState(mockPersonState, targetDate);
    
    expect(result?.partners).toHaveLength(1);
    expect(result?.leeftijd).toBe(21);
  });

  test('before children born - no children visible', () => {
    const targetDate = new Date('2003-01-01');
    const result = calculateHistoricalState(mockPersonState, targetDate);
    
    expect(result?.kinderen).toBeUndefined();
  });

  test('after children born - children visible with correct age', () => {
    const targetDate = new Date('2005-01-01');
    const result = calculateHistoricalState(mockPersonState, targetDate);
    
    expect(result?.kinderen).toHaveLength(1);
    expect(result?.kinderen?.[0].leeftijd).toBe(1); // Child age in 2005
  });

  test('before birth - returns null', () => {
    const targetDate = new Date('1979-01-01');
    const result = calculateHistoricalState(mockPersonState, targetDate);
    
    expect(result).toBeNull();
  });
});
```

### Integration Testing Timeline Component

**File:** `packages/frontend/src/components/__tests__/Timeline.test.tsx`

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import Timeline from '../Timeline';
import type { BRPEvent } from '../../types/brp.types';

describe('Timeline Component', () => {
  const mockEvents: BRPEvent[] = [
    {
      id: 'birth',
      type: 'birth',
      date: new Date('1980-12-12'),
      label: 'Geboren',
      description: 'Geboorte Wessel Kooyman',
    },
    {
      id: 'marriage',
      type: 'marriage',
      date: new Date('2002-02-02'),
      label: 'Getrouwd',
      description: 'Huwelijk met Catootje Altena',
    },
  ];

  const mockOnDateChange = jest.fn();

  test('renders timeline with events', () => {
    render(
      <Timeline
        events={mockEvents}
        minDate={new Date('1978-01-01')}
        maxDate={new Date('2030-01-01')}
        selectedDate={new Date()}
        onDateChange={mockOnDateChange}
        isLoading={false}
      />
    );

    expect(screen.getByText('Vandaag')).toBeInTheDocument();
    expect(screen.getByText('Geboren')).toBeInTheDocument();
    expect(screen.getByText('Getrouwd')).toBeInTheDocument();
  });

  test('clicking event button calls onDateChange', () => {
    render(
      <Timeline
        events={mockEvents}
        minDate={new Date('1978-01-01')}
        maxDate={new Date('2030-01-01')}
        selectedDate={new Date()}
        onDateChange={mockOnDateChange}
        isLoading={false}
      />
    );

    fireEvent.click(screen.getByText('Geboren'));
    expect(mockOnDateChange).toHaveBeenCalledWith(new Date('1980-12-12'));
  });

  test('shows loading overlay when isLoading is true', () => {
    render(
      <Timeline
        events={mockEvents}
        minDate={new Date('1978-01-01')}
        maxDate={new Date('2030-01-01')}
        selectedDate={new Date()}
        onDateChange={mockOnDateChange}
        isLoading={true}
      />
    );

    expect(screen.getByText(/laden/i)).toBeInTheDocument();
  });
});
```

### E2E Testing with Playwright

**File:** `e2e/timeline.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Timeline Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:5173');
    await page.fill('input[name="username"]', 'test-citizen-utrecht');
    await page.fill('input[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('loads timeline with events', async ({ page }) => {
    // Click timeline button
    await page.click('button:has-text("Toon Tijdlijn")');

    // Wait for timeline to load
    await page.waitForSelector('text=Geboren');

    // Verify events are visible
    await expect(page.locator('text=Geboren')).toBeVisible();
    await expect(page.locator('text=Getrouwd')).toBeVisible();
    await expect(page.locator('text=Kinderen geboren')).toBeVisible();
  });

  test('clicking event jumps to date', async ({ page }) => {
    await page.click('button:has-text("Toon Tijdlijn")');
    await page.waitForSelector('text=Geboren');

    // Click "Geboren" event
    await page.click('button:has-text("Geboren")');

    // Verify age is 0 (at birth)
    await expect(page.locator('text=Leeftijd: 0 jaar')).toBeVisible();

    // Verify no partner/children sections
    await expect(page.locator('text=Partner')).not.toBeVisible();
    await expect(page.locator('text=Kinderen')).not.toBeVisible();
  });

  test('shows partner after marriage date', async ({ page }) => {
    await page.click('button:has-text("Toon Tijdlijn")');
    await page.waitForSelector('text=Getrouwd');

    // Click "Getrouwd" event
    await page.click('button:has-text("Getrouwd")');

    // Verify partner section is visible
    await expect(page.locator('text=Partner')).toBeVisible();
    await expect(page.locator('text=Catootje Altena')).toBeVisible();
  });
});
```

---

## Common Development Tasks

### Task: Add New Field to Person Display

1. Check if field exists in BRP API response
2. Add to `timeline-config.json`:
   ```json
   {
     "displayFields": {
       "person": [
         "burgerservicenummer",
         "geslacht.omschrijving"  // ✅ Add new field
       ]
     }
   }
   ```
3. Update `PersonalDataPanel.tsx` to render the field

### Task: Change Timeline Date Range

Modify `getPersonTimeline()` in `brp.timeline.ts`:

```typescript
// Start from first address instead of birth
const firstAddressDate = addressHistory?.[0]?.datumVan?.datum
  ? new Date(addressHistory[0].datumVan.datum)
  : birthDate;

const earliestDate = new Date(firstAddressDate);
earliestDate.setFullYear(earliestDate.getFullYear() - 1);
```

### Task: Add Event Filtering

Allow users to show/hide event types:

```typescript
// In Dashboard.tsx state
const [visibleEventTypes, setVisibleEventTypes] = useState<BRPEventType[]>([
  'birth',
  'marriage',
  'address_change',
]);

// Filter events before passing to Timeline
const filteredEvents = timelineData.events.filter((e) =>
  visibleEventTypes.includes(e.type)
);

// Add checkboxes to toggle event types
<label>
  <input
    type="checkbox"
    checked={visibleEventTypes.includes('marriage')}
    onChange={(e) => {
      if (e.target.checked) {
        setVisibleEventTypes([...visibleEventTypes, 'marriage']);
      } else {
        setVisibleEventTypes(visibleEventTypes.filter((t) => t !== 'marriage'));
      }
    }}
  />
  Toon huwelijken
</label>
```

---

## Debugging Tips

### Timeline Not Loading

1. **Check browser console** for errors
2. **Verify backend route** is registered:
   ```bash
   curl http://localhost:3002/v1/health
   ```
3. **Check JWT token** has `preferred_username`:
   ```javascript
   // In browser console
   JSON.parse(atob(localStorage.getItem('kc_token').split('.')[1]));
   ```
4. **Verify BSN mapping**:
   ```typescript
   console.log('User:', user);
   console.log('BSN:', getUserBSN(user));
   ```

### Events Not Appearing

1. **Check BRP API response** in Network tab
2. **Verify date parsing**:
   ```typescript
   console.log('Raw date:', partner.aangaanHuwelijkPartnerschap.datum.datum);
   console.log('Parsed date:', new Date('2002-02-02'));
   ```
3. **Check event extraction**:
   ```typescript
   const events = extractEvents(currentState);
   console.log('Extracted events:', events);
   ```

### Historical State Incorrect

1. **Log calculation inputs**:
   ```typescript
   console.log('Current state:', currentState);
   console.log('Target date:', targetDate);
   console.log('Historical state:', historicalState);
   ```
2. **Verify date comparisons**:
   ```typescript
   const marriageDate = new Date(partner.aangaanHuwelijkPartnerschap.datum.datum);
   console.log('Marriage date:', marriageDate);
   console.log('Target >= Marriage?', targetDate >= marriageDate);
   ```

---

## Performance Optimization

### Memoize Historical Calculations

```typescript
import { useMemo } from 'react';

// In Dashboard.tsx
const historicalState = useMemo(
  () => calculateHistoricalState(timelineData.currentState, selectedDate),
  [timelineData.currentState, selectedDate]
);
```

### Debounce Slider Updates

```typescript
import { useDebouncedCallback } from 'use-debounce';

const debouncedDateChange = useDebouncedCallback(
  (date: Date) => {
    setSelectedDate(date);
  },
  100 // 100ms delay
);

<Timeline onDateChange={debouncedDateChange} />
```

### Lazy Load Address History

```typescript
// Only fetch when user scrolls to address section
const [addressHistory, setAddressHistory] = useState(null);

useEffect(() => {
  if (showAddressSection && !addressHistory) {
    brpApi.getVerblijfplaatshistorie(bsn).then(setAddressHistory);
  }
}, [showAddressSection, addressHistory, bsn]);
```

---

## Related Documentation

- [Feature Overview](../features/timeline-navigation.md)
- [Technical Architecture](../references/brp-timeline-integration.md)
- [API Reference](../references/brp-api-endpoints.md)
