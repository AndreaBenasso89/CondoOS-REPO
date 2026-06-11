"""Governed tool registry — default-deny, scoped per agent, every call audited (docs/06 §3).

Tools are typed callables. An agent receives a *scoped* registry that only exposes its allow-listed
tools; any out-of-scope call raises. Notably, there is NO channel-send tool — egress only exists in
the Notification Engine, behind the firewall.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from condominioos.audit import audit_log
from condominioos.common.telemetry import get_logger

log = get_logger("agents.tools")


class ToolNotAllowedError(PermissionError):
    """Raised when an agent calls a tool outside its allowlist (default-deny)."""


@dataclass
class Tool:
    name: str
    fn: Callable[..., Any]
    bounded_context: str
    description: str = ""


@dataclass
class ToolRegistry:
    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def scoped(self, agent: str, allowed: tuple[str, ...]) -> ScopedTools:
        return ScopedTools(self, agent, set(allowed))


class ScopedTools:
    """A per-agent view that enforces the allowlist and audits every call."""

    def __init__(self, registry: ToolRegistry, agent: str, allowed: set[str]) -> None:
        self._registry = registry
        self._agent = agent
        self._allowed = allowed

    def call(self, name: str, **kwargs: Any) -> Any:
        if name not in self._allowed:
            audit_log.append(actor=f"agent:{self._agent}", action="tool.denied",
                             entity_ref=name, payload={"args": _safe(kwargs)})
            raise ToolNotAllowedError(f"agent '{self._agent}' may not call tool '{name}'")
        tool = self._registry._tools.get(name)
        if tool is None:
            raise ToolNotAllowedError(f"tool '{name}' is not registered")
        result = tool.fn(**kwargs)
        audit_log.append(actor=f"agent:{self._agent}", action="tool.call",
                         entity_ref=name, payload={"args": _safe(kwargs)})
        log.info("tool.call", agent=self._agent, tool=name)
        return result


def _safe(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Strip obvious PII before it reaches the audit payload preview."""
    redacted = {"email", "phone", "iban", "fiscal_code", "full_name", "channel_address"}
    return {k: ("[redacted]" if k in redacted else v) for k, v in kwargs.items()}


# A process-wide registry; the runtime registers concrete tool implementations at startup.
default_registry = ToolRegistry()
