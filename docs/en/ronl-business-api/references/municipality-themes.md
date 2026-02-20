# Municipality Themes

Each municipality has a colour theme defined in `packages/frontend/public/tenants.json`. The theme is applied at login time based on the `municipality` JWT claim.

## Configured themes

### Utrecht

| Property | Value |
|---|---|
| `primary` | `#C41E3A` |
| `primaryDark` | `#9B1830` |
| `primaryLight` | `#E56B7D` |
| `secondary` | `#2C5F2D` |
| `accent` | `#C41E3A` |

### Amsterdam

| Property | Value |
|---|---|
| `primary` | `#EC0000` |
| `primaryDark` | `#C00000` |
| `primaryLight` | `#FF6666` |
| `secondary` | `#003B5C` |
| `accent` | `#EC0000` |

### Rotterdam

| Property | Value |
|---|---|
| `primary` | `#00811F` |
| `primaryDark` | `#006619` |
| `primaryLight` | `#4DB86A` |
| `secondary` | `#0C2340` |
| `accent` | `#00811F` |

### Den Haag

| Property | Value |
|---|---|
| `primary` | `#007BC7` |
| `primaryDark` | `#005A99` |
| `primaryLight` | `#4DA6E0` |
| `secondary` | `#E17000` |
| `accent` | `#007BC7` |

## TenantConfig schema

```typescript
interface TenantTheme {
  primary: string;       // Main brand colour — buttons, active nav
  primaryDark: string;   // Hover/focus states
  primaryLight: string;  // Backgrounds, borders
  secondary: string;     // Accent colour for secondary actions
  accent: string;        // Highlight colour
}

interface TenantFeatures {
  zorgtoeslag: boolean;     // Healthcare allowance service
  kinderbijslag: boolean;   // Child benefit service
  huurtoeslag: boolean;     // Rent allowance service
  processes: string[];      // Allowed Operaton process keys
}

interface TenantContact {
  phone: string;
  email: string;
  address: string;
  postalCode: string;
  city: string;
}

interface TenantConfig {
  id: string;                 // Must match JWT `municipality` claim
  name: string;               // Internal identifier
  displayName: string;        // Shown in portal header (e.g. "Gemeente Utrecht")
  municipalityCode: string;   // CBS municipality code (4 digits)
  theme: TenantTheme;
  features: TenantFeatures;
  contact: TenantContact;
  enabled: boolean;           // Set to false to disable without deleting
}
```

## CSS custom properties

`applyTenantTheme()` sets these properties on `document.documentElement`:

```css
--color-primary
--color-primary-dark
--color-primary-light
--color-secondary
--color-accent
```

Tailwind utility classes in the frontend use `var(--color-primary)` etc. as their colour values. This means the entire theme switches dynamically — no page reload, no per-municipality CSS bundle.

## Adding a theme

See [Adding a Municipality](../user-guide/adding-municipality.md) for the complete onboarding process.
