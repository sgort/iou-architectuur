# DB Type Layer

The LDE backend uses a three-layer type pattern to safely bridge PostgreSQL row data and service-layer domain objects. This pattern was introduced in v1.3.0 for the asset storage service and extended to the RoPA service in v1.4.0. It eliminates implicit `any` casts that TypeScript strict mode rejects on some platforms and keeps the mapping logic in one testable place.

---

## The three layers
```
PostgreSQL
    │
    │  pg driver returns raw rows
    ▼
src/db/types.ts          — DB row types       (snake_case, pg-native types)
    │
    │  mappers transform row → domain object
    ▼
src/db/mappers.ts        — mapper functions   (one per entity)
    │
    │  services work exclusively with domain types
    ▼
src/domain/types.ts      — domain types       (camelCase, serialisable)
src/types/ropa.types.ts  — RoPA domain types  (camelCase, serialisable)
```

---

## DB row types (`src/db/types.ts`)

Each type mirrors the exact column names and pg-native TypeScript types for one database table. The `pg` driver maps PostgreSQL types as follows:

| PostgreSQL type | TypeScript type |
|---|---|
| `TEXT`, `VARCHAR`, `UUID` | `string` |
| `TEXT` (nullable) | `string \| null` |
| `BOOLEAN` | `boolean` |
| `INTEGER`, `SERIAL` | `number` |
| `TIMESTAMPTZ` | `Date` |
| `JSONB` | `string` (returned as parsed object by pg, but typed as string for safety — mappers handle both) |
| `TEXT[]` | `string[] \| null` |

```typescript
// Example — process_definitions table
export type BpmnRow = {
  lde_id: string;
  bpmn_process_id: string;
  name: string;
  description: string | null;
  xml: string;
  process_role: string;
  called_element: string | null;
  linked_dmn_templates: string[] | null;
  status: string;
  readonly: boolean;
  schema_version: number;
  created_at: Date;
  updated_at: Date;
};
```

These types are passed as the generic parameter to `pool.query<T>()`:
```typescript
const { rows } = await pool.query<BpmnRow>(
  `SELECT lde_id, bpmn_process_id, ... FROM process_definitions`
);
```

TypeScript now knows the exact shape of each row. No `as` casts, no `unknown` index access.

---

## Domain types (`src/domain/types.ts`, `src/types/ropa.types.ts`)

Domain types use camelCase property names and serialisable types. `Date` objects from `pg` are converted to ISO strings so service return values can be sent directly to `res.json()` without a secondary serialisation step.
```typescript
// Example — domain type for process_definitions
export type Bpmn = {
  id: string;
  bpmnProcessId: string;
  name: string;
  description?: string;
  xml: string;
  processRole: string;
  calledElement?: string;
  linkedDmnTemplates: string[];
  status: string;
  readonly: boolean;
  schemaVersion: number;
  createdAt: Date;   // kept as Date — res.json() calls .toISOString() automatically
  updatedAt: Date;
};
```

RoPA types live in `src/types/ropa.types.ts` rather than `src/domain/types.ts` because they are shared with the frontend (via the frontend mirror at `packages/frontend/src/types/ropa.types.ts`). The RoPA domain types use `string` for `createdAt` / `updatedAt` because the mappers call `.toISOString()` explicitly before returning.

---

## Mappers (`src/db/mappers.ts`)

Each mapper is a pure function that takes a typed row and returns a typed domain object. This is the only place where snake_case → camelCase conversion happens, `null` → `undefined` coercion happens, `Date` → `string` (`.toISOString()`) conversion happens where needed, and JSON string → object parsing happens defensively for JSONB columns.
```typescript
export function mapBpmn(row: BpmnRow): Bpmn {
  return {
    id:                  row.lde_id,
    bpmnProcessId:       row.bpmn_process_id,
    name:                row.name,
    description:         row.description ?? undefined,
    xml:                 row.xml,
    processRole:         row.process_role,
    calledElement:       row.called_element ?? undefined,
    linkedDmnTemplates:  row.linked_dmn_templates ?? [],
    status:              row.status,
    readonly:            row.readonly,
    schemaVersion:       row.schema_version,
    createdAt:           row.created_at,
    updatedAt:           row.updated_at,
  };
}
```

The JSONB defensive guard used in `mapForm` and `mapDocument`:
```typescript
schema: typeof r.schema === 'string' ? JSON.parse(r.schema) : r.schema,
```

The `pg` driver returns JSONB columns as already-parsed objects, so the `JSON.parse` branch will never fire in normal operation. The guard exists for resilience if a test fixture or a future driver version returns a raw string.

---

## Services

Services import the row types, domain types, and mappers. They never use `as` casts on query results:
```typescript
import { BpmnRow } from '../db/types';
import { Bpmn }    from '../domain/types';
import { mapBpmn } from '../db/mappers';

export async function listBpmn(): Promise<Bpmn[]> {
  if (!pool) return [];
  const { rows } = await pool.query<BpmnRow>(
    `SELECT ... FROM process_definitions ORDER BY updated_at DESC`
  );
  return rows.map(mapBpmn);
}
```

---

## Entities covered

| Entity | DB row type | Domain type | Mapper |
|---|---|---|---|
| BPMN process | `BpmnRow` | `Bpmn` | `mapBpmn` |
| Form schema | `FormRow` | `Form` | `mapForm` |
| Document template | `DocumentRow` | `Document` | `mapDocument` |
| RoPA record | `RopaRecordRow` | `RopaRecord` | `mapRopaRecord` |
| RoPA field | `RopaFieldRow` | `RopaPersonalDataField` | `mapRopaField` |

---

## Adding a new entity

1. Add a `XxxRow` type to `src/db/types.ts` matching the DDL column names exactly.
2. Add a domain type to `src/domain/types.ts` (or `src/types/` if it is shared with the frontend).
3. Add a `mapXxx` function to `src/db/mappers.ts`.
4. In the service, type the `pool.query<XxxRow>()` call and map results with `rows.map(mapXxx)`.

Never add row-to-domain mapping logic inside a service or route handler — all conversion belongs in `mappers.ts`.

---

## Related pages

- [Asset Storage](asset-storage.md) — write-through cache, hydration, and DB schema
- [RoPA Records](ropa-records.md) — RoPA service and type layer
- [Backend Architecture](backend.md) — service and route overview