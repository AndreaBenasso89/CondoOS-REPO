"""Event catalog — typed envelope + event-type registry. See docs/14.

Events are immutable facts named ``context.entity.verb``. Every event shares the :class:`EventEnvelope`
and is published on a tenant-scoped subject ``condo.{tenant_id}.{event_type}``.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class EventType(StrEnum):
    # Communications
    MESSAGE_RECEIVED = "comms.message.received"
    OUTBOUND_DRAFTED = "comms.outbound.drafted"
    MESSAGE_SENT = "comms.message.sent"
    REMINDER_DRAFTED = "comms.reminder.drafted"
    # Orchestration
    TASK_CREATED = "orchestration.task.created"
    TASK_ROUTED = "orchestration.task.routed"
    TASK_COMPLETED = "orchestration.task.completed"
    TASK_FAILED = "orchestration.task.failed"
    # Documents
    DOCUMENT_UPLOADED = "doc.document.uploaded"
    DOCUMENT_CLASSIFIED = "doc.document.classified"
    KNOWLEDGE_INDEXED = "doc.knowledge.indexed"
    # Accounting
    INVOICE_POSTED = "acc.invoice.posted"
    PAYMENT_MATCHED = "acc.payment.matched"
    RECONCILIATION_COMPLETED = "acc.reconciliation.completed"
    CHARGE_OVERDUE_DETECTED = "acc.charge.overdue_detected"
    ARREARS_CONFIRMED = "acc.arrears.confirmed"
    # Maintenance / vendors
    TICKET_REQUESTED = "mnt.ticket.requested"
    TICKET_TRIAGED = "mnt.ticket.triaged"
    VENDOR_SCHEDULED = "ven.workorder.scheduled"
    # Governance
    CONVOCATION_ISSUED = "gov.convocation.issued"
    MINUTES_SIGNED = "gov.minutes.signed"
    # Compliance
    COMPLIANCE_ALERT_RAISED = "cmp.compliance.alert_raised"
    # Firewall / review / risk / qa
    FIREWALL_VERDICT_ISSUED = "firewall.verdict.issued"
    FIREWALL_ACTION_BLOCKED = "firewall.action.blocked"
    REVIEW_ITEM_CREATED = "review.item.created"
    REVIEW_DECISION_RECORDED = "review.decision.recorded"
    RISK_SCORED = "risk.scored"
    QA_SCORECARD_PUBLISHED = "qa.scorecard.published"
    # Platform
    AUDIT_EVENT_APPENDED = "platform.audit.event_appended"
    TENANT_PROVISIONED = "platform.tenant.provisioned"


class EventEnvelope(BaseModel):
    """The shared envelope wrapping every domain event."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: EventType
    version: int = 1
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tenant_id: uuid.UUID
    correlation_id: uuid.UUID | None = None
    causation_id: uuid.UUID | None = None
    actor: str = "system"
    trace_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

    def subject(self) -> str:
        return f"condo.{self.tenant_id}.{self.event_type}"
