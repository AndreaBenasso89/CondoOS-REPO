"""LangGraph orchestration blueprint (docs/13 §7).

Topology: orchestrator (classify+route) → specialist agent → [Risk → 🛡️ Firewall] gate → either
APPROVE (Notification) or HOLD/escalate (Human Escalation → review queue). Every outbound passes the
firewall; agents have no channel access.

The graph is expressed with LangGraph's StateGraph when available; a dependency-free fallback executor
runs the same node functions so the skeleton works without the package installed. The node functions
are identical in both paths — wiring LangGraph is a drop-in.
"""

from __future__ import annotations

from condominioos.agents import AgentState
from condominioos.agents.escalation import HumanEscalationAgent
from condominioos.common.telemetry import get_logger
from condominioos.firewall import ReputationFirewall, VerdictType
from condominioos.notification import NotificationEngine
from condominioos.review import ReviewItem, review_queue

log = get_logger("runtime.graph")


class AgentRuntime:
    """Builds and runs the orchestration graph for a single inbound task."""

    def __init__(
        self,
        *,
        orchestrator,
        specialists: dict[str, object],
        firewall: ReputationFirewall,
        notification: NotificationEngine,
        escalation: HumanEscalationAgent,
    ) -> None:
        self.orchestrator = orchestrator
        self.specialists = specialists
        self.firewall = firewall
        self.notification = notification
        self.escalation = escalation

    async def handle(self, state: AgentState) -> AgentState:
        """Run one task through classify → specialist → gate → send/hold."""
        # 1) Orchestrate (classify + route).
        state = await self.orchestrator.run(state)
        if state.escalate:
            return await self._escalate(state)

        # 2) Route to the specialist.
        route = state.context.get("route_to", "escalation")
        specialist = self.specialists.get(route)
        if specialist is None:
            return await self._escalate(state)
        state = await specialist.run(state)
        if state.escalate:
            return await self._escalate(state)

        # 3) Mandatory gate: firewall every draft; only APPROVE may be sent.
        for draft in state.drafts:
            verdict = self.firewall.evaluate(draft, agent=route, confidence=state.confidence or 0.8)
            if verdict.verdict == VerdictType.APPROVE:
                await self.notification.send(draft, verdict)
                state.trail.append(f"runtime: sent ({verdict.autonomy_tier})")
            elif verdict.verdict == VerdictType.BLOCK:
                state.trail.append("runtime: BLOCKED by firewall (incident)")
                await self._escalate(state, reason="firewall BLOCK")
            else:  # HOLD or REVISE → human review
                self._hold(state, draft, verdict)
        return state

    async def _escalate(self, state: AgentState, reason: str | None = None) -> AgentState:
        state.escalate = True
        if reason:
            state.escalation_reason = reason
        return await self.escalation.run(state)

    def _hold(self, state: AgentState, draft, verdict) -> None:
        review_queue.create(ReviewItem(
            tenant_id=state.tenant_id,
            kind=f"firewall_hold:{draft.kind}",
            priority="high" if verdict.autonomy_tier in ("A0", "A1") else "normal",
            payload={
                "draft": draft.model_dump(mode="json"),
                "verdict": verdict.model_dump(mode="json"),
                "trail": state.trail,
            },
        ))
        state.trail.append(f"runtime: held for review ({verdict.verdict}/{verdict.autonomy_tier})")
