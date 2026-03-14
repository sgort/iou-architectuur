# Caseworker Dashboard

The MijnOmgeving caseworker dashboard is the primary interface for municipality staff. It is a shell-based single-page application that loads at `/dashboard/caseworker` and remains publicly accessible — authentication is handled inside the component rather than at the route level, allowing unauthenticated visitors to browse public content before logging in.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Caseworker Dashboard — authenticated shell](../../../assets/screenshots/ronl-caseworker-dashboard-shell.png)
  <figcaption>The three-zone caseworker dashboard: top navigation bar, left panel, and main content area</figcaption>
</figure>

---

## Shell layout

The dashboard is divided into three permanent zones:

```
┌─────────────────────────────────────────────────────────────┐
│  Top navigation bar (header)                                │
│  MijnOmgeving  [Home] [Persoonlijke info] [Projecten]  User │
├──────────────┬──────────────────────────────────────────────┤
│ Left panel   │                                              │
│ (w-56)       │  Main content area                           │
│              │                                              │
│ Section nav  │  Rendered by renderContent()                 │
│              │  based on activeSection                      │
└──────────────┴──────────────────────────────────────────────┘
```

### Top navigation bar

The header contains three top-level navigation pages and a user block on the right:

| Page ID         | Label             | Default first section |
| --------------- | ----------------- | --------------------- |
| `home`          | Home              | Nieuws                |
| `personal-info` | Persoonlijke info | Profiel               |
| `projects`      | Projecten         | Taken                 |

When tasks are pending, the page button for Projecten shows a count badge (`tasks.length`) so caseworkers can see open work at a glance without navigating there first.

The user block shows:

- `preferred_username` from the JWT (set via Keycloak `username` → `preferred_username` protocol mapper)
- LoA badge (`loa` claim, e.g. `hoog`)
- One badge per role in `realm_access.roles` (e.g. `caseworker`, `hr-medewerker`)
- **Uitloggen** button when authenticated, or an **Inloggen als medewerker** button when not

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Caseworker Dashboard — header user block](../../../assets/screenshots/ronl-caseworker-dashboard-header-user.png)
  <figcaption>Header showing username, LoA badge, and role badges for a user with both caseworker and hr-medewerker roles</figcaption>
</figure>

### Left panel

The left panel is driven entirely by `tenantConfig.leftPanelSections[activeTopNavPage]` — an array of section objects configured per tenant in `public/tenants.json`. Switching the top-nav page swaps the entire left-panel contents. Each section object has the shape:

```json
{ "id": "nieuws", "label": "Nieuws", "isPublic": true }
```

The `isPublic` flag controls whether the section is accessible without authentication (see [Public and private sections](#public-and-private-sections) below).

The active section is highlighted using the tenant's primary colour (`--color-primary`). Clicking a section stores the choice in `sectionMemory` so returning to the same top-nav page restores the last visited section rather than defaulting to the first.

### Main content area

The main area renders the component for `activeSection`. Each section ID maps to a dedicated render function:

| Section ID           | Render function             | Auth required                  |
| -------------------- | --------------------------- | ------------------------------ |
| `nieuws`             | `renderNieuws()`            | No                             |
| `berichten`          | `renderBerichten()`         | No                             |
| `regelcatalogus`     | `<RegelCatalogus />`        | No                             |
| `taken`              | `renderTaskQueue()`         | Yes                            |
| `profiel`            | `renderProfiel()`           | Yes                            |
| `rollen`             | `renderRollen()`            | Yes                            |
| `hr-onboarding`      | `renderHrOnboarding()`      | Yes + `hr-medewerker` role     |
| `onboarding-archief` | `renderOnboardingArchief()` | Yes + `hr-medewerker` role     |
| `rip-fase1`          | `renderRipPhase1()`         | Yes + `infra-projectteam` role |
| `rip-fase1-wip`      | `renderRipFase1Wip()`       | Yes + `infra-projectteam` role |
| `rip-fase1-gereed`   | `renderRipFase1Gereed()`    | Yes + `infra-projectteam` role |

Sections not yet implemented render a placeholder card ("Deze sectie is in ontwikkeling.").

---

## Public and private sections

The dashboard is accessible without login. Whether a section renders its content or a login prompt depends on the `isPublic` field in `tenants.json`:

- **`isPublic: true`** — content renders for all visitors, authenticated or not.
- **`isPublic: false`** — an unauthenticated visitor clicking the section sees a login prompt instead of the content. No redirect occurs; the user remains on the page.

When an unauthenticated visitor lands on the dashboard and navigates to a top-nav page whose first section is private, the dashboard selects the first _public_ section for that page automatically, avoiding an empty content area.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Caseworker Dashboard — unauthenticated login prompt](../../../assets/screenshots/ronl-caseworker-dashboard-unauthenticated.png)
  <figcaption>Clicking a private section while unauthenticated shows the login prompt inline without leaving the page</figcaption>
</figure>

Clicking **Inloggen als medewerker** in the prompt stores `medewerker` in `sessionStorage` and navigates to `/auth`, following the same caseworker login path described in [Logging In](../user-guide/login-flow.md#caseworker-path).

---

## Home tab

The Home tab contains three public sections, all visible without authentication.

### Nieuws

Fetches the latest government news from the Rijksoverheid RSS feed via `GET /v1/public/nieuws`. Items are shown as expandable cards with title, publication date, and stripped body text. The feed is cached for 10 minutes on the backend; on cache failure the stale result is returned to prevent a blank UI.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Caseworker Dashboard — Home Nieuws](../../../assets/screenshots/ronl-caseworker-dashboard-home-nieuws.png)
  <figcaption>Home → Nieuws — government news items from Rijksoverheid</figcaption>
</figure>

### Berichten

Fetches internal portal messages via `GET /v1/public/berichten`. Messages are typed (`announcement`, `maintenance`, `update`) and prioritised (`high`, `normal`, `low`), with colour-coded priority badges.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Caseworker Dashboard — Home Berichten](../../../assets/screenshots/ronl-caseworker-dashboard-home-berichten.png)
  <figcaption>Home → Berichten — internal portal messages with type and priority indicators</figcaption>
