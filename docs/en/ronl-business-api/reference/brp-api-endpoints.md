---
component: RONL Business API
---

# BRP API Endpoints - API Reference

**Base URL (ACC):** `https://acc.api.open-regels.nl/v1`  
**Base URL (PROD):** `https://api.open-regels.nl/v1`  
**Authentication:** JWT Bearer Token (DigiD)

---

## Table of Contents

1. [Authentication](#authentication)
2. [POST /brp/personen](#post-brppersonen)
3. [Error Responses](#error-responses)
4. [Test Data & the `bsn` Claim](#test-data-the-bsn-claim)

`POST /v1/brp/personen` is the only BRP operation the API serves. It forwards the request body to the Haal Centraal BRP mock at `https://brp-api-mock.open-regels.nl/haalcentraal/api/brp`, the base URL in `services/brp-upstream.ts`, for ACC and PROD alike. Whether the mock can be reached is also reported by `GET /v1/health`, under `dependencies.brp`.

---

## Authentication

The endpoint requires a valid JWT token from Keycloak, and decides who may look up whom before the BRP API is called (`auth/brp-access.ts`):

| Caller | Assurance level | May look up |
|---|---|---|
| Holder of `brp-raadpleger`, which every caseworker has through the `caseworker` composite | `substantieel` or higher, the level an Entra ID login carries | Anyone; the query is not restricted |
| Anyone else | `hoog` | Only their own record: the token must carry a `bsn` claim, and `burgerservicenummer` must be a non-empty list naming that BSN and nothing else |

A query that is not by BSN can return anyone, so it is refused for the second group. No tenant check applies: a caseworker of any organisation holds the role.

### Request Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### JWT Token Structure

```json
{
  "sub": "user-uuid",
  "preferred_username": "test-citizen-utrecht",
  "bsn": "999992235",
  "municipality": "utrecht",
  "loa": "hoog",
  "realm_access": { "roles": ["citizen"] },
  "exp": 1771757983
}
```

The backend reads `sub`, `municipality`, `loa`, the realm roles and `bsn` into the request's user. The BSN to query still comes from the request body; for a caller without `brp-raadpleger` it has to equal the token's `bsn`.

The frontend takes that BSN from the token's `bsn` claim only. A token without one gets no lookup, and the citizen's **Tijdlijn** tab says no timeline is available.

---

## POST /brp/personen

Fetch person data including partner and children information from BRP.

### Endpoint

```
POST /v1/brp/personen
```

### Request Body

```json
{
  "type": "RaadpleegMetBurgerservicenummer",
  "burgerservicenummer": ["999992235"],
  "fields": [
    "burgerservicenummer",
    "geboorte",
    "kinderen",
    "leeftijd",
    "naam",
    "partners"
  ]
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Query type. Must be `"RaadpleegMetBurgerservicenummer"` |
| `burgerservicenummer` | string[] | Yes | Array with single BSN to query |
| `fields` | string[] | Yes | List of fields to return |

### Available Fields

| Field | Description | Returns |
|-------|-------------|---------|
| `burgerservicenummer` | BSN number | string |
| `naam` | Full name details | object with voornamen, geslachtsnaam, volledigeNaam |
| `geboorte` | Birth information | object with datum, plaats, land |
| `leeftijd` | Current age | number |
| `partners` | Partner information | array of partner objects |
| `kinderen` | Children information | array of child objects |
| `geslacht` | Gender | object with code and omschrijving |
| `nationaliteiten` | Nationalities | array |
| `verblijfplaats` | Current address | object |

### Response - Success

```json
{
  "success": true,
  "data": {
    "type": "RaadpleegMetBurgerservicenummer",
    "personen": [
      {
        "burgerservicenummer": "999992235",
        "leeftijd": 45,
        "naam": {
          "aanduidingNaamgebruik": {
            "code": "E",
            "omschrijving": "eigen geslachtsnaam"
          },
          "voornamen": "Wessel",
          "geslachtsnaam": "Kooyman",
          "voorletters": "W.",
          "volledigeNaam": "Wessel Kooyman"
        },
        "geboorte": {
          "land": {
            "code": "6030",
            "omschrijving": "Nederland"
          },
          "plaats": {
            "code": "0545",
            "omschrijving": "Leerdam"
          },
          "datum": {
            "type": "Datum",
            "datum": "1980-12-12",
            "langFormaat": "12 december 1980"
          }
        },
        "kinderen": [
          {
            "burgerservicenummer": "999991231",
            "naam": {
              "voornamen": "Stefano",
              "geslachtsnaam": "Kooyman",
              "voorletters": "S."
            },
            "geboorte": {
              "land": {
                "code": "6030",
                "omschrijving": "Nederland"
              },
              "plaats": {
                "code": "0518",
                "omschrijving": "'s-Gravenhage"
              },
              "datum": {
                "type": "Datum",
                "datum": "2003-03-03",
                "langFormaat": "3 maart 2003"
              }
            }
          }
        ],
        "partners": [
          {
            "burgerservicenummer": "999991450",
            "geslacht": {
              "code": "V",
              "omschrijving": "vrouw"
            },
            "soortVerbintenis": {
              "code": "H",
              "omschrijving": "huwelijk"
            },
            "naam": {
              "voornamen": "Catootje",
              "geslachtsnaam": "Altena",
              "voorletters": "C."
            },
            "geboorte": {
              "land": {
                "code": "6030",
                "omschrijving": "Nederland"
              },
              "plaats": {
                "code": "0796",
                "omschrijving": "'s-Hertogenbosch"
              },
              "datum": {
                "type": "Datum",
                "datum": "1981-09-21",
                "langFormaat": "21 september 1981"
              }
            },
            "aangaanHuwelijkPartnerschap": {
              "datum": {
                "type": "Datum",
                "datum": "2002-02-02",
                "langFormaat": "2 februari 2002"
              },
              "land": {
                "code": "6030",
                "omschrijving": "Nederland"
              },
              "plaats": {
                "code": "0637",
                "omschrijving": "Zoetermeer"
              }
            }
          }
        ]
      }
    ]
  }
}
```

### Response - Error

Errors are RFC 9457 problem details (`application/problem+json`). When the BRP API answers a 4xx, the endpoint answers with that same status, code `BRP_API_ERROR`, and the upstream body in a `details` extension member:

```json
{
  "details": {
    "type": "https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.4",
    "title": "Persoon niet gevonden",
    "status": 404,
    "detail": "De gevraagde resource is niet gevonden"
  },
  "type": "about:blank",
  "status": 404,
  "title": "Brp api error",
  "detail": "BRP API returned an error",
  "instance": "/v1/brp/personen",
  "code": "BRP_API_ERROR"
}
```

The upstream body above is illustrative; `details` carries whatever the BRP API returned.

When the request never gets an HTTP answer — DNS, the connection, the TLS handshake or the timeout failed — the endpoint answers `502` with code `BRP_UPSTREAM_UNREACHABLE` and no `details`. The transport error's code is logged as `transportError`, not returned: it describes infrastructure the caller cannot act on.

```json
{
  "type": "about:blank",
  "status": 502,
  "title": "Brp upstream unreachable",
  "detail": "The BRP API could not be reached",
  "instance": "/v1/brp/personen",
  "code": "BRP_UPSTREAM_UNREACHABLE"
}
```

### Example Request (cURL)

```bash
curl -X POST https://acc.api.open-regels.nl/v1/brp/personen \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6..." \
  -H "Content-Type: application/json" \
  -d '{
    "type": "RaadpleegMetBurgerservicenummer",
    "burgerservicenummer": ["999992235"],
    "fields": [
      "burgerservicenummer",
      "naam",
      "geboorte",
      "leeftijd",
      "partners",
      "kinderen"
    ]
  }'
```

### Example Request (JavaScript)

```javascript
const response = await fetch('https://acc.api.open-regels.nl/v1/brp/personen', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    type: 'RaadpleegMetBurgerservicenummer',
    burgerservicenummer: ['999992235'],
    fields: [
      'burgerservicenummer',
      'naam',
      'geboorte',
      'leeftijd',
      'partners',
      'kinderen',
    ],
  }),
});

