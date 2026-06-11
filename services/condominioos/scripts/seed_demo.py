"""Seed a demo condominium and run a sample message through the runtime (offline).

Run with: `python -m condominioos.scripts.seed_demo`. Demonstrates the end-to-end skeleton without
external infra: classify → concierge → knowledge → firewall → send/hold, fully audited.
"""

from __future__ import annotations

import asyncio
import uuid

from condominioos.agents import AgentState
from condominioos.audit import audit_log
from condominioos.common.telemetry import configure_telemetry
from condominioos.common.tenancy import TenantContext, tenant_scope
from condominioos.knowledge import InMemoryKnowledge
from condominioos.runtime import build_runtime


async def main() -> None:
    configure_telemetry("seed")
    tenant_id = uuid.uuid4()
    runtime = build_runtime(offline=True)

    # Seed a tiny per-tenant knowledge corpus so the concierge can ground its answer.
    knowledge: InMemoryKnowledge = runtime.specialists["concierge"].knowledge  # type: ignore[attr-defined]
    knowledge.seed(knowledge.collection_for(tenant_id), [
        {"text": "Gli orari del portiere sono dalle 8 alle 12 dal lunedì al venerdì.",
         "source": "doc:regolamento#art3", "doc_id": "regolamento"},
        {"text": "Il portiere riceve nello stabile al piano terra durante gli orari indicati.",
         "source": "doc:regolamento#art4", "doc_id": "regolamento"},
    ])

    ctx = TenantContext(condominium_id=tenant_id, actor="system", correlation_id=uuid.uuid4())
    with tenant_scope(ctx):
        state = AgentState(
            tenant_id=tenant_id,
            input_text="Buongiorno, quali sono gli orari del portiere?",
            context={"channel": "whatsapp", "unit_id": uuid.uuid4()},
        )
        result = await runtime.handle(state)

    print("\n=== Demo run ===")
    print(f"Intent       : {result.intent} ({result.confidence:.2f})")
    print(f"Escalated    : {result.escalate}")
    print("Trail        :")
    for step in result.trail:
        print(f"   - {step}")
    print(f"Audit chain  : {'VALID' if audit_log.verify() else 'TAMPERED'} "
          f"({len(audit_log._events)} events)")


if __name__ == "__main__":
    asyncio.run(main())
