"""Orchestrator Agent — intent classification + routing (docs/04 §1)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent
from condominioos.llm import LLMRouter

# Intent -> specialist agent name.
INTENT_ROUTING = {
    "info_request": "concierge",
    "maintenance": "maintenance",
    "payment": "accounting",
    "arrears": "collections",
    "assembly": "assembly",
    "document": "document",
    "complaint": "escalation",
    "legal": "escalation",
    "compliance": "compliance",
}
CONFIDENCE_FLOOR = 0.6


class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    bounded_context = "agent_orchestration"
    allowed_tools = ("classify_intent", "create_task", "check_budget")
    prompt_name = "orchestrator"
    default_autonomy = "A3"

    def __init__(self, tools, llm: LLMRouter) -> None:
        super().__init__(tools)
        self.llm = llm

    async def run(self, state: AgentState) -> AgentState:
        intent, confidence = await self._classify(state.input_text or "")
        state.intent, state.confidence = intent, confidence
        state.trail.append(f"orchestrator: intent={intent} conf={confidence:.2f}")
        if confidence < CONFIDENCE_FLOOR or intent == "unknown":
            return self._escalate(state, f"low-confidence intent ({confidence:.2f})")
        state.context["route_to"] = INTENT_ROUTING.get(intent, "escalation")
        return state

    async def _classify(self, text: str) -> tuple[str, float]:
        # Lightweight keyword pre-classifier; the LLM refines in production.
        t = text.lower()
        rules = {
            "maintenance": ("perdita", "guasto", "rotto", "ascensore", "riscaldamento"),
            "arrears": ("sollecito", "insoluto", "morosità", "non ho pagato"),
            "payment": ("pagamento", "bonifico", "ricevuta", "quota"),
            "assembly": ("assemblea", "convocazione", "delega", "verbale"),
            "document": ("documento", "regolamento", "polizza", "contratto"),
            "legal": ("avvocato", "diffida", "causa", "legale"),
            "complaint": ("reclamo", "vergogna", "inaccettabile"),
        }
        for intent, kws in rules.items():
            if any(k in t for k in kws):
                return intent, 0.88
        if t.strip():
            return "info_request", 0.82
        return "unknown", 0.0
