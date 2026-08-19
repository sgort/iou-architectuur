---
component: RONL Business API
---

# Features Overview

RONL Business API is a platform of shared capabilities for running government business processes: deploying and starting BPMN processes on an Operaton engine, evaluating DMN decision tables, moving work through a task lifecycle (visible → claimed → handled → completed), rendering dynamic forms, and enforcing identity, authorisation and audit around all of it.

These capabilities are generic. They are not tied to any one process, form, or board — the same task lifecycle applies whether the running process is a permit application, a subsidy calculation, or an internal review, and multi-tenancy lets the same deployment serve more than one organisation without those organisations seeing each other's data.

---

## How this section relates to the User Guides

**Features** describes what the platform can do, at the level of the capability itself: what happens when a process is started, what makes a task visible, what claiming and completing mean. It names no particular process, form, or dashboard.

**[User Guides](../user-guide/getting-started.md)** describe how a particular surface puts those capabilities to work — the werkomgeving's boards and the public knowledge base, each with their own screens, wording, and audience. If a page depends on a specific case to make sense, it belongs there rather than here.

---

## The surfaces

The capabilities described in this section are instantiated by two surfaces:

- A signed-in **werkomgeving**, where authenticated staff work through role-scoped boards.
- A public **knowledge base**, reachable with no login, publishing the same underlying information for anyone to read.

See [Getting Started](../user-guide/getting-started.md) for how these surfaces are organised.

---

## Capabilities in this section

- [Processes](processes.md) — deploying BPMN process definitions, starting instances, and how tenancy scopes a running process
- [Tasks](tasks.md) — the task lifecycle: visibility, claiming, handling, and completion
- [Authentication & IAM](authentication-iam.md) — token validation, claims mapping, and role-based authorisation
- [Business Rules Execution](business-rules-execution.md) — DMN decision evaluation via Operaton
- [Dynamic Forms](dynamic-forms.md) — rendering start and task forms from deployed schemas
- [Documents](documents.md) — a case's documents held in an external system
- [Regelcatalogus](regelcatalogus.md) and [Procesbibliotheek](procesbibliotheek.md) — public, read-only views into the underlying rule and process catalogues
- [Public Publication](public-publication.md) — the public, unauthenticated surface those catalogues are exposed on
- [Timeline Navigation](timeline-navigation.md) — presenting a process instance's history along a time axis
- [Notifications & Watches](notifications-and-watches.md) — being told when something newly matches a person's interest
- [Security & Compliance](security-compliance.md) — audit logging and compliance posture
- [API Design](api-design.md) — the versioned REST surface and its conventions

---

## Deployment

RONL Business API is deployed for the Province of Flevoland, currently on the acceptance environment. See [Getting Started](../user-guide/getting-started.md) for the werkomgeving and public knowledge base URLs.
