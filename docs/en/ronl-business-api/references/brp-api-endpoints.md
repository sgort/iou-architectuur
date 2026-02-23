# BRP API Endpoints - API Reference

**Base URL (ACC):** `https://acc.api.open-regels.nl/v1`  
**Base URL (PROD):** `https://api.open-regels.nl/v1`  
**Authentication:** JWT Bearer Token (DigiD)

---

## Table of Contents

1. [Authentication](#authentication)
2. [POST /brp/personen](#post-brppersonen)
3. [POST /brp/verblijfplaatshistorie](#post-brpverblijfplaatshistorie) (Future)
4. [Error Responses](#error-responses)
5. [Test Data & BSN Mapping](#test-data-bsn-mapping)

---

## Authentication

All BRP endpoints require a valid JWT token from Keycloak.

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
  "roles": ["citizen"],
  "exp": 1771757983
}
```

**Required Claims:**

- `sub` - User identifier (UUID)
- `municipality` - Tenant identifier
- `loa` - Level of Assurance (must be "hoog" for timeline access)
- `roles` - Must include "citizen" or "caseworker"

**Optional Claims:**

- `preferred_username` - Used for test BSN mapping
- `bsn` - Burgerservicenummer (production only, from DigiD)

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

```json
{
  "success": false,
  "error": {
    "code": "BRP_API_ERROR",
    "message": "BRP API returned an error",
    "details": {
      "type": "https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.4",
      "title": "Persoon niet gevonden",
      "status": 404,
      "detail": "De gevraagde resource is niet gevonden"
    }
  }
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

if (data.success) {
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

- **Per User:** 100 requests per hour
- **Per Tenant:** 1000 requests per hour
- **Burst:** 10 requests per second

Rate limit headers in response:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1771760000
```

### Audit Logging

All requests are logged with:

- `userId` - From JWT sub claim
- `tenantId` - From JWT municipality claim
- `timestamp` - Request timestamp
- `bsn` - Queried BSN (masked in logs: `999-99-2235`)
- `result` - "success" or "error"
- `duration` - Request duration in ms

Logs retained for 7 years per AVG/GDPR compliance.

---

## POST /brp/verblijfplaatshistorie

**Status:** 🚧 Future Implementation

Fetch address history for a person.

### Endpoint

```
POST /v1/brp/verblijfplaatshistorie
```

### Request Body

```json
{
  "type": "RaadpleegMetPeriode",
  "burgerservicenummer": ["999992235"],
  "datumVan": "2000-01-01",
  "datumTot": "2023-12-31"
}
```

### Response - Success

```json
{
  "success": true,
  "data": {
    "verblijfplaatshistorie": [
      {
        "datumVan": {
          "datum": "2020-05-15",
          "langFormaat": "15 mei 2020"
        },
        "datumTot": {
          "datum": "2023-08-20",
          "langFormaat": "20 augustus 2023"
        },
        "verblijfadres": {
          "straat": "Kalverstraat",
          "huisnummer": 92,
          "postcode": "1012 PH",
          "woonplaats": "Amsterdam"
        },
        "gemeenteVanInschrijving": {
          "code": "0363",
          "omschrijving": "Amsterdam"
        }
      }
    ]
  }
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Error Codes

| HTTP Status | Code | Description | Solution |
|-------------|------|-------------|----------|
| 400 | `INVALID_REQUEST` | Malformed request body | Check request format |
| 401 | `INVALID_TOKEN` | JWT token invalid or expired | Re-authenticate |
| 403 | `INSUFFICIENT_PERMISSIONS` | User lacks required roles | Check user roles in Keycloak |
| 403 | `INSUFFICIENT_ASSURANCE` | LoA too low (not "hoog") | Upgrade to DigiD with higher LoA |
| 404 | `PERSON_NOT_FOUND` | BSN not found in BRP | Verify BSN number |
| 406 | `NOT_ACCEPTABLE` | Missing Accept header | Add `Accept: application/json` |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry after `X-RateLimit-Reset` |
| 500 | `BRP_API_ERROR` | External BRP API failure | Retry or contact support |
| 503 | `SERVICE_UNAVAILABLE` | Backend service down | Check system status |

### Example Error Responses

#### 401 Unauthorized

```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Token validation failed"
  }
}
```

#### 403 Insufficient Assurance

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_ASSURANCE",
    "message": "Assurance level 'hoog' or higher required"
  }
}
```

#### 404 Person Not Found

```json
{
  "success": false,
  "error": {
    "code": "BRP_API_ERROR",
    "message": "BRP API returned an error",
    "details": {
      "type": "https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.4",
      "title": "Persoon niet gevonden",
      "status": 404,
      "detail": "De persoon met opgegeven burgerservicenummer is niet gevonden"
    }
  }
}
```

#### 429 Rate Limit Exceeded

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again after 1771760000"
  }
}
```

---

## Test Data & BSN Mapping

### Test Environment BSN Mapping

In development and ACC environments, test users are mapped to BSN numbers via their Keycloak username.

#### Available Test Personas

| Username | BSN | Municipality | Description |
|----------|-----|--------------|-------------|
| `test-citizen-utrecht` | 999992235 | utrecht | Wessel Kooyman (45 jaar, getrouwd, 3 kinderen) |
| `test-citizen-amsterdam` | 999992235 | amsterdam | Same persona, Amsterdam tenant |
| `test-citizen-rotterdam` | 999992235 | rotterdam | Same persona, Rotterdam tenant |
| `test-citizen-denhaag` | 999992235 | denhaag | Same persona, Den Haag tenant |

**Note:** All test users currently map to the same persona (Wessel Kooyman). In future, additional personas with different life situations will be added.

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

**Test/ACC Environment:**
```typescript
// BSN derived from username or municipality
function getUserBSN(user) {
  // 1. Check JWT for BSN (production)
  if (user.bsn) return user.bsn;
  
  // 2. Map by username (test users)
  const usernameMapping = {
    'test-citizen-utrecht': '999992235',
    'test-citizen-amsterdam': '999992235',
    // ... other mappings
  };
  
  if (user.preferred_username in usernameMapping) {
    return usernameMapping[user.preferred_username];
  }
  
  // 3. Fallback to municipality mapping
  const municipalityMapping = {
    'utrecht': '999992235',
    'amsterdam': '999992235',
    // ... other mappings
  };
  
  if (user.municipality in municipalityMapping) {
    return municipalityMapping[user.municipality];
  }
  
  return null; // No BSN available
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

- **TLS 1.3** - All communication encrypted in transit
- **JWT Validation** - Backend validates signature, expiry, audience
- **BSN Masking** - BSN masked in logs: `999-99-2235`
- **Audit Trail** - All access logged for 7 years
- **Rate Limiting** - Prevents abuse and DoS attacks

### Privacy (AVG/GDPR)

- **Purpose Limitation** - BRP data used only for timeline feature
- **Data Minimization** - Only request fields actually needed
- **Access Control** - Users can only access their own data
- **Retention** - No BRP data stored, only audit logs (7 years)
- **Right to Access** - Users can request their audit logs
- **Right to Erasure** - Audit logs anonymized on request

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

## Changelog

### February 2026 - Initial Release

**Added:**

- `POST /v1/brp/personen` endpoint for person data retrieval
- JWT authentication with Keycloak
- Audit logging for all BRP requests
- BSN mapping for test environment
- Rate limiting per user and tenant

**Future:**

- `POST /v1/brp/verblijfplaatshistorie` for address history
- Additional test personas with diverse life situations
- Caching layer for BRP responses (5 min TTL)

---

## Related Documentation

- [Feature Overview](../features/timeline-navigation.md)
- [Technical Architecture](../references/brp-timeline-integration.md)
- [Developer Guide](../developer/implementing-timeline.md)
- [Haal Centraal BRP API Documentation](https://github.com/VNG-Realisatie/Haal-Centraal-BRP-bevragen)
