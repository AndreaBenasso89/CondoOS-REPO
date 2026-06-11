# 08 — MVP Implementation Roadmap (Sprint-by-Sprint)

2-week sprints. Goal: a **safe, supervised** managed service for a handful of design-partner buildings
by end of Phase 2, scaling autonomy in Phase 3. The **Reputation Firewall and audit are built first**
and are never optional.

---

## Phasing overview

| Phase | Sprints | Theme | Exit criteria |
|---|---|---|---|
| **0 — Foundations** | 1–2 | Platform skeleton, security, firewall scaffold | Services boot; audit + firewall gate work end-to-end with stub agents. |
| **1 — Core agents** | 3–6 | Concierge, Document, Knowledge, Accounting | Residents get grounded answers; docs ingested; invoices posted — all firewall-gated. |
| **2 — Operational depth** | 7–10 | Maintenance, Vendor, Collections, Compliance | Tickets→dispatch; reconciled reminders; deadline alerts. Design partners live (supervised). |
| **3 — Governance & ramp** | 11–14 | Assembly, Risk/QA hardening, autonomy ramp | First AI-assisted assembly; autonomy raised per QA sign-off; multi-tenant scale. |

---

## Sprint 1 — Platform foundations & security spine
- Monorepo, CI (lint/type/test), local stack (Postgres, Redis, NATS, MinIO, Qdrant, Temporal).
- Tenancy + RLS; identity/authz skeleton; tenant context propagation.
- **Audit service** (hash-chained `audit_event`) — done before any agent acts.
- Event bus + Event Catalog v0; OpenAPI gateway skeleton.
- **Deliverable:** `make up && make migrate && make dev` boots; an event round-trips and is audited.

## Sprint 2 — Reputation Firewall scaffold + agent runtime
- LangGraph agent runtime + `BaseAgent` contract; Orchestrator skeleton with intent classifier (stub).
- **Reputation Firewall** L1/L3/L8 working (schema/policy, recipient/PII, autonomy gate) + signed
  verdicts; Notification Engine refuses unsigned artifacts.
- Human review queue + Ops Console v0 (list/approve/reject).
- **Deliverable:** a stub agent draft → firewall → HOLD → human approve → send (mock channel), fully audited.

## Sprint 3 — Channels & Resident Concierge (read-only)
- WhatsApp Business + Email adapters (ACL → `message.received`); web resident portal v0.
- Concierge Agent (grounded FAQ) + Knowledge Agent (RAG) over a seeded legal corpus.
- Firewall L2 (grounding) + L6 (tone) online.
- **Deliverable:** resident asks a question on WhatsApp → grounded, cited, firewall-approved reply.

## Sprint 4 — Document & Knowledge pipeline
- Document Agent: ingest → OCR → classify → PII tag → index (per-tenant Qdrant namespace).
- Onboarding doc-drop flow; entity linking; admin portal v0 (registry + docs).
- **Deliverable:** drop regolamento/verbali/polizza → searchable; Concierge answers from them.

## Sprint 5 — Accounting ingestion
- Accounting Agent: invoice OCR/extract/validate/classify/post; chart-of-accounts; ledger.
- Anomaly + duplicate detection; A1 review for anomalies.
- **Deliverable:** email an invoice → extracted, validated, posted (anomalies held).

## Sprint 6 — Payments & reconciliation
- Bank feed import (CSV/MT940); Payment matching; reconciliation engine.
- Charge allocation by millesimi; unit balance views in portal.
- **Deliverable:** payments matched; per-unit balances correct (foundation for Collections).

## Sprint 7 — Maintenance & Vendor
- Maintenance Agent (triage, dedup, SLA timers); Vendor Agent (registry, compliance: DURC/insurance).
- Dispatch flow with cost-threshold + compliance gates; resident status updates.
- **Deliverable:** report a leak → triaged → compliant vendor scheduled (or A1 approval) → SLA tracked.

## Sprint 8 — Collections (the careful one)
- Collections Agent with **mandatory reconciliation gate**; reminder ladder T1/T2/T3.
- Firewall L4 (financial integrity) + debtor resolution (owner vs tenant) fully enforced.
- Payment-plan proposals; T2/T3 human-led.
- **Deliverable:** a confirmed-overdue unit gets a correct, kind, reconciled T1 reminder; mismatches blocked.

## Sprint 9 — Compliance monitoring
- Compliance Agent: obligation catalog, expiry/deadline computation, alerts with lead time.
- Insurance/cert expiry → remediation tasks → Vendor renewal flow.
- **Deliverable:** lapsing polizza detected weeks ahead → alert + remediation task created.

## Sprint 10 — Design-partner go-live (supervised)
- Hardening: observability dashboards, kill-switch, runbooks, DSAR tooling, backups/restore drill.
- Onboard 3–5 design-partner buildings in **fully supervised mode**.
- **Deliverable:** real residents served; every risky action human-approved; metrics flowing.

## Sprint 11 — Assembly lifecycle
- Assembly Agent: agenda assembly, convocation generation + legal validators, proxy/quorum, minutes draft.
- AoR signature flow (e-signature); follow-up task spawning.
- **Deliverable:** end-to-end AI-assisted assembly with AoR chairing/signing; legally-valid convocation.

## Sprint 12 — Risk & QA hardening
- Risk Agent composite scoring live in L7; QA Agent eval suite + golden sets + LLM-judge calibration.
- Red-team firewall suite in CI; release gate enforced.
- **Deliverable:** deploys blocked on eval regression; risk scoring drives tiering.

## Sprint 13 — Autonomy ramp & PEC
- Per-tenant autonomy gate (supervised → A2 → A3) driven by QA scorecards.
- PEC channel for legal-grade communications; Collections T2 partial automation under tight gates.
- **Deliverable:** first tenants raised to higher autonomy with measured human-touch reduction.

## Sprint 14 — Scale & multi-tenant ops
- Performance/load; per-tenant budgets; cost dashboards; SLO alerting.
- Onboarding self-service; billing integration.
- **Deliverable:** GA-candidate: scalable, observable, autonomy-tiered, audit-complete.

---

## Cross-cutting "always-on" workstreams
- **Security & GDPR** every sprint (DPIA kept current; pen-test before go-live).
- **Evals** grow with every feature; the four moments of truth covered from Sprint 3.
- **Docs & runbooks** updated per feature; nothing risky ships without a rollback path.

## Definition of Done (per feature)
1. Tests + types + lint pass. 2. Firewall gating verified. 3. Audit events emitted. 4. Eval cases
added & passing. 5. Observability (traces/metrics). 6. Runbook updated. 7. Autonomy tier configured.
