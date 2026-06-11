# 14 — Event Catalog

All domain events on the bus (NATS JetStream). Naming: **`context.entity.verb`** (verb = past tense).
Subjects are tenant-scoped: `condo.{condominium_id}.{context}.{entity}.{verb}`.

Machine-readable schemas live in `packages/events/` (JSON Schema) and
`services/condominioos/events/catalog.py` (Pydantic). All events share the envelope below.

---

## Envelope (every event)

```jsonc
{
  "event_id": "uuid",
  "event_type": "acc.invoice.posted",
  "version": 1,
  "occurred_at": "RFC3339",
  "tenant_id": "condominium uuid",
  "correlation_id": "uuid",      // ties a whole journey together
  "causation_id": "uuid",        // the event/command that caused this
  "actor": "agent:accounting | human:user_id | system",
  "trace_id": "otel trace id",
  "payload": { /* event-specific, schema-versioned */ }
}
```

Rules: events are **immutable facts**, **additive-only** schema evolution, consumers **idempotent**
(dedup on `event_id`), and **every** event also yields a `platform.audit.event_appended`.

---

## Catalog

### Communications (`comms`)
| Event | Payload (key fields) | Emitted by | Consumed by |
|---|---|---|---|
| `comms.message.received` | channel, party_ref, body_ref, lang | channels | orchestrator |
| `comms.outbound.drafted` | draft_ref, intent, confidence | agents | firewall |
| `comms.message.sent` | channel, party_ref, verdict_id | notification | audit, conversation view |
| `comms.reminder.drafted` | case_id, tier, amount, recipient | collections | firewall |

### Orchestration (`orchestration`)
| Event | Payload | By | For |
|---|---|---|---|
| `orchestration.task.created` | intent, priority, sla | orchestrator | runtime |
| `orchestration.task.routed` | agent, task_id | orchestrator | agents |
| `orchestration.task.completed` | task_id, outcome | agents | orchestrator |
| `orchestration.task.failed` | task_id, reason | agents | escalation |

### Documents (`doc`)
| Event | Payload | By | For |
|---|---|---|---|
| `doc.document.uploaded` | storage_key, source | channels/portal | documents |
| `doc.document.classified` | doc_id, type, confidence | documents | accounting/compliance |
| `doc.pii.tagged` | doc_id, pii_tags | documents | security |
| `doc.knowledge.indexed` | doc_id, chunks, namespace | documents | knowledge |

### Accounting (`acc`)
| Event | Payload | By | For |
|---|---|---|---|
| `acc.invoice.extracted` | invoice_id, fields | accounting | accounting |
| `acc.invoice.validated` | invoice_id | accounting | accounting |
| `acc.invoice.anomaly_flagged` | invoice_id, reason | accounting | review |
| `acc.invoice.posted` | invoice_id, coa_code, amount | accounting | ledger view |
| `acc.payment.received` | payment_id, amount, ref | accounting | accounting |
| `acc.payment.matched` | payment_id, charge_ids | accounting | collections |
| `acc.payment.unmatched` | payment_id | accounting | review |
| `acc.reconciliation.completed` | period, result | accounting | collections |
| `acc.charge.overdue_detected` | unit_id, amount, due_date | accounting | collections |
| `acc.arrears.confirmed` | case_id, balance, debtor_ref | collections | collections |

### Maintenance (`mnt`) & Vendors (`ven`)
| Event | Payload | By | For |
|---|---|---|---|
| `mnt.ticket.requested` | reporter, description | maintenance | maintenance |
| `mnt.ticket.triaged` | ticket_id, severity, category | maintenance | vendor |
| `mnt.sla.breach_warning` | ticket_id, due | maintenance | escalation |
| `ven.quote.received` | ticket_id, vendor_id, amount | vendor | vendor |
| `ven.vendor.compliance_verified` | vendor_id, durc, insurance | vendor | vendor |
| `ven.vendor.compliance_flagged` | vendor_id, reason | vendor | review |
| `ven.workorder.scheduled` | wo_id, vendor_id, when | vendor | maintenance |
| `ven.vendor.dispatched` | wo_id, eta | vendor | maintenance |

### Governance (`gov`)
| Event | Payload | By | For |
|---|---|---|---|
| `gov.assembly.scheduled` | assembly_id, type, when | assembly | assembly |
| `gov.agenda.assembled` | assembly_id, items | assembly | assembly |
| `gov.convocation.issued` | assembly_id, notice_days | assembly | firewall/notification |
| `gov.proxy.recorded` | assembly_id, grantor, share | assembly | assembly |
| `gov.quorum.computed` | assembly_id, call_no, met | assembly | assembly |
| `gov.resolution.recorded` | assembly_id, topic, outcome | assembly | followups |
| `gov.minutes.drafted` | assembly_id, content_ref | assembly | review |
| `gov.minutes.signed` | assembly_id, signed_by | assembly | followups |

### Compliance (`cmp`)
| Event | Payload | By | For |
|---|---|---|---|
| `cmp.deadline.computed` | obligation_id, next_due | compliance | compliance |
| `cmp.compliance.alert_raised` | obligation_id, severity | compliance | ops/vendor |
| `cmp.document.missing_detected` | kind | compliance | ops |
| `cmp.obligation.satisfied` | obligation_id | compliance | dashboard |

### Reputation Firewall (`firewall`)
| Event | Payload | By | For |
|---|---|---|---|
| `firewall.verdict.issued` | artifact_hash, verdict, layer_scores, confidence | firewall | notification/review/audit |
| `firewall.action.blocked` | artifact_hash, layer, reason | firewall | incident/risk |
| `firewall.revision.requested` | artifact_hash, fixes | firewall | originating agent |

### Review / Risk / QA (`review`,`risk`,`qa`)
| Event | Payload | By | For |
|---|---|---|---|
| `review.item.created` | item_id, priority, sla | escalation | ops console |
| `review.decision.recorded` | item_id, decision, reviewer | review | firewall/originating agent |
| `risk.scored` | action_ref, score, factors | risk | firewall |
| `risk.escalation_forced` | action_ref, new_tier | risk | firewall |
| `qa.scorecard.published` | scope, metrics | qa | governance |
| `qa.release.gated` | candidate, pass/fail | qa | ci/cd |

### Platform (`platform`)
| Event | Payload | By | For |
|---|---|---|---|
| `platform.audit.event_appended` | hash, prev_hash, entity_ref | audit | (immutable) |
| `platform.tenant.provisioned` | tenant_id, plan | identity | all |
| `platform.dsar.requested` | subject_ref, kind | identity | gdpr workflow |

## Consumer expectations
- **Idempotent** on `event_id`; **ordered** per `correlation_id` where needed (JetStream ordered
  consumers / per-subject ordering).
- **Outbox pattern** on the producer side to guarantee event emission with the DB transaction.
- **Dead-letter** stream for poison messages; replayable for recovery.
