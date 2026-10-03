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
| `flv-role-iou-poc-user` | `IOU_USERS` | `caseworker` |
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

Roles assigned by hand in Keycloak — `pa-author`, `pa-editor`, `pa-admin`, the `rip-*` and `besluit-*` roles — are not touched by the mappers. Assign them to the brokered user after their first login.

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

The script is idempotent: it creates what is missing, updates what exists, and deletes a mapper on the provider that `scripts/keycloak-entra-idp.json` no longer defines, reporting it as `removed mapper …`. Re-running it is also how a rotated secret goes in.

```bash
KEYCLOAK_URL=https://acc.keycloak.open-regels.nl \
ENTRA_TENANT_ID=95f3a7d8-730c-4f35-a909-867d3fbde8fe \
ENTRA_CLIENT_ID=ef967eb0-3902-408f-8161-4e294c826473 \
  bash scripts/keycloak-add-entra-idp.sh
```

It prompts for the Keycloak admin password and the Entra client secret. The secret is never printed or written to disk. `--dry-run` shows what would be sent, with the secret redacted, without contacting Keycloak.

Before creating anything the script checks that the four mapped realm roles exist, and stops with their names if one is missing.

It also normalises what you paste. Both GUIDs are trimmed of surrounding whitespace and of the carriage return a copied value can carry — the Flevoland client id arrived with a leading space — and both are then **lower-cased**. That last step matters: Entra issues tokens with the tenant id in lower case and Keycloak compares the token's `iss` to the configured issuer as an exact string, so an upper-case paste passes the GUID check and then fails every login.

It handles the Keycloak credentials the same way as `keycloak-add-rip-roles.sh` and `keycloak-add-token-claim-mappers.sh`. The admin password reaches `curl` on stdin, never as an argument, so it does not show in the process list. The admin token is passed to `curl` through a config file readable only by you (mode `0600`), in a private temporary directory the script removes however it ends. When Keycloak cannot be reached at all, the error reads `could not obtain an admin token (HTTP 000)`.

At the end the script checks the provider's mappers against the file: a mapper missing after the run, a duplicate, or one present in Keycloak but not in the file fails the run.

Locally, run it again after every fresh `--import-realm`.

---

## Rolling out to an environment

Every Keycloak has its own realm. Each environment therefore needs the provider, and each employee there needs the roles that do not come from Entra, set up separately. The landing-page button reaches ACC when a pull request merges into `acc`, and PROD with the `acc` → `main` promotion. The fallback button on the Keycloak login page works as soon as the provider exists.

