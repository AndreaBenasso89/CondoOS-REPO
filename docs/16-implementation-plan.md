# 16 — Detailed Implementation Plan & Developer Guide

How to go from this skeleton to a running, then production, system. Pairs with the sprint roadmap
(doc 08).

---

## 1. Repository layout (monorepo)

```
condominioos/
├── apps/
│   ├── resident-portal/        # Next.js — residents/owners
│   ├── admin-portal/           # Next.js — AoR
│   └── ops-console/            # Next.js — review queue, monitoring
├── services/
│   ├── pyproject.toml          # single Python project (uv), packaged as condominioos.*
│   └── condominioos/
│       ├── gateway/            # FastAPI API gateway
│       ├── channels/           # WhatsApp/Email/PEC/Web adapters (ACL)
│       ├── agents/             # agent fleet (BaseAgent + 13 agents)
│       ├── runtime/            # LangGraph orchestration graph
│       ├── firewall/           # Reputation Firewall (8 layers)
│       ├── notification/       # egress engine (verdict-gated)
│       ├── knowledge/          # RAG retrieval
│       ├── domains/            # registry/accounting/maintenance/vendors/assemblies/compliance/documents
│       ├── audit/              # hash-chained audit log
│       ├── review/             # human review queue
│       ├── llm/                # router, prompt registry
│       ├── events/             # event catalog + bus client
│       ├── db/                 # models, schema.sql, session, migrations
│       ├── evals/              # QA eval framework + suites
│       ├── common/             # config, security, tenancy, telemetry
│       └── scripts/            # seed, admin
├── packages/
│   ├── events/                 # JSON Schema event contracts (shared)
│   ├── sdk-ts/                 # generated TS client for the portals
│   └── ui/                     # shared React components
├── infra/
│   ├── docker/                 # docker-compose for local stack
│   ├── terraform/              # cloud infra (EU)
│   ├── helm/                   # k8s charts per service
│   └── ci/                     # pipelines
├── docs/                       # this documentation set
└── tools/                      # dev scripts, evaluators
```

## 2. Local development

```bash
make up           # postgres, redis, nats, minio, qdrant, temporal
make migrate      # alembic upgrade head
make seed         # demo condominium + tenant + sample docs
make dev          # gateway + agent runtime (hot reload)
make test lint typecheck eval
```

Prereqs: Docker, Python 3.12 + `uv`, Node 20 + `pnpm`. Copy `.env.example` → `.env`.

## 3. Build order (dependency-respecting)

1. **common** (config, tenancy, telemetry, security) → everything depends on it.
2. **db** (models, schema, RLS, session) + **audit** (used by all).
3. **events** (catalog + bus client) — the integration backbone.
4. **firewall** + **notification** — built before any agent can send.
5. **llm** (router, prompt registry) + **agents/base** + **runtime** (graph).
6. **knowledge** + **documents** — grounding before Q&A.
7. **domains** one by one, following the sprint plan.
8. **review** + **ops-console** — human-in-the-loop.
9. **channels** + **gateway** + **portals** — the edges.

## 4. Engineering standards
- **Python:** ruff (lint+format), mypy (strict on `condominioos`), pytest, Pydantic v2 everywhere.
- **TS:** eslint, prettier, strict tsconfig, generated SDK from OpenAPI.
- **Contracts first:** event schemas (`packages/events`) and OpenAPI are source of truth; code
  conforms; contract tests in CI.
- **Tenancy is non-negotiable:** no DB query without a tenant context; CI lints for raw sessions.
- **Every outbound through the firewall:** the only egress is `notification`; CI asserts no agent
  imports a channel client directly.

## 5. Testing strategy
| Level | What | Tooling |
|---|---|---|
| Unit | pure logic, guards, validators | pytest |
| Contract | events ↔ schema, API ↔ OpenAPI | schemathesis, jsonschema |
| Integration | service + DB + bus (testcontainers) | pytest + docker |
| Agent eval | rubric/reference/LLM-judge, golden sets | `condominioos.evals` |
| Red-team | injection, wrong-recipient, over-collection | firewall suite (CI gate) |
| E2E | journey flows across services | playwright + harness |

**Release gate (CI):** unit+contract+integration pass **and** QA eval scorecard ≥ thresholds **and**
firewall red-team suite green → only then deploy.

## 6. Definition of Done (per feature) — same as doc 08
tests+types+lint • firewall-gated • audit events emitted • eval cases added • observability • runbook
• autonomy tier configured.

## 7. Environments & deploy
- `dev` (compose) → `staging` (k8s EU) → `prod` (k8s EU multi-AZ).
- Helm per service; Terraform for infra; GitHub Actions for CI/CD with the eval gate.
- Canary + per-tenant autonomy flags; one-click kill-switch; fast rollback.

## 8. First runnable milestone (what this skeleton targets)
After `make dev`, you can:
1. POST a `comms.message.received` (or hit the WhatsApp webhook stub).
2. Watch the Orchestrator route → Concierge → Knowledge (stub) → draft.
3. See the draft hit the **Firewall** and produce a signed verdict.
4. On HOLD, see a review item appear in the Ops Console; approve it.
5. See the (mock) Notification send and the **hash-chained audit trail** for the whole journey.

From there, each sprint fills in real tools, real channels, and real domain logic.

## 9. Key risks for engineering & how the skeleton mitigates them
- **Agents sending unvetted output:** structurally impossible — no channel client in agents; firewall
  verdict required by notification.
- **Cross-tenant leakage:** tenant context + RLS + namespaced vectors enforced in `common`/`db`/`knowledge`.
- **Unreproducible AI decisions:** every `AgentRun` records model+prompt_version+tools+io+cost.
- **Silent regressions:** QA eval gate + firewall red-team in CI.
