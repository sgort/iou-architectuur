---
component: RONL Business API
---

# Municipality Themes

Each tenant — municipalities, but also the province, national organisations and an insurer — has a colour theme defined in `packages/frontend/public/tenants.json`. The theme is applied in two places:

- **On the landing page**, before sign-in: the board grid at `/` uses the default tenant (`"default": "flevoland"`), and a single-board tenant's page at `/<id>` uses that tenant's theme.
- **On the dashboards**, after sign-in: the theme of the tenant named in the `municipality` JWT claim.

---

## Configured themes

### Utrecht

`utrecht` · Gemeente Utrecht · `organisationType: municipality`

| Property | Value |
|---|---|
| `primary` | `#C41E3A` |
| `primaryDark` | `#9B1830` |
| `primaryLight` | `#E85770` |
| `secondary` | `#2C5F2D` |
| `accent` | `#FF6B00` |

### Amsterdam

`amsterdam` · Gemeente Amsterdam · `organisationType: municipality`

| Property | Value |
|---|---|
| `primary` | `#EC0000` |
| `primaryDark` | `#B80000` |
| `primaryLight` | `#FF4444` |
| `secondary` | `#000000` |
| `accent` | `#FFD700` |

### Rotterdam

`rotterdam` · Gemeente Rotterdam · `organisationType: municipality`

| Property | Value |
|---|---|
| `primary` | `#00811F` |
| `primaryDark` | `#006619` |
| `primaryLight` | `#00A828` |
| `secondary` | `#0F6CB6` |
| `accent` | `#FFB81C` |

### Den Haag

`denhaag` · Gemeente Den Haag · `organisationType: municipality`

| Property | Value |
|---|---|
| `primary` | `#007BC7` |
| `primaryDark` | `#00599C` |
| `primaryLight` | `#4DA6E0` |
| `secondary` | `#E17000` |
| `accent` | `#6EC4E8` |

### Heusden

`heusden` · Gemeente Heusden · `organisationType: municipality`

| Property | Value |
|---|---|
| `primary` | `#00505c` |
| `primaryDark` | `#003a43` |
| `primaryLight` | `#009ee0` |
| `secondary` | `#7ab929` |
| `accent` | `#009ee0` |
| `background` | `#eef1ee` |

### Flevoland

`flevoland` · Provincie Flevoland · `organisationType: province`

| Property | Value |
|---|---|
| `primary` | `#0046ad` |
| `primaryDark` | `#134F7D` |
| `primaryLight` | `#4A8FC0` |
| `secondary` | `#e70077` |
| `accent` | `#F5A623` |

### Dienst Toeslagen

`toeslagen` · Dienst Toeslagen · `organisationType: national`

| Property | Value |
|---|---|
| `primary` | `#154273` |
| `primaryDark` | `#0d2f52` |
| `primaryLight` | `#4a7aad` |
| `secondary` | `#6EC4E8` |
| `accent` | `#FFB81C` |

### Univé Verzekeringen

`unive` · Univé Verzekeringen · `organisationType: commercial`

| Property | Value |
|---|---|
| `primary` | `#E4007D` |
| `primaryDark` | `#B3005F` |
| `primaryLight` | `#FF4DAF` |
| `secondary` | `#1A1A2E` |
| `accent` | `#FF6B6B` |

### UWV

`uwv` · UWV · `organisationType: national`

| Property | Value |
|---|---|
| `primary` | `#0067A5` |
| `primaryDark` | `#004F7C` |
| `primaryLight` | `#3D8DC4` |
| `secondary` | `#E85612` |
| `accent` | `#FFB81C` |

---

## TenantConfig schema

The frontend reads `tenants.json` with these types (`packages/frontend/src/services/tenant.ts`):

```typescript
type OrganisationType = 'municipality' | 'province' | 'national' | 'commercial';

interface TenantTheme {
  primary: string;       // Main brand colour — buttons, active nav
  primaryDark: string;   // Hover/focus states
  primaryLight: string;  // Backgrounds, borders
  secondary: string;     // Accent colour for secondary actions
  accent: string;        // Highlight colour
  background?: string;   // Landing-page background (--color-background)
}

interface TenantContact {
  phone: string;
  email: string;
  address: string;
  postalCode: string;
  city: string;
}

interface TenantLogo {
  src: string;               // e.g. "/tenants/heusden/logo.jpg"
  shape: 'wide' | 'square';  // 'wide' carries the name in the artwork; 'square' gets the name beside it
  height?: number;           // Height in the landing top bar, in px (default 44)
}

interface TenantConfig {
  id: string;                    // Must match JWT `municipality` claim
  name: string;                  // Internal identifier
  displayName: string;           // Shown in portal header (e.g. "Gemeente Utrecht")
  organisationType: OrganisationType;
  municipalityCode?: string;     // CBS municipality code (municipalities)
  organisationCode?: string;     // Code for the other organisation types
  theme: TenantTheme;
  contact: TenantContact;
  enabled: boolean;              // Set to false to disable without deleting
  leftPanelSections?: LeftPanelSections;  // Left-panel sections per dashboard page
  boards?: BoardId[];            // Boards on the landing page; missing means all of them
  logo?: TenantLogo;
  share?: { title: string; description: string };  // Link preview for the /<id> page
}
```

A tenant with exactly one entry in `boards` gets its own landing page at `/<id>` (Amsterdam, Heusden, Dienst Toeslagen and Univé). `share` is written into that page's HTML at build time.

`tenants.json` lists no citizen services: which services a citizen sees is decided by the `CITIZEN_SERVICES` registry in `@ronl/shared` and by what is deployed under each tenant. A guard test (`citizenServices.test.ts`) fails if a tenant carries a `features` key.

---

## CSS custom properties

`applyTenantTheme()` sets these properties on `document.documentElement`:

```css
--color-primary
--color-primary-dark
--color-primary-light
--color-secondary
--color-accent
--color-background   /* only when the theme sets background; removed otherwise */
```

Tailwind utility classes in the frontend use `var(--color-primary)` etc. as their colour values. This means the entire theme switches dynamically — no page reload, no per-municipality CSS bundle. The single-board landing page uses `var(--color-background, #f6f8fb)`, so a tenant without a `background` keeps the default.

---

## Adding a theme

See [Adding a Municipality](../user-guide/archive/adding-municipality.md) for the complete onboarding process.
