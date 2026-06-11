"""Accounting Agent — invoice OCR → validate → classify → post; payment matching (docs/04 §4)."""

from __future__ import annotations

from condominioos.agents.base import AgentState, BaseAgent


class AccountingAgent(BaseAgent):
    name = "accounting"
    bounded_context = "financial"
    allowed_tools = ("document.ocr", "invoice.extract", "invoice.validate", "coa.classify",
                     "ledger.post", "payment.match", "reconcile.run")
    default_autonomy = "A2"

    async def run(self, state: AgentState) -> AgentState:
        doc_ref = state.context.get("document_ref")
        fields = self.tools.call("invoice.extract", document_ref=doc_ref)
        validation = self.tools.call("invoice.validate", fields=fields)
        if not validation["ok"]:
            return self._escalate(state, f"invoice anomaly: {validation['reason']}")
        coa = self.tools.call("coa.classify", fields=fields)
        posted = self.tools.call("ledger.post", fields=fields, coa_code=coa["code"])
        state.context["invoice_id"] = posted["invoice_id"]
        state.trail.append(f"accounting: posted invoice {posted['invoice_id']} -> {coa['code']}")
        return state
