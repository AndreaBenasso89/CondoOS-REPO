# 05 — Data Architecture

Polyglot persistence with **hard multi-tenant isolation**, EU residency, and **audit-by-design**.
Canonical schemas (DDL) live in `services/condominioos/db/schema.sql`; ORM models in
`services/condominioos/db/models.py`. ER diagrams are in **doc 12**.

---

## 1. Storage technologies & responsibilities

| Store | Tech | Holds | Isolation |
|---|---|---|---|
| **Operational DB** | PostgreSQL 16 | All transactional aggregates (condo, units, invoices, tickets, …) | Row-level (RLS) by `condominium_id` + per-tenant schema option |
| **Vector DB** | Qdrant (+ pgvector fallback) | Knowledge chunks/embeddings | Per-tenant **namespace/collection** |
| **Object storage** | S3-compatible (EU) | Documents, scans, attachments, generated PDFs | Per-tenant key prefix + bucket policy |
| **Audit DB** | PostgreSQL (separate, append-only) | Hash-chained `audit_event` | Write-only app role; immutable |
| **Cache / queues** | Redis | Sessions, rate limits, short-lived state | Keyspace prefix by tenant |
| **Event log** | NATS JetStream | Domain events (replayable) | Subject prefix `condo.{tenant}.*` |
| **Workflow state** | Temporal | Durable saga state | Namespace per env |

## 2. Multi-tenancy model

- **Tenant = condominium** (or a managing organization grouping several).
- **Default:** shared database, **Row-Level Security** keyed on `condominium_id`, enforced by Postgres
  RLS policies + an app-layer tenant context that *must* be set per request/agent-run.
- **Premium / sensitive tenants:** dedicated schema (and optionally dedicated DB) — same ORM, switched
  by connection routing.
- **Every table** carrying tenant data has a non-null `condominium_id` FK and an RLS policy. No query
  runs without a tenant context (enforced in `db/session.py`).

## 3. Canonical entities (overview)

| Entity | Key fields | Notes |
|---|---|---|
| `Condominium` | id, name, fiscal_code, address, units_count, admin_id, plan | Tenant root. |
| `Unit` | id, condo_id, identifier, type, floor, owner_id, resident_id | Apartment/shop/garage. |
| `MillesimiTable` / `MillesimiEntry` | table_id, unit_id, share | Σ shares = 1000 per table. |
| `Owner` | id, person/company fields, fiscal_code, contacts | Liable for extraordinary. |
| `Resident` | id, unit_id, person fields, contacts, consent | Occupant; ordinary costs. |
| `Vendor` | id, name, p_iva, category, durc_status, insurance_expiry, rating | Compliance fields. |
| `Invoice` | id, condo_id, vendor_id, number, date, amount, vat, due_date, status, coa_code | OCR-extracted. |
| `Payment` | id, condo_id, amount, date, method, matched_charge_ids, status | Bank-fed. |
| `Charge` | id, condo_id, unit_id, period, amount, due_date, status | Allocated by millesimi. |
| `Ticket` | id, condo_id, reporter, category, severity, status, sla_due | Maintenance. |
| `WorkOrder` | id, ticket_id, vendor_id, cost, status, scheduled_at | |
| `Assembly` | id, condo_id, type, scheduled_at, call_no, status | Ordinary/extraordinary. |
| `Convocation` | id, assembly_id, sent_at, notice_days, content_ref | Legal notice. |
| `Proxy` | id, assembly_id, grantor_owner_id, grantee, share | Delega. |
| `Resolution` | id, assembly_id, topic, votes_for/against, millesimi_for/against, outcome | |
| `Minutes` | id, assembly_id, content_ref, signed_by, signed_at, status | Verbale. |
| `Document` | id, condo_id, type, title, storage_key, version, pii_tags[], expiry_date | |
| `Communication` | id, condo_id, channel, direction, parties, body_ref, firewall_verdict | Every message. |
| `AuditEvent` | id, ts, actor, action, entity, prev_hash, hash, payload | Hash-chained. |
| `AgentRun` | id, agent, task_id, model, prompt_version, inputs, outputs, tokens, cost | Reproducibility. |

Full DDL: `services/condominioos/db/schema.sql`. ER diagram: doc 12.

## 4. Audit-by-design (hash chain)

Every state-changing action writes an `audit_event`:

```
hash_n = SHA256( prev_hash || canonical_json(payload_n) )
```

- Append-only table; the app's audit role has `INSERT` only (no `UPDATE`/`DELETE`).
- Periodic anchoring: the latest hash is checkpointed (e.g., to object storage / external notary) so
  tampering with history is detectable.
- Each `AgentRun` is fully reproducible: model id, prompt version, retrieved context refs, tool calls,
  inputs, outputs, token/cost — enabling post-hoc review and dispute defense.

## 5. Knowledge / RAG data

- **Chunking:** layout-aware for legal/structured docs; semantic for free text.
- **Per-tenant collections** in Qdrant: `kb_tenant_{condo_id}`; a separate shared, read-only
  `kb_legal_corpus` (Codice Civile arts. 1117–1139, L.220/2012, disp. att., regional norms).
- **Metadata filters:** `doc_type`, `entity_id`, `effective_date`, `pii` — used for precise,
  access-controlled retrieval.
- **Isolation guarantee:** retrieval API requires tenant context; cross-tenant query is impossible by
  construction (collection name derived from authenticated context, never from user input).

## 6. PII & data classification

| Class | Examples | Controls |
|---|---|---|
| **Special/sensitive** | health (accessibility), disputes | Extra access control, never in prompts unless essential, redaction-first. |
| **Personal** | names, contacts, fiscal codes, unit balances | RLS, encryption at rest, minimization in prompts. |
| **Financial** | invoices, payments, arrears | Restricted roles, full audit. |
| **Operational** | tickets, schedules | Standard tenant scope. |
| **Public** | regolamento (within condo) | Standard. |

PII is **detected and tagged at ingestion** (Document Agent) and **minimized at prompt-assembly time**
(only what the task needs is sent to the LLM; see doc 06 §PII-minimization).

## 7. Data lifecycle & retention

| Data | Retention | Basis |
|---|---|---|
| Accounting records | 10 years | Italian civil/tax law. |
| Minutes / assembly records | Indefinite (condo history) | Governance. |
| Communications | Contract duration + 24 months | Legitimate interest / contract. |
| Conversation transcripts | 12–24 months | Service quality; minimization. |
| Audit log | 10 years (immutable) | Compliance/dispute defense. |
| Agent run telemetry | 90–180 days (then aggregate) | Ops; minimization. |

DSAR/erasure: personal data erasure honored except where legal retention (accounting/minutes) applies;
crypto-shredding for object storage; audit log keeps a tombstone, not the personal payload.

## 8. Migrations & evolution

- **Alembic** migrations, forward-only in prod, reviewed; expand/contract pattern for zero-downtime.
- **Event schema** versioned via the Event Catalog (doc 14) with a schema registry; consumers tolerate
  additive changes.
- **No destructive migration** runs without a verified backup and a documented rollback.
