# Caddy Reverse Proxy

Caddy handles TLS termination, automatic Let's Encrypt certificate provisioning, and reverse-proxy routing for all VM-hosted services (Keycloak ACC, Keycloak PROD, Operaton).

## Repository structure

```
deployment/vm/caddy/
└── Caddyfile       # Reverse proxy configuration
```

The `Caddyfile` is version-controlled but must be copied to the VM and loaded by the Caddy container. It is **not** committed with secrets.

## Caddyfile

```
acc.keycloak.open-regels.nl {
    reverse_proxy keycloak-acc:8080
}

keycloak.open-regels.nl {
    reverse_proxy keycloak-prod:8080
}

operaton.open-regels.nl {
    reverse_proxy operaton:8080
}
```

Caddy automatically provisions and renews Let's Encrypt certificates for all listed domains. HTTP requests are automatically redirected to HTTPS.

## Retrieving the Caddyfile from a running VM

If the Caddyfile on the VM has diverged from the version in the repository, retrieve the live version and commit it:

```bash
ssh user@open-regels.nl "docker exec caddy cat /etc/caddy/Caddyfile" \
  > deployment/vm/caddy/Caddyfile
```

Review the diff before committing — the VM copy is authoritative for any manual changes made outside of the normal deploy flow.

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
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
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

## Docker network

All VM containers communicate over a shared Docker network named `npm-network`. Caddy resolves Keycloak and Operaton by their container names (`keycloak-acc`, `keycloak-prod`, `operaton`) within this network. Ensure all containers specify `networks: npm-network` in their `docker-compose.yml`.

## Security hardening

### Security headers

Add a reusable `import` snippet to apply security headers to all proxied services:

```
(security_headers) {
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}

acc.keycloak.open-regels.nl {
    import security_headers
    reverse_proxy keycloak-acc:8080
}

keycloak.open-regels.nl {
    import security_headers
    reverse_proxy keycloak-prod:8080
}

operaton.open-regels.nl {
    import security_headers
    reverse_proxy operaton:8080
}
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

