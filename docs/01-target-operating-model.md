# 01 — Target Operating Model (TOM)

How CondominioOS delivers a regulated, trust-sensitive service while keeping humans on the loop and
agents doing the work.

---

## 1. Operating philosophy: humans *on* the loop, agents *in* the loop

| | Traditional admin | CondominioOS |
|---|---|---|
| Who does the work | Human admin + clerks | Agent fleet (90%+) |
| Human role | Executes everything | Supervises, approves the risky 10%, is legal principal |
| Cost driver | Labor hours | Compute + the supervised exception rate |
| Scale limit | ~30–60 buildings/admin | 150–400 buildings/admin |

The licensed **Amministratore of Record (AoR)** remains the legally accountable party
(Art. 1129 CC). CondominioOS is the *managed service and toolchain* the AoR uses; agents act as
delegated assistants whose risky outputs the AoR ratifies.

## 2. Roles & responsibilities (RACI)

| Function | AoR (human) | Ops Pod (human) | Agent Fleet | Customer (resident/owner) |
|---|---|---|---|---|
| Legal accountability | **A/R** | C | I | I |
| Resident Q&A | I | C | **R** | — |
| Invoice processing | A | C | **R** | I |
| Payment collection | **A** | C | **R** | I |
| Vendor dispatch | A | **C/R** | **R** | I |
| Assembly convocation | **A/R** | C | **R** (draft) | I |
| Minutes finalization | **A** (sign) | C | **R** (draft) | I |
| Compliance deadlines | A | C | **R** | I |
| Escalations | **R** | **R** | I | I |

`A`=Accountable, `R`=Responsible, `C`=Consulted, `I`=Informed.

## 3. The human team (lean by design)

| Role | Ratio (GA) | Responsibilities |
|---|---|---|
| **Amministratore of Record** | 1 : 150–400 buildings | Legal principal, signs minutes/filings, approves A0 actions, assembly chair. |
| **Operations Specialist** | 1 : 300–600 buildings | Works the human review queue, vendor exceptions, customer success. |
| **Compliance Officer** | 1 : platform | Policy, DPO interface, audit, regulation updates. |
| **Agent SRE / Eng** | platform | Runtime, evals, prompt/version governance, incident response. |

## 4. Autonomy tiers (the core governance dial)

Every agent action is assigned an **autonomy tier** = function of *risk class* × *confidence score*.

| Tier | Meaning | Example | Human involvement |
|---|---|---|---|
| **A3 — Auto** | Execute & log | Answer a FAQ, file a document, post a low-risk invoice | None (post-hoc audit) |
| **A2 — Auto + notify** | Execute, then notify supervisor | Schedule a known vendor, send a 1st-tier soft reminder | Async review |
| **A1 — Propose** | Draft, hold for 1-click approval | Convocation notice, 2nd reminder, vendor >€X | Synchronous approval |
| **A0 — Human-led** | Agent assists only | Legal interpretation, dispute, minutes signature, derogation | Human executes |

The mapping of (function × risk × confidence) → tier is policy-as-code (see doc 07 §5).

## 5. Service tiers (commercial)

| Tier | Price target | Includes |
|---|---|---|
| **Self-managed Lite** | €8–15/unit/yr | Portal, docs, FAQ concierge, compliance alerts, payment tracking. No AoR. |
| **Managed Core** | €25–40/unit/yr | Everything + AoR of record, collections, vendor dispatch, assemblies. |
| **Managed Plus** | €45–70/unit/yr | + PEC, advanced accounting, dispute support, priority human SLA. |

(All materially below the traditional €60–120/unit/yr.)

## 6. Cost-to-serve model (illustrative, per building/month)

| Item | Traditional | CondominioOS target |
|---|---|---|
| Human labor | €40–70 | €4–10 (supervision share) |
| Software | €2–5 | €3 |
| LLM / compute | — | €1–3 |
| Channels (WhatsApp/PEC/email) | — | €0.5–1.5 |
| **Total** | **€45–80** | **€9–18** |

Unit economics improve with **autonomy ramp** (more A3) and **portfolio density** (buildings/admin).

## 7. Service-level objectives (SLOs)

| Interaction | SLO |
|---|---|
| Resident message acknowledged | < 30 s (auto) |
| Resident question resolved (FAQ class) | < 5 min |
| Maintenance ticket triaged | < 15 min |
| Emergency maintenance dispatched | < 60 min |
| Invoice ingested → posted | < 1 business day |
| Human review queue SLA (A1) | < 4 business hours |
| Assembly convocation lead time | ≥ 5 days (legal min) + buffer |

## 8. The exception engine (how scale holds)

Scale depends on keeping the **human-touch rate low and bounded**. Every escalation is:
1. **Classified** (why it escalated: low confidence, risk class, policy, novelty).
2. **Measured** (escalation rate per agent, per tenant, per intent — a first-class KPI).
3. **Fed back** (recurring escalations become new playbooks, tools, or eval cases → re-automated).

Target: human-touch rate decreases monotonically per cohort as the system learns.

## 9. Governance forums

| Forum | Cadence | Purpose |
|---|---|---|
| Agent Quality Review | Weekly | Review QA evals, escalation trends, prompt/version changes. |
| Risk & Compliance Board | Monthly | Incidents, regulation updates, autonomy-tier policy changes. |
| Tenant Autonomy Gate | Per-tenant | Approve raising a tenant from supervised → autonomous tiers. |

## 10. Onboarding flow (new condominium)

1. Contract + DPA signed; tenant provisioned (isolated schema/namespace).
2. Document drop: regolamento, verbali, polizza, contratti, fatture → Document Agent ingests/classifies.
3. Anagrafica import: units, owners, residents, millesimi (thousandths table).
4. Channel setup: WhatsApp number, email alias, optional PEC.
5. **Supervised mode** for first 30–60 days (all A1/A0 escalate) → autonomy ramp after QA sign-off.
