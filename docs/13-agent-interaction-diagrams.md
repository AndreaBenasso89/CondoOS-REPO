# 13 — Agent Interaction Diagrams

Sequence & state diagrams for the key agent flows. Firewall (🛡️) and Audit are implicit on every
outbound/financial/legal action.

---

## 1. Resident question (grounded FAQ, fully automated)

```mermaid
sequenceDiagram
  autonumber
  participant CH as Channel
  participant O as Orchestrator
  participant C as Concierge
  participant K as Knowledge
  participant R as Risk
  participant F as 🛡️ Firewall
  participant N as Notification
  CH->>O: message.received
  O->>O: classify_intent → info_request (0.93)
  O->>C: route task
  C->>K: knowledge.query(condo, q)
  K-->>C: facts + citations + coverage(0.91)
  C->>C: draft_reply (grounded, cited)
  C->>F: submit OutboundDraft (conf 0.9)
  F->>R: risk.score_action
  R-->>F: risk=low
  F->>F: L1..L8 pass → APPROVE (signed)
  F->>N: approved verdict
  N->>CH: send reply
```

## 2. Concierge → human escalation (legal intent)

```mermaid
sequenceDiagram
  autonumber
  participant C as Concierge
  participant F as 🛡️ Firewall
  participant HE as Human Escalation
  participant Q as Review Queue
  participant H as AoR
  C->>C: intent = legal_interpretation
  C->>F: submit draft (legal claim)
  F->>F: L5 Legal Safety → HOLD (A0)
  F->>HE: hold(draft, context, risk)
  HE->>Q: create review (priority high)
  Q->>H: present + 1-click actions
  H-->>Q: Edit & approve (adds disclaimer, cites article)
  Q-->>F: signed human verdict
  F->>F: re-validate final text → APPROVE
  F-->>C: send via Notification
```

## 3. Maintenance dispatch (with compliance + cost gate)

```mermaid
sequenceDiagram
  autonumber
  participant R as Resident
  participant M as Maintenance
  participant V as Vendor
  participant DURC as Public registry
  participant F as 🛡️ Firewall
  participant H as Ops (if needed)
  R->>M: report "water leak"
  M->>M: triage → high (not emergency), category=plumbing
  M->>M: search_duplicates → none
  M->>V: request_dispatch(plumbing, budget)
  V->>V: vendor.search → top candidate
  V->>DURC: check_compliance (DURC, insurance)
  DURC-->>V: valid
  alt cost <= threshold
    V->>F: schedule + resident update (A2)
    F-->>R: "Tecnico martedì 9–12" (approved)
  else cost > threshold
    V->>H: A1 approval request
    H-->>V: approve
    V->>F: schedule + update
  end
```

## 4. Collections (reconciliation gate — the careful flow)

```mermaid
sequenceDiagram
  autonumber
  participant L as Accounting/Ledger
  participant CO as Collections
  participant REC as Reconciliation
  participant F as 🛡️ Firewall
  participant N as Notification
  L->>CO: charge.overdue_detected(unit, amount)
  CO->>REC: confirm reconciliation (balance match?)
  alt mismatch
    REC-->>CO: MISMATCH
    CO->>F: (blocked) → Ops investigation
    Note over CO,F: NO reminder is ever sent on mismatch
  else confirmed
    REC-->>CO: arrears.confirmed(exact balance, debtor=owner)
    CO->>CO: tier = T1 (first, soft), cooldown ok
    CO->>F: draft reminder (amount, recipient)
    F->>F: L3 recipient + L4 financial + L6 tone
    F-->>N: APPROVE (A2, T1)
    N-->>L: reminder sent; case tracked
  end
```

## 5. Assembly lifecycle (state machine)

```mermaid
stateDiagram-v2
  [*] --> Scheduled: AoR schedules
  Scheduled --> AgendaReady: Assembly Agent assembles agenda
  AgendaReady --> Convoked: convocation generated→legal validate→🛡️→AoR approve→sent (≥5d)
  Convoked --> ProxiesOpen: distribute, collect RSVP/proxies
  ProxiesOpen --> QuorumCheck: at meeting time
  QuorumCheck --> FirstCallFailed: quorum not met (1st call)
  FirstCallFailed --> SecondCall: 2nd call (lower quorum)
  QuorumCheck --> InSession: quorum met
  SecondCall --> InSession: quorum met
  SecondCall --> Adjourned: still no quorum
  InSession --> Resolved: record resolutions (votes+millesimi)
  Resolved --> MinutesDraft: Assembly Agent drafts verbale
  MinutesDraft --> MinutesSigned: AoR reviews & signs (A0)
  MinutesSigned --> FollowupsSpawned: tasks created across contexts
  FollowupsSpawned --> [*]
  Adjourned --> [*]
```

## 6. Document ingestion → multi-agent fan-out

```mermaid
sequenceDiagram
  autonumber
  participant U as Uploader/Email
  participant D as Document
  participant K as Knowledge
  participant A as Accounting
  participant CM as Compliance
  U->>D: document.uploaded
  D->>D: OCR → classify → PII tag → version
  D->>K: vector.index (tenant namespace)
  alt type = invoice
    D->>A: invoice extraction trigger
  else type = polizza/contract/cert
    D->>CM: register obligation + expiry
  end
  D-->>U: document.ingested (searchable)
```

## 7. Orchestration graph (LangGraph topology)

```mermaid
flowchart TB
  START((message/event)) --> INTENT[Orchestrator: classify]
  INTENT -->|info| CONCIERGE
  INTENT -->|maintenance| MAINT
  INTENT -->|invoice/payment| ACCT
  INTENT -->|arrears| COLL
  INTENT -->|assembly| ASSEM
  INTENT -->|document| DOCA
  INTENT -->|compliance| COMP
  INTENT -->|unknown<0.6| ESC[Human Escalation]
  CONCIERGE --> KQ{needs facts?}
  KQ -->|yes| KNOW[Knowledge] --> CONCIERGE
  MAINT --> VEND[Vendor]
  subgraph GATE[Mandatory gate]
    RISK[Risk score] --> FW{{🛡️ Firewall}}
  end
  CONCIERGE & MAINT & ACCT & COLL & ASSEM & VEND & COMP --> GATE
  FW -->|APPROVE| SEND[Notification / Executor]
  FW -->|HOLD| ESC
  FW -->|BLOCK| INC[Incident]
  ESC --> HUMAN[(Human verdict)] --> FW
  SEND --> END((done + audit))
```
