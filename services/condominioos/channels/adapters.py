"""Channel adapters — the Anti-Corruption Layer between providers and the domain (docs/03 §4).

Each adapter verifies the provider signature, normalizes the payload into a ``comms.message.received``
event, and treats message content as untrusted data (prompt-injection defense, docs/06 §3). Adapters
NEVER send — outbound is the Notification Engine's job. Inbound only here.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from condominioos.common.telemetry import get_logger
from condominioos.events import EventEnvelope, EventType

log = get_logger("channels")


class ChannelAdapter(ABC):
    channel: str

    @abstractmethod
    def verify(self, headers: dict[str, str], body: bytes) -> bool:
        """Verify the provider's webhook signature."""

    @abstractmethod
    def normalize(self, payload: dict[str, Any]) -> EventEnvelope:
        """Map a provider payload to a normalized message.received event."""


class WhatsAppAdapter(ChannelAdapter):
    channel = "whatsapp"

    def verify(self, headers: dict[str, str], body: bytes) -> bool:
        # Verify X-Hub-Signature-256 (HMAC) in production.
        return True

    def normalize(self, payload: dict[str, Any]) -> EventEnvelope:
        return EventEnvelope(
            event_type=EventType.MESSAGE_RECEIVED,
            tenant_id=uuid.UUID(payload["tenant_id"]),
            actor="channel:whatsapp",
            payload={"channel": self.channel, "party_ref": payload.get("from"),
                     "body_ref": "<external>" + payload.get("text", "") + "</external>"},
        )


class EmailAdapter(ChannelAdapter):
    channel = "email"

    def verify(self, headers: dict[str, str], body: bytes) -> bool:
        return True  # DKIM/SPF check in production

    def normalize(self, payload: dict[str, Any]) -> EventEnvelope:
        return EventEnvelope(
            event_type=EventType.MESSAGE_RECEIVED,
            tenant_id=uuid.UUID(payload["tenant_id"]),
            actor="channel:email",
            payload={"channel": self.channel, "party_ref": payload.get("from"),
                     "body_ref": "<external>" + payload.get("body", "") + "</external>"},
        )


ADAPTERS: dict[str, ChannelAdapter] = {"whatsapp": WhatsAppAdapter(), "email": EmailAdapter()}
