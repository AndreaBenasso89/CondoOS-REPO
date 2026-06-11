"""Compliance Agent — expiry/deadline monitoring & missing-document detection (docs/04 §8)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent


class ComplianceAgent(BaseAgent):
    name = "compliance"
    bounded_context = "compliance"
    allowed_tools = ("obligation.list", "deadline.compute", "document.check_present",
                     "alert.raise", "task.create", "regulation.lookup")
    default_autonomy = "A3"  # detection/alerting; remediation actions with cost are A1

    async def run(self, state: AgentState) -> AgentState:
        obligations = self.tools.call("obligation.list", tenant_id=str(state.tenant_id))
        raised = 0
        for ob in obligations["items"]:
            due = self.tools.call("deadline.compute", obligation=ob)
            if due["within_lead_time"]:
                self.tools.call("alert.raise", obligation_id=ob["id"], severity=due["severity"])
                self.tools.call("task.create", kind="remediation", obligation_id=ob["id"])
                raised += 1
        state.trail.append(f"compliance: raised {raised} alert(s)")
        return state
