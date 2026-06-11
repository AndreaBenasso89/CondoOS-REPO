"""Human review queue — the human-in-the-loop control surface (Ops Console backend).

Firewall HOLD verdicts and agent escalations create review items here. A human decision is recorded
and fed back so the originating task can resume; the final text is re-validated by the firewall
before sending (docs/07 §6).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from condominioos.common.telemetry import get_logger

log = get_logger("review")


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class ReviewDecision(BaseModel):
    status: ReviewStatus
    reviewer: str
    edited_text: str | None = None
    note: str | None = None
    at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReviewItem(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    kind: str
    priority: str = "normal"
    payload: dict  # the draft + context + risk + citations the reviewer needs
    status: ReviewStatus = ReviewStatus.PENDING
    decision: ReviewDecision | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReviewQueue:
    """In-memory queue for the skeleton; persisted to `review_item` table in prod."""

    def __init__(self) -> None:
        self._items: dict[uuid.UUID, ReviewItem] = {}

    def create(self, item: ReviewItem) -> ReviewItem:
        self._items[item.id] = item
        log.info("review.created", item_id=str(item.id), kind=item.kind, priority=item.priority)
        return item

    def pending(self, tenant_id: uuid.UUID | None = None) -> list[ReviewItem]:
        return [i for i in self._items.values()
                if i.status == ReviewStatus.PENDING and (tenant_id is None or i.tenant_id == tenant_id)]

    def decide(self, item_id: uuid.UUID, decision: ReviewDecision) -> ReviewItem:
        item = self._items[item_id]
        item.status = decision.status
        item.decision = decision
        log.info("review.decided", item_id=str(item_id), status=decision.status,
                 reviewer=decision.reviewer)
        return item


review_queue = ReviewQueue()
