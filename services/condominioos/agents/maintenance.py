"""Maintenance Agent — triage → work order → SLA (docs/04 §3)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent

SAFETY_KEYWORDS = ("gas", "fumo", "incendio", "crollo", "scossa", "allagamento grave")


class MaintenanceAgent(BaseAgent):
    name = "maintenance"
    bounded_context = "maintenance"
    allowed_tools = ("ticket.create", "ticket.update", "ticket.search_duplicates",
                     "vendor.request_dispatch", "budget.check_coverage", "sla.start_timer")
    default_autonomy = "A2"

    async def run(self, state: AgentState) -> AgentState:
        text = (state.input_text or "").lower()
        severity = "emergency" if any(k in text for k in SAFETY_KEYWORDS) else "high"
        dupes = self.tools.call("ticket.search_duplicates", text=text)
        if dupes.get("found"):
            state.trail.append("maintenance: duplicate ticket — linked")
            return state
        ticket = self.tools.call("ticket.create", description=state.input_text, severity=severity)
        self.tools.call("sla.start_timer", ticket_id=ticket["id"], severity=severity)
        if severity == "emergency":
            # Life-safety: dispatch on-call AND require human notification (A0).
            self.tools.call("vendor.request_dispatch", ticket_id=ticket["id"], emergency=True)
            return self._escalate(state, "life-safety emergency — human notified, on-call dispatched")
        self.tools.call("vendor.request_dispatch", ticket_id=ticket["id"], emergency=False)
        state.context["ticket_id"] = ticket["id"]
        state.trail.append(f"maintenance: ticket {ticket['id']} severity={severity}")
        return state
