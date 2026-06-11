# 12 — Data Model Diagrams

ER diagrams (Mermaid). Canonical DDL: `services/condominioos/db/schema.sql`. ORM:
`services/condominioos/db/models.py`. All tenant tables carry `condominium_id` with RLS (doc 05).

---

## 1. Core registry & governance

```mermaid
erDiagram
  CONDOMINIUM ||--o{ UNIT : has
  CONDOMINIUM ||--o{ MILLESIMI_TABLE : defines
  CONDOMINIUM ||--o{ ASSEMBLY : holds
  CONDOMINIUM }o--|| ADMIN : managed_by
  UNIT ||--o{ MILLESIMI_ENTRY : shares
  MILLESIMI_TABLE ||--o{ MILLESIMI_ENTRY : contains
  UNIT }o--|| OWNER : owned_by
  UNIT }o--o{ RESIDENT : occupied_by
  ASSEMBLY ||--|| CONVOCATION : announced_by
  ASSEMBLY ||--o{ PROXY : collects
  ASSEMBLY ||--o{ RESOLUTION : decides
  ASSEMBLY ||--|| MINUTES : recorded_in
  OWNER ||--o{ PROXY : grants

  CONDOMINIUM {
    uuid id PK
    string name
    string fiscal_code
    string address
    int units_count
    uuid admin_id FK
    string plan
    string status
    timestamptz created_at
  }
  UNIT {
    uuid id PK
    uuid condominium_id FK
    string identifier
    string type
    string floor
    numeric area_sqm
    uuid owner_id FK
    uuid resident_id FK
  }
  MILLESIMI_TABLE {
    uuid id PK
    uuid condominium_id FK
    string name
    int total "1000"
  }
  MILLESIMI_ENTRY {
    uuid id PK
    uuid table_id FK
    uuid unit_id FK
    numeric share
  }
  OWNER {
    uuid id PK
    uuid condominium_id FK
    string kind "person|company"
    string full_name
    string fiscal_code
    string email
    string phone
  }
  RESIDENT {
    uuid id PK
    uuid condominium_id FK
    uuid unit_id FK
    string full_name
    string email
    string phone
    jsonb consent
  }
  ASSEMBLY {
    uuid id PK
    uuid condominium_id FK
    string type "ordinary|extraordinary"
    timestamptz scheduled_at
    int call_no
    string status
  }
  CONVOCATION {
    uuid id PK
    uuid assembly_id FK
    timestamptz sent_at
    int notice_days
    string content_ref
    string firewall_verdict_id
  }
  PROXY {
    uuid id PK
    uuid assembly_id FK
    uuid grantor_owner_id FK
    string grantee
    numeric share
  }
  RESOLUTION {
    uuid id PK
    uuid assembly_id FK
    string topic
    numeric millesimi_for
    numeric millesimi_against
    int votes_for
    int votes_against
    string outcome
  }
  MINUTES {
    uuid id PK
    uuid assembly_id FK
    string content_ref
    uuid signed_by FK
    timestamptz signed_at
    string status
  }
```

## 2. Financial

```mermaid
erDiagram
  CONDOMINIUM ||--o{ INVOICE : receives
  CONDOMINIUM ||--o{ CHARGE : levies
  CONDOMINIUM ||--o{ PAYMENT : records
  VENDOR ||--o{ INVOICE : issues
  UNIT ||--o{ CHARGE : owes
  CHARGE ||--o{ PAYMENT_ALLOCATION : settled_by
  PAYMENT ||--o{ PAYMENT_ALLOCATION : allocates
  CHARGE ||--o{ COLLECTIONS_CASE : may_trigger

  INVOICE {
    uuid id PK
    uuid condominium_id FK
    uuid vendor_id FK
    string number
    date issue_date
    date due_date
    numeric amount_net
    numeric vat
    numeric amount_gross
    string coa_code
    string status "extracted|validated|posted|paid|anomaly"
    string document_ref
  }
  CHARGE {
    uuid id PK
    uuid condominium_id FK
    uuid unit_id FK
    string period
    string kind "ordinary|extraordinary"
    numeric amount
    date due_date
    string status "open|partial|paid|overdue"
  }
  PAYMENT {
    uuid id PK
    uuid condominium_id FK
    numeric amount
    date value_date
    string method
    string reference
    string status "unmatched|matched|partial"
  }
  PAYMENT_ALLOCATION {
    uuid id PK
    uuid payment_id FK
    uuid charge_id FK
    numeric amount
  }
  COLLECTIONS_CASE {
    uuid id PK
    uuid condominium_id FK
    uuid unit_id FK
    numeric balance
    string tier "T1|T2|T3"
    string status
    timestamptz last_reminder_at
  }
```

