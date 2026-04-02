---

# IOU GitLab Integration

The RONL Business API includes a lightweight proxy to the IOU Architecture GitLab repository (`git.open-regels.nl`). It is used by the IOU tab in the Flevoland tenant of the caseworker dashboard to allow external contributors to submit use-case scenarios, provide feedback, and browse submitted work items — without requiring a GitLab account.

---

## Architecture
```
Browser (IOU tab)
    ↓ HTTP (no auth required for public endpoints)
RONL Business API /v1/public/*
    ↓ PRIVATE-TOKEN header (GITLAB_TOKEN)
GitLab API (git.open-regels.nl)
```

All three public endpoints in this integration require no user authentication. The backend uses its own `GITLAB_TOKEN` service account to call the GitLab API on the caller's behalf.

---

## Endpoints

### `POST /v1/public/use-case`

Receives a use-case submission and creates a GitLab issue with the label defined in `GITLAB_UC_LABEL`. The title is automatically prefixed with `[Use Case]`.

**Request body (JSON):**

| Field | Type | Required |
|---|---|---|
| `title` | string | Yes |
| `description` | string | Yes — full markdown body |

**Response:** `201 { success: true, data: { iid, web_url } }`

The frontend component `IouGebruiksscenarioSection.tsx` builds the markdown body from a 10-section form. The organisation field is pre-filled as "Provincie Flevoland" for the Flevoland tenant.

---

### `GET /v1/public/use-cases`

Lists GitLab issues for the project. Used by both the Actieve zaken and Archief sections in the IOU tab.

**Query param:** `state=opened` (default) | `closed`

**Response fields per item:** `iid`, `title`, `state`, `created_at`, `updated_at`, `web_url`, `labels`, `assignees[]`, `description`

Up to 100 items are returned, sorted by `created_at` descending.

---

### `POST /v1/public/feedback`

Accepts a `multipart/form-data` form with optional screenshot attachments. Each file is uploaded to the GitLab project uploads API first; the returned markdown image references are embedded in the issue body.

**Form fields:**

| Field | Type | Required |
|---|---|---|
| `name` | string | Yes |
| `org` | string | No |
| `role` | string | No |
| `contact` | string | Yes |
| `description` | string | Yes |
| `screenshots` | file[] | No — up to 5 images, 10 MB each |

**Response:** `201 { success: true, data: { iid, web_url } }`

Multer is configured with in-memory storage and an image-only MIME filter. The file size limit is enforced per file, not for the whole request.

---

## Configuration

| Variable | Description |
|---|---|
| `GITLAB_TOKEN` | Personal access token with `api` scope |
| `GITLAB_BASE_URL` | Default: `https://git.open-regels.nl` |
| `GITLAB_PROJECT_PATH` | URL-encoded path, e.g. `showcases%2Fiou-architectuur` |
| `GITLAB_UC_LABEL` | Label for new use-case issues, e.g. `Submitted` |

All four variables must be set for any of the three endpoints to function. Missing `GITLAB_TOKEN` or `GITLAB_PROJECT_PATH` causes the endpoint to return `503 GITLAB_NOT_CONFIGURED`.

---

## Enabling the IOU tab for a tenant

The IOU tab is rendered only when `leftPanelSections.iou` is present in the tenant's `tenants.json` entry. To enable it for a tenant, add:
```json
"iou": [
  { "id": "iou-gebruiksscenario", "label": "Gebruiksscenario indienen", "isPublic": false },
  { "id": "iou-feedback",         "label": "Feedback geven",            "isPublic": false },
  { "id": "iou-actieve-zaken",    "label": "Actieve zaken",             "isPublic": true  },
  { "id": "iou-archief",          "label": "Archief",                   "isPublic": true  }
]
```

The `isPublic: true` sections (`iou-actieve-zaken`, `iou-archief`) are visible without login. The submission sections require authentication.

---

## Adding a new IOU section

Add a new entry to `leftPanelSections.iou` in `tenants.json`, create a React component for the section, and add the corresponding `case` to the `renderContent()` switch in `CaseworkerDashboard.tsx`:
```typescript
case 'iou-my-new-section':
  return <MyNewIouSection />;
```

No backend changes are required if the section only reads from existing endpoints.

---

## Related documentation

- [Caseworker Dashboard](../features/caseworker-dashboard.md) — IOU tab and tenant-scoped sections
- [API Endpoints](../references/api-endpoints.md) — Full endpoint reference
- [Environment Variables](../references/environment-variables.md) — GitLab configuration