# Frontends

Three Next.js 14 (App Router, TypeScript, Tailwind) applications sharing `@condominioos/ui` and the
generated `@condominioos/sdk-ts` client (from the gateway OpenAPI).

| App | Audience | Purpose |
|---|---|---|
| `resident-portal` | Residents / owners | Ask questions, view documents, pay, open tickets, see assembly info. |
| `admin-portal` | Amministratore (AoR) | Registry, accounting, assemblies, compliance, sign minutes. |
| `ops-console` | AoR / Ops Specialist | **Human-in-the-loop:** review queue, approvals, monitoring, kill-switch. |

The **ops-console** is the most safety-critical UI: it renders firewall HOLD items with the draft,
grounding/citations, recipient, and risk rationale, and offers one-click Approve / Edit / Reject
(docs/07 §6).

Run a single app: `pnpm --filter resident-portal dev` (ports 3000/3001/3002).