## 3. Maintenance & vendors

```mermaid
erDiagram
  CONDOMINIUM ||--o{ TICKET : raises
  TICKET ||--o| WORK_ORDER : fulfilled_by
  WORK_ORDER }o--|| VENDOR : assigned_to
  VENDOR ||--o{ QUOTE : provides
  TICKET ||--o{ QUOTE : for

  TICKET {
    uuid id PK
    uuid condominium_id FK
    string reporter_ref
    string category
    string severity "low|medium|high|emergency"
    string status
    timestamptz sla_due
    timestamptz created_at
  }
  WORK_ORDER {
    uuid id PK
    uuid ticket_id FK
    uuid vendor_id FK
    numeric cost
    string status
    timestamptz scheduled_at
    timestamptz completed_at
  }
  VENDOR {
    uuid id PK
    string name
    string p_iva
    string category
    string durc_status
    date insurance_expiry
    numeric rating
    string status "active|suspended"
  }
  QUOTE {
    uuid id PK
    uuid ticket_id FK
    uuid vendor_id FK
    numeric amount
    string status
    timestamptz received_at
  }
```

## 4. Documents, communications, compliance, audit, agents

```mermaid
erDiagram
  CONDOMINIUM ||--o{ DOCUMENT : keeps
  DOCUMENT ||--o{ DOCUMENT_VERSION : versions
  CONDOMINIUM ||--o{ COMMUNICATION : exchanges
  CONDOMINIUM ||--o{ OBLIGATION : subject_to
  OBLIGATION ||--o{ COMPLIANCE_ALERT : raises
  COMMUNICATION }o--o| FIREWALL_VERDICT : gated_by
  AGENT_RUN ||--o{ TOOL_CALL : makes

  DOCUMENT {
    uuid id PK
    uuid condominium_id FK
    string type
    string title
    string storage_key
    int version
    string[] pii_tags
    date expiry_date
    timestamptz created_at
  }
  COMMUNICATION {
    uuid id PK
    uuid condominium_id FK
    string channel "whatsapp|email|pec|web"
    string direction "in|out"
    string party_ref
    string body_ref
    string firewall_verdict_id
    timestamptz at
  }
  OBLIGATION {
    uuid id PK
    uuid condominium_id FK
    string kind
    date next_due
    int lead_days
    string status
  }
  COMPLIANCE_ALERT {
    uuid id PK
    uuid obligation_id FK
    string severity
    timestamptz raised_at
    string status
  }
  FIREWALL_VERDICT {
    uuid id PK
    uuid condominium_id FK
    string artifact_hash
    string verdict "APPROVE|REVISE|HOLD|BLOCK"
    jsonb layer_scores
    numeric confidence
    string signature
    timestamptz at
  }
  AUDIT_EVENT {
    uuid id PK
    timestamptz ts
    string actor
    string action
    string entity_ref
    string prev_hash
    string hash
    jsonb payload
  }
  AGENT_RUN {
    uuid id PK
    uuid condominium_id FK
    string agent
    uuid task_id
    string model
    string prompt_version
    jsonb inputs
    jsonb outputs
    int tokens
    numeric cost
    timestamptz at
  }
  TOOL_CALL {
    uuid id PK
    uuid agent_run_id FK
    string tool
    jsonb args
    jsonb result
    boolean allowed
  }
```
