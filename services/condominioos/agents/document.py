"""Document Agent — ingest → OCR → classify → PII tag → index (docs/04 §9)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent

CLASSIFY_CONFIDENCE_FLOOR = 0.75
SENSITIVE_TYPES = {"dispute", "medical", "legal_correspondence"}


class DocumentAgent(BaseAgent):
    name = "document"
    bounded_context = "documents_knowledge"
    allowed_tools = ("ocr.run", "doc.classify", "metadata.extract", "pii.detect",
                     "pii.redact", "vector.index", "doc.version", "doc.link_entity")
    default_autonomy = "A3"

    async def run(self, state: AgentState) -> AgentState:
        storage_key = state.context["storage_key"]
        text = self.tools.call("ocr.run", storage_key=storage_key)["text"]
        classification = self.tools.call("doc.classify", text=text)
        self.tools.call("pii.detect", text=text)  # tags PII for minimization downstream
        if (classification["confidence"] < CLASSIFY_CONFIDENCE_FLOOR
                or classification["type"] in SENSITIVE_TYPES):
            return self._escalate(state, "low-confidence/sensitive document — human label")
        self.tools.call("vector.index", storage_key=storage_key, text=text,
                        tenant_id=str(state.tenant_id))  # tenant-scoped namespace
        state.context["doc_type"] = classification["type"]
        state.trail.append(f"document: classified={classification['type']} indexed")
        return state
