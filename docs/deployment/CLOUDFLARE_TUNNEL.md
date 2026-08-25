# Xpharma Cloudflare Tunnel Configuration

This document describes the one-time configuration used to expose
the local Xpharma FastAPI service through a public HTTPS hostname.

## Architecture

DigitalPlat
    |
    | Domain registration
    v
adithya.dpdns.org
    |
    | Nameservers
    v
Cloudflare
    |
    | DNS
    v
api.adithya.dpdns.org
    |
    | Cloudflare Tunnel
    v
cloudflared
    |
    v
http://localhost:8000
    |
    v
Xpharma FastAPI

---

# Domain

Domain:

    adithya.dpdns.org

Registrar/domain provider:

    DigitalPlat

DNS provider:

    Cloudflare

Application hostname:

    api.adithya.dpdns.org

---

# DNS Configuration

The domain was originally using DigitalPlat nameservers:

    dns1.digitalplat.org
    dns2.digitalplat.org

Cloudflare was added as the authoritative DNS provider.

The Cloudflare-provided nameservers were configured in:

    DigitalPlat
      |
      +--> Use other nameservers

Do not modify the Cloudflare nameservers unless intentionally
migrating DNS again.

---

# Cloudflare Plan

Cloudflare Zero Trust:

    Free

Cloudflare Tunnel:

    xpharma

---

# Tunnel Connector

The connector is installed as a macOS service.

Service:

    com.cloudflare.cloudflared

Check:

    sudo launchctl list | grep cloudflared

Do not place tunnel credentials in Git.

---

# Published Application

Tunnel:

    xpharma

Public hostname:

    api.adithya.dpdns.org

Origin service:

    HTTP

Origin URL:

    localhost:8000

IMPORTANT:

The public connection uses HTTPS:

    https://api.adithya.dpdns.org

The local origin uses HTTP:

    http://localhost:8000

Do NOT configure the origin as:

    https://localhost:8000

unless FastAPI is explicitly configured with TLS certificates.

---

# Cloudflare Route

Route type:

    Published application

Hostname:

    api.adithya.dpdns.org

Service:

    HTTP localhost:8000

---

# Why Cloudflare Tunnel Is Used

The Mac does not expose port 8000 directly to the Internet.

Instead:

Internet
    |
    v
Cloudflare
    |
    v
Cloudflare Tunnel
    |
    v
cloudflared
    |
    v
localhost:8000

This avoids:

- opening router port 8000
- exposing the Mac directly
- provisioning AWS
- provisioning Oracle Cloud
- paying for a VM

---

# Creating A New Tunnel

Only perform these steps if the current tunnel is intentionally
being replaced.

Install cloudflared:

    brew install cloudflared

Authenticate:

    cloudflared tunnel login

Create tunnel:

    cloudflared tunnel create xpharma

IMPORTANT:

Do not paste tunnel tokens or credentials into Git or documentation.

---

# Dashboard Route Configuration

In Cloudflare:

    Tunnels
      |
      +--> xpharma
            |
            +--> Routes
                  |
                  +--> Add route
                        |
                        +--> Published application

Configure:

    Subdomain: api
    Domain: adithya.dpdns.org

Service:

    HTTP
    localhost:8000

---

# Verification

Check DNS/public API:

    curl https://api.adithya.dpdns.org/health

Expected:

    {"status":"ok"}

Check API:

    curl -X POST https://api.adithya.dpdns.org/query \
      -H "Content-Type: application/json" \
      -d '{"query":"how is nicotine related to CHRNA4"}'

Swagger:

    https://api.adithya.dpdns.org/docs

---

# Security Notes

Never commit:

    .env

Never commit:

    Cloudflare tunnel credentials

Never expose:

    GEMINI_API_KEY

Never put:

    cloudflared tunnel tokens

inside source code.

The public API should eventually have:

- authentication
- rate limiting
- request validation
- structured logging
- appropriate CORS policy
- safe error responses

---

# Current Rate Limit

The API currently uses an in-process rate limiter.

Current configuration:

    14 requests / 60 seconds / client

The 15th request within the same window should receive:

    HTTP 429

This limiter is suitable for the current single-process deployment.

If the deployment becomes multi-process or moves to multiple hosts,
replace the in-memory limiter with shared infrastructure.