const data = await response.json();

if (response.ok) {
  const person = data.data.personen[0];
  console.log('Person:', person.naam.volledigeNaam);
  console.log('Age:', person.leeftijd);
}
```

### Example Request (TypeScript with Axios)

```typescript
import axios from 'axios';

interface BRPPersonenRequest {
  type: 'RaadpleegMetBurgerservicenummer';
  burgerservicenummer: string[];
  fields: string[];
}

interface BRPPersonenResponse {
  success: boolean;
  data: {
    type: string;
    personen: PersonState[];
  };
}

const fetchPerson = async (bsn: string, token: string): Promise<PersonState | null> => {
  try {
    const response = await axios.post<BRPPersonenResponse>(
      'https://acc.api.open-regels.nl/v1/brp/personen',
      {
        type: 'RaadpleegMetBurgerservicenummer',
        burgerservicenummer: [bsn],
        fields: [
          'burgerservicenummer',
          'naam',
          'geboorte',
          'leeftijd',
          'partners',
          'kinderen',
        ],
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.data.success && response.data.data.personen.length > 0) {
      return response.data.data.personen[0];
    }

    return null;
  } catch (error) {
    console.error('Failed to fetch person:', error);
    throw error;
  }
};
```

### Rate Limits

The endpoint has no limit of its own. It shares the API's global limiter: by default 1,000 requests per minute per client IP (`RATE_LIMIT_MAX_REQUESTS`, `RATE_LIMIT_WINDOW_MS`). The limiter sends the standard `RateLimit-*` headers, not `X-RateLimit-*`.

### Logging

- A lookup that is carried out writes the audit entry `brp.personen.fetch` as `success`, with `via` (`brp-raadpleger` or `own-record`). A refusal writes the same action as `failure`, with the code. Both record a BSN on purpose: the first one in the query's `burgerservicenummer`. The others in a list are not recorded, and a query by name or address records none ([#478](https://github.com/sgort/ronl-business-api/issues/478)). A transport or unexpected failure writes the action as `error`, with the message. A 4xx from the BRP API writes no entry of this action.
- The route's own log lines never carry the request body, the upstream body or a BSN: they record the user, the tenant, the query type and how many BSNs were asked for. Every audit entry is also written to the application log at `info` level, so the audited BSN does reach that log.

---

## Error Responses

### Problem details

Every error is RFC 9457 problem details, served as `application/problem+json`: `type` (`about:blank`), `status`, `title` (derived from the code), `detail` and `instance` (the request path), plus a `code` extension member. See [API Design — Error handling](../features/api-design.md#error-handling).

### Error Codes

| HTTP Status | Code | Description | Solution |
|-------------|------|-------------|----------|
| 400 | `MALFORMED_BODY` | The request body is not valid JSON | Check request format |
| 401 | `MISSING_TOKEN` | No `Authorization: Bearer` header | Send the token |
| 401 | `INVALID_TOKEN` | JWT token invalid or expired | Re-authenticate |
| 403 | `INSUFFICIENT_ASSURANCE` | Below `substantieel` with `brp-raadpleger`, or below `hoog` without it | Sign in at the required level |
| 403 | `BSN_CLAIM_MISSING` | No `brp-raadpleger`, and the token carries no `bsn` claim | The account needs a BSN |
| 403 | `BRP_SUBJECT_MISMATCH` | No `brp-raadpleger`, and the query is not a lookup of the caller's own BSN only | Query your own BSN |
| 4xx | `BRP_API_ERROR` | The BRP API refused the request; the status is the BRP API's own, its body is in `details` | Check the query against the BRP API |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry after the `RateLimit-Reset` seconds |
| 5xx | `BRP_API_ERROR` | The BRP API answered with a server error; the status is the BRP API's own, or `500` for an error that is not an HTTP failure | Retry or contact support |
| 502 | `BRP_UPSTREAM_UNREACHABLE` | The BRP API could not be reached: DNS, the connection, the TLS handshake or the timeout failed | Check `dependencies.brp` in `/v1/health`; see [Troubleshooting](../developer/troubleshooting.md#the-citizen-timeline-is-blank) |

### Example Error Responses

#### 401 Unauthorized

```json
{
  "type": "about:blank",
  "status": 401,
  "title": "Invalid token",
  "detail": "Token validation failed",
  "instance": "/v1/brp/personen",
  "code": "INVALID_TOKEN"
}
```

#### BRP API unreachable

When the call to the BRP API fails without a response, `detail` carries the error message and there is no `details` member:

```json
{
  "type": "about:blank",
  "status": 500,
  "title": "Brp api error",
  "detail": "timeout of 10000ms exceeded",
  "instance": "/v1/brp/personen",
  "code": "BRP_API_ERROR"
}
```

#### 429 Rate Limit Exceeded

```json
{
  "type": "about:blank",
  "status": 429,
  "title": "Rate limit exceeded",
  "detail": "Too many requests, please try again later",
  "instance": "/v1/brp/personen",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

---

## Test Data & the `bsn` Claim

### Test accounts with a BSN

The test citizens carry their BSN as the Keycloak user attribute `bsn`, which a protocol mapper puts in the token. The realm export holds it, and `scripts/keycloak-add-brp-raadpleger.sh` sets it on the ACC and PROD realms.

| Username | BSN | Municipality | Description |
|----------|-----|--------------|-------------|
| `test-citizen-utrecht` | 999992235 | utrecht | Wessel Kooyman (45 jaar, getrouwd, 3 kinderen) |
| `test-citizen-amsterdam` | 999992235 | amsterdam | Same persona, Amsterdam tenant |
| `test-citizen-heusden` | 999992235 | heusden | Same persona, Heusden tenant |
| `test-citizen-bes` | 999992235 | bes | Same persona, Caribisch Nederland tenant |
| `test-citizen-rotterdam` | 999992235 | rotterdam | Same persona, Rotterdam tenant |
| `test-citizen-denhaag` | 999992235 | denhaag | Same persona, Den Haag tenant |
| `test-citizen-flevoland` | 999992235 | flevoland | Same persona, Flevoland tenant |

**Note:** All seven share one persona (Wessel Kooyman). `test-citizen-uwv`, `test-citizen-toeslagen` and `test-citizen-unive` have no `bsn`, so they have no timeline.

### Test BSN: 999992235 (Wessel Kooyman)

**Person Details:**

- **Name:** Wessel Kooyman
- **BSN:** 999992235
- **Birth Date:** December 12, 1980 (45 years old)
- **Birth Place:** Leerdam, Netherlands
- **Gender:** Male

**Partner:**

- **Name:** Catootje Altena
- **BSN:** 999991450
- **Birth Date:** September 21, 1981
- **Marriage Date:** February 2, 2002
- **Marriage Place:** Zoetermeer

**Children (Triplets):**

1. **Stefano Kooyman**
    - BSN: 999991231
    - Birth Date: March 3, 2003 (22 years old)

2. **Serena Kooyman**
    - BSN: 999994554
    - Birth Date: March 3, 2003 (22 years old)

3. **Sierra Kooyman**
    - BSN: 999991954
    - Birth Date: March 3, 2003 (22 years old)

### Timeline Events

The test persona has 3 major life events:

1. **Geboren** - December 12, 1980
2. **Getrouwd** - February 2, 2002
3. **Kinderen geboren (drieling)** - March 3, 2003

### Where the BSN comes from

The claim is a user attribute on the test realms and is to be the DigiD subject where DigiD is real.

`packages/frontend/src/services/bsn.mapping.ts`:

```typescript
export function getUserBSN(user: {
  sub: string;
  preferred_username?: string;
  bsn?: string;
}): string | null {
  if (user.bsn) {
    return user.bsn;
  }

  // Logs the username only, not the whole claims object: this branch cannot
  // carry a BSN (it is the one where there isn't one), but `user` also holds
  // `sub` and whatever else the token brought, and none of that is needed to
  // explain the warning.
  console.warn('No BSN found for user', user.preferred_username ?? '(no username)');
  return null;
}
```

### Adding New Test Personas

To add a new test persona:

1. **Add BSN to mock BRP API** (if you control it)
2. **Create a Keycloak user** with the `citizen` role and `assurance_level` `hoog`, and **set the attribute** `bsn` on it, with a number from the reserved `99999xxxx` range
3. **Test** by logging in as that user

---

## Security Considerations

### Data Protection

- **JWT Validation** - Backend validates signature, expiry, audience
- **No BSN in the route's own log lines** - neither the request body nor the upstream body is logged; the audit entry, which also reaches the application log, carries one
- **Audit Trail** - Every lookup is audited, with the first BSN of the query ([#478](https://github.com/sgort/ronl-business-api/issues/478)); nothing purges audit records
- **Rate Limiting** - The API's global limiter applies

### Privacy (AVG/GDPR)

- **Data Minimization** - The caller chooses the `fields`; request only those actually needed
- **Server-side subject check** - A caller without `brp-raadpleger` gets only their own record; a `brp-raadpleger` may look up anyone, and the lookup is audited
- **Retention** - No BRP data is stored by the API; only the audit entries are kept

### Production Checklist

Before going to production with real DigiD:

- [ ] Keycloak configured with real DigiD IdP
- [ ] BSN attribute mapped from DigiD SAML assertion
- [ ] Keycloak maps the DigiD subject to the `bsn` claim (today the mapper reads a user attribute)
- [ ] The frontend no longer writes the decoded token to the browser console ([#477](https://github.com/sgort/ronl-business-api/issues/477))
- [ ] Backend validates BSN format (9 digits, valid check digit)
- [ ] Rate limits configured per municipality
- [ ] Audit logging enabled with 7-year retention
- [ ] BSN masking enabled in logs
- [ ] TLS certificate valid and trusted
- [ ] BRP API credentials secured in Azure Key Vault
- [ ] Monitoring alerts configured for errors
- [ ] Privacy impact assessment (DPIA) completed

---

## Related Documentation

- [Feature Overview](../features/timeline-navigation.md)
- [Technical Architecture](../reference/brp-timeline-integration.md)
- [Developer Guide](../developer/implementing-timeline.md)
- [Haal Centraal BRP API Documentation](https://github.com/VNG-Realisatie/Haal-Centraal-BRP-bevragen)
