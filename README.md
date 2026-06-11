# CondominioOS

> **AI-first Agentic Managed Service for ultra-low-cost administration of small Italian condominiums (4–30 units).**

CondominioOS is a production-grade, multi-tenant, event-driven platform where **90%+ of operational
activity is executed by AI agents** operating under strict governance, a mandatory **Reputation
Firewall**, and human-in-the-loop supervision.

It is designed for the cost-sensitive segment of small Italian condominiums (_piccoli condomìni_),
delivering the duties of an _amministratore di condominio_ (Art. 1129–1130 Codice Civile) at a
fraction of the traditional cost.

---

## Why CondominioOS

Traditional administration of a small condominium costs €600–€1,500/year per building and is
dominated by repetitive, low-complexity work: chasing payments, fielding resident questions,
dispatching plumbers, preparing assemblies, tracking insurance expiries. CondominioOS automates this
work with a governed agent fleet, keeping a licensed human administrator *on the loop* (supervising)
rather than *in the loop* (doing).

| Principle | Meaning in CondominioOS |
|---|---|
| **Agent-native** | Work is modelled as agent tasks, not CRUD screens. |
| **Event-driven** | Every state change is an immutable domain event on the bus. |
| **API-first** | All capabilities exposed via versioned, contract-tested APIs. |
| **Cloud-native** | Containerized, horizontally scalable, 12-factor. |
| **Multi-tenant** | Hard tenant isolation at row, storage, and vector-namespace level. |
| **Human-supervised** | Risky actions require typed human approval. |
| **Audit-by-design** | Append-only, hash-chained audit log of every decision. |
| **GDPR compliant** | Lawful basis, data minimization, DSAR tooling, EU data residency. |
| **Regulation-aware** | Encodes Italian condominium law (CC 1117–1139, L. 220/2012). |
| **Reputation-safe** | No outbound message bypasses the Reputation Firewall. |

---

## Repository map

```
condominioos/
├── apps/            # Frontends: resident portal, admin portal, ops console
├── services/        # Backend microservices (FastAPI) + agent runtime (LangGraph)
├── packages/        # Shared libraries (schemas, events, sdk, ui)
├── infra/           # Terraform, Helm, k8s, CI/CD
├── docs/            # Architecture, blueprints, diagrams, roadmap (START HERE)
└── tools/           # Dev tooling, scripts, evaluators
```

## Documentation index (read in order)

| # | Document | Deliverable |
|---|---|---|
| 00 | [Executive Architecture](docs/00-executive-architecture.md) | A |
| 01 | [Target Operating Model](docs/01-target-operating-model.md) | 1 |
| 02 | [Service Blueprint](docs/02-service-blueprint.md) | 2 |
| 03 | [Domain Architecture](docs/03-domain-architecture.md) | 3 |
| 04 | [Agent Architecture](docs/04-agent-architecture.md) | 4 |
| 05 | [Data Architecture](docs/05-data-architecture.md) | 5 |
| 06 | [Security Architecture](docs/06-security-architecture.md) | 6 |
| 07 | [Reputation Firewall & Risk Framework](docs/07-reputation-firewall.md) | 7, F |
| 08 | [MVP Roadmap (sprint-by-sprint)](docs/08-mvp-roadmap.md) | 8, H |
| 09 | [Technical Architecture](docs/09-technical-architecture.md) | 9 |
| 10 | [C4 Diagrams (Mermaid)](docs/10-c4-diagrams.md) | B |
| 11 | [Event Storming Model](docs/11-event-storming.md) | C |
| 12 | [Data Model Diagrams](docs/12-data-model-diagrams.md) | D |
| 13 | [Agent Interaction Diagrams](docs/13-agent-interaction-diagrams.md) | E |
| 14 | [Event Catalog](docs/14-event-catalog.md) | 6 |
| 15 | [API Specifications](docs/15-api-specifications.md) | 5 |
| 16 | [Implementation Plan](docs/16-implementation-plan.md) | I |
| 17 | [User-Testing & "Where to Focus" Guide](docs/17-user-testing-guide.md) | — |

## Quick start

**Fastest way to see it work (no infra, no Node):**

```bash
cd services && pip install -e ".[dev]"
make walkthrough          # guided end-to-end journeys + firewall probes + a "where to focus" report
```

**Full local dev:**

```bash
# 1. Boot the local stack (Postgres, Redis, NATS, MinIO, Qdrant)
make up

# 2. Run database migrations + seed a demo condominium
make migrate && make seed

# 3. Start the API gateway and agent runtime
make dev                  # http://localhost:8080/docs  (Swagger — drive any journey yourself)

# 4. Open the portals
pnpm install
pnpm --filter resident-portal dev   # http://localhost:3000/ask
pnpm --filter ops-console dev        # http://localhost:3002/reviews
```

New here? Read [docs/17 — User-Testing Guide](docs/17-user-testing-guide.md) to navigate the
end-to-end experience and decide where to focus, then [docs/16](docs/16-implementation-plan.md) for
the full developer guide.

## Tech stack (summary)

- **Backend / agents:** Python 3.12, FastAPI, LangGraph, Pydantic v2, SQLAlchemy 2.
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind, shadcn/ui.
- **Data:** PostgreSQL 16 (+ pgvector), Qdrant (vectors), S3-compatible object store, Redis.
- **Messaging:** NATS JetStream (event bus), Temporal (durable workflows).
- **AI:** Claude (Anthropic) as primary LLM, with an LLM router; RAG over Qdrant.
- **Infra:** Docker, Kubernetes, Helm, Terraform, GitHub Actions; EU region only.

## License

Proprietary — © CondominioOS. All rights reserved.