| | ACC | PROD |
|---|---|---|
| Keycloak | `https://acc.keycloak.open-regels.nl` | `https://keycloak.open-regels.nl` |
| Landing page | `https://acc.mijn.open-regels.nl` | `https://mijn.open-regels.nl` |
| Redirect URI registered in Entra | Yes | **Ask Flevoland IT first** — see [The Entra side](#the-entra-side) |
| Keycloak admin password | `KEYCLOAK_ADMIN_PASSWORD` in the `.env` beside the Keycloak `docker-compose.yml` on the ACC VM | The same, on the PROD VM |

Run the commands from a checkout of `ronl-business-api` that contains the change, in Git Bash. Set `KEYCLOAK_URL` once per environment:

```bash
KEYCLOAK_URL=https://acc.keycloak.open-regels.nl   # PROD: https://keycloak.open-regels.nl
```

**1. Check the secret against Entra, then create the provider.** Entra is asked for a token with the secret first. Only if it accepts does the script run, so a secret ID or a mis-pasted value cannot reach Keycloak:

```bash
read -rsp "Entra client secret VALUE: " ENTRA_CLIENT_SECRET; echo; export ENTRA_CLIENT_SECRET
printf '%s' "$ENTRA_CLIENT_SECRET" | curl -s -X POST \
  https://login.microsoftonline.com/95f3a7d8-730c-4f35-a909-867d3fbde8fe/oauth2/v2.0/token \
  -d client_id=ef967eb0-3902-408f-8161-4e294c826473 -d grant_type=client_credentials \
  --data-urlencode scope=https://graph.microsoft.com/.default --data-urlencode client_secret@- \
  | jq -e '.access_token' >/dev/null && echo "SECRET OK" \
&& KEYCLOAK_URL=$KEYCLOAK_URL \
   ENTRA_TENANT_ID=95f3a7d8-730c-4f35-a909-867d3fbde8fe \
   ENTRA_CLIENT_ID=ef967eb0-3902-408f-8161-4e294c826473 \
   bash scripts/keycloak-add-entra-idp.sh
```

Expected: `SECRET OK`, `all mapped roles present in realm ronl`, `created provider entra-flevoland`, seven `created mapper` lines and `verified: provider entra-flevoland with 7 mappers in realm ronl`, followed by the redirect URI to register in Entra. On a re-run the lines read `updated` instead of `created`, and a mapper no longer in the file shows as `removed mapper`. If the script reports that the realm lacks a mapped role, create that role in the realm first; do not remove the mapper.

**2. First login.** Each employee signs in once through **Inloggen met uw Flevoland-account**. This creates their Keycloak user, with the tenant attributes and the roles of their Entra groups. Until step 3 an Infra-board user sees the board without tasks.

**3. Grant the roles that do not come from Entra.** Per employee, after their first login:

```bash
KEYCLOAK_URL=$KEYCLOAK_URL GRANT_USER=steven.gort@flevoland.nl \
  bash scripts/keycloak-add-rip-roles.sh
```

The script also creates any `rip-*` role the realm lacks. It grants **every** `rip-*` role to `GRANT_USER`; leave `GRANT_USER` out and they go to its default, `test-infra-flevoland`.

For colleagues who take part in Besluitvorming onder gedelegeerde bevoegdheid, create the five `besluit-*` roles once per environment with the same script:

```bash
KEYCLOAK_URL=$KEYCLOAK_URL ROLE_PREFIX=besluit- GRANT_USER= \n  bash scripts/keycloak-add-rip-roles.sh
```

With `GRANT_USER` empty the script only creates the roles. `GRANT_USER=<username>` would grant all five to that one user, which suits a demonstration account that plays every lane but not a colleague who holds one; without `GRANT_USER` at all, all five go to `test-infra-flevoland`. Assign each colleague the role of their lane in the admin console instead — see [Caseworker — Besluitvorming](../../user-guide/caseworker.md#besluitvorming) for which lane does what.

Then, in the admin console (Users → the employee → Role mapping), assign `infra-medewerker` to Infra-board users, and where needed `woo-coordinatie` (Woo board), `pa-author`, `pa-editor` or `pa-admin` (Dossierbeheer) and a `besluit-*` role (Besluitvorming). Never assign `admin`, `caseworker`, `public-affairs` or `infra-projectteam` here; see [The Keycloak side](#the-keycloak-side).

**4. Sign out and in again, and check.** A new token carries the new roles. In the admin console the employee's **Attributes** show `municipality=flevoland`, `organisation_type=province` and `assurance_level=substantieel`, and **Role mapping** shows the Entra-mapped roles plus those from step 3. The Flevoland button lands on the highest-priority board the roles allow (Woo, then Infra-board, then PA-Cockpit, then Caseworker). The other boards open through their cards on the landing page.

**5. Record the secret's expiry date** for this environment. Rotation means repeating step 1 in every environment; see below.

---

## Adding and removing an employee

Flevoland IT grants access by adding a colleague to one or more of the four Entra groups. Some of the result is automatic; the rest is a manual step in Keycloak that is easy to forget. Everything below applies **per environment**: ACC and PROD each create their own Keycloak user.

### When a colleague is added to a group

**Nothing can be done before their first login.** The Keycloak user does not exist until the colleague has signed in once through **Inloggen met uw Flevoland-account**. That first login creates it with `municipality=flevoland`, `organisation_type=province`, `assurance_level=substantieel` and the roles of their groups (`IOU_ADMIN` → `admin`, `IOU_USERS` → `caseworker`, `IOU_PA` → `public-affairs`, `IOU_INFRA` → `infra-projectteam`).

**After that first login**, depending on what they need:

| Group or board | Action in Keycloak | Why |
|---|---|---|
| `flv-role-iou-poc-admin` or `flv-role-iou-poc-user` only | None | Everything comes from Entra |
| `Flv-role-IOU-infra-contributors` (Infra-board) | `GRANT_USER=<email> bash scripts/keycloak-add-rip-roles.sh`, then assign `infra-medewerker` | Without the `rip-*` roles the board shows no tasks; see [Infra-board users](#infra-board-users) |
| The infra group, but **not** `flv-role-iou-poc-user` | None possible — ask Flevoland IT to add them to the user group too | Without `caseworker` the Infra-board assistant answers `403` ([ronl-business-api#251](https://github.com/sgort/ronl-business-api/issues/251)) |
| Woo board | Assign `woo-coordinatie` | No Entra app role exists for it |
| PA-Cockpit authoring (Dossierbeheer) | Assign `pa-author`, `pa-editor` or `pa-admin` as needed | These are finer than `IOU_PA` |
| Besluitvorming (Caseworker) | Assign the `besluit-*` role of their lane: `besluit-indiener`, `besluit-jurist`, `besluit-bestuursautoriteit`, `besluit-ondertekenaar` or `besluit-registratie` | No Entra app role exists for them; they also need `caseworker`, from `flv-role-iou-poc-user` |

Assign roles in the admin console: Users → the colleague (their username is their e-mail address) → Role mapping → Assign role. **Never assign `admin`, `caseworker`, `public-affairs` or `infra-projectteam` there**; the next login removes them again.

The colleague signs out and in once more to receive a token with the new roles.

### When a colleague is removed from a group, or leaves

- **Removed from a group:** the mapped role disappears at their next login. Roles assigned by hand — `rip-*`, `besluit-*`, `infra-medewerker`, `woo-coordinatie`, `pa-*` — **remain** until removed by hand in each environment.
- **Leaves the organisation:** once Flevoland IT disables the Entra account, the colleague can no longer sign in. The Keycloak user and its hand-assigned roles remain. Disable or delete the user in each environment.
- **An active session** keeps its roles until the access token expires, at most 15 minutes.

### What is manual today

For a discussion of proper user and application management, these are the steps nothing automates yet:

- **Per environment, per colleague:** the first login has to happen before any role can be granted, and every hand-assigned role is granted separately on ACC and on PROD.
- **Roles without an Entra source:** `rip-*`, `besluit-*`, `infra-medewerker`, `woo-coordinatie`, `pa-author`, `pa-editor`, `pa-admin`. The script grants all 34 `rip-*` roles at once; nothing models which RIP role a colleague actually holds.
- **No deprovisioning:** removing someone from a group, or disabling their account, leaves their hand-assigned roles and their Keycloak user in place.
- **No overview:** which colleague holds which hand-assigned role is only visible per user, per environment, in the admin console.
- **Group composition:** an infra colleague needs two groups ([ronl-business-api#251](https://github.com/sgort/ronl-business-api/issues/251)); nothing checks that.

---

## Rotating the client secret

Flevoland IT issues a new secret before the current one expires. Run step 1 of [Rolling out to an environment](#rolling-out-to-an-environment) again with the new secret, in every environment and locally; it updates the provider in place. Logins fail from the moment the old secret expires until the new one is in. Once every environment has the new secret, ask Flevoland IT to delete the old one.

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
| Keycloak log: wrong issuer, and **every** login fails from the moment the provider was created | The configured issuer does not match the `iss` Entra sends, which is the tenant id in lower case. Re-run the script; it lower-cases both IDs before it builds the endpoints |
| Several Microsoft accounts in the browser | Entra shows its account picker; choose the Flevoland account |
| A script fails with `curl: (35) schannel: … CRYPT_E_NO_REVOCATION_CHECK`, then "could not obtain an admin token (HTTP 000)" | On the Flevoland network, TLS is re-signed by a *Provincie Flevoland* CA whose revocation cannot be checked, and Git Bash's curl (Schannel) treats that as fatal; the browser does not. For the shell session, before running the scripts: `export CURL_HOME=$(mktemp -d); echo ssl-revoke-best-effort > "$CURL_HOME/.curlrc"`. The chain is still verified against the Windows store; only an uncheckable revocation is tolerated |

---

## Related

- [Keycloak (VM)](keycloak.md)
- [Authentication & IAM](../../features/authentication-iam.md)
- [Keycloak Realm Configuration](../../reference/keycloak-realm.md)
