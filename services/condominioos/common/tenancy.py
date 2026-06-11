"""Tenant context propagation.

Multi-tenancy is non-negotiable: every request and every agent run carries a tenant context.
DB sessions set ``app.current_tenant`` so PostgreSQL Row-Level Security policies apply (see
db/schema.sql). No data access is permitted without an active tenant context.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID

_current: ContextVar[TenantContext | None] = ContextVar("tenant_context", default=None)


@dataclass(frozen=True)
class TenantContext:
    """The authenticated tenant + actor for the current unit of work."""

    condominium_id: UUID
    actor: str  # e.g. "agent:concierge", "human:<user_id>", "system"
    correlation_id: UUID | None = None
    trace_id: str | None = None


class MissingTenantContextError(RuntimeError):
    """Raised when tenant-scoped work is attempted without a tenant context set."""


def current_tenant() -> TenantContext:
    ctx = _current.get()
    if ctx is None:
        raise MissingTenantContextError(
            "No tenant context. Wrap tenant-scoped work in `with tenant_scope(ctx): ...`"
        )
    return ctx


@contextmanager
def tenant_scope(ctx: TenantContext) -> Iterator[TenantContext]:
    """Bind a tenant context for the duration of the block (sync + async safe via ContextVar)."""
    token = _current.set(ctx)
    try:
        yield ctx
    finally:
        _current.reset(token)
