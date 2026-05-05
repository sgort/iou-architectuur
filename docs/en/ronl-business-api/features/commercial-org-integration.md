# Commercial Organisation Integration

The RONL Business API supports **commercial organisations** as a first-class tenant
category alongside municipalities, provinces, and national agencies. This enables
private-sector parties — such as health insurers — to offer a branded MijnOmgeving
portal to their customers while delegating the actual administrative processing to
the appropriate government authority.

## Organisation types

The `OrganisationType` union currently covers four values:

| Value          | Example tenants     | Has MijnOmgeving | Processes AWB  |
| -------------- | ------------------- | ---------------- | -------------- |
| `municipality` | Utrecht, Den Haag   | ✅               | ✅             |
| `province`     | Flevoland           | ✅               | ✅             |
| `national`     | UWV, Toeslagen      | caseworker only  | ✅             |
| `commercial`   | Unive Verzekeringen | ✅               | ❌ (delegates) |

The `organisation_type` user attribute in Keycloak determines which category a user
belongs to. It is injected into every JWT as the `organisation_type` claim via a
protocol mapper and propagated through `AuthenticatedUser` into all backend middleware
and BPMN process variables.

## Cross-tenant processing authority

A commercial organisation can surface government services — such as the AWB
zorgtoeslag application — within its own branded portal. The government authority
responsible for the actual processing is a separate national tenant.

For zorgtoeslag this works as follows:

```
Citizen (municipality = unive)
    ↓ logs in via DigiD, enters Unive MijnOmgeving
    ↓ submits AwbZorgtoeslagProcess via ProcessStartFormViewer
Backend POST /v1/process/AwbZorgtoeslagProcess/start
    ↓ overrides municipality variable → "toeslagen"
    ↓ records originTenantId → "unive"
Operaton (AwbZorgtoeslagProcess instance, municipality = toeslagen)
    ↓ caseworker task queue filtered by municipality = toeslagen
test-caseworker-toeslagen picks up the task
    ↓ completes AWB review phases
Decision document available
    ↓ citizen reads it from Unive MijnOmgeving via applicantId ownership check
```

The key design principle is that **the channel and the processing authority are
decoupled**. The citizen never leaves the Unive MijnOmgeving, but the dossier is
handled entirely by Dienst Toeslagen.

## Processing authority override

The `POST /v1/process/:key/start` route applies a per-process-key override for
`AwbZorgtoeslagProcess`:

- `municipality` is set to `toeslagen` regardless of the requesting user's tenant
- `originTenantId` records the originating channel (e.g. `unive`) for reporting

This override runs after variable coercion and before forwarding to Operaton.

## Cross-tenant access control

Two endpoints implement a dual-check access model to allow commercial org citizens
to read their own dossiers even when the underlying process ran under a different
processing authority:

**`GET /v1/process/:id/historic-variables`** and
**`GET /v1/process/:instanceId/decision-document`**

Access is granted when **either**:

- `municipality` on the process matches the requesting user's `tenantId` (normal
  same-tenant access), **or**
- `applicantId` on the process matches the requesting user's `userId` (citizen
  self-access across tenant boundaries)

This means a Unive citizen can read their own zorgtoeslag decision document.
A Toeslagen caseworker can still access all processes in their municipality scope.
No other tenant can cross boundaries.

## History endpoint

`GET /v1/process/history` normally filters by both `applicantId` and `municipality`.
For users with `organisationType = commercial` the `municipality` filter is omitted,
so the citizen's own dossiers are returned regardless of which authority processed
them.

## Tenant configuration

Each commercial organisation is registered as a tenant in `tenants.json` with:

- `organisationType: "commercial"`
- A branded theme (primary colour, etc.)
- `features.zorgtoeslag: true` (or whichever services apply)
- Standard `leftPanelSections` for the citizen portal

A corresponding Keycloak user carries `organisation_type: commercial` and
`municipality: <tenant-id>` as user attributes, which are mapped to JWT claims
by the existing protocol mappers. No additional Keycloak configuration is needed
beyond adding the user.

## Reference tenants

| Tenant ID   | Name                | Type         | Role                                   |
| ----------- | ------------------- | ------------ | -------------------------------------- |
| `unive`     | Unive Verzekeringen | `commercial` | Channel — citizen portal               |
| `toeslagen` | Dienst Toeslagen    | `national`   | Processing authority — AWB zorgtoeslag |
