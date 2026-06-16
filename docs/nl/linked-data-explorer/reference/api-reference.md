# API Referentie

!!! info "Documentatie in ontwikkeling"
    De Nederlandse vertaling van deze pagina is nog niet beschikbaar.
    Raadpleeg de <a href="/linked-data-explorer/reference/api-reference/">Engelse versie</a> voor de huidige inhoud.

---

**Status:** Concept
**Engelstalige bron:** `linked-data-explorer/reference/api-reference.md`

---

## Root

### `GET /`

---

## Health

### `GET /v1/health`

---

## DMN discovery

### `GET /v1/dmns`

### `GET /v1/dmns/enhanced-chain-links`

### `GET /v1/dmns/semantic-equivalences`

### `GET /v1/dmns/cycles`

---

## Chain discovery

### `GET /v1/chains`

---

## Chain execution

### `POST /v1/chains/execute`

### `POST /v1/chains/execute/heusdenpas`

### `POST /v1/chains/export`

---

## TriplyDB proxy

### `POST /v1/triplydb/query`

---

## eDOCS

### `GET /v1/edocs/status`

### `POST /v1/edocs/workspaces/ensure`

### `POST /v1/edocs/documents`

### `GET /v1/edocs/workspaces/:workspaceId/documents`

---

## Asset Storage

### `GET /v1/assets/bpmn`

### `POST /v1/assets/bpmn`

### `DELETE /v1/assets/bpmn/:id`

### `GET /v1/assets/bpmn/by-bpmn-id/:bpmnProcessId`

### `GET /v1/assets/forms`

### `POST /v1/assets/forms`

### `DELETE /v1/assets/forms/:id`

### `GET /v1/assets/documents`

### `POST /v1/assets/documents`

### `DELETE /v1/assets/documents/:id`

---

## SHACL validation

### `POST /v1/shacl/validate`

### `POST /v1/shacl/validate-merged`

---

## DSO Integration

### `GET /v1/dso/begrippen`

### `GET /v1/dso/activiteiten`

### `GET /v1/dso/activiteiten/:urn`

### `POST /v1/dso/activiteiten/oin`

### `POST /v1/dso/activiteiten/zoek`

### `POST /v1/dso/werkzaamheden/zoek`

### `POST /v1/dso/werkzaamheden/suggereer`

### `GET /v1/dso/werkzaamheden/:urn`

### `GET /v1/dso/toepasbare-regels`

### `GET /v1/dso/toepasbare-regels/:id/sttr`

### `GET /v1/dso/toepasbare-regels/:id/dmn`

### `GET /v1/dso/toepasbare-regels/:id/form-scaffold`

---

## Error responses

---

## Legacy endpoints and deprecation