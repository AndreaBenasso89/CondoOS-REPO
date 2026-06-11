"""BaseAgent contract shared by the whole fleet (docs/04).

Every agent is a LangGraph node that takes the shared :class:`AgentState`, may call governed tools
scoped to its bounded context, and produces outputs. Agents NEVER send to a channel: any outbound is
emitted as an :class:`~condominioos.firewall.OutboundArtifact` for the firewall to gate.

Each run is recorded as an ``AgentRun`` (model, prompt_version, tools, io, cost) for reproducibility.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from condominioos.agents.tools import ToolRegistry
from condominioos.common.telemetry import get_logger
from condominioos.firewall.contracts import OutboundArtifact

log = get_logger("agents")


class AgentState(BaseModel):
    """Shared blackboard passed between graph nodes."""

    task_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    intent: str | None = None
    confidence: float = 0.0
    input_text: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    drafts: list[OutboundArtifact] = Field(default_factory=list)
    escalate: bool = False
    escalation_reason: str | None = None
    trail: list[str] = Field(default_factory=list)  # human-readable step log


class BaseAgent(ABC):
    """Common contract. Subclasses declare their bounded context, allowed tools, and prompt."""

    name: str
    bounded_context: str
    allowed_tools: tuple[str, ...] = ()
    prompt_name: str | None = None
    default_autonomy: str = "A1"

    def __init__(self, tools: ToolRegistry) -> None:
        # The runtime hands each agent a registry scoped to its allowed tools (default-deny).
        self.tools = tools.scoped(self.name, self.allowed_tools)

    @abstractmethod
    async def run(self, state: AgentState) -> AgentState:
        """Advance the task. Pure of side effects beyond governed tool calls + drafts."""

    # Helpers --------------------------------------------------------------
    def _draft(self, state: AgentState, artifact: OutboundArtifact) -> None:
        state.drafts.append(artifact)
        state.trail.append(f"{self.name}: drafted {artifact.kind}")

    def _escalate(self, state: AgentState, reason: str) -> AgentState:
        state.escalate = True
        state.escalation_reason = reason
        state.trail.append(f"{self.name}: escalate ({reason})")
        log.info("agent.escalate", agent=self.name, reason=reason)
        return state
