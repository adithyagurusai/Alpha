# Xpharma Local Operations Guide

This document describes how to start, stop, restart, inspect, and test
the Xpharma FastAPI deployment on macOS.

## Architecture

Internet
    |
    v
Cloudflare
    |
    v
Cloudflare Tunnel
    |
    v
localhost:8000
    |
    v
FastAPI
    |
    +--> Kuzu Medical Knowledge Graph
    |
    +--> Gemini

---

# Project Paths

Project root:

    /Users/kothavamsi/Git/Alpha

Backend:

    /Users/kothavamsi/Git/Alpha/backend

Python:

    /Users/kothavamsi/Git/Alpha/.venv/bin/python

Uvicorn:

    /Users/kothavamsi/Git/Alpha/.venv/bin/uvicorn

Kuzu database:

    /Users/kothavamsi/Git/Alpha/data/xpharma_graph

Logs:

    /Users/kothavamsi/Git/Alpha/logs/

Public API:

    https://api.adithya.dpdns.org

Local API:

    http://localhost:8000

---

# IMPORTANT: Kuzu

Kuzu uses a database lock.

Only one application process should own the Kuzu database.

Do NOT manually start another Uvicorn process while the launchd service
is already running.

Incorrect:

    launchd Uvicorn
        +
    manually started Uvicorn
        =
    Kuzu lock conflict

The launchd service is the authoritative FastAPI process.

---

# STARTING XPHARMA

Normally no manual FastAPI startup is required.

The FastAPI service is managed by macOS launchd.

Check status:

    launchctl print gui/$(id -u)/com.xpharma.fastapi | \
        grep -E "state|runs|last exit code"

Expected:

    state = running

If it is not running:

    launchctl kickstart -k gui/$(id -u)/com.xpharma.fastapi

Then verify:

    curl http://localhost:8000/health

Expected:

    {"status":"ok"}

---

# STARTING CLOUDFLARED

Cloudflare Tunnel is installed as a macOS service.

Check:

    sudo launchctl list | grep cloudflared

The service should appear as:

    com.cloudflare.cloudflared

Normally do NOT manually run:

    cloudflared tunnel run xpharma

when the macOS service is already installed.

---

# PUBLIC HEALTH CHECK

Test:

    curl https://api.adithya.dpdns.org/health

Expected:

    {"status":"ok"}

---

# PUBLIC QUERY TEST

Run:

    curl -X POST https://api.adithya.dpdns.org/query \
      -H "Content-Type: application/json" \
      -d '{"query":"how is nicotine related to CHRNA4"}'

Expected result:

    success = true

The answer should contain the grounded relationship between
NICOTINE and CHRNA4.

---

# SWAGGER

Open:

    https://api.adithya.dpdns.org/docs

FastAPI Swagger UI should load.

---

# RESTART FASTAPI

After changing Python application code:

    launchctl kickstart -k gui/$(id -u)/com.xpharma.fastapi

Then:

    curl http://localhost:8000/health

Then:

    curl https://api.adithya.dpdns.org/health

---

# STOP FASTAPI

To stop the launchd-managed FastAPI service:

    launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.xpharma.fastapi.plist

WARNING:

This disables the FastAPI process.

Cloudflare may continue running, but the public API will return an
origin/service error until FastAPI is started again.

---

# START FASTAPI AGAIN

After stopping it:

    launchctl bootstrap gui/$(id -u) \
        ~/Library/LaunchAgents/com.xpharma.fastapi.plist

Then:

    launchctl kickstart -k gui/$(id -u)/com.xpharma.fastapi

---

# VIEW FASTAPI LOGS

Application log:

    tail -f ~/Git/Alpha/logs/fastapi.log

Error log:

    tail -f ~/Git/Alpha/logs/fastapi-error.log

Last 50 errors:

    tail -50 ~/Git/Alpha/logs/fastapi-error.log

---

# CHECK FASTAPI PROCESS

    ps aux | grep '[u]vicorn'

There should normally be one Xpharma Uvicorn process.

Do not start another one manually if launchd already owns it.

---

# CHECK PORT 8000

    lsof -nP -iTCP:8000 -sTCP:LISTEN

Expected:

    uvicorn ... TCP 127.0.0.1:8000 (LISTEN)

---

# CHECK CLOUDFLARE

    sudo launchctl list | grep cloudflared

Then inspect the Cloudflare dashboard:

    Tunnels
      |
      +--> xpharma
            |
            +--> Connector
            +--> Published application

---

# FULL DEPLOYMENT TEST

Run these in order.

1. Local health:

    curl http://localhost:8000/health

2. Public health:

    curl https://api.adithya.dpdns.org/health

3. Public query:

    curl -X POST https://api.adithya.dpdns.org/query \
      -H "Content-Type: application/json" \
      -d '{"query":"how is nicotine related to CHRNA4"}'

4. Swagger:

    https://api.adithya.dpdns.org/docs

---

# AFTER REBOOT

macOS launchd should automatically start:

    FastAPI
    Cloudflare Tunnel

After logging back into macOS, verify:

    launchctl print gui/$(id -u)/com.xpharma.fastapi | \
        grep -E "state|runs|last exit code"

Then:

    curl https://api.adithya.dpdns.org/health

If both services are configured correctly, no manual terminal startup
should be required.

---

# TROUBLESHOOTING

## FastAPI exits with code 3

Check:

    tail -50 ~/Git/Alpha/logs/fastapi-error.log

Common causes:

- Kuzu database lock
- missing GEMINI_API_KEY
- missing Python dependency
- invalid application import
- port 8000 already occupied

---

## Kuzu lock error

Example:

    Could not set lock on file:
    .../data/xpharma_graph

Check:

    ps aux | grep '[u]vicorn'

and:

    lsof +D ~/Git/Alpha/data/xpharma_graph 2>/dev/null

Do not delete Kuzu database files.

Stop duplicate Uvicorn processes and allow the launchd-managed
process to own the database.

---

## Gemini API key error

Example:

    GEMINI_API_KEY is not configured.

The application loads:

    ~/Git/Alpha/.env

Required variable:

    GEMINI_API_KEY

Configured model:

    GEMINI_MODEL

Current default:

    gemini-3.1-flash-lite

Never commit `.env` to Git.

---

## Public API returns 502

First test:

    curl http://localhost:8000/health

If local health fails, fix FastAPI first.

If local health succeeds, check the Cloudflare Tunnel connector and
published application configuration.

The origin service should be:

    HTTP
    localhost:8000

NOT:

    HTTPS
    https://localhost:8000
