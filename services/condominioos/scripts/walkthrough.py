"""Guided end-to-end walkthrough — the "user-test kit".

Runs a curated set of resident journeys through the real runtime (Orchestrator → specialist agent →
Reputation Firewall → send / hold / escalate), prints a human-readable trace of *what each component
decided and why*, then prints a **maturity & gap report** so you can see where to focus the first
round of structural improvement.

Run:  make walkthrough     (or)  python -m condominioos.scripts.walkthrough

No external infrastructure required — everything runs offline with in-memory stubs.
"""

from __future__ import annotations

import asyncio
import uuid

from condominioos.agents import AgentState
from condominioos.agents.tools import default_registry
from condominioos.audit import audit_log
from condominioos.common.tenancy import TenantContext, tenant_scope
from condominioos.firewall import (
    ArtifactKind,
    Financials,
    OutboundArtifact,
    Recipient,
    ReputationFirewall,
)
from condominioos.firewall.layers import GuardContext
from condominioos.knowledge import InMemoryKnowledge
from condominioos.review import review_queue
from condominioos.runtime import build_runtime

# ── tiny console helpers ────────────────────────────────────────────────────
BOLD, DIM, GREEN, RED, YELLOW, CYAN, RESET = (
    "\033[1m", "\033[2m", "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[0m")


def h1(t: str) -> None:
    print(f"\n{BOLD}{CYAN}{'═' * 78}{RESET}\n{BOLD}{CYAN}  {t}{RESET}\n{BOLD}{CYAN}{'═' * 78}{RESET}")


def h2(t: str) -> None:
    print(f"\n{BOLD}▶ {t}{RESET}")


def verdict_color(v: str) -> str:
    return {"APPROVE": GREEN, "BLOCK": RED, "HOLD": YELLOW, "REVISE": YELLOW}.get(v, RESET)


# ── scenario definitions ────────────────────────────────────────────────────
SCENARIOS = [
    ("Grounded FAQ (happy path)", "whatsapp",
     "Buongiorno, quali sono gli orari del portiere?",
     "Should be answered automatically and sent (low risk, grounded, high confidence)."),
    ("Knowledge gap (no grounding)", "whatsapp",
     "Posso tenere un cane di grossa taglia sul balcone?",
     "Concierge has no grounded source -> should escalate, NOT improvise."),
    ("Maintenance — emergency (safety)", "whatsapp",
     "C'è una forte perdita di gas nel vano scale!",
     "Life-safety -> on-call dispatch AND human notified (A0)."),
    ("Maintenance — routine", "whatsapp",
     "Il citofono d'ingresso è rotto, può venire un tecnico?",
     "Triage -> compliant vendor under cost threshold -> scheduled (internal, no resident outbound)."),
    ("Arrears reminder", "email",
     "Ho ricevuto un sollecito ma non ricordo l'importo.",
     "Routes to Collections -> reconcile first -> draft T1 -> held for human (A1)."),
    ("Legal request", "email",
     "Voglio inviare una diffida legale all'amministratore.",
     "Legal interpretation is never automated -> escalate to AoR."),
]


