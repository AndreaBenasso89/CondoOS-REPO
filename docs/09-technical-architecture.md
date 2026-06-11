# 09 — Production Technical Architecture

The runtime view: components, tech stack, microservices, AI layer, and how a request flows end-to-end.
C4 diagrams in doc 10; events in doc 14; APIs in doc 15.

---

## 1. Recommended tech stack

| Layer | Choice | Rationale |
|---|---|---|
| **Language (backend/agents)** | Python 3.12 | First-class LLM/agent ecosystem. |
| **Agent framework** | LangGraph | Explicit, inspectable, durable graph orchestration with human-in-the-loop checkpoints. |
| **API framework** | FastAPI + Pydantic v2 | Async, typed, OpenAPI-native. |
| **ORM / DB** | SQLAlchemy 2 + Alembic, PostgreSQL 16 | Mature, RLS support, pgvector option. |
| **Vector DB** | Qdrant | Per-tenant collections, hybrid search, EU-hostable. |
| **Object storage** | S3-compatible (EU) / MinIO local | Documents & attachments. |
| **Event bus** | NATS JetStream | Lightweight, replayable, subject-based multi-tenant isolation. |
| **Durable workflows** | Temporal | Sagas (assembly, dispatch) survive restarts; not agent-driven. |
| **Cache/locks** | Redis | Sessions, rate limits, idempotency. |
| **Frontend** | Next.js 14 (App Router), TS, Tailwind, shadcn/ui | Three portals, SSR, fast. |
| **LLM** | Claude (Anthropic) primary via router | Strong reasoning + safety; EU/no-train config. |
| **Observability** | OpenTelemetry, Prometheus, Grafana, Loki | Traces/metrics/logs with tenant+trace ids. |
| **Infra** | Docker, Kubernetes, Helm, Terraform | Cloud-native, reproducible, EU regions. |
| **CI/CD** | GitHub Actions | Tests, scans, eval gate, staged deploy. |

## 2. Microservices

| Service | Responsibility | Bounded context |
|---|---|---|
| `gateway` | API gateway: authn/z, routing, rate limit, OpenAPI. | Platform |
| `channels` | WhatsApp/Email/PEC/Web adapters (ACL → events). | Communications |
| `agent-runtime` | LangGraph orchestrator + agent fleet host. | Agent Orchestration |
| `firewall` | Reputation Firewall (8 layers) + verdict signing. | Reputation Firewall |
| `notification` | **Only** egress to channels; refuses unsigned verdicts. | Communications |
| `registry` | Condominium/unit/owner/resident/millesimi. | Property & Registry |
| `accounting` | Invoices, ledger, payments, reconciliation. | Financial |
| `maintenance` | Tickets, work orders, SLAs. | Maintenance |
| `vendors` | Vendor registry, quotes, compliance, scheduling. | Maintenance/Vendors |
| `assemblies` | Assembly lifecycle, convocations, minutes. | Governance |
| `compliance` | Obligations, deadlines, alerts. | Compliance |
| `documents` | Ingest/OCR/classify/PII/index. | Documents & Knowledge |
| `knowledge` | RAG retrieval API (tenant-scoped + legal corpus). | Documents & Knowledge |
| `audit` | Append-only hash-chained audit log + verification. | Platform |
| `review` | Human review queue + approvals. | Platform |
| `identity` | Users, tenants, roles, channel identities. | Platform |
| `workflows` | Temporal workers for sagas. | Platform |

Services communicate via **events (NATS)** for state propagation and **sync APIs (gateway/mesh)** for
queries and tool calls. Each owns its tables; no cross-service DB access.

## 3. Component view (runtime)

