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
4. [Test Data & BSN Mapping](#test-data-bsn-mapping)

`POST /v1/brp/personen` is the only BRP operation the API serves. It forwards the request body to the Haal Centraal BRP mock at `https://brp-api-mock.open-regels.nl/haalcentraal/api/brp`.

---

## Authentication

The endpoint requires a valid JWT token from Keycloak. It checks the token and nothing else: no role, tenant or assurance-level check applies.

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

The backend reads `sub`, `municipality`, `loa` and the realm roles into the request's user, but the BRP route does not act on them. The BSN to query comes from the request body, not from the token.

The frontend picks that BSN from the token:

- `bsn` - Burgerservicenummer, when the token carries one (DigiD)
- `preferred_username` - otherwise, mapped to a test BSN (see [Test Data & BSN Mapping](#test-data-bsn-mapping))

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

- A successful lookup writes the audit entry `brp.personen.fetch`, which records the queried BSN on purpose; a failed one writes the same action with the error.
- The application log never carries the request body, the upstream body or a BSN: it records the user, the tenant, the query type and how many BSNs were asked for.

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
| 4xx | `BRP_API_ERROR` | The BRP API refused the request; the status is the BRP API's own, its body is in `details` | Check the query against the BRP API |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry after the `RateLimit-Reset` seconds |
| 5xx | `BRP_API_ERROR` | The BRP API failed or could not be reached; the status is the BRP API's own, or `500` when there was no response | Retry or contact support |

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

## Test Data & BSN Mapping

### Test Environment BSN Mapping

A token without a `bsn` claim is mapped to a test BSN by its Keycloak username, in the frontend's `services/bsn.mapping.ts`.

#### Available Test Personas

| Username | BSN | Municipality | Description |
|----------|-----|--------------|-------------|
| `test-citizen-utrecht` | 999992235 | utrecht | Wessel Kooyman (45 jaar, getrouwd, 3 kinderen) |
| `test-caseworker-utrecht` | 999992235 | utrecht | Same persona |
| `test-citizen-amsterdam` | 999992235 | amsterdam | Same persona, Amsterdam tenant |
| `test-citizen-heusden` | 999992235 | heusden | Same persona, Heusden tenant |
| `test-citizen-rotterdam` | 999992235 | rotterdam | Same persona, Rotterdam tenant |
| `test-citizen-denhaag` | 999992235 | denhaag | Same persona, Den Haag tenant |
| `test-citizen-flevoland` | 999992235 | flevoland | Same persona, Flevoland tenant |

**Note:** All mapped test users share one persona (Wessel Kooyman). Any other username without a `bsn` claim gets no BSN.

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

### BSN Mapping Logic

**Production (with DigiD):**
```typescript
// BSN comes from JWT token (DigiD SAML assertion)
const bsn = user.bsn; // From JWT claim
```

**Without a `bsn` claim** (`packages/frontend/src/services/bsn.mapping.ts`):
```typescript
export function getUserBSN(user: {
  sub: string;
  preferred_username?: string;
  bsn?: string;
}): string | null {
  // If BSN is in the JWT (production with DigiD), use it
  if (user.bsn) {
    return user.bsn;
  }

  // For test users, map username to BSN
  if (user.preferred_username && user.preferred_username in testUserBSNMapping) {
    return testUserBSNMapping[user.preferred_username];
  }

  console.warn('No BSN found for user', user.preferred_username ?? '(no username)');
  return null;
}
```

### Adding New Test Personas

To add a new test persona:

1. **Add BSN to mock BRP API** (if you control it)
2. **Update username mapping:**
   ```typescript
   'test-citizen-single': '999991111',  // New BSN
   ```
3. **Create Keycloak user** with that username
4. **Test** by logging in as that user

---

## Security Considerations

### Data Protection

- **JWT Validation** - Backend validates signature, expiry, audience
- **No BSN in the application log** - neither the request body nor the upstream body is logged
- **Audit Trail** - Every lookup is audited, with the queried BSN; nothing purges audit records
- **Rate Limiting** - The API's global limiter applies

### Privacy (AVG/GDPR)

- **Data Minimization** - The caller chooses the `fields`; request only those actually needed
- **No server-side subject check** - The endpoint answers for any BSN in the request body; it is the frontend that queries the signed-in user's own BSN
- **Retention** - No BRP data is stored by the API; only the audit entries are kept

### Production Checklist

Before going to production with real DigiD:

- [ ] Keycloak configured with real DigiD IdP
- [ ] BSN attribute mapped from DigiD SAML assertion
- [ ] Keycloak protocol mapper adds BSN to JWT token
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