async def run_journeys(tenant_id: uuid.UUID) -> None:
    h1("PART 1 — Resident journeys through the live pipeline")
    runtime = build_runtime(offline=True)

    # Seed a small per-tenant knowledge base so grounded answers are possible.
    kn: InMemoryKnowledge = runtime.specialists["concierge"].knowledge  # type: ignore[attr-defined]
    kn.seed(kn.collection_for(tenant_id), [
        {"text": "Gli orari del portiere sono dalle 8 alle 12 dal lunedì al venerdì.",
         "source": "doc:regolamento#art3", "doc_id": "regolamento"},
        {"text": "Il portiere riceve al piano terra durante gli orari indicati.",
         "source": "doc:regolamento#art4", "doc_id": "regolamento"},
    ])

    for title, channel, text, expectation in SCENARIOS:
        h2(title)
        print(f'  {DIM}Resident ({channel}):{RESET} "{text}"')
        print(f"  {DIM}Expected:{RESET} {expectation}")
        with tenant_scope(TenantContext(condominium_id=tenant_id, actor="system",
                                        correlation_id=uuid.uuid4())):
            state = AgentState(tenant_id=tenant_id, input_text=text,
                               context={"channel": channel, "unit_id": uuid.uuid4(),
                                        "category": "generic"})
            result = await runtime.handle(state)
        print(f"  {DIM}Pipeline:{RESET}")
        for step in result.trail:
            print(f"     · {step}")
        sent = any("runtime: sent" in s for s in result.trail)
        held = any("held for review" in s for s in result.trail)
        if result.escalate:
            outcome, color = "ESCALATED → human", YELLOW
        elif sent:
            outcome, color = "SENT (auto)", GREEN
        elif held:
            outcome, color = "HELD → review queue", YELLOW
        else:
            outcome, color = "COMPLETED (internal action, no resident outbound)", GREEN
        print(f"  {BOLD}Outcome: {color}{outcome}{RESET}  "
              f"{DIM}(intent={result.intent}, confidence={result.confidence:.2f}){RESET}")


def run_firewall_probes() -> None:
    h1("PART 2 — Reputation Firewall probes (the safety net)")
    print(f"{DIM}These submit artifacts directly to the firewall to show it catching unsafe "
          f"outbound BEFORE anything is sent.{RESET}")
    unit = uuid.uuid4()

    probes = [
        ("Over-collection: reminder for €999 when only €120 is owed",
         OutboundArtifact(kind=ArtifactKind.REMINDER, channel="email",
                          recipient=Recipient(type="owner", unit_id=unit), text="Sollecito €999.",
                          financials=Financials(amount=999.0, ledger_balance=120.0)),
         GuardContext(ledger_balance_resolver=lambda r: 120.0,
                      recipient_unit_resolver=lambda r: r.unit_id), "BLOCK"),
        ("Wrong recipient: message addressed to the wrong unit",
         OutboundArtifact(kind=ArtifactKind.MESSAGE, channel="whatsapp",
                          recipient=Recipient(type="resident", unit_id=unit),
                          text="Il suo saldo è €120."),
         GuardContext(recipient_unit_resolver=lambda r: uuid.uuid4()), "BLOCK"),
        ("Unfounded legal threat in a reminder",
         OutboundArtifact(kind=ArtifactKind.REMINDER, channel="email",
                          recipient=Recipient(type="owner", unit_id=unit),
                          text="Pagare subito o procederemo con pignoramento.",
                          financials=Financials(amount=120.0, ledger_balance=120.0)),
         GuardContext(ledger_balance_resolver=lambda r: 120.0,
                      recipient_unit_resolver=lambda r: r.unit_id), "HOLD"),
        ("Ungrounded factual claim (no citation)",
         OutboundArtifact(kind=ArtifactKind.MESSAGE, channel="whatsapp",
                          recipient=Recipient(type="resident", unit_id=unit),
                          text="L'assemblea è il 20 giugno.",
                          claims=[{"text": "assemblea 20 giugno", "source": None}]),
         GuardContext(recipient_unit_resolver=lambda r: r.unit_id,
                      grounding_verifier=lambda claim, cites: False), "HOLD"),
    ]
    for title, artifact, ctx, expect in probes:
        fw = ReputationFirewall(ctx)
        v = fw.evaluate(artifact, agent="probe", confidence=0.95)
        ok = "✓" if v.verdict.value == expect else "✗"
        col = verdict_color(v.verdict.value)
        mark = f"{GREEN}{ok}{RESET}" if ok == "✓" else f"{RED}{ok}{RESET}"
        failed_layers = [r.layer for r in v.layer_results if not r.passed]
        h2(title)
        print(f"  Verdict: {col}{BOLD}{v.verdict.value}{RESET} (expected {expect}) {mark}"
              f"  {DIM}tripped: {', '.join(failed_layers) or 'none'}{RESET}")


