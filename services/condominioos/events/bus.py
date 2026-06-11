"""Event bus client (NATS JetStream) with an in-memory fallback for local dev/tests.

Producers publish with the outbox pattern (write event in the same DB tx, then relay). Consumers are
idempotent on ``event_id``. The in-memory bus lets the skeleton run end-to-end without infra.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable

from condominioos.common.telemetry import get_logger
from condominioos.events.catalog import EventEnvelope, EventType

log = get_logger("events.bus")
Handler = Callable[[EventEnvelope], Awaitable[None]]


class InMemoryBus:
    """A trivial pub/sub used in dev/tests. Swap for NatsBus in staging/prod."""

    def __init__(self) -> None:
        self._subscribers: dict[EventType, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        self._subscribers[event_type].append(handler)

    async def publish(self, event: EventEnvelope) -> None:
        log.info("event.published", event_type=event.event_type, tenant=str(event.tenant_id))
        handlers = self._subscribers.get(event.event_type, [])
        await asyncio.gather(*(h(event) for h in handlers))


# Process-wide bus instance (replaced by a real NATS client via dependency injection in prod).
bus = InMemoryBus()
