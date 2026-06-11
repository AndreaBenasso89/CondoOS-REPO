# 17 — User-Testing & "Where to Focus" Guide

How to run a user test of CondominioOS today, navigate the end-to-end experience, and decide where to
invest the first round of structural improvement.

> **Reality check.** The **backend pipeline is runnable end-to-end right now** (offline, no infra):
> resident message → Orchestrator → specialist agent → Reputation Firewall → send / hold / escalate,
> all audited. The **agents, tools, RAG, and LLM are stubs**, and the **frontends are skeletons**.
> So your first user test is about the *shape and safety of the flow*, not yet the quality of the
> AI's answers. That's exactly the right thing to validate first.

---

## Three ways to navigate the experience (increasing fidelity & effort)

| # | Path | What you see | Effort | Needs |
|---|---|---|---|---|
| **1** | **Scenario walkthrough (recommended first)** | All key journeys + firewall probes + a gap report, printed | 1 command | Python only |
| **2** | **Interactive API (Swagger)** | Drive any journey yourself, inspect the review queue, approve items | a few min | Python + FastAPI |
| **3** | **Clickable UI** | Resident asks a question; you approve held items in the Ops Console | ~15 min | Node + the API running |

---

## Path 1 — Scenario walkthrough (start here)

```bash
cd services
pip install -e ".[dev]"          # or: uv sync
python -m condominioos.scripts.walkthrough     # or: make walkthrough
```

It prints four parts:
1. **Resident journeys** through the live pipeline (FAQ, knowledge-gap, emergency, routine
   maintenance, arrears, legal) — each shows the intent, the agent steps, the firewall verdict, and
   the **outcome** (SENT / HELD / ESCALATED / COMPLETED).
2. **Firewall probes** — unsafe outbound (over-collection, wrong recipient, legal threat, ungrounded
   claim) submitted directly so you can watch the firewall **BLOCK/HOLD** it and see *which layer*
   tripped.
3. **Audit trail & review queue** — proves the run is tamper-evident and shows what's waiting for a
   human.
4. **Maturity & gap report** — a prioritized table of what's wired vs stubbed, with the recommended
   first round of work.

This single command is the fastest way to "feel" the system and find the seams.

---

## Path 2 — Interactive API (drive it yourself)

```bash
cd services
make dev                          # uvicorn on http://localhost:8080
# open http://localhost:8080/docs  (Swagger UI)
```

Then:
1. `POST /v1/webhooks/whatsapp` with
   ```json
   { "tenant_id": "<any-uuid>", "channel": "whatsapp",
     "unit_id": "<any-uuid>", "text": "Quali sono gli orari del portiere?" }
   ```
   → returns the intent, confidence, trail, and whether it was sent or held.
2. `GET /v1/reviews` → see items the firewall **held** for a human.
3. `POST /v1/reviews/{id}/approve` with `{ "reviewer": "you@studio.it" }` → approve a held draft.
4. `GET /v1/audit/verify` (once wired) → confirm the hash-chain is intact.

> Tip: send a deliberately unsafe message (e.g. an arrears question) and watch it land in the review
> queue instead of going out — that's the Reputation Firewall doing its job.

---

## Path 3 — Clickable UI (the human-in-the-loop experience)

Two of the three portals are scaffolded to run. The **Ops Console review queue** is the most valuable
to user-test because it *is* the human-in-the-loop control surface.

```bash
# Terminal 1 — API
cd services && make dev

# Terminal 2 — UIs
pnpm install
pnpm --filter resident-portal dev   # http://localhost:3000  (ask a question)
pnpm --filter ops-console dev       # http://localhost:3002/reviews  (approve held items)
```

Flow to demo to a design partner:
1. In the **resident portal** `/ask`, submit a question → it calls the gateway webhook.
2. If the firewall holds it, open the **ops-console** `/reviews` → you see the draft, the recipient,
   citations, the verdict, and the tripped layers → click **Approve**.
3. Point out: *nothing reached the resident without a human seeing it.* That's the trust story.

(The admin portal is a navigation skeleton; flesh it out once the journeys you care about are solid.)

---

## A structured method for deciding where to focus

Run the walkthrough, then score each **journey** (FAQ, documents, maintenance, accounting,
collections, assemblies, compliance) on this rubric. Focus where **impact × risk** is high and
**maturity** is low.

| Dimension | Question | 1 (weak) → 5 (strong) |
|---|---|---|
| **Correctness** | Does it do the right thing on the happy path? | |
| **Safety** | Does the firewall catch the unsafe variants? | |
| **Grounding** | Are answers cited / refused when unknown? | |
| **Escalation** | Does it escalate the right cases (not too much/little)? | |
| **Observability** | Can you reconstruct *why* from the trail + audit? | |
| **Effort-to-real** | How far from stub → production for this journey? | |

### The "seams" checklist (what the walkthrough exposes today)
- [ ] **Intent classifier is keyword-based** → misroutes phrasings without a keyword (you'll see a
      maintenance request classified as `info_request`). *First-class candidate for the LLM upgrade.*
- [ ] **Grounding (firewall L2) and tone (L6) are heuristics** → the firewall's safety quality is
      only as good as these; this is the #1 structural investment.
- [ ] **All domain tools are stubs** → behaviour is canned; replace per bounded context, starting
      with the ones that gate money/safety (`reconcile.confirm`, `vendor.check_compliance`).
- [ ] **RAG is in-memory keyword match** → drives both answer quality and the escalation rate.
- [ ] **Notification is a mock** → wire one real channel to test the true resident experience.
- [ ] **Stores are in-memory** → run `make up && make migrate` to test multi-tenant isolation (RLS)
      for real.

---

## Recommended sequence for the first improvement round

Based on impact × risk (also printed by the walkthrough's gap report):

1. **Harden the Reputation Firewall's smart layers** (L2 grounding verifier, L6 tone classifier,
   L7 risk model). Everything else depends on this being trustworthy. Grow the red-team eval suite
   (`condominioos.evals`) alongside.
2. **Turn on real agent reasoning** (add an Anthropic key, wire prompts, replace the keyword
   classifier). Now the *quality* failure modes become visible and testable.
3. **Make one journey real end-to-end** — pick **Collections** (highest reputational risk) or
   **Resident FAQ** (highest volume): real tools, real RAG, real channel, Postgres-backed.
4. **Flesh out the Ops Console** so humans can actually work the review queue at speed.
5. **Switch persistence to Postgres + RLS** and run the multi-tenant isolation tests.

Repeat: each loop, re-run the walkthrough and re-score the rubric. The escalation rate and the
firewall's block/hold/approve mix are your north-star quality signals.
