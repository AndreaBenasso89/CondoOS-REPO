"""Reputation Firewall contracts: the artifacts that go in and the verdicts that come out.

See docs/07. No outbound communication, financial action, or legal statement may leave the platform
without an ``APPROVE`` verdict from the pipeline over the exact artifact.
"""

from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ArtifactKind(StrEnum):
    MESSAGE = "message"
    REMINDER = "reminder"
    CONVOCATION = "convocation"
    FINANCIAL_ACTION = "financial_action"
    VENDOR_MESSAGE = "vendor_message"
    LEGAL_STATEMENT = "legal_statement"


class Recipient(BaseModel):
    type: Literal["resident", "owner", "vendor", "admin"]
    id: uuid.UUID | None = None
    unit_id: uuid.UUID | None = None
    channel_address: str | None = None  # phone/email — PII, never logged in plain


class Claim(BaseModel):
    """A factual assertion the artifact makes, with its grounding source (for L2)."""

    text: str
    source: str | None = None  # e.g. "assembly:<uuid>", "doc:<uuid>#art.1130"


class Citation(BaseModel):
    doc_id: str
    span: str | None = None


class Financials(BaseModel):
    amount: float
    currency: str = "EUR"
    iban: str | None = None
    ledger_balance: float | None = None  # what the ledger says is owed (for L4 reconciliation)
    debtor_kind: Literal["owner", "tenant"] | None = None


class OutboundArtifact(BaseModel):
    kind: ArtifactKind
    channel: Literal["whatsapp", "email", "pec", "web"] | None = None
    recipient: Recipient | None = None
    text: str = ""
    claims: list[Claim] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    financials: Financials | None = None
    intent: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VerdictType(StrEnum):
    APPROVE = "APPROVE"
    REVISE = "REVISE"
    HOLD = "HOLD"
    BLOCK = "BLOCK"


class AutonomyTier(StrEnum):
    A3 = "A3"  # auto
    A2 = "A2"  # auto + notify
    A1 = "A1"  # propose / 1-click approve
    A0 = "A0"  # human-led


class LayerResult(BaseModel):
    layer: str
    passed: bool
    score: float | None = None  # 0..1 where applicable
    verdict_hint: VerdictType | None = None  # strongest action this layer demands
    reasons: list[str] = Field(default_factory=list)
    fixes: list[str] = Field(default_factory=list)  # suggested auto-revisions


class FirewallVerdict(BaseModel):
    verdict_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    verdict: VerdictType
    artifact_hash: str
    signature: str | None = None
    expires_at: str | None = None
    confidence: float | None = None
    autonomy_tier: AutonomyTier | None = None
    layer_results: list[LayerResult] = Field(default_factory=list)
    revisions: list[str] = Field(default_factory=list)
