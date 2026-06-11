# 11 — Event Storming Model

Big-picture event storming for CondominioOS. Notation:
🟧 **Domain Event** (past tense fact) · 🟦 **Command** · 🟨 **Aggregate** · 🟪 **Policy/Reaction**
(when X then Y) · 🟩 **Read Model** · 👤 **Actor** · ⬜ **External system**.

Event names use the canonical catalog (doc 14): `context.entity.verb`.

---

## 1. Resident communication

```
👤 Resident ──🟦 SendMessage──▶ ⬜ WhatsApp ──▶ 🟧 comms.message.received
🟪 when message.received → classify intent (Orchestrator)
   ──🟦 RouteTask──▶ 🟧 orchestration.task.routed
🟪 when task.routed(info) → 🟦 DraftReply (Concierge) → 🟧 comms.outbound.drafted
🟪 when outbound.drafted → 🟦 GateOutbound (Firewall) → 🟧 firewall.verdict.issued
🟪 when verdict=APPROVE → 🟦 SendOutbound (Notification) → 🟧 comms.message.sent
🟪 when verdict=HOLD → 🟧 review.item.created → 👤 Ops → 🟧 review.decision.recorded
🟩 Read models: ConversationView, ResidentInboxView
```

## 2. Document ingestion

```
👤/⬜ Upload/Email ──🟦 IngestDocument──▶ 🟨 Document
🟧 doc.document.uploaded → 🟪 OCR+Classify (Document Agent)
   → 🟧 doc.document.classified → 🟧 doc.pii.tagged → 🟧 doc.knowledge.indexed
🟪 when classified(type=invoice) → 🟦 ProcessInvoice (Accounting)  [see §3]
🟪 when classified(type=polizza) → 🟦 RegisterObligation (Compliance) [see §6]
🟩 DocumentLibraryView, KnowledgeIndex
```

## 3. Accounting

```
🟧 doc.document.classified(invoice) ──🟦 ExtractInvoice──▶ 🟨 Invoice
   → 🟧 acc.invoice.extracted
🟪 validate (duplicate/P.IVA/VAT) → 🟧 acc.invoice.validated | acc.invoice.anomaly_flagged
🟪 when anomaly → 🟧 review.item.created (A1)
🟪 when validated → 🟦 PostToLedger → 🟧 acc.invoice.posted
⬜ Bank feed ──🟦 ImportPayments──▶ 🟧 acc.payment.received
🟪 match → 🟧 acc.payment.matched | acc.payment.unmatched
🟪 reconcile period → 🟧 acc.reconciliation.completed
🟩 LedgerView, UnitBalanceView
```

## 4. Collections

```
🟪 when reconciliation.completed & balance overdue → 🟧 acc.charge.overdue_detected
🟪 GATE: when overdue_detected → 🟦 ConfirmReconciliation (Collections)
   → 🟧 acc.arrears.confirmed   [no message before this]
🟪 when arrears.confirmed → 🟦 ResolveDebtor → determine tier
   T1: 🟦 DraftReminder → 🟧 comms.reminder.drafted → Firewall(L4 financial) → send
   T2/T3: 🟧 collections.escalated → 👤 AoR
🟪 when payment.matched(for case) → 🟦 CancelPendingReminder → 🟧 collections.case.closed
🟩 ArrearsView, CollectionsCaseView
```

## 5. Maintenance & vendor

```
👤 Resident ──🟦 ReportIssue──▶ 🟧 mnt.ticket.requested
🟪 triage → 🟧 mnt.ticket.triaged (severity, category)
🟪 when severity=emergency → 🟦 DispatchOnCall → 🟧 ven.vendor.dispatched (≤60m) + 👤 notify
🟪 when routine → 🟦 RequestQuotes (Vendor) → 🟧 ven.quote.received
🟪 GATE: 🟦 CheckCompliance (DURC/insurance) → 🟧 ven.vendor.compliance_verified | flagged
🟪 when compliant & cost≤threshold → 🟦 Schedule → 🟧 ven.workorder.scheduled
🟪 when cost>threshold → 🟧 review.item.created (A1)
🟪 SLA timer → 🟧 mnt.sla.breach_warning → escalate
🟩 TicketBoardView, VendorRegistryView
```

## 6. Compliance

```
🟧 doc.document.classified(polizza/contract/cert) ──🟦 RegisterObligation──▶ 🟨 Obligation
🟪 scheduler tick → 🟦 ComputeDeadlines → 🟧 cmp.deadline.computed
🟪 when expiry within lead_time → 🟧 cmp.compliance.alert_raised
🟪 when alert(insurance) → 🟦 OpenRemediation → 🟧 mnt/ven renewal task
🟪 when mandatory doc missing → 🟧 cmp.document.missing_detected
🟩 ComplianceDashboardView, ObligationCalendarView
```

## 7. Assembly lifecycle

```
👤 AoR ──🟦 ScheduleAssembly──▶ 🟨 Assembly → 🟧 gov.assembly.scheduled
🟪 assemble agenda (open items, budget, deadlines) → 🟧 gov.agenda.assembled
🟪 🟦 GenerateConvocation → validate legal (≥5 days, content) → 🟧 gov.convocation.issued
   → Firewall(L5 legal) → 👤 AoR approve → send
👤 Owners ──🟦 SubmitProxy──▶ 🟧 gov.proxy.recorded (enforce limits)
🟪 at meeting: 🟦 ComputeQuorum → 🟧 gov.quorum.computed (1st/2nd call)
🟪 record decisions → 🟧 gov.resolution.recorded (votes + millesimi)
🟪 🟦 DraftMinutes → 🟧 gov.minutes.drafted → 👤 AoR sign → 🟧 gov.minutes.signed
🟪 when minutes.signed → 🟦 SpawnFollowups → tasks across contexts
🟩 AssemblyView, MinutesArchive
```

## 8. Cross-cutting (always)

```
🟪 ANY state change → 🟧 platform.audit.event_appended (hash-chained)
🟪 ANY outbound/financial/legal action → 🟦 GateOutbound (Firewall) FIRST
🟪 ANY agent output sampled → 🟦 Evaluate (QA) → 🟧 qa.scorecard.published
🟪 ANY action above risk threshold → 🟦 ScoreRisk (Risk) → may force tier escalation
```

## 9. Hotspots (decisions/risks flagged during storming)

| Hotspot | Why it matters | Resolution |
|---|---|---|
| Reconciliation-before-reminder | Over-collection = top reputational risk | Hard gate (§4) |
| Owner vs tenant for a charge | Wrong debtor = complaint | Debtor resolution by expense type |
| Convocation legal validity | Defects void the assembly | Legal validators + AoR approval |
| Vendor compliance | Liability for uninsured work | Compliance gate before dispatch |
| Emergency latency | Safety | On-call dispatch ≤60m, bypass quote |
| Cross-tenant retrieval | GDPR/leak | Namespace derived from auth context only |
