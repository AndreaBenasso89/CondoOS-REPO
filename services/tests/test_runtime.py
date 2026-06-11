"""End-to-end runtime tests: classify → specialist → firewall → send/hold, plus audit integrity."""

from __future__ import annotations

import uuid

from condominioos.agents import AgentState
from condominioos.audit import audit_log
from condominioos.common.tenancy import TenantContext, tenant_scope
from condominioos.knowledge import InMemoryKnowledge
from condominioos.runtime import build_runtime


async def test_grounded_question_is_answered_and_audited():
    tenant = uuid.uuid4()
    runtime = build_runtime(offline=True)
    knowledge: InMemoryKnowledge = runtime.specialists["concierge"].knowledge  # type: ignore
    knowledge.seed(knowledge.collection_for(tenant), [
        {"text": "Gli orari del portiere sono 8-12.", "source": "doc:reg#art3", "doc_id": "reg"},
    ])
    with tenant_scope(TenantContext(condominium_id=tenant, actor="system")):
        state = AgentState(tenant_id=tenant, input_text="orari del portiere?",
                           context={"channel": "whatsapp", "unit_id": uuid.uuid4()})
        result = await runtime.handle(state)
    assert result.intent == "info_request"
    assert audit_log.verify()


async def test_legal_intent_escalates_to_human():
    tenant = uuid.uuid4()
    runtime = build_runtime(offline=True)
    with tenant_scope(TenantContext(condominium_id=tenant, actor="system")):
        state = AgentState(tenant_id=tenant,
                           input_text="Voglio mandare una diffida legale all'amministratore",
                           context={"channel": "email"})
        result = await runtime.handle(state)
    assert result.escalate is True
