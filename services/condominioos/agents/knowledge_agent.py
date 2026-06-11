"""Knowledge Agent — grounded retrieval backbone; refuses when ungrounded (docs/04 §10).

Thin agent wrapper over the tenant-scoped RAG retriever. Its job is to return grounded, cited facts
or an honest miss — it never improvises.
"""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent
from condominioos.knowledge import KnowledgeRetriever


class KnowledgeAgent(BaseAgent):
    name = "knowledge"
    bounded_context = "documents_knowledge"
    allowed_tools = ("vector.search", "keyword.search", "rerank", "legal_corpus.search")
    default_autonomy = "A3"

    def __init__(self, tools, retriever: KnowledgeRetriever) -> None:
        super().__init__(tools)
        self.retriever = retriever

    async def run(self, state: AgentState) -> AgentState:
        result = self.retriever.query(state.tenant_id, state.input_text or "")
        state.context["retrieval"] = result.model_dump()
        if not result.grounded:
            state.trail.append("knowledge: miss (no coverage)")
        else:
            state.confidence = result.coverage
            state.trail.append(f"knowledge: coverage={result.coverage:.2f}")
        return state
