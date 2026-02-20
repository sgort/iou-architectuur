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
