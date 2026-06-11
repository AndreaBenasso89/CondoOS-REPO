"""Notification Engine — the ONLY component allowed to emit to channels.

It refuses any artifact lacking a valid, signed, unexpired firewall verdict whose ``artifact_hash``
matches the exact payload (docs/07 §8). No agent has a channel client; this is the sole egress.
"""

from __future__ import annotations

from datetime import UTC, datetime

from condominioos.audit import audit_log
from condominioos.common.security import artifact_hash, verify_verdict
from condominioos.common.telemetry import get_logger
from condominioos.firewall.contracts import FirewallVerdict, OutboundArtifact, VerdictType

log = get_logger("notification")


class UnauthorizedSendError(RuntimeError):
    """Raised when a send is attempted without a valid APPROVE verdict."""


class ChannelClient:
    """Abstract channel sender. Concrete adapters (WhatsApp/Email/PEC/Web) implement `send`."""

    async def send(self, artifact: OutboundArtifact) -> str:  # returns provider message id
        raise NotImplementedError


class MockChannelClient(ChannelClient):
    async def send(self, artifact: OutboundArtifact) -> str:
        log.info("notification.sent", channel=artifact.channel, kind=artifact.kind)
        return "mock-message-id"


class NotificationEngine:
    def __init__(self, clients: dict[str, ChannelClient] | None = None) -> None:
        self._clients = clients or {}

    async def send(self, artifact: OutboundArtifact, verdict: FirewallVerdict) -> str:
        self._enforce(artifact, verdict)
        client = self._clients.get(artifact.channel or "", MockChannelClient())
        message_id = await client.send(artifact)
        audit_log.append(actor="system:notification", action="comms.message.sent",
                         entity_ref=verdict.artifact_hash,
                         payload={"channel": artifact.channel, "kind": artifact.kind.value,
                                  "message_id": message_id})
        return message_id

    # ---- the trust boundary ----------------------------------------------
    def _enforce(self, artifact: OutboundArtifact, verdict: FirewallVerdict) -> None:
        if verdict.verdict != VerdictType.APPROVE:
            raise UnauthorizedSendError(f"verdict is {verdict.verdict}, not APPROVE")
        if verdict.signature is None or verdict.expires_at is None:
            raise UnauthorizedSendError("verdict is not signed")
        # The verdict must be over THIS exact artifact.
        if artifact_hash(artifact.model_dump(mode="json")) != verdict.artifact_hash:
            raise UnauthorizedSendError("artifact hash mismatch — payload changed after approval")
        # Signature + expiry.
        if datetime.fromisoformat(verdict.expires_at) < datetime.now(UTC):
            raise UnauthorizedSendError("verdict expired")
        if not verify_verdict(verdict.artifact_hash, verdict.verdict.value, verdict.expires_at,
                              verdict.signature):
            raise UnauthorizedSendError("invalid verdict signature")
