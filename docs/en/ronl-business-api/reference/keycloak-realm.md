---
component: RONL Business API
---

# Keycloak Realm Configuration

The `ronl` realm is defined in `config/keycloak/ronl-realm.json`. A Keycloak imports it when it starts with `--import-realm` and has no `ronl` realm yet: a fresh local Keycloak, or a new environment. An existing realm is not re-imported. ACC and PROD keep their own realms and are changed through scripts, not by importing the file again — see [Changing the realm](#changing-the-realm).

---

## Realm settings

| Setting | Value |
|---|---|
| Realm name | `ronl` |
| Display name | RONL - Regels Overheid Nederland |
| SSL required | External requests only |
| Registration | Disabled |
| Brute force protection | Enabled |
| Max failed attempts | 5 |
| Wait increment | 60 seconds |
| Max delta time | 12 hours |

---

## Token lifespans

| Token | Lifespan |
|---|---|
| Access token | 15 minutes (`accessTokenLifespan: 900`) |
| Access token (implicit flow) | 15 minutes |
| SSO session idle | 30 minutes (`ssoSessionIdleTimeout: 1800`) |
| SSO session max | 10 hours (`ssoSessionMaxLifespan: 36000`) |
| Offline session idle | 30 days |
| Auth code | 60 seconds |

---

## Client: `ronl-business-api`

| Setting | Value |
|---|---|
| Client ID | `ronl-business-api` |
| Client authentication | Off (public client) |
| Standard flow | Enabled |
| Implicit flow | Disabled |
| Direct access grants | Enabled |
| Service accounts | Disabled |
| PKCE | Not set in the export (no `pkce.code.challenge.method` attribute) |
| Valid redirect URIs | `*` (restrict in production) |
| Web origins | `*` (restrict in production) |

---

## Protocol mappers

The following protocol mappers are configured on the `ronl-business-api-dedicated` client scope:

| Mapper name | Type | Token claim | Source attribute |
|---|---|---|---|
| `municipality` | User Attribute | `municipality` | `municipality` |
| `organisation_type` | User Attribute | `organisation_type` | `organisation_type` |
| `assurance_level` | User Attribute | `loa` | `assurance_level` |
| `mandate` | User Attribute | `mandate` | `mandate` |
| `realm_roles` | User Realm Role | `realm_access.roles` | Realm roles |
| `audience-mapper` | Audience | `aud` | Fixed: `ronl-business-api` |
| `employee_id` | User Attribute | `employeeId` | `employee_id` |
| `preferred_username` | User Property | `preferred_username` | `username` |
| `email` | User Property | `email` | `email` |
| `given_name` | User Property | `given_name` | `firstName` |
| `family_name` | User Property | `family_name` | `lastName` |

All mappers except `audience-mapper` have `id.token.claim`, `access.token.claim`, and `userinfo.token.claim` set to `true`; `audience-mapper` adds the audience to the access token only.
The `employeeId` claim is present only for users who have the `employee_id` attribute set (caseworkers and HR staff). It is used by the dashboard to auto-fetch onboarding data on login without requiring a manual ID input.

`email`, `given_name` and `family_name` identify the signer for ValidSign: without an `email` claim the backend refuses to create a signing package. ACC and PROD receive these three with `scripts/keycloak-add-token-claim-mappers.sh`.

---

## Machine-to-machine clients

Three confidential clients authenticate with a service account and no user:

| Client ID | Name | Description |
|---|---|---|
| `operaton-mcp-client` | Operaton MCP Client | Machine-to-machine client for MCP-based Operaton interaction via the RONL Business API |
| `edocs-mcp-client` | eDOCS MCP Client | Used by the AI Assistant's eDOCS MCP subprocess to call this backend's own `/v1/edocs/*` HTTP surface |
| `copilot-studio-edocs` | Copilot Studio — eDOCS | Machine-to-machine client for Microsoft Copilot Studio eDOCS POC |

---

## Identity provider: `entra-flevoland`

An OIDC provider for Provincie Flevoland's Entra ID, configured by `scripts/keycloak-add-entra-idp.sh` rather than by the realm export, because it carries a client secret. Its mappers set `municipality = flevoland`, `organisation_type = province` and `assurance_level = substantieel`, and map the Entra app roles `IOU_ADMIN`, `IOU_USERS`, `IOU_PA` and `IOU_INFRA` to `admin`, `caseworker`, `public-affairs` and `infra-projectteam`, on every login. The provider is hidden on the Keycloak login form (`hideOnLogin`); Flevoland employees reach it through the landing page. It stores the Entra tokens it receives (`storeToken`, with `offline_access` in its default scope), so the backend can act in eDOCS as the person; the same script adds the `broker` client's `read-token` role to `default-roles-ronl` and the `broker-roles` client mapper to `ronl-business-api`. None of this is in the realm export. See [Entra ID](../developer/deployment/entra-id.md).

The export itself carries two SAML providers, `digid` (DigiD) and `eidas` (eIDAS), both disabled.

---

## Realm roles

The realm defines 60 roles.

### General

| Role | Description |
|---|---|
| `citizen` | Regular citizen using municipality services |
| `representative` | Representative acting on behalf of a citizen (with mandate) |
| `caseworker` | Municipality caseworker processing applications |
| `admin` | Municipality administrator |
| `hr-medewerker` | HR department employee who manages staff onboarding |
| `infra-projectteam` | Infrastructure project team member — can claim RIP Phase 1 tasks |
| `infra-medewerker` | Infrastructure employee role assigned via HR onboarding DMN |

### Management capacity claim

| Role | Description |
|---|---|
| `manager` | Line manager — can start a management capacity claim and prepare intake/staffing/hiring forms |
| `board-secretary` | Board Secretary — schedules capacity claims on the Board of Directors agenda |
| `board-director` | Board of Directors member — decides approval/rejection of capacity claims |
| `hrm-unit` | HRM unit — handles recruitment handover for approved staffing claims |
| `procurement-unit` | Procurement unit — handles procurement handover for approved hiring claims |
| `planning-control-officer` | Planning & Control officer — co-recipient of procurement handover |
| `financial-controller` | Financial controller — registers the financial reservation for approved claims |
| `hr-business-partner` | HR Business Partner — participates in the reconsideration meeting on rejected claims |
| `personnel-controller` | Personnel Controller — participates in the reconsideration meeting on rejected claims |

### Besluitvorming onder gedelegeerde bevoegdheid

One role per human lane of the process; see [Caseworker — Besluitvorming](../user-guide/caseworker.md#besluitvorming).

| Role | Description |
|---|---|
| `besluit-indiener` | Besluitvorming gedelegeerde bevoegdheid — Aanvrager / Indiener: bereidt het besluit voor en dient het in |
| `besluit-jurist` | Besluitvorming gedelegeerde bevoegdheid — Juridische Zaken / Compliance: toetst en adviseert |
| `besluit-bestuursautoriteit` | Besluitvorming gedelegeerde bevoegdheid — Bevoegde bestuursautoriteit: neemt geëscaleerde besluiten |
| `besluit-ondertekenaar` | Besluitvorming gedelegeerde bevoegdheid — Gemachtigde ondertekenaar: ondertekent het besluit via ValidSign |
| `besluit-registratie` | Besluitvorming gedelegeerde bevoegdheid — Registratie & Beheer: registreert en archiveert |

### Public Affairs and Woo

| Role | Description |
|---|---|
| `public-affairs` | Provincial Public Affairs adviser — access to the PA-cockpit |
| `pa-author` | PA Dossierbeheer — Auteur: maakt en bewerkt dossiers (create, edit) |
| `pa-editor` | PA Dossierbeheer — Redacteur: + sjablonen beheren en publiceren (templates, publish) |
| `pa-admin` | PA Dossierbeheer — Beheerder: + Archiefwet-archivering en definitief verwijderen (archive, delete) |
| `woo-coordinatie` | Woo-coördinator — beheert en verantwoordt Woo-verzoeken (Wet open overheid) |

### RIP

The candidate groups the RIP process models address their tasks to. A task list shows only the tasks addressed to a role the user holds.

| Role | Description |
|---|---|
| `rip-aandrager` | RIP Fase 1 (R2.1) — aandrager/indiener: levert het projectplan en intakeformulier aan |
| `rip-adviseur` | RIP — adviseur |
| `rip-adviseur-veiligheid-gezondheid` | RIP — adviseur veiligheid & gezondheid |
| `rip-ao` | RIP Fase 1 (R2.1) — ambtelijk opdrachtgever |
| `rip-beheerder` | RIP — beheerder |
| `rip-beheerder-assetmanagement` | RIP — beheerder assetmanagement |
| `rip-communicatieadviseur` | RIP — communicatieadviseur |
| `rip-concerndirecteur` | RIP — concerndirecteur |
| `rip-databeheerder` | RIP — databeheerder |
| `rip-deelnemers-evaluatie` | RIP — deelnemer evaluatie |
| `rip-deelnemers-psu` | RIP Fase 1 (R2.1) — deelnemers project start-up (PSU) |
| `rip-directievoerder` | RIP — directievoerder |
| `rip-financien` | RIP — financiën |
| `rip-infra-overleg` | RIP — Infra-overleg |
| `rip-inkoopadviseur` | RIP — inkoopadviseur |
| `rip-inkoopadviseur-werken` | RIP — inkoopadviseur werken |
| `rip-kosten-contractdeskundige` | RIP — kosten- en contractdeskundige |
| `rip-kostenadviseur` | RIP — kostenadviseur |
| `rip-kwaliteit` | RIP — kwaliteitstoetsing |
| `rip-manager-financien` | RIP — manager financiën |
| `rip-manager-pb` | RIP Fase 1 (R2.1) — manager planvoorbereiding |
| `rip-omgevingsmanager` | RIP — omgevingsmanager |
| `rip-ondersteuner` | RIP — ondersteuner |
| `rip-ontwerper` | RIP — ontwerper |
| `rip-opdrachtnemer` | RIP — opdrachtnemer (externe partij) |
| `rip-pkt` | RIP — projectkwaliteitsteam (PKT) |
| `rip-projectbeheersing` | RIP — projectbeheersing |
| `rip-projectleider` | RIP Fase 1 (R2.1) — projectleider |
| `rip-projectondersteuner` | RIP — projectondersteuner |
| `rip-team` | RIP Fase 1 (R2.1) — RIP-team |
| `rip-technisch-administratief-medewerker` | RIP — technisch-administratief medewerker |
| `rip-technisch-adviseur` | RIP — technisch adviseur |
| `rip-toezichthouder` | RIP — toezichthouder |
| `rip-vestigingsmanager` | RIP — vestigingsmanager |

---

## Test users

The export defines 27 test users, all with password `test123` and `assurance_level = hoog`. The `ronl-business-api` client allows direct access grants, so a test token can be requested with a username and password.

| Username | `municipality` | `organisation_type` | Realm roles |
|---|---|---|---|
| `test-citizen-utrecht` | `utrecht` | `municipality` | `citizen` |
| `test-caseworker-utrecht` | `utrecht` | `municipality` | `caseworker` |
| `test-citizen-amsterdam` | `amsterdam` | `municipality` | `citizen` |
| `test-caseworker-amsterdam` | `amsterdam` | `municipality` | `caseworker` |
| `test-citizen-heusden` | `heusden` | `municipality` | `citizen` |
| `test-caseworker-heusden` | `heusden` | `municipality` | `caseworker` |
| `test-citizen-rotterdam` | `rotterdam` | `municipality` | `citizen` |
| `test-caseworker-rotterdam` | `rotterdam` | `municipality` | `caseworker` |
| `test-citizen-denhaag` | `denhaag` | `municipality` | `citizen` |
| `test-caseworker-denhaag` | `denhaag` | `municipality` | `caseworker` |
| `test-hr-denhaag` | `denhaag` | `municipality` | `caseworker`, `hr-medewerker` |
| `test-onboarded-denhaag` | `denhaag` | `municipality` | `caseworker` |
| `test-citizen-flevoland` | `flevoland` | `province` | `citizen` |
| `test-caseworker-flevoland` | `flevoland` | `province` | `caseworker`, `besluit-indiener` |
| `test-hr-flevoland` | `flevoland` | `province` | `caseworker`, `hr-medewerker`, `board-secretary`, `board-director`, `hrm-unit`, `procurement-unit`, `planning-control-officer`, `financial-controller`, `hr-business-partner`, `personnel-controller` |
| `test-mngr-flevoland` | `flevoland` | `province` | `caseworker`, `manager` |
| `test-indiener-flevoland` | `flevoland` | `province` | `caseworker`, `besluit-indiener` |
| `test-besluit-flevoland` | `flevoland` | `province` | `caseworker`, `besluit-jurist`, `besluit-bestuursautoriteit`, `besluit-ondertekenaar`, `besluit-registratie` |
| `test-infra-flevoland` | `flevoland` | `province` | `caseworker`, `infra-projectteam`, `infra-medewerker`, and all 34 `rip-*` roles |
| `test-pa-flevoland` | `flevoland` | `province` | `public-affairs`, `pa-author`, `pa-editor`, `pa-admin` |
| `test-woo-flevoland` | `flevoland` | `province` | `woo-coordinatie` |
| `test-citizen-uwv` | `uwv` | `national` | `citizen` |
| `test-caseworker-uwv` | `uwv` | `national` | `caseworker` |
| `test-citizen-toeslagen` | `toeslagen` | `national` | `citizen` |
| `test-caseworker-toeslagen` | `toeslagen` | `national` | `caseworker` |
| `test-citizen-unive` | `unive` | `commercial` | `citizen` |
| `test-caseworker-unive` | `unive` | `commercial` | `caseworker` |

`test-hr-denhaag` is the primary HR test account — it holds the `hr-medewerker` realm role and can start onboarding processes and view the Afgeronde onboardingen archive. `test-onboarded-denhaag` simulates an employee who has already been onboarded; logging in with this account triggers an auto-fetch of the completed onboarding record for `emp-test-01`.

`test-hr-flevoland` is the Flevoland HR account for onboarding infrastructure employees, and also holds every role of the management capacity claim except `manager`; `test-mngr-flevoland` is the manager who starts a claim. `test-infra-flevoland` is a pre-configured infrastructure team member (`employeeId: EMP-FLV-001`) who can start and work through the RIP processes.

For Besluitvorming onder gedelegeerde bevoegdheid, `test-indiener-flevoland` prepares a besluit and `test-besluit-flevoland` holds the four other lanes. `test-caseworker-flevoland`, the everyday Flevoland caseworker, can prepare a besluit too. Both besluit accounts have an e-mail address, which signing with ValidSign needs.

`test-pa-flevoland` opens the PA-cockpit and `test-woo-flevoland` the Woo board.

---

## Changing the realm

Editing `config/keycloak/ronl-realm.json` changes a **local** Keycloak, the next time it imports the file. An existing realm is not imported again, so start from an empty volume:

```bash
npm run docker:down:volumes && npm run docker:up
```

This also removes what was added to the local realm by hand or by script; run `scripts/keycloak-add-entra-idp.sh` again afterwards if you use the Entra provider locally.

**ACC and PROD are not re-imported.** An import either skips what already exists or overwrites whole definitions, discarding what those environments configured by hand — redirect URIs, web origins, client secrets, the identity provider, roles granted to employees. Their realms are changed through the admin REST API by idempotent scripts in `scripts/`:

| Change | Script |
|---|---|
| New realm roles | `keycloak-add-rip-roles.sh` — creates every role in the realm file whose name starts with `ROLE_PREFIX` (default `rip-`), and grants them all to `GRANT_USER` (default `test-infra-flevoland` for `rip-`, empty for any other prefix; empty grants nothing) |
| The ValidSign token claims | `keycloak-add-token-claim-mappers.sh` |
| The Entra ID identity provider, its token storage, the `read-token` default role and the `broker-roles` client mapper | `keycloak-add-entra-idp.sh` |

For the besluit roles, for example:

```bash
KEYCLOAK_URL=https://acc.keycloak.open-regels.nl ROLE_PREFIX=besluit- GRANT_USER= \
  bash scripts/keycloak-add-rip-roles.sh
```

Anything else — a new test user, a role for one particular user — is done in the admin console. See [Entra ID — Rolling out to an environment](../developer/deployment/entra-id.md#rolling-out-to-an-environment) for running the scripts.