def maturity_report() -> None:
    h1("PART 3 — Maturity & gap report — WHERE TO FOCUS")
    n_tools = len(default_registry._tools)
    rows = [
        ("Reputation Firewall (8 layers)", "WIRED — heuristic", "high",
         "L2 grounding & L6 tone are simple heuristics; swap in an NLI grounding verifier and a "
         "tone classifier. L7 risk is a rules stub. THIS IS THE #1 PLACE TO INVEST."),
        ("Agent reasoning (LLM)", "STUB (offline)", "high",
         "All agents use deterministic stubs; the orchestrator intent classifier is keyword-based. "
         "Add an ANTHROPIC key + wire real prompts to see true behaviour & failure modes."),
        (f"Governed tools ({n_tools} registered)", "ALL STUBBED", "high",
         "Every domain tool returns canned data. Replace per bounded context, starting with "
         "reconcile.confirm / ledger.* (gates Collections) and vendor.check_compliance."),
        ("Knowledge / RAG", "IN-MEMORY", "high",
         "Keyword match over a seeded list. Stand up Qdrant + real ingestion to test grounding "
         "quality — directly drives the firewall's L2 and the escalation rate."),
        ("Channels (WhatsApp/Email/PEC)", "ADAPTERS + MOCK send", "medium",
         "Inbound normalization exists; Notification uses a mock client. Wire one real channel to "
         "test the true resident experience."),
        ("Frontends (3 portals)", "SKELETON", "medium",
         "Only package.json + a page each. Flesh out ops-console (review queue) first — it is the "
         "human-in-the-loop surface you most need to user-test."),
        ("Persistence (Postgres/RLS/audit)", "SCHEMA + IN-MEMORY", "medium",
         "schema.sql + RLS designed; runtime uses in-memory stores. Run `make up && make migrate` "
         "and switch repositories to Postgres to test multi-tenant isolation for real."),
        ("Durable workflows (assembly/dispatch sagas)", "NOT WIRED", "low",
         "Temporal is in compose but sagas aren't implemented; fine for the first user test."),
    ]
    print(f"\n  {BOLD}{'Component':<42}{'Status':<22}{'Priority':<8}{RESET}")
    print(f"  {'-'*42}{'-'*22}{'-'*8}")
    for name, status, prio, _ in rows:
        pc = {"high": RED, "medium": YELLOW, "low": DIM}[prio]
        print(f"  {name:<42}{status:<22}{pc}{prio:<8}{RESET}")
    print(f"\n  {BOLD}Recommended first round of structural work:{RESET}")
    for i, (name, _, _prio, note) in enumerate([r for r in rows if r[2] == "high"], 1):
        print(f"  {BOLD}{i}. {name}{RESET}\n     {DIM}{note}{RESET}")


def audit_and_queue_summary() -> None:
    h1("PART 4 — Audit trail & human review queue")
    print(f"  Audit chain: {GREEN if audit_log.verify() else RED}"
          f"{'VALID (tamper-evident)' if audit_log.verify() else 'TAMPERED'}{RESET} "
          f"— {len(audit_log._events)} events recorded across the run.")
    pending = review_queue.pending()
    print(f"  Human review queue: {len(pending)} item(s) awaiting a human decision:")
    for item in pending:
        print(f"     · {YELLOW}{item.kind}{RESET} (priority={item.priority})  id={str(item.id)[:8]}")
    print(f"\n  {DIM}In the running system these items appear in the Ops Console "
          f"(apps/ops-console) for one-click Approve / Edit / Reject.{RESET}")


async def main() -> None:
    tenant_id = uuid.uuid4()
    await run_journeys(tenant_id)
    run_firewall_probes()
    audit_and_queue_summary()
    maturity_report()
    print(f"\n{DIM}Next: see docs/17-user-testing-guide.md for the interactive API and UI paths, "
          f"and the prioritization rubric.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
