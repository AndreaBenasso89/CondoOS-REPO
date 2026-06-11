"""Risk Agent — cross-cutting risk scoring; can only RAISE tiers, never lower them (docs/04 §11)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent
from condominioos.firewall.contracts import OutboundArtifact

HIGH_RISK_INTENTS = {"legal", "arrears", "complaint"}
LARGE_AMOUNT_EUR = 2000


class RiskAgent(BaseAgent):
    """Used by the firewall (L7) as a scorer. Exposes :meth:`score` for direct use."""

    name = "risk"
    bounded_context = "platform"
    allowed_tools = ("risk.score_action", "policy.lookup", "history.lookup")
    default_autonomy = "A3"

    def score(self, artifact: OutboundArtifact) -> tuple[str, float]:
        score = 0.1
        if artifact.intent in HIGH_RISK_INTENTS:
            score += 0.4
        if artifact.financials and artifact.financials.amount >= LARGE_AMOUNT_EUR:
            score += 0.4
        if artifact.kind.value in {"legal_statement", "convocation"}:
            score += 0.3
        level = "high" if score >= 0.6 else "medium" if score >= 0.3 else "low"
        return level, min(score, 1.0)

    async def run(self, state: AgentState) -> AgentState:
        for draft in state.drafts:
            level, score = self.score(draft)
            state.trail.append(f"risk: {draft.kind}={level} ({score:.2f})")
        return state
