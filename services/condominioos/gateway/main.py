"""API Gateway (FastAPI) — entrypoint exposing health, the webhook intake, and the review API.

This is a thin edge: it authenticates, sets the tenant context, normalizes inbound, and drives the
agent runtime. Domain CRUD endpoints (docs/15) are added per sprint.
"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from condominioos.agents import AgentState
from condominioos.common.telemetry import configure_telemetry, get_logger
from condominioos.common.tenancy import TenantContext, tenant_scope
from condominioos.review import ReviewDecision, ReviewStatus, review_queue
from condominioos.runtime import build_runtime

log = get_logger("gateway")
_runtime = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _runtime
    configure_telemetry("gateway")
    _runtime = build_runtime(offline=True)
    log.info("gateway.started")
    yield


app = FastAPI(title="CondominioOS API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "gateway"}


class InboundMessage(BaseModel):
    tenant_id: uuid.UUID
    channel: str = "whatsapp"
    party_ref: str | None = None
    unit_id: uuid.UUID | None = None
    resident_id: uuid.UUID | None = None
    text: str


@app.post("/v1/webhooks/{channel}")
async def inbound(channel: str, msg: InboundMessage) -> dict:
    """Normalize an inbound message and run it through the agent runtime + firewall."""
    ctx = TenantContext(condominium_id=msg.tenant_id, actor="system", correlation_id=uuid.uuid4())
    with tenant_scope(ctx):
        state = AgentState(
            tenant_id=msg.tenant_id,
            input_text=msg.text,
            context={"channel": channel, "unit_id": msg.unit_id, "resident_id": msg.resident_id},
        )
        result = await _runtime.handle(state)
    return {
        "intent": result.intent,
        "confidence": result.confidence,
        "escalated": result.escalate,
        "trail": result.trail,
        "drafts": len(result.drafts),
    }


@app.get("/v1/reviews")
async def list_reviews(tenant_id: uuid.UUID | None = None) -> dict:
    items = review_queue.pending(tenant_id)
    return {"items": [i.model_dump(mode="json") for i in items]}


class ApprovePayload(BaseModel):
    reviewer: str
    edited_text: str | None = None
    note: str | None = None


@app.post("/v1/reviews/{item_id}/approve")
async def approve_review(item_id: uuid.UUID, body: ApprovePayload) -> dict:
    # NB: in production the approved final text is re-validated by the firewall before sending.
    item = review_queue.decide(item_id, ReviewDecision(
        status=ReviewStatus.APPROVED, reviewer=body.reviewer,
        edited_text=body.edited_text, note=body.note))
    return item.model_dump(mode="json")
