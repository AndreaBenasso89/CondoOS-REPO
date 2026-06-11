"""Collections Agent — graduated, provably-owed, compliant reminders (docs/04 §5).

The hard rule: NO reminder is drafted before reconciliation confirms the exact balance and the
correct debtor. The firewall's L4 enforces it again as defense-in-depth.
"""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent
from condominioos.firewall.contracts import (
    ArtifactKind,
    Financials,
    OutboundArtifact,
    Recipient,
)
from condominioos.llm import LLMRouter, TaskClass, prompt_registry


class CollectionsAgent(BaseAgent):
    name = "collections"
    bounded_context = "financial"
    allowed_tools = ("ledger.get_arrears", "reconcile.confirm", "debtor.resolve",
                     "collections.get_policy", "payment_plan.propose", "handoff_to_human")
    prompt_name = "collections"
    default_autonomy = "A1"

    def __init__(self, tools, llm: LLMRouter) -> None:
        super().__init__(tools)
        self.llm = llm

    async def run(self, state: AgentState) -> AgentState:
        unit_id = state.context.get("unit_id")
        # 1) Reconcile FIRST — never act on an unreconciled balance.
        reconciliation = self.tools.call("reconcile.confirm", unit_id=unit_id)
        if not reconciliation["confirmed"]:
            return self._escalate(state, "reconciliation mismatch — blocked from any reminder")

        balance = reconciliation["balance"]
        debtor = self.tools.call("debtor.resolve", unit_id=unit_id,
                                 expense_kind=state.context.get("expense_kind", "ordinary"))
        tier = self.tools.call("collections.get_policy", unit_id=unit_id)["tier"]
        if tier in ("T2", "T3"):
            return self._escalate(state, f"tier {tier} is human-led")

        prompt = prompt_registry.get(self.prompt_name)
        body = await self.llm.complete(
            system=prompt.system,
            prompt=f"Draft a kind T1 reminder. Amount owed (reconciled): EUR {balance:.2f}. "
                   f"Debtor: {debtor['name']}.",
            task=TaskClass.REASONING,
        )
        artifact = OutboundArtifact(
            kind=ArtifactKind.REMINDER,
            channel=state.context.get("channel", "email"),
            recipient=Recipient(type=debtor["type"], id=debtor["id"], unit_id=unit_id),
            text=body.text,
            intent="arrears",
            financials=Financials(amount=balance, ledger_balance=balance,
                                  debtor_kind=debtor["type"]),
        )
        self._draft(state, artifact)
        return state