```mermaid
flowchart TB
  subgraph Edge
    GW[API Gateway]:::p
    WAF[WAF / rate limit]:::p
  end
  subgraph Channels
    WA[WhatsApp adapter]; EM[Email adapter]; PEC[PEC adapter]; WEB[Web BFF]
  end
  subgraph AI[AI / Agent layer]
    RT[Agent Runtime / LangGraph]:::a
    RF[Reputation Firewall]:::r
    KN[Knowledge / RAG]:::a
    ROUT[LLM Router]:::a
    PR[Prompt Registry]:::a
    EVAL[Eval Framework]:::a
  end
  subgraph Domain[Domain services]
    REG[registry]; ACC[accounting]; MNT[maintenance]; VEN[vendors]; ASM[assemblies]; CMP[compliance]; DOC[documents]
  end
  subgraph Platform
    NOTIF[Notification Engine]; REV[Review]; AUD[Audit]; IDN[Identity]; WF[Temporal]
  end
  subgraph Data
    PG[(PostgreSQL)]; QD[(Qdrant)]; OS[(Object store)]; AUDDB[(Audit DB)]; RDS[(Redis)]; NATS{{NATS JetStream}}
  end
  WAF-->GW-->Channels-->NATS
  NATS-->RT-->ROUT-->LLM[(Claude / LLM)]
  RT-->KN-->QD
  RT-->Domain
  RT-->RF-->NOTIF-->Channels
  RF-->REV
  Domain-->PG; DOC-->OS; AUD-->AUDDB; Domain-->NATS
  RT & RF & Domain --> AUD
  WF-->Domain
  classDef a fill:#e3f2fd; classDef r fill:#ffebee; classDef p fill:#f3e5f5;
```

## 4. AI layer detail

- **LLM Router** (`agent-runtime/llm/router.py`): selects model by task class, cost, latency, and
  fallback; enforces per-tenant token/cost budgets; supports degraded "human-only" mode on outage.
- **Agent orchestration:** LangGraph state graph; nodes = agents/tools; **interrupt checkpoints** for
  human-in-the-loop (firewall HOLD) using LangGraph's persistence/interrupt model.
- **RAG:** Knowledge service does hybrid retrieval (vector+keyword+metadata) with reranking,
  tenant-scoped collections, and citation assembly; refuses on low coverage.
- **Tool calling:** typed tools (Pydantic-validated args), default-deny allowlist per agent, every
  call audited and budget-counted.
- **Prompt management:** versioned prompt registry (text + model + params), referenced by id in every
  `AgentRun` for reproducibility; changes gated by QA evals.
- **Evaluation framework:** rubric + reference evals, LLM-as-judge (calibrated), red-team suites,
  release gate; production sampling drives autonomy ramp.

## 5. End-to-end request flow (resident question)

1. WhatsApp webhook → `channels` (verify signature, identity) → emits `message.received` (NATS).
2. `agent-runtime`: Orchestrator classifies intent → routes to Concierge.
3. Concierge calls `knowledge.query` → grounded context + citations + confidence.
4. Concierge builds `OutboundDraft` → `firewall` (L1–L8).
5. Firewall: grounded + low-risk + high-confidence → **APPROVE** (signed verdict) → `notification`.
6. `notification` verifies verdict signature & artifact hash → sends via WhatsApp adapter.
7. Every step writes `audit_event` (hash-chained); OTel trace spans the whole path.

If not approved → HOLD → `review` → Ops Console → human verdict → re-validate → send. All audited.

## 6. Scalability & resilience

- Stateless services scale horizontally; agent-runtime workers scale by queue depth.
- Idempotency keys on all event handlers; exactly-once effects via dedup + outbox pattern.
- Sagas on Temporal survive restarts; LangGraph checkpoints persist interrupted runs.
- Per-tenant budgets and rate limits protect against runaway cost/abuse.
- Circuit breakers + LLM failover; degraded mode keeps humans in control if AI is down.

## 7. Environments & residency

- `dev` (docker-compose) → `staging` (k8s, EU) → `prod` (k8s, EU, multi-AZ).
- EU-only data residency; LLM provider region pinned; sub-processor DPAs in place.
- Blue/green or canary deploys with the eval gate; per-tenant autonomy flags allow safe rollout.
