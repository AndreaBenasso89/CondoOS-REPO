"""Firewall red-team + notification trust-boundary tests."""

from __future__ import annotations

import uuid

import pytest

from condominioos.evals import run_suite
from condominioos.firewall import (
    ArtifactKind,
    Financials,
    OutboundArtifact,
    Recipient,
    ReputationFirewall,
    VerdictType,
)
from condominioos.firewall.layers import GuardContext
from condominioos.notification import NotificationEngine, UnauthorizedSendError


def test_red_team_suite_all_pass():
    passed, total, failures = run_suite()
    assert not failures, failures
    assert passed == total


def test_over_collection_is_blocked():
    unit = uuid.uuid4()
    ctx = GuardContext(ledger_balance_resolver=lambda r: 120.0,
                       recipient_unit_resolver=lambda r: r.unit_id)
    fw = ReputationFirewall(ctx)
    artifact = OutboundArtifact(
        kind=ArtifactKind.REMINDER, channel="email",
        recipient=Recipient(type="owner", unit_id=unit),
        text="Sollecito.", financials=Financials(amount=999.0, ledger_balance=120.0))
    verdict = fw.evaluate(artifact, agent="collections", confidence=0.95)
    assert verdict.verdict == VerdictType.BLOCK


async def test_notification_refuses_unsigned_verdict():
    unit = uuid.uuid4()
    ctx = GuardContext(grounding_verifier=lambda c, cites: True)
    fw = ReputationFirewall(ctx)
    artifact = OutboundArtifact(kind=ArtifactKind.MESSAGE, channel="whatsapp",
                                recipient=Recipient(type="resident", unit_id=unit), text="Ciao")
    verdict = fw.evaluate(artifact, agent="concierge", confidence=0.9)
    verdict.signature = None  # tamper: strip the signature
    with pytest.raises(UnauthorizedSendError):
        await NotificationEngine().send(artifact, verdict)


async def test_notification_refuses_payload_tampering():
    unit = uuid.uuid4()
    fw = ReputationFirewall(GuardContext())
    artifact = OutboundArtifact(kind=ArtifactKind.MESSAGE, channel="whatsapp",
                                recipient=Recipient(type="resident", unit_id=unit), text="Ciao")
    verdict = fw.evaluate(artifact, agent="concierge", confidence=0.9)
    if verdict.verdict == VerdictType.APPROVE:
        artifact.text = "Tampered after approval"
        with pytest.raises(UnauthorizedSendError):
            await NotificationEngine().send(artifact, verdict)
