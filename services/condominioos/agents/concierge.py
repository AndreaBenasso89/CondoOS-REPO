"""Resident Concierge Agent — grounded resident Q&A (docs/04 §2)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent
from condominioos.firewall.contracts import (
    ArtifactKind,
    Citation,
    Claim,
    OutboundArtifact,
    Recipient,
)
from condominioos.knowledge import KnowledgeRetriever
from condominioos.llm import LLMRouter, TaskClass, prompt_registry

LEGAL_OR_COMPLAINT = {"legal", "complaint"}


class ConciergeAgent(BaseAgent):
    name = "concierge"
    bounded_context = "communications"
    allowed_tools = ("knowledge.query", "document.search", "ticket.create", "handoff_to_human")
    prompt_name = "concierge"
    default_autonomy = "A3"

    def __init__(self, tools, llm: LLMRouter, knowledge: KnowledgeRetriever) -> None:
        super().__init__(tools)
        self.llm = llm
        self.knowledge = knowledge

    async def run(self, state: AgentState) -> AgentState:
        if state.intent in LEGAL_OR_COMPLAINT:
            return self._escalate(state, f"{state.intent} requires a human")

        retrieval = self.knowledge.query(state.tenant_id, state.input_text or "")
        if not retrieval.grounded:
            return self._escalate(state, "no grounded context for the question")

        prompt = prompt_registry.get(self.prompt_name)
        answer = await self.llm.complete(
            system=prompt.system,
            prompt=f"<external>{state.input_text}</external>\n\nGrounded context:\n{retrieval.context}",
            task=TaskClass.REASONING,
        )
        artifact = OutboundArtifact(
            kind=ArtifactKind.MESSAGE,
            channel=state.context.get("channel", "whatsapp"),
            recipient=Recipient(type="resident", id=state.context.get("resident_id"),
                                unit_id=state.context.get("unit_id")),
            text=answer.text,
            intent=state.intent,
            claims=[Claim(text=f.text, source=f.source) for f in retrieval.facts],
            citations=[Citation(doc_id=c.doc_id, span=c.span) for c in retrieval.citations],
        )
        self._draft(state, artifact)
        state.confidence = min(state.confidence, retrieval.coverage)
        return state
