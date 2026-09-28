---
component: RONL Business API
---

# Entra ID (Provincie Flevoland)

Employees of Provincie Flevoland sign in to RBA with their Flevoland M365 account. Keycloak brokers the sign-in: the browser goes to Entra ID, Entra authenticates the employee (with MFA, required by Flevoland's conditional-access policy), and Keycloak issues the token RBA validates. The backend still trusts one issuer — Keycloak — and did not change.

---

## What the employee sees

The landing page's primary button, **Inloggen met uw Flevoland-account**, sends the browser through Keycloak straight to Microsoft. On a Flevoland-managed Windows laptop, Entra signs the employee in with the account the device is joined to, usually without a prompt. This works natively in Edge; Chrome needs the Windows Accounts extension, Firefox the "Allow Windows single sign-on" setting. The Keycloak login page also shows a **Flevoland (Entra ID)** button, as a fallback.

After sign-in the employee lands on the dashboard for their role.

---

## The Entra side

Flevoland IT owns the app registration **IOU-demonstrator**.

| Setting | Value |
|---|---|
| Tenant ID | `95f3a7d8-730c-4f35-a909-867d3fbde8fe` |
| Application (client) ID | `ef967eb0-3902-408f-8161-4e294c826473` |
| Platform | Web |
| Optional ID-token claims | `email`, `given_name`, `family_name` |
| Assignment required | Yes |

Redirect URIs, one per Keycloak:

| Environment | Redirect URI |
|---|---|
| Local | `http://localhost:8080/realms/ronl/broker/entra-flevoland/endpoint` |
| ACC | `https://acc.keycloak.open-regels.nl/realms/ronl/broker/entra-flevoland/endpoint` |
| PROD | `https://keycloak.open-regels.nl/realms/ronl/broker/entra-flevoland/endpoint` |

Access is granted through Entra groups, each assigned one app role:

| Entra group | App role | RBA realm role |
|---|---|---|
| `flv-role-iou-poc-admin` | `IOU_ADMIN` | `admin` |
| `flv-role-iou-poc-user` | `IOU_USER` | `caseworker` |
| `Flv-role-IOU-publicAffairs-contributors` | `IOU_PA` | `public-affairs` |
| `Flv-role-IOU-infra-contributors` | `IOU_INFRA` | `infra-projectteam` |

An employee in none of the groups cannot sign in: Entra refuses before Keycloak is involved.

---

## The Keycloak side

The identity provider `entra-flevoland` in realm `ronl` is created by `scripts/keycloak-add-entra-idp.sh`, from the definition in `scripts/keycloak-entra-idp.json`. It is not in the realm export, because it carries a client secret.

Its mappers run on every login (sync mode `FORCE`):

| Mapper | Effect |
|---|---|
| `municipality` | `municipality = flevoland` |
| `organisation-type` | `organisation_type = province` |
| `assurance-level` | `assurance_level = substantieel` |
| `role-iou-admin`, `role-iou-user`, `role-iou-pa`, `role-iou-infra` | Add the realm role while the Entra app role is present; remove it once it is gone |

Roles assigned by hand in Keycloak — `pa-author`, `pa-editor`, `pa-admin`, the `rip-*` groups — are not touched by the mappers. Assign them to the brokered user after their first login.

The four mapped roles are the exception. A hand-assigned `admin`, `caseworker`, `public-affairs` or `infra-projectteam` is removed at the next login whenever the Entra token lacks the matching app role. Grant those through the Entra groups only.

---

## Infra-board users

`infra-projectteam` opens the Infra-board, but its task list is filtered by the `rip-*` candidate groups the RIP processes address their tasks to. Without them the board shows no tasks. After the employee's first login — the Keycloak user must exist — grant the `rip-*` roles with the existing script, and `infra-medewerker` in the admin console (Users → the employee → Role mapping):

```bash
KEYCLOAK_URL=https://acc.keycloak.open-regels.nl \
GRANT_USER=steven.gort@flevoland.nl \
  bash scripts/keycloak-add-rip-roles.sh
```

The brokered user's username is their Entra `preferred_username`, e.g. `steven.gort@flevoland.nl`.

---

## Running the script

The script is idempotent: it creates what is missing and updates what exists. Re-running it is also how a rotated secret goes in.

```bash
KEYCLOAK_URL=https://acc.keycloak.open-regels.nl \
ENTRA_TENANT_ID=95f3a7d8-730c-4f35-a909-867d3fbde8fe \
ENTRA_CLIENT_ID=ef967eb0-3902-408f-8161-4e294c826473 \
  bash scripts/keycloak-add-entra-idp.sh
```

It prompts for the Keycloak admin password and the Entra client secret. The secret is never printed or written to disk. `--dry-run` shows what would be sent, with the secret redacted, without contacting Keycloak.

Before creating anything the script checks that the four mapped realm roles exist, and stops with their names if one is missing.

Locally, run it again after every fresh `--import-realm`.

---

## Rotating the client secret

Flevoland IT issues a new secret before the current one expires. Run the script again with the new secret; it updates the provider in place. Logins fail from the moment the old secret expires until the new one is in.

---

## Troubleshooting

| Symptom | Cause |
|---|---|
| Microsoft shows `AADSTS50011` (redirect URI mismatch) | The environment's redirect URI is not registered on the app registration. The script prints the exact URI |
| Microsoft shows `AADSTS50105` (not assigned) | The employee is in none of the four groups |
| Microsoft shows `AADSTS700016` (application not found in the directory) | The client ID is wrong — typically the secret's ID was used. Re-run the script with the app registration's *Application (client) ID* |
| Keycloak: "Unexpected error when authenticating with identity provider" (HTTP 502 on `/broker/entra-flevoland/endpoint`) | Keycloak could not exchange the code at Entra. The Keycloak container log (`docker compose logs keycloak` locally) names the Entra error |
| Keycloak log: `AADSTS7000215` (invalid client secret) | The secret in Keycloak is not the secret's **value** — often the secret ID, or a mis-pasted value. Re-run the script with the value from the *Value* column; it is shown only when the secret is created |
| Signed in, but `403 INSUFFICIENT_ASSURANCE` | The `assurance-level` mapper is missing; re-run the script |
| Infra-board opens, but shows no tasks | The employee lacks the `rip-*` roles; see [Infra-board users](#infra-board-users) |
| Signed in, but no tasks or dashboard | The employee's Entra group gives a role that is not the one the dashboard needs; check the token's `realm_access.roles` |
| Several Microsoft accounts in the browser | Entra shows its account picker; choose the Flevoland account |

---

## Related

- [Keycloak (VM)](keycloak.md)
- [Authentication & IAM](../../features/authentication-iam.md)
- [Keycloak Realm Configuration](../../reference/keycloak-realm.md)
