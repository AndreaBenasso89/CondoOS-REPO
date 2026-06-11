"""SQLAlchemy 2.0 ORM models (subset) mirroring db/schema.sql.

Only the aggregates exercised by the MVP skeleton are mapped here; the full schema is in schema.sql
and grows table-by-table with the sprint plan (docs/08).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def _pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class Condominium(Base):
    __tablename__ = "condominium"
    id: Mapped[uuid.UUID] = _pk()
    name: Mapped[str] = mapped_column(Text)
    fiscal_code: Mapped[str | None] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(Text)
    units_count: Mapped[int] = mapped_column(default=0)
    plan: Mapped[str] = mapped_column(String, default="managed_core")
    autonomy_mode: Mapped[str] = mapped_column(String, default="supervised")
    status: Mapped[str] = mapped_column(String, default="active")


class Unit(Base):
    __tablename__ = "unit"
    id: Mapped[uuid.UUID] = _pk()
    condominium_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("condominium.id"))
    identifier: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String, default="apartment")
    floor: Mapped[str | None] = mapped_column(String)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    resident_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class Charge(Base):
    __tablename__ = "charge"
    id: Mapped[uuid.UUID] = _pk()
    condominium_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("condominium.id"))
    unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("unit.id"))
    period: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String, default="ordinary")
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    due_date: Mapped[date | None] = mapped_column()
    status: Mapped[str] = mapped_column(String, default="open")


class Ticket(Base):
    __tablename__ = "ticket"
    id: Mapped[uuid.UUID] = _pk()
    condominium_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("condominium.id"))
    reporter_ref: Mapped[str | None] = mapped_column(String)
    category: Mapped[str | None] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String, default="medium")
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="open")
    sla_due: Mapped[datetime | None] = mapped_column()


class Document(Base):
    __tablename__ = "document"
    id: Mapped[uuid.UUID] = _pk()
    condominium_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("condominium.id"))
    type: Mapped[str | None] = mapped_column(String)
    title: Mapped[str | None] = mapped_column(Text)
    storage_key: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(default=1)
    expiry_date: Mapped[date | None] = mapped_column()


class FirewallVerdict(Base):
    __tablename__ = "firewall_verdict"
    id: Mapped[uuid.UUID] = _pk()
    condominium_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("condominium.id"))
    artifact_hash: Mapped[str] = mapped_column(Text)
    verdict: Mapped[str] = mapped_column(String)
    layer_scores: Mapped[dict] = mapped_column(JSONB, default=dict)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3))
    autonomy_tier: Mapped[str | None] = mapped_column(String)
    signature: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column()


class ReviewItem(Base):
    __tablename__ = "review_item"
    id: Mapped[uuid.UUID] = _pk()
    condominium_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("condominium.id"))
    kind: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String, default="normal")
    payload: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String, default="pending")
    decision: Mapped[dict | None] = mapped_column(JSONB)


class AgentRun(Base):
    __tablename__ = "agent_run"
    id: Mapped[uuid.UUID] = _pk()
    condominium_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("condominium.id"))
    agent: Mapped[str] = mapped_column(String)
    task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    model: Mapped[str | None] = mapped_column(String)
    prompt_version: Mapped[str | None] = mapped_column(String)
    inputs: Mapped[dict | None] = mapped_column(JSONB)
    outputs: Mapped[dict | None] = mapped_column(JSONB)
    tokens: Mapped[int | None] = mapped_column()
    cost: Mapped[float | None] = mapped_column(Numeric(10, 4))
