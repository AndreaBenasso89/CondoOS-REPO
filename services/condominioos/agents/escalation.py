"""Human Escalation Agent — packages context, routes to the right human (docs/04 §13)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent
from condominioos.review import ReviewItem, review_queue


class HumanEscalationAgent(BaseAgent):
    name = "escalation"
    bounded_context = "platform"
    allowed_tools = ("review.create", "reviewer.route", "context.package", "sla.track")
    default_autonomy = "A3"  # routes; the human decides

    async def run(self, state: AgentState) -> AgentState:
        priority = "high" if state.intent in {"legal", "complaint"} else "normal"
        item = ReviewItem(
            tenant_id=state.tenant_id,
            kind=f"escalation:{state.intent or 'unknown'}",
            priority=priority,
            payload={
                "reason": state.escalation_reason,
                "input": state.input_text,
                "trail": state.trail,
                "drafts": [d.model_dump(mode="json") for d in state.drafts],
            },
        )
        review_queue.create(item)
        state.context["review_item_id"] = str(item.id)
        state.trail.append(f"escalation: created review {item.id} (priority={priority})")
        return state
