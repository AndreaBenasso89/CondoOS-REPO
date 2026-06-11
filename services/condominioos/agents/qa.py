"""QA Agent — rubric/reference evaluation and release gating (docs/04 §12)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent


class QAAgent(BaseAgent):
    name = "qa"
    bounded_context = "platform"
    allowed_tools = ("eval.run_rubric", "eval.judge", "eval.compare_versions",
                     "scorecard.publish", "release.gate")
    default_autonomy = "A3"  # may BLOCK a release; humans approve overrides

    async def run(self, state: AgentState) -> AgentState:
        # In production this samples real outputs; here it scores the drafts on a simple rubric.
        for draft in state.drafts:
            grounded = bool(draft.citations) or not draft.claims
            polite = len(draft.text) > 0
            state.context.setdefault("qa", []).append(
                {"kind": draft.kind, "grounded": grounded, "polite": polite}
            )
        state.trail.append("qa: scored drafts")
        return state
