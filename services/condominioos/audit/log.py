"""Hash-chained, append-only audit log (docs/05 §4).

Every state-changing action and every firewall verdict is recorded as an immutable, tamper-evident
event: ``hash_n = SHA256(prev_hash || canonical_json(payload_n))``. The audit DB role has INSERT
only. This module provides the append + verify primitives; the persistence is abstracted so the
skeleton runs in-memory and prod uses the separate audit database.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from condominioos.common.security import canonical_json
from condominioos.common.telemetry import get_logger

log = get_logger("audit")

_GENESIS = "0" * 64


class AuditEvent(BaseModel):
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor: str
    action: str
    entity_ref: str
    tenant_id: str | None = None
    prev_hash: str
    hash: str
    payload: dict


class AuditLog:
    """Append-only log. Replace the in-memory list with the audit DB in prod (INSERT-only role)."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    @property
    def _last_hash(self) -> str:
        return self._events[-1].hash if self._events else _GENESIS

    def append(self, *, actor: str, action: str, entity_ref: str, payload: dict,
               tenant_id: str | None = None) -> AuditEvent:
        prev = self._last_hash
        body = canonical_json({"actor": actor, "action": action, "entity_ref": entity_ref,
                               "payload": payload, "tenant_id": tenant_id})
        digest = hashlib.sha256((prev + body).encode("utf-8")).hexdigest()
        event = AuditEvent(actor=actor, action=action, entity_ref=entity_ref, payload=payload,
                           tenant_id=tenant_id, prev_hash=prev, hash=digest)
        self._events.append(event)
        log.info("audit.appended", action=action, entity_ref=entity_ref, hash=digest[:12])
        return event

    def verify(self) -> bool:
        """Recompute the chain; returns False if any link was tampered with."""
        prev = _GENESIS
        for e in self._events:
            body = canonical_json({"actor": e.actor, "action": e.action, "entity_ref": e.entity_ref,
                                   "payload": e.payload, "tenant_id": e.tenant_id})
            if e.prev_hash != prev:
                return False
            if e.hash != hashlib.sha256((prev + body).encode("utf-8")).hexdigest():
                return False
            prev = e.hash
        return True


audit_log = AuditLog()
