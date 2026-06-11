"""Composition root — wires the fleet, firewall, knowledge, and notification together.

This is where dependency injection happens. ``build_runtime`` returns a ready :class:`AgentRuntime`
with the firewall's guard context populated from domain resolvers (ledger, recipient, risk). In the
skeleton these resolvers are in-memory stubs; in prod they call the domain services.
"""

from __future__ import annotations

from condominioos.agents import (
    AccountingAgent,
    AssemblyAgent,
    CollectionsAgent,
    ComplianceAgent,
    ConciergeAgent,
    DocumentAgent,
    HumanEscalationAgent,
    KnowledgeAgent,
    MaintenanceAgent,
    OrchestratorAgent,
    RiskAgent,
    VendorAgent,
)
from condominioos.agents.tools import default_registry
from condominioos.firewall import GuardContext, ReputationFirewall
from condominioos.knowledge import InMemoryKnowledge
from condominioos.llm import LLMRouter
from condominioos.notification import NotificationEngine
from condominioos.runtime.graph import AgentRuntime
from condominioos.runtime.stub_tools import register_stub_tools


def build_runtime(*, offline: bool = True) -> AgentRuntime:
    llm = LLMRouter(offline=offline)
    knowledge = InMemoryKnowledge()
    register_stub_tools(default_registry)

    risk = RiskAgent(default_registry)

    # The firewall's risk scorer is the Risk Agent; ledger/recipient resolvers are stubs here.
    guard_ctx = GuardContext(
        risk_scorer=risk.score,
        ledger_balance_resolver=lambda r: 120.0,  # stub: reconciled balance
        recipient_unit_resolver=lambda r: r.unit_id,  # stub: recipient matches
        grounding_verifier=lambda claim, cites: bool(claim.source),
        last_reminder_days=lambda r: None,
    )
    firewall = ReputationFirewall(guard_ctx)
    notification = NotificationEngine()

    specialists = {
        "concierge": ConciergeAgent(default_registry, llm, knowledge),
        "maintenance": MaintenanceAgent(default_registry),
        "accounting": AccountingAgent(default_registry),
        "collections": CollectionsAgent(default_registry, llm),
        "vendor": VendorAgent(default_registry),
        "assembly": AssemblyAgent(default_registry),
        "compliance": ComplianceAgent(default_registry),
        "document": DocumentAgent(default_registry),
        "knowledge": KnowledgeAgent(default_registry, knowledge),
    }
    return AgentRuntime(
        orchestrator=OrchestratorAgent(default_registry, llm),
        specialists=specialists,
        firewall=firewall,
        notification=notification,
        escalation=HumanEscalationAgent(default_registry),
    )
