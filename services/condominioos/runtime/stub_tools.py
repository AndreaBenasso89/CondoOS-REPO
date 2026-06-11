"""In-memory stub tool implementations so the skeleton runs end-to-end.

Each is replaced by a real call to the owning domain service, sprint by sprint (docs/08). The names
here match the ``allowed_tools`` declared on each agent.
"""

from __future__ import annotations

import uuid

from condominioos.agents.tools import Tool, ToolRegistry


def register_stub_tools(registry: ToolRegistry) -> None:
    def reg(name: str, ctx: str, fn) -> None:
        registry.register(Tool(name=name, fn=fn, bounded_context=ctx))

    # Maintenance / vendors
    reg("ticket.search_duplicates", "maintenance", lambda text: {"found": False})
    reg("ticket.create", "maintenance",
        lambda description, severity: {"id": str(uuid.uuid4()), "severity": severity})
    reg("ticket.update", "maintenance", lambda **k: {"ok": True})
    reg("sla.start_timer", "maintenance", lambda ticket_id, severity: {"started": True})
    reg("vendor.request_dispatch", "maintenance",
        lambda ticket_id, emergency: {"dispatched": emergency})
    reg("budget.check_coverage", "maintenance", lambda **k: {"covered": True})
    reg("vendor.search", "vendors", lambda category: {"top": {"id": str(uuid.uuid4())}})
    reg("vendor.check_compliance", "vendors",
        lambda vendor_id: {"compliant": True, "reason": ""})
    reg("quote.request", "vendors",
        lambda vendor_id, ticket_id: {"id": str(uuid.uuid4()), "amount": 250.0})
    reg("quote.compare", "vendors", lambda **k: {"best": None})
    reg("schedule.book", "vendors",
        lambda vendor_id, quote_id: {"work_order_id": str(uuid.uuid4())})
    reg("vendor.rate", "vendors", lambda **k: {"ok": True})

    # Accounting
    reg("document.ocr", "financial", lambda **k: {"text": "stub invoice text"})
    reg("invoice.extract", "financial",
        lambda document_ref: {"number": "INV-1", "amount_gross": 100.0, "vendor": "ACME"})
    reg("invoice.validate", "financial", lambda fields: {"ok": True, "reason": ""})
    reg("coa.classify", "financial", lambda fields: {"code": "60.10"})
    reg("ledger.post", "financial", lambda fields, coa_code: {"invoice_id": str(uuid.uuid4())})
    reg("payment.match", "financial", lambda **k: {"matched": True})
    reg("reconcile.run", "financial", lambda **k: {"ok": True})

    # Collections
    reg("ledger.get_arrears", "financial", lambda unit_id: {"balance": 120.0})
    reg("reconcile.confirm", "financial",
        lambda unit_id: {"confirmed": True, "balance": 120.0})
    reg("debtor.resolve", "financial",
        lambda unit_id, expense_kind: {"type": "owner", "id": str(uuid.uuid4()), "name": "Sig. Rossi"})
    reg("collections.get_policy", "financial", lambda unit_id: {"tier": "T1"})
    reg("payment_plan.propose", "financial", lambda **k: {"plan": None})
    reg("handoff_to_human", "platform", lambda **k: {"escalated": True})

    # Assembly
    reg("agenda.assemble", "governance", lambda assembly_id: {"items": ["Approvazione rendiconto"]})
    reg("convocation.generate", "governance",
        lambda assembly_id, agenda: {"content": "Convocazione assemblea ordinaria..."})
    reg("convocation.validate_legal", "governance",
        lambda convocation, min_notice_days: {"valid": True, "reason": ""})
    reg("proxy.register", "governance", lambda **k: {"ok": True})
    reg("quorum.compute", "governance", lambda **k: {"met": True})
    reg("minutes.draft", "governance", lambda **k: {"content": "Verbale..."})
    reg("task.spawn_followups", "governance", lambda **k: {"spawned": 0})

    # Compliance
    reg("obligation.list", "compliance",
        lambda tenant_id: {"items": [{"id": str(uuid.uuid4()), "kind": "insurance"}]})
    reg("deadline.compute", "compliance",
        lambda obligation: {"within_lead_time": True, "severity": "medium"})
    reg("document.check_present", "compliance", lambda **k: {"present": True})
    reg("alert.raise", "compliance", lambda obligation_id, severity: {"raised": True})
    reg("task.create", "compliance", lambda **k: {"id": str(uuid.uuid4())})
    reg("regulation.lookup", "compliance", lambda **k: {"article": "1130 c.c."})

    # Documents
    reg("ocr.run", "documents", lambda storage_key: {"text": "stub doc text regolamento"})
    reg("doc.classify", "documents",
        lambda text: {"type": "regolamento", "confidence": 0.92})
    reg("metadata.extract", "documents", lambda **k: {"meta": {}})
    reg("pii.detect", "documents", lambda text: {"tags": []})
    reg("pii.redact", "documents", lambda **k: {"redacted": True})
    reg("vector.index", "documents", lambda storage_key, text, tenant_id: {"indexed": True})
    reg("doc.version", "documents", lambda **k: {"version": 1})
    reg("doc.link_entity", "documents", lambda **k: {"linked": True})

    # Knowledge
    for t in ("vector.search", "keyword.search", "rerank", "legal_corpus.search"):
        reg(t, "documents_knowledge", lambda **k: {"hits": []})

    # Concierge / orchestrator / platform
    reg("knowledge.query", "communications", lambda **k: {"grounded": True})
    reg("document.search", "communications", lambda **k: {"docs": []})
    reg("classify_intent", "agent_orchestration", lambda **k: {"intent": "info_request"})
    reg("create_task", "agent_orchestration", lambda **k: {"id": str(uuid.uuid4())})
    reg("check_budget", "agent_orchestration", lambda **k: {"ok": True})
    reg("risk.score_action", "platform", lambda **k: {"level": "low"})
    reg("policy.lookup", "platform", lambda **k: {"policy": {}})
    reg("history.lookup", "platform", lambda **k: {"history": []})
    reg("eval.run_rubric", "platform", lambda **k: {"score": 1.0})
    reg("eval.judge", "platform", lambda **k: {"score": 1.0})
    reg("eval.compare_versions", "platform", lambda **k: {"regression": False})
    reg("scorecard.publish", "platform", lambda **k: {"published": True})
    reg("release.gate", "platform", lambda **k: {"pass": True})
    reg("review.create", "platform", lambda **k: {"id": str(uuid.uuid4())})
    reg("reviewer.route", "platform", lambda **k: {"assignee": "ops"})
    reg("context.package", "platform", lambda **k: {"packaged": True})
    reg("sla.track", "platform", lambda **k: {"tracked": True})
