"""Assembly Agent — agenda, convocation, proxies, quorum, minutes (docs/04 §7)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent
from condominioos.firewall.contracts import ArtifactKind, OutboundArtifact

LEGAL_MIN_NOTICE_DAYS = 5


class AssemblyAgent(BaseAgent):
    name = "assembly"
    bounded_context = "governance"
    allowed_tools = ("agenda.assemble", "convocation.generate", "convocation.validate_legal",
                     "proxy.register", "quorum.compute", "minutes.draft", "task.spawn_followups")
    default_autonomy = "A1"  # AoR approves; signature is A0

    async def run(self, state: AgentState) -> AgentState:
        assembly_id = state.context.get("assembly_id")
        agenda = self.tools.call("agenda.assemble", assembly_id=assembly_id)
        convocation = self.tools.call("convocation.generate", assembly_id=assembly_id, agenda=agenda)
        legal = self.tools.call("convocation.validate_legal", convocation=convocation,
                                min_notice_days=LEGAL_MIN_NOTICE_DAYS)
        if not legal["valid"]:
            return self._escalate(state, f"convocation legally invalid: {legal['reason']}")
        artifact = OutboundArtifact(
            kind=ArtifactKind.CONVOCATION,
            channel=state.context.get("channel", "pec"),
            text=convocation["content"],
            intent="assembly",
        )
        self._draft(state, artifact)  # → firewall L5 → AoR approval (A1)
        state.trail.append("assembly: convocation drafted (awaiting AoR approval)")
        return state
