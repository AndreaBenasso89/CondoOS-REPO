# Frontends

A single Next.js 14 app — **`console`** — delivers all three experiences (Resident, Operations,
Admin) over a shared simulation layer, with login, seeded personas, and a “view as” profile switcher.
This unified design is what makes **cross-visibility** work (an action by one profile is visible to
the others) and lets you assess every interface in one test environment.

| Experience | Audience | Purpose |
|---|---|---|
| Resident (`/resident/*`) | Residents / owners | Ask questions, view documents, pay, open tickets, see assembly info. |
| Operations (`/operator/*`) | Ops Specialist | **Human-in-the-loop:** review queue, all conversations, tickets, activity. |
| Admin (`/admin/*`) | Amministratore (AoR) | Building/units, accounting, assemblies, compliance, audit log. |

```bash
pnpm install
pnpm --filter console dev    # http://localhost:3000
```

See [`console/README.md`](console/README.md) for personas and the cross-visibility walkthrough. The
role-scoped routes map cleanly to three separate deployments later.
