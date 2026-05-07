# RoPA Records Implementation

The RoPA Records feature implements GDPR Article 30 record-keeping for deployed
process bundles. It adds two PostgreSQL tables, a transactional service layer,
authenticated asset routes, a CORS-open public endpoint, a full LDE editor UI,
and a standalone static public site.

---

## Component structure
```
packages/backend/src/
├── db/
│   ├── migrate.ts                  # DDL — ropa_records + ropa_personal_data_fields tables
│   └── seed-ropa.ts                # One-time idempotent seed for example records
├── services/
│   └── ropa.service.ts             # CRUD + transactional upsert + public listing
├── routes/
│   ├── ropa.routes.ts              # Authenticated asset routes (/v1/assets/ropa)
│   └── ropa.public.routes.ts       # Public CORS-open route (/v1/ropa/public)
└── types/
    └── ropa.types.ts               # RopaRecord, RopaPersonalDataField, PublicRopaRecord

packages/frontend/src/
├── types/
│   └── ropa.types.ts               # Frontend mirror of backend types
├── services/
│   └── ropaService.ts              # fetch-based API client
└── components/
    └── RopaEditor/
        ├── RopaEditor.tsx          # Root — list state, load/save/delete orchestration
        ├── RopaList.tsx            # Left panel — record list with status badges
        └── RopaRecordEditor.tsx    # Right panel — four-tab editor

packages/frontend/src/components/BpmnModeler/
├── RopaSelector.tsx                # Footer panel in ProcessList
└── ronlModdleDescriptor.json       # Extended with ropaRef on bpmn:Process

packages/ropa-site/
├── index.html                      # Complete zero-dependency static public site
├── staticwebapp.config.json        # Azure Static Web Apps config
└── README.md
```

---

## Database schema

Two tables are appended to the existing `migrate.ts` query block. Migrations run
automatically at backend startup via `migrate()` called from `index.ts`.
```sql
CREATE TABLE IF NOT EXISTS ropa_records (
  id                       UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  bpmn_process_id          VARCHAR(255) NOT NULL,
  process_level            VARCHAR(20)  NOT NULL
                             CHECK (process_level IN ('shell', 'subprocess')),
  title                    VARCHAR(500) NOT NULL,
  controller_name          TEXT         NOT NULL,
  controller_contact       TEXT         NOT NULL,
  dpo_contact              TEXT,
  purpose                  TEXT         NOT NULL,
  legal_basis_uri          TEXT         NOT NULL,
  legal_basis_label        TEXT         NOT NULL,
  gdpr_article             VARCHAR(50)  NOT NULL,
  data_subjects            TEXT         NOT NULL,
  recipients               TEXT         NOT NULL,
  third_country_transfers  BOOLEAN      NOT NULL DEFAULT FALSE,
  third_country_details    TEXT,
  retention_period         TEXT         NOT NULL,
  security_measures        TEXT         NOT NULL,
  status                   VARCHAR(20)  NOT NULL DEFAULT 'draft'
                             CHECK (status IN ('draft', 'active', 'archived')),
  schema_version           INTEGER      NOT NULL DEFAULT 1,
  created_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ropa_bpmn_process_id_unique
  ON ropa_records (bpmn_process_id);

CREATE INDEX IF NOT EXISTS idx_ropa_status
  ON ropa_records (status);

CREATE TABLE IF NOT EXISTS ropa_personal_data_fields (
  id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  ropa_record_id   UUID         NOT NULL
                     REFERENCES ropa_records(id) ON DELETE CASCADE,
  form_id          TEXT         NOT NULL,
  field_key        VARCHAR(255) NOT NULL,
  field_label      TEXT         NOT NULL,
  data_category    VARCHAR(100) NOT NULL,
  special_category BOOLEAN      NOT NULL DEFAULT FALSE,
  sort_order       INTEGER      NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_rpdf_ropa_record_id
  ON ropa_personal_data_fields (ropa_record_id);
```

The unique index on `bpmn_process_id` is what makes the seed idempotent — `ON
CONFLICT (bpmn_process_id) DO UPDATE` replaces rows rather than inserting
duplicates.

`ropa_personal_data_fields` uses `ON DELETE CASCADE` so deleting a record
removes all its field rows in a single operation.

