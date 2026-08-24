# Xpharma Graph Architecture

## 1. Purpose

Xpharma uses a graph-first medical knowledge architecture.

Kuzu is the authoritative runtime medical knowledge graph.

Open Targets provides structured biomedical knowledge that will later be
processed through DuckDB and loaded into Kuzu.

FDA label data provides regulatory and safety evidence and will be represented
as a distinct FDA domain inside the Kuzu graph.

The openFDA API will eventually provide a remote fallback for FDA-relevant
queries when applicable evidence is not available in the local graph.

---

## 2. Runtime Architecture

```text
User Query
    |
    v
Query Analysis
    |
    v
Entity Resolution
    |
    v
Intent / Workflow Routing
    |
    +--------------------+
    |                    |
    v                    v
Knowledge Workflow   Safety / Evidence Workflow
    |                    |
    v                    v
Kuzu Graph          Kuzu FDA Evidence
    |                    |
    |                    v
    |                openFDA fallback
    |                    |
    +---------+----------+
              |
              v
        Retrieved Evidence
              |
              v
        Response Generation