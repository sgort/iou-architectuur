---
component: Linked Data Explorer
---

# Form Editor Implementation

The Form Editor wraps the `@bpmn-io/form-js` library in a two-panel React component. This page covers the component structure, storage layer, and the integration points with the BPMN Modeler.

---

## Component structure

```
packages/frontend/src/components/FormEditor/
├── FormEditor.tsx        main orchestrator — state, seeding, CRUD callbacks
├── FormCanvas.tsx        @bpmn-io/form-js editor canvas wrapper
└── FormList.tsx          left-panel list with create / rename / delete actions

packages/frontend/src/
├── services/
│   └── formService.ts    localStorage CRUD for FormSchema records
└── types/
    └── index.ts          FormSchema interface
```

---

## `FormSchema` type

```typescript
interface FormSchema {
  id: string;                          // internal UUID used as list key
  name: string;                        // display name
  description?: string;
  schema: Record<string, unknown>;     // the @bpmn-io/form-js JSON schema
  createdAt: string;                   // ISO 8601
  updatedAt: string;
  readonly?: boolean;                  // skips the backend write; no seeded form sets it
  status?: 'example' | 'wip' | 'dso' | 'e2e';
  language?: 'en' | 'nl' | 'de';
  organization?: string;
}
```

The `schema.id` field inside the JSON schema object is the **form identifier** used in BPMN XML (`camunda:formRef`) and in the Operaton deployment. It is distinct from the outer `FormSchema.id` used as the localStorage record key.

---

## `FormService`

`FormService` is a static class providing synchronous localStorage CRUD:

```typescript
import { FormService } from '../../services/formService';

const STORAGE_KEY = 'linkedDataExplorer_formSchemas';

FormService.getForms(): FormSchema[]
FormService.getForm(formId: string): FormSchema | null   // by FormSchema.id
FormService.saveForm(form: FormSchema): void             // upsert by .id
FormService.deleteForm(formId: string): void
```

The methods read/write the entire array on each call. There is no batching or indexedDB fallback.

---

## `FormEditor.tsx` — seeding logic

`EXAMPLE_FORMS` at the top of `FormEditor.tsx` lists 22 example forms — id, display name, description, path under `public/examples/`, `language` and `organization`. On mount, a `useEffect` seeds them by version rather than by presence:

```typescript
for (const def of EXAMPLE_FORMS) {
  if (getStoredVersion(def.id) >= EXAMPLE_VERSIONS[def.id]) continue;

  const schema = await fetch(def.path).then((r) => r.json());
  const form: FormSchema = {
    id: def.id,
    // name, description, schema, createdAt, updatedAt …
    readonly: false,
    status: 'example',
    language: def.language,
    organization: def.organization,
  };
  FormService.saveForm(form);
  setStoredVersion(def.id, EXAMPLE_VERSIONS[def.id]);
}
```

`EXAMPLE_VERSIONS`, `getStoredVersion` and `setStoredVersion` live in `utils/exampleVersions.ts`, shared with the BPMN Modeler's seed. The recorded versions sit in `localStorage` under `linkedDataExplorer_exampleVersions`, so they are per browser. A form is re-fetched and its record overwritten when its number in `EXAMPLE_VERSIONS` is higher than the recorded one, or when none is recorded; to ship a changed `.form` file to existing users, bump its entry. When any form was seeded, the effect refreshes the list and opens the first one.

Seeded records are `readonly: false` with `status: 'example'`, and the two fields do different jobs:

- **`status: 'example'`** shows the **EXAMPLE** badge and makes `handleDeleteForm` refuse with *Cannot delete example forms*.
- **`readonly`** is what `FormList` checks for the rename and delete controls and the footer's language and organization fields, and what `FormService.saveForm` checks before POSTing to `/v1/assets/forms`. Because it is `false`, an example can be edited, saved and renamed, and seeding itself writes every example to the backend.

A user's edit to an example therefore survives only until the seed runs for that id again — after a version bump, or in a browser with no recorded version — when the bundled file overwrites it locally and on the backend.

The Kapvergunning examples `example_kapvergunning_start`, `example_tree_felling_review` and `example_awb_notify_applicant` embed the `schema.id` values `kapvergunning-start`, `tree-felling-review` and `awb-notify-applicant` — the values written into `camunda:formRef`.

---

## `FormCanvas.tsx` — editor lifecycle

`FormCanvas.tsx` mounts a `@bpmn-io/form-js` `FormEditor` instance:

```typescript
import { FormEditor as FormJsEditor } from '@bpmn-io/form-js';

useEffect(() => {
  const editor = new FormJsEditor({ container: containerRef.current });
  editorRef.current = editor;

  editor.importSchema(schema);
  editor.on('changed', () => setHasChanges(true));

  return () => {
    editor.destroy();
    editorRef.current = null;
  };
}, [schema]);   // re-mounts on schema identity change (new form selected)
```

The `schema` prop is the `FormSchema.schema` object for the currently active form. Because `schema` is a new object reference each time a different form is selected, the `useEffect` re-runs and the editor instance is replaced cleanly.

### Save flow

```typescript
const handleSave = async () => {
  const { schema: savedSchema } = await editorRef.current.saveSchema();
  onSave(savedSchema);   // parent writes to FormService
  setHasChanges(false);
};
```

### Export flow

```typescript
const handleExport = async () => {
  const { schema: exportSchema } = await editorRef.current.saveSchema();
  const formId = exportSchema.id ?? 'form';
  // ... download as `{formId}.form`
};
```

---

## Integration with `FormTemplateSelector`

`FormTemplateSelector` (in `BpmnModeler/`) reads forms directly from `FormService.getForms()` on mount. Because both `FormEditor` and `FormTemplateSelector` use the same `FormService` singleton over shared `localStorage`, no pub/sub or context is needed — a form saved in the Form Editor is immediately visible the next time the properties panel mounts for a `UserTask` or `StartEvent`.

---

## Form schema requirements for Operaton

Every form deployed to Operaton must satisfy:

1. `schemaVersion: 16` — the version Operaton resolves at runtime.
2. A `schema.id` that matches the `camunda:formRef` value in the BPMN XML.
3. A `Button` component with `action: "submit"` at the end of the `components` array. `@bpmn-io/form-js` does not inject one automatically; omitting it causes the form to render but never emit the `submit` event.
4. Deployed in the **same Operaton deployment** as the BPMN that references it. The deploy modal in the BPMN Modeler handles this automatically — see [BPMN Modeler Implementation — Deploy modal](bpmn-modeler.md#deploy-modal).

---

## CSS

`@bpmn-io/form-js` requires two stylesheet imports:

```typescript
import '@bpmn-io/form-js/dist/assets/form-js.css';
import '@bpmn-io/form-js/dist/assets/form-js-editor.css';
```

Both are imported at the top of `FormCanvas.tsx`. They are bundled by Vite and apply globally to the form editor canvas.