</figure>

### Regelcatalogus

Displays the RONL knowledge graph via `GET /v1/public/regelcatalogus`. See [Regelcatalogus](regelcatalogus.md) for the full feature description.

---

## Persoonlijke info tab

The Persoonlijke info tab exposes four left-panel sections, all requiring authentication. See [HR Onboarding Workflow](../user-guide/hr-onboarding.md) for a full walkthrough of each section.

| Section                | Accessible to             |
| ---------------------- | ------------------------- |
| Profiel                | All caseworkers           |
| Rollen & rechten       | All caseworkers           |
| Medewerker onboarden   | `hr-medewerker` role only |
| Afgeronde onboardingen | `hr-medewerker` role only |

---

## Projecten tab

The Projecten tab contains the task queue and, for tenants with active BPMN processes, dedicated project management sections. The sections shown depend on the tenant configuration in `public/tenants.json`.

The Flevoland province tenant exposes the following sections:

| Section            | Accessible to       | Description                                               |
| ------------------ | ------------------- | --------------------------------------------------------- |
| Taken              | All caseworkers     | Full task queue with claim and complete                   |
| RIP Fase 1 starten | `infra-projectteam` | Start a new RipPhase1Process instance                     |
| RIP Fase 1 WIP     | `infra-projectteam` | Browse active RIP Phase 1 projects and their documents    |
| RIP Fase 1 gereed  | `infra-projectteam` | Browse completed RIP Phase 1 projects and their documents |
| Actieve zaken      | All caseworkers     | Placeholder                                               |
| Archief            | All caseworkers     | Placeholder                                               |

See [Caseworker Workflow](../user-guide/caseworker-workflow.md) for the task queue and [RIP Phase 1 Workflow](../user-guide/rip-phase1-workflow.md) for the full RIP process walkthrough.

---

## Tenant configuration

Each tenant defines its own left-panel section lists in `public/tenants.json`. This means different organisation types (municipality, province, national) can expose a different set of sections without any code change:

```json
"leftPanelSections": {
  "home": [
    { "id": "nieuws",          "label": "Nieuws",          "isPublic": true  },
    { "id": "berichten",       "label": "Berichten",        "isPublic": true  },
    { "id": "regelcatalogus",  "label": "Regelcatalogus",   "isPublic": true  }
  ],
  "personal-info": [
    { "id": "profiel",             "label": "Profiel",                 "isPublic": false },
    { "id": "rollen",              "label": "Rollen & rechten",        "isPublic": false },
    { "id": "hr-onboarding",       "label": "Medewerker onboarden",    "isPublic": false },
    { "id": "onboarding-archief",  "label": "Afgeronde onboardingen",  "isPublic": false }
  ],
  "projects": [
    { "id": "taken",           "label": "Taken",              "isPublic": false },
    { "id": "rip-fase1",       "label": "RIP Fase 1 starten", "isPublic": false },
    { "id": "rip-fase1-wip",   "label": "RIP Fase 1 WIP",     "isPublic": false },
    { "id": "rip-fase1-gereed","label": "RIP Fase 1 gereed",  "isPublic": false },
    { "id": "actief",          "label": "Actieve zaken",      "isPublic": false },
    { "id": "archief",         "label": "Archief",            "isPublic": false }
  ]
}
```

To add a new section, add an entry here and implement the corresponding case in `renderContent()` in `CaseworkerDashboard.tsx`. The RIP sections are Flevoland-specific — other tenants omit them entirely from their `tenants.json`.

---

## Related documentation

- [Caseworker Workflow](../user-guide/caseworker-workflow.md) — Task queue, claim, complete, AWB Kapvergunning
- [HR Onboarding Workflow](../user-guide/hr-onboarding.md) — Persoonlijke info sections in detail
- [RIP Phase 1 Workflow](../user-guide/rip-phase1-workflow.md) — Projecten tab RIP sections in detail
- [Regelcatalogus](regelcatalogus.md) — Knowledge graph browser
- [Multi-Tenant Municipality Portal](multi-tenant-portal.md) — Tenant theming and isolation
- [Frontend Development](../developer/frontend-development.md) — CaseworkerDashboard.tsx architecture
