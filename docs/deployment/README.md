# Xpharma Deployment

## Quick start

For normal operation:

1. Check FastAPI:

       curl http://localhost:8000/health

2. Check public API:

       curl https://api.adithya.dpdns.org/health

3. Open Swagger:

       https://api.adithya.dpdns.org/docs

FastAPI and Cloudflare Tunnel are managed by macOS launchd.

## Guides

- [Local Operations](./LOCAL_OPERATIONS.md)
- [Cloudflare Tunnel](./CLOUDFLARE_TUNNEL.md)

## Architecture

DigitalPlat
    |
    v
Cloudflare DNS
    |
    v
Cloudflare Tunnel
    |
    v
FastAPI
    |
    +--> Kuzu
    |
    +--> Gemini
