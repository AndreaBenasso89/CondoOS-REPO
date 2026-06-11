"""Vendor Agent — sourcing, compliance (DURC/insurance), quotes, scheduling (docs/04 §6)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent

COST_THRESHOLD_EUR = 800


class VendorAgent(BaseAgent):
    name = "vendor"
    bounded_context = "maintenance_vendors"
    allowed_tools = ("vendor.search", "vendor.check_compliance", "quote.request",
                     "quote.compare", "schedule.book", "vendor.rate")
    default_autonomy = "A2"

    async def run(self, state: AgentState) -> AgentState:
        category = state.context.get("category", "generic")
        candidates = self.tools.call("vendor.search", category=category)
        chosen = candidates["top"]
        # Compliance gate — never dispatch a non-compliant/uninsured vendor.
        compliance = self.tools.call("vendor.check_compliance", vendor_id=chosen["id"])
        if not compliance["compliant"]:
            return self._escalate(state, f"no compliant vendor (DURC/insurance): {compliance['reason']}")
        quote = self.tools.call("quote.request", vendor_id=chosen["id"],
                                ticket_id=state.context.get("ticket_id"))
        if quote["amount"] > COST_THRESHOLD_EUR:
            return self._escalate(state, f"quote EUR {quote['amount']} > threshold — needs approval")
        booking = self.tools.call("schedule.book", vendor_id=chosen["id"], quote_id=quote["id"])
        state.context["work_order_id"] = booking["work_order_id"]
        state.trail.append(f"vendor: scheduled {chosen['id']} (EUR {quote['amount']})")
        return state
