# Caseworker Workflow

Caseworkers (medewerkers) have elevated access compared to citizens. They can view all process instances submitted by residents of their municipality and take action on them.

![Screenshot: RONL Business API Caseworker Dashboard](../../../assets/screenshots/ronl-business-api-caseworker-dashboard.png)

## Logging in as a caseworker

Use the same DigiD login flow as a citizen ([Logging In — DigiD Flow](login-digid-flow.md)), but with an account that has the `caseworker` role assigned in Keycloak.

In the test environment, use:

```
Username: test-caseworker-utrecht
Password: test123
```

After login, the JWT will contain `"roles": ["caseworker"]`. The portal detects this role and displays the caseworker dashboard instead of the citizen view.

## What caseworkers can do

| Action | Endpoint | Description |
|---|---|---|
| View application queue | `GET /v1/process?status=active` | All active process instances for the municipality |
| View a specific application | `GET /v1/process/:id/variables` | Full input and output variables for one instance |
| Update application status | `PUT /v1/process/:id/status` | Move an application to the next process step |
| Cancel an application | `DELETE /v1/process/:id` | Cancel a process instance |

All results are automatically filtered to the caseworker's own municipality via the `municipality` JWT claim. A caseworker from Utrecht cannot see Amsterdam's applications.

## Reviewing a citizen's application

**Step 1** — From the dashboard, select an application from the queue.

**Step 2** — The detail view shows all input variables the citizen submitted and the DMN evaluation result. The caseworker's name and timestamp are added to the audit trail on each view.

**Step 3** — If the result requires manual review (e.g. an edge case in the DMN), the caseworker can override the result and document the reason. The override is logged in the audit trail with the caseworker's user ID.

## Role differences at a glance

| Capability | Citizen | Caseworker | Admin |
|---|---|---|---|
| Submit a calculation | ✓ | ✓ | ✓ |
| View own applications | ✓ | ✓ | ✓ |
| View all municipality applications | — | ✓ | ✓ |
| Override DMN result | — | ✓ | ✓ |
| View audit logs | — | — | ✓ |
| Manage users in Keycloak | — | — | ✓ |

## Audit trail

Every action a caseworker takes is recorded in the audit log with their `sub` (user ID), the action performed, the affected process instance, and a UTC timestamp. Audit records are retained for 7 years.
