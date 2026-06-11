# CondominioOS Console (test environment)

A single, polished Next.js app that contains **all three experiences** — Resident, Operations, and
Admin — over a **shared simulation layer**, so you can navigate every interface with different
profiles and see how actions by one user become visible to the others.

## Run it

```bash
pnpm install                 # from the repo root (workspace)
pnpm --filter console dev    # http://localhost:3000
```

No backend or infrastructure required: the app ships a faithful in-browser simulation of the
CondominioOS pipeline (orchestrator intent routing → Reputation Firewall → send / hold / escalate),
persisted to `localStorage`.

## Log in & switch profiles

The login screen lists **seeded demo personas** grouped by role — click one to enter (no password).
Once inside, use **“Visualizza come”** (top-right) to instantly switch to any other persona and assess
their experience.

| Role | Personas | Sees |
|---|---|---|
| **Resident** | Giulia Conti (Int. 3), Marco Rossi (Int. 5, moroso), Anna Verdi (Int. 2) | Their own unit, conversations, payments, tickets, assembly. |
| **Operations** | Luca Ferrari | The review queue, **all** conversations, all tickets, full activity feed. |
| **Admin (AoR)** | Avv. Sara Bianchi | Building/units, accounting, assemblies (approvals), compliance, **audit log**, activity. |

## Cross-visibility (the point)

State is shared across every profile in the same browser, so a full loop is visible end-to-end:

1. As a **resident**, ask a risky question (e.g. *“non ricordo l'importo del mio saldo”* or *“vorrei
   inviare una diffida legale”*) → it’s **held/escalated**, not auto-sent.
2. Switch to **Operations** → the item is waiting in the **review queue**; approve/edit/reject it.
3. Switch back to the **resident** → the approved answer now appears in their chat thread.
4. Switch to **Admin → Audit log** → the whole sequence is recorded in the hash-chained trail.

Try a grounded question (*“orari del portiere?”*) to see it answered automatically (Firewall APPROVE),
and an emergency ticket (*“perdita di gas”*) to see safety escalation.

## Where things live

```
app/                 routes: /login, /resident/*, /operator/*, /admin/*
components/          Shell (role nav), ProfileSwitcher, ReviewQueue, ActivityFeed, ui primitives
lib/auth.tsx         demo session + "view as" switching
lib/sim/             the shared simulated backend:
  ├─ types.ts        domain model (mirrors services/condominioos)
  ├─ personas.ts     seeded identities
  ├─ seed.ts         the demo condominium (Via Dante 12, Milano)
  ├─ engine.ts       intent classifier + Reputation Firewall logic (TS port of the backend)
  └─ store.tsx       React store + actions + hash-chained activity log (localStorage)
```

> The role-scoped route areas (`/resident`, `/operator`, `/admin`) map cleanly to three separate
> deployments later; they share one app here purely to make cross-visibility and profile-switching
> seamless for testing. To point the resident chat at the **real** FastAPI gateway instead of the
> simulation, swap `useStore().ask` for a `fetch` to `/v1/webhooks/whatsapp` (see docs/17).
