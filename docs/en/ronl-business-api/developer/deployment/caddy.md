---
component: RONL Business API
---

# Caddy Reverse Proxy

Caddy handles TLS termination, automatic Let's Encrypt certificate provisioning, and reverse-proxy routing for all VM-hosted services (Keycloak ACC, Keycloak PROD, Operaton).

---

## Repository structure

```
deployment/vm/caddy/
├── Caddyfile                    # Reverse proxy configuration
├── operaton-engine-rest.caddy   # The rules for Operaton's REST API, imported by the Caddyfile
├── docker-compose.yml           # The Caddy container as it runs on the VM
├── README.md
├── Caddyfile.backup-*           # Two dated backups copied from the VM
└── static/                      # security.txt per site, and the key it names
```

The directory is a copy of what the VM runs, taken from the VM in v2026.11.1 and kept in step by hand: nothing deploys it automatically ([#196](https://github.com/sgort/ronl-business-api/issues/196)). It is **not** committed with secrets: the one secret the Operaton rules need comes from `caddy.env`, which exists only on the VM.

---

## Caddyfile

```
acc.keycloak.open-regels.nl {
    reverse_proxy keycloak-acc:8080
}

keycloak.open-regels.nl {
    reverse_proxy keycloak-prod:8080
}

operaton.open-regels.nl {
    import operaton-engine-rest.caddy
    # ...static files and security headers
}
```

The Operaton block does not proxy the engine wholesale; see [Operaton](#operaton) below.

Caddy automatically provisions and renews Let's Encrypt certificates for all listed domains. HTTP requests are automatically redirected to HTTPS.

---

## Retrieving the Caddyfile from a running VM

If the Caddyfile on the VM has diverged from the version in the repository, retrieve the live version and commit it:

```bash
ssh user@open-regels.nl "docker exec caddy cat /etc/caddy/Caddyfile" \
  > deployment/vm/caddy/Caddyfile
```

Review the diff before committing — the VM copy is authoritative for any manual changes made outside of the normal deploy flow.

---

## Deploying Caddy

```bash
ssh user@open-regels.nl
mkdir -p ~/caddy
```

Copy the Caddyfile to the VM:

```bash
scp deployment/vm/caddy/Caddyfile user@open-regels.nl:~/caddy/
```

Create `~/caddy/docker-compose.yml` on the VM:

```yaml
version: '3.8'
services:
  caddy:
    image: caddy:2-alpine
    container_name: caddy
    ports:
      - "80:80"
      - "443:443"
    env_file: ./caddy.env   # VM-only; read by operaton-engine-rest.caddy
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./operaton-engine-rest.caddy:/etc/caddy/operaton-engine-rest.caddy:ro
      - caddy-data:/data
      - caddy-config:/config
    restart: always
    networks:
      - npm-network

volumes:
  caddy-data:
  caddy-config:

networks:
  npm-network:
    external: true
```

Start Caddy:

```bash
cd ~/caddy
docker compose up -d
docker compose logs -f caddy    # verify certificate provisioning
```

Caddy is ready when you see: `certificate obtained successfully`

The image is the floating tag `caddy:2-alpine`, while the Operaton test harness pins Caddy 2.10.2; pinning the VM's images waits on #196. A change to `caddy.env` needs `docker compose up -d` (a recreate), not a reload.

---

## Operaton

Since v2026.11.1 Operaton's REST API requires a login ([#415](https://github.com/sgort/ronl-business-api/issues/415)), and `operaton-engine-rest.caddy`, imported into the engine's site block, keeps the rules public:

- A request **without credentials** that reads definitions, their XML, deployments or their resources, or that evaluates a decision, is forwarded with the read-only account's credentials, which the engine limits to exactly that. The proxy takes that account's header from `OPERATON_PUBLIC_READER_AUTH` in `caddy.env`.
- **Every other request** is forwarded unchanged: without the caller's own credentials the engine answers `401`.
- **CORS** — `*`, without credentials — is answered on the public paths only. The proxy strips the CORS headers the engine might send, so a browser never receives `Access-Control-Allow-Origin` twice.
- The rules use named matchers only, so the `handle` blocks keep the order they are written in.

The rules are proven by `deployment/vm/operaton/test/check-allowlist.sh` against the same Caddy and engine versions, including path tricks and kept caller credentials. See [Operaton deployment](operaton.md) for the engine side.

!!! note "A temporary access log"
    The rollout added an access log of every request to the engine's REST API, so no caller would be missed before the login went on. At v2026.11.1 it is still in the `Caddyfile`; the rollout's last step removes it.

---

## Adding a new domain

To expose a new VM service through Caddy:

1. Add a DNS A record pointing the new subdomain to the VM's public IP
2. Add a new block to the `Caddyfile`:
   ```
   newservice.open-regels.nl {
       reverse_proxy newservice-container:8080
   }
   ```
3. Copy the updated `Caddyfile` to the VM and reload:
   ```bash
   scp deployment/vm/caddy/Caddyfile user@open-regels.nl:~/caddy/
   ssh user@open-regels.nl 'docker exec caddy caddy reload --config /etc/caddy/Caddyfile'
   ```

---

## Docker network

All VM containers communicate over a shared Docker network named `npm-network`. Caddy resolves Keycloak and Operaton by their container names (`keycloak-acc`, `keycloak-prod`, `operaton`) within this network. Ensure all containers specify `networks: npm-network` in their `docker-compose.yml`.

---

## Security hardening

### Security headers

Each kind of site imports its own header snippet, defined at the top of the `Caddyfile`: `basic_security_headers` for CPRMV, `keycloak_security_headers` for both Keycloak sites, `enhanced_security_headers` for the Operaton sites, and one each for Skosmos and Nextcloud. The Keycloak snippet is the least restrictive, because OAuth and OIDC need it to be:

```
(keycloak_security_headers) {
    header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    header X-Content-Type-Options "nosniff"
    header X-Frame-Options "SAMEORIGIN"
    @kc_3p_cookies path /realms/*/protocol/openid-connect/3p-cookies/*
    header @kc_3p_cookies -X-Frame-Options
    header X-XSS-Protection "1; mode=block"
    header Referrer-Policy "strict-origin-when-cross-origin"
    header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=()"
}

acc.keycloak.open-regels.nl {
    # ...static files
    import keycloak_security_headers
    reverse_proxy keycloak-acc:8080
}
```

`keycloak.open-regels.nl` imports the same snippet in front of `keycloak-prod:8080`.

**Keycloak's third-party-cookie check is the one exception to `SAMEORIGIN`** (since v2026.11.2). Before every silent `check-sso`, keycloak-js loads two pages under `/realms/<realm>/protocol/openid-connect/3p-cookies/` in a hidden frame on the application's origin. Keycloak serves them frameable on purpose — they have no UI and only test cookies — but the snippet's `SAMEORIGIN` blocked them, so the Linked Data Explorer and the ttl-editor could not pick up a session after the sign-in popup or on reload ([linked-data-explorer#163](https://github.com/sgort/linked-data-explorer/issues/163)). Caddy defers a header deletion until the response is written, so the `-X-Frame-Options` on that path wins over the line above it; the login pages keep their framing protection.

To check a site, request both paths with `GET` — Keycloak answers `HEAD` with `405`:

```bash
# No X-Frame-Options on the cookie check...
curl -s -D - -o /dev/null https://acc.keycloak.open-regels.nl/realms/ronl/protocol/openid-connect/3p-cookies/step1.html | grep -i x-frame
# ...and SAMEORIGIN everywhere else
curl -s -D - -o /dev/null https://acc.keycloak.open-regels.nl/realms/ronl/account | grep -i x-frame
```

### Rate limiting

To protect Keycloak login from brute-force attempts at the proxy level:

```
acc.keycloak.open-regels.nl {
    import security_headers
    rate_limit {
        zone acc_keycloak {
            key {remote_host}
            events 100
            window 1m
        }
    }
    reverse_proxy keycloak-acc:8080
}
```

Note: Keycloak's built-in brute-force protection (5 failed attempts → lockout) is configured in the realm settings and operates independently of Caddy rate limiting.

---

## Verifying SSL certificates

```bash
# Check certificate expiry for each domain
echo | openssl s_client -servername acc.keycloak.open-regels.nl \
  -connect acc.keycloak.open-regels.nl:443 2>/dev/null | openssl x509 -noout -dates

echo | openssl s_client -servername keycloak.open-regels.nl \
  -connect keycloak.open-regels.nl:443 2>/dev/null | openssl x509 -noout -dates

echo | openssl s_client -servername operaton.open-regels.nl \
  -connect operaton.open-regels.nl:443 2>/dev/null | openssl x509 -noout -dates
```

Caddy stores certificates in the `caddy-data` volume and renews them automatically ~30 days before expiry. No manual intervention is required unless DNS or the VM IP changes.

---

## Metrics and monitoring

Caddy exposes a metrics/admin endpoint on port 2019 (localhost only, not exposed to internet):

```bash
# From the VM
curl http://localhost:2019/metrics
```

To follow access logs:

```bash
docker logs -f caddy

# Filter for a specific domain
docker logs caddy 2>&1 | grep "acc.keycloak.open-regels.nl"
```

---

## Troubleshooting

**Service returns 502 Bad Gateway** — Caddy can reach the domain but can't reach the backend container. Check:

1. Container is running: `docker ps`
2. Container is on `npm-network`: `docker network inspect npm-network | grep <container-name>`
3. Container name in Caddyfile matches exactly: `docker ps --format '{{.Names}}'`

**Certificate not provisioning** — Check that:

1. DNS A record for the domain points to the VM's public IP: `dig acc.keycloak.open-regels.nl`
2. Ports 80 and 443 are open on the VM: `sudo ufw status`
3. Caddy logs for ACME errors: `docker logs caddy | grep -i "acme\|certificate\|error"`

**Validate Caddyfile syntax before reloading:**

```bash
docker exec caddy caddy validate --config /etc/caddy/Caddyfile
```