---

## Service layer

`ropa.service.ts` provides five functions following the same `if (!pool) return
...` guard pattern used throughout `assets.service.ts`:

| Function                                | Description                                                                                                              |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `listRopa()`                            | Returns all records with their fields, ordered by `updated_at DESC`                                                      |
| `getRopaById(id)`                       | Single record with fields by UUID                                                                                        |
| `getRopaByBpmnProcessId(bpmnProcessId)` | Used by the BPMN Link tab to check current linkage                                                                       |
| `upsertRopa(record)`                    | Transactional: upserts the record header then replaces all field rows atomically                                         |
| `deleteRopa(id)`                        | Deletes the record; CASCADE removes fields                                                                               |
| `listPublicRopa(organisation?)`         | Returns only `status = 'active'` records; strips `controllerContact`, `dpoContact`, and `schemaVersion` before returning |

### Transactional upsert

`upsertRopa` uses a client connection with explicit `BEGIN` / `COMMIT` /
`ROLLBACK`:

1. `INSERT ... ON CONFLICT (bpmn_process_id) DO UPDATE` — upserts the record
   header, returns the UUID
2. `DELETE FROM ropa_personal_data_fields WHERE ropa_record_id = $id` — clears
   existing fields
3. `INSERT` loop — writes all field rows with `sort_order` preserved
4. `COMMIT` — both operations land together or neither does

---

## API routes

### Authenticated routes — `/v1/assets/ropa`

Registered in `routes/index.ts` alongside the other asset routes. All require
the same database availability check as the other asset routes.

| Method   | Path                                        | Description                        |
| -------- | ------------------------------------------- | ---------------------------------- |
| `GET`    | `/v1/assets/ropa`                           | List all records with fields       |
| `POST`   | `/v1/assets/ropa`                           | Upsert a record (returns `{ id }`) |
| `DELETE` | `/v1/assets/ropa/:id`                       | Delete a record                    |
| `GET`    | `/v1/assets/ropa/by-bpmn-id/:bpmnProcessId` | Lookup by BPMN process ID          |

### Public route — `/v1/ropa/public`

Registered separately in `routes/index.ts` as `router.use('/v1/ropa/public',
ropaPublicRoutes)`.

| Method | Path              | Description                                                                                      |
| ------ | ----------------- | ------------------------------------------------------------------------------------------------ |
| `GET`  | `/v1/ropa/public` | List active records — `?organisation=flevoland` filters by `controller_name ILIKE '%flevoland%'` |

The public route applies `cors({ origin: '*', methods: ['GET', 'OPTIONS'] })` at
the route level. However, the global CORS middleware in `index.ts` evaluates
origins before route handlers are reached. The solution is a path-aware
middleware in `index.ts` that bypasses the origin whitelist for
`/v1/ropa/public`:
```typescript
app.use((req, res, next) => {
  if (req.path.startsWith('/v1/ropa/public')) {
    cors({ origin: '*', methods: ['GET', 'OPTIONS'] })(req, res, next);
  } else {
    cors(corsOptions)(req, res, next);
  }
});
```

The same pattern applies to the preflight `app.options('*', ...)` handler.

---

## BPMN moddleDescriptor

`ronlModdleDescriptor.json` is extended with a second type entry that adds
`ropaRef` as an attribute on `bpmn:Process`:
```json
{
  "name": "RopaRefMixin",
  "extends": ["bpmn:Process"],
  "properties": [
    { "name": "ropaRef", "isAttr": true, "type": "String" }
  ]
}
```

This registers the attribute with the bpmn-js moddle system so it survives
`saveXML()` serialisation. Without this registration the attribute is silently
dropped on every save.

Serialised in BPMN XML as:
```xml
<bpmn:process id="TreeFellingPermitSubProcess"
              ronl:ropaRef="b1c8f84a-bfac-43e3-9c0e-65bb1c1aadaf"
              ...>
```

---

## RopaSelector — ProcessList integration

`RopaSelector.tsx` is rendered as a fixed footer panel inside `ProcessList.tsx`,
outside the scrollable list container. It is only shown when `activeProcess` is
non-null.

`ProcessList` receives two new props:
```typescript
activeProcess: BpmnProcess | null;
onRopaRefChange: (ropaRef: string | undefined) => void;
```

