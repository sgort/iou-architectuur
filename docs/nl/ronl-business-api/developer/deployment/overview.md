# Implementatieoverzicht

!!! info "Documentatie in ontwikkeling"
    De Nederlandse vertaling van deze pagina is nog niet beschikbaar.
    Raadpleeg de <a href="/ronl-business-api/developer/deployment/overview/">Engelse versie</a> voor de huidige inhoud.

---

**Status:** Concept  
**Engelstalige bron:** `ronl-business-api/developer/deployment/overview.md`

---

## Architecture

## Environments

### ACC (Acceptance)

### PROD (Production)

## Why the split?

## Deployment guides

## Azure resource groups

## Monitoring

### VM health checks

# Container resource usage (one-shot)

# All VM service status

# Service health endpoints (from the VM itself)

# Follow logs

### Azure monitoring

## Disaster recovery

### VM total failure

### Azure region failure

## VM maintenance

### OS security updates

# If a kernel update was applied:

### Updating Keycloak

# Update the image tag in docker-compose.yml, then:

# Repeat for PROD during a maintenance window

### Updating Caddy

### Keycloak database backups

# Run daily (add to cron on VM)