The current `ropaRef` is extracted from the active process XML by a simple
regex:
```typescript
currentRopaRef={activeProcess.xml.match(/ronl:ropaRef="([^"]+)"/)?.[1]}
```

`handleRopaRefChange` in `BpmnModeler.tsx` performs three operations:

1. Ensures `xmlns:ronl="http://ronl.nl/schema/1.0"` is declared on the
   `<definitions>` element
2. Either sets, updates, or removes `ronl:ropaRef` depending on whether a value
   is passed
3. Saves the modified XML via `BpmnService.saveProcess`

---

## Deploy modal warning

`BpmnCanvas.tsx` sets a `ropaRefMissing` flag during bundle assembly in
`handleOpenDeployModal`:
```typescript
const ropaRefMissing = !xml.includes('ronl:ropaRef=');
```

When `true`, an amber warning banner is rendered in the deploy modal between the
resource list and the resource count line. The **Deploy** button remains enabled
— the warning is advisory, not blocking.

---

## Seed script

`packages/backend/src/db/seed-ropa.ts` seeds four active records covering the
two example bundles:

| Record                                           | `bpmnProcessId`                    | `processLevel` |
| ------------------------------------------------ | ---------------------------------- | -------------- |
| AWB Shell — Tree Felling Permit                  | `AwbShellProcess`                  | `shell`        |
| Tree Felling Permit — material law assessment    | `TreeFellingPermitSubProcess`      | `subprocess`   |
| AWB Shell — Zorgtoeslag                          | `AwbZorgtoeslagProcess`            | `shell`        |
| Zorgtoeslag — provisional entitlement assessment | `ZorgtoeslagProvisionalSubProcess` | `subprocess`   |

Run from `packages/backend`:
```bash
npx ts-node --project tsconfig.json src/db/seed-ropa.ts
```

The script is idempotent — re-running it updates existing rows in place via `ON
CONFLICT (bpmn_process_id) DO UPDATE`.

---

## Public site

`packages/ropa-site/` is a zero-dependency static site with no build step. It
fetches from `GET /v1/ropa/public` on load and renders collapsible cards.

Deployed as a separate Azure Static Web Apps resource — independent of the LDE
frontend SWA. The GitHub Actions workflow file generated by `az staticwebapp
create` is committed to `.github/workflows/` and scoped to changes in
`packages/ropa-site/**`.

To find the deployed URL:
```bash
az staticwebapp show \
  --name ropa-flevoland-acc \
  --resource-group rg-ronl-acc \
  --query "defaultHostname" \
  --output tsv
```

Custom domain configuration is done in the Azure Portal under **Static Web Apps
→ ropa-flevoland-acc → Custom domains**.

---

## Type safety — DB row types and mappers

`ropa.service.ts` follows the same three-layer DB type pattern used by
`assets.service.ts`. Row types `RopaRecordRow` and `RopaFieldRow` in
`src/db/types.ts` mirror the exact column names and pg-native types of
`ropa_records` and `ropa_personal_data_fields`. The mapper functions
`mapRopaRecord` and `mapRopaField` in `src/db/mappers.ts` perform all snake_case
→ camelCase conversion, `null` → `undefined` coercion, and `Date` → ISO string
serialisation in one place. Services use `pool.query<RopaRecordRow>()` — no `as`
casts appear in query results.

RoPA types live in `src/types/ropa.types.ts` rather than `src/domain/types.ts`
because they are mirrored on the frontend at
`packages/frontend/src/types/ropa.types.ts`. The pattern is otherwise identical.

See [DB Type Layer](db-type-layer.md) for the full pattern description and
guidance on adding new entities.

---

## Related pages

- [RoPA Records features](../features/ropa-records.md)
- [RoPA Records user guide](../user-guide/ropa-records.md)
- [Asset Storage](asset-storage.md) — PostgreSQL write-through cache
  architecture
- [DB Type Layer](db-type-layer.md) — DB row types, domain types, and mapper
  pattern
- [PostgreSQL deployment](deployment-postgresql.md) — firewall rules and schema
  management
- [BPMN Modeler developer docs](bpmn-modeler.md) — moddleDescriptor,
  ProcessList, deploy modal
