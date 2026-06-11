-- CondominioOS canonical operational schema (PostgreSQL 16).
-- Multi-tenant via Row-Level Security keyed on condominium_id. See docs/05 and docs/12.
-- This DDL is the source of truth; Alembic migrations are generated to match it.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;  -- pgvector (Qdrant is primary; this is the fallback)

-- ---------------------------------------------------------------------------
-- Tenancy helper: every tenant-scoped table enables RLS using this setting.
-- The app sets it per unit of work:  SET app.current_tenant = '<uuid>';
-- ---------------------------------------------------------------------------

-- =========================== Registry & governance =========================

CREATE TABLE admin_user (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    role            TEXT NOT NULL CHECK (role IN ('aor','ops','compliance','engineer')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE condominium (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL,
    fiscal_code     TEXT,
    address         TEXT,
    units_count     INT NOT NULL DEFAULT 0,
    admin_id        UUID REFERENCES admin_user(id),
    plan            TEXT NOT NULL DEFAULT 'managed_core',
    autonomy_mode   TEXT NOT NULL DEFAULT 'supervised',
    status          TEXT NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE owner (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    kind            TEXT NOT NULL DEFAULT 'person' CHECK (kind IN ('person','company')),
    full_name       TEXT NOT NULL,
    fiscal_code     TEXT,
    email           TEXT,
    phone           TEXT
);

CREATE TABLE resident (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    unit_id         UUID,
    full_name       TEXT NOT NULL,
    email           TEXT,
    phone           TEXT,
    consent         JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE unit (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    identifier      TEXT NOT NULL,            -- e.g. "Int. 3, Scala A"
    type            TEXT NOT NULL DEFAULT 'apartment',
    floor           TEXT,
    area_sqm        NUMERIC(10,2),
    owner_id        UUID REFERENCES owner(id),
    resident_id     UUID REFERENCES resident(id),
    UNIQUE (condominium_id, identifier)
);
ALTER TABLE resident ADD CONSTRAINT resident_unit_fk FOREIGN KEY (unit_id) REFERENCES unit(id);

CREATE TABLE millesimi_table (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,            -- generale | riscaldamento | ascensore ...
    total           INT NOT NULL DEFAULT 1000
);

CREATE TABLE millesimi_entry (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_id        UUID NOT NULL REFERENCES millesimi_table(id) ON DELETE CASCADE,
    unit_id         UUID NOT NULL REFERENCES unit(id) ON DELETE CASCADE,
    share           NUMERIC(8,3) NOT NULL     -- Σ per table must equal table.total (enforced in app)
);

CREATE TABLE assembly (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    type            TEXT NOT NULL CHECK (type IN ('ordinary','extraordinary')),
    scheduled_at    TIMESTAMPTZ,
    call_no         INT NOT NULL DEFAULT 1,
    status          TEXT NOT NULL DEFAULT 'scheduled'
);

CREATE TABLE convocation (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    assembly_id     UUID NOT NULL REFERENCES assembly(id) ON DELETE CASCADE,
    sent_at         TIMESTAMPTZ,
    notice_days     INT,
    content_ref     TEXT,
    firewall_verdict_id UUID
);

CREATE TABLE proxy (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    assembly_id     UUID NOT NULL REFERENCES assembly(id) ON DELETE CASCADE,
    grantor_owner_id UUID NOT NULL REFERENCES owner(id),
    grantee         TEXT NOT NULL,
    share           NUMERIC(8,3) NOT NULL
);

CREATE TABLE resolution (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    assembly_id     UUID NOT NULL REFERENCES assembly(id) ON DELETE CASCADE,
    topic           TEXT NOT NULL,
    millesimi_for   NUMERIC(8,3) NOT NULL DEFAULT 0,
    millesimi_against NUMERIC(8,3) NOT NULL DEFAULT 0,
    votes_for       INT NOT NULL DEFAULT 0,
    votes_against   INT NOT NULL DEFAULT 0,
    outcome         TEXT
);

CREATE TABLE minutes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    assembly_id     UUID NOT NULL REFERENCES assembly(id) ON DELETE CASCADE,
    content_ref     TEXT,
    signed_by       UUID REFERENCES admin_user(id),
    signed_at       TIMESTAMPTZ,
    status          TEXT NOT NULL DEFAULT 'draft'
);

-- =============================== Financial ==================================

CREATE TABLE vendor (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL,
    p_iva           TEXT,
    category        TEXT,
    durc_status     TEXT,                     -- valid | expired | unknown
    insurance_expiry DATE,
    rating          NUMERIC(3,2),
    status          TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE invoice (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    vendor_id       UUID REFERENCES vendor(id),
    number          TEXT,
    issue_date      DATE,
    due_date        DATE,
    amount_net      NUMERIC(12,2),
    vat             NUMERIC(12,2),
    amount_gross    NUMERIC(12,2),
    coa_code        TEXT,
    status          TEXT NOT NULL DEFAULT 'extracted',
    document_ref    TEXT,
    UNIQUE (condominium_id, vendor_id, number)   -- duplicate-invoice guard
);

CREATE TABLE charge (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    unit_id         UUID NOT NULL REFERENCES unit(id),
    period          TEXT NOT NULL,
    kind            TEXT NOT NULL DEFAULT 'ordinary' CHECK (kind IN ('ordinary','extraordinary')),
    amount          NUMERIC(12,2) NOT NULL,
    due_date        DATE,
    status          TEXT NOT NULL DEFAULT 'open'
);

CREATE TABLE payment (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    amount          NUMERIC(12,2) NOT NULL,
    value_date      DATE,
    method          TEXT,
    reference       TEXT,
    status          TEXT NOT NULL DEFAULT 'unmatched'
);

CREATE TABLE payment_allocation (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id      UUID NOT NULL REFERENCES payment(id) ON DELETE CASCADE,
    charge_id       UUID NOT NULL REFERENCES charge(id) ON DELETE CASCADE,
    amount          NUMERIC(12,2) NOT NULL
);

CREATE TABLE collections_case (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    unit_id         UUID NOT NULL REFERENCES unit(id),
    balance         NUMERIC(12,2) NOT NULL,
    tier            TEXT NOT NULL DEFAULT 'T1' CHECK (tier IN ('T1','T2','T3')),
    status          TEXT NOT NULL DEFAULT 'open',
    last_reminder_at TIMESTAMPTZ
);

-- ========================= Maintenance & vendors ============================

CREATE TABLE ticket (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    reporter_ref    TEXT,
    category        TEXT,
    severity        TEXT NOT NULL DEFAULT 'medium'
                    CHECK (severity IN ('low','medium','high','emergency')),
    description     TEXT,
    status          TEXT NOT NULL DEFAULT 'open',
    sla_due         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE work_order (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    ticket_id       UUID NOT NULL REFERENCES ticket(id) ON DELETE CASCADE,
    vendor_id       UUID REFERENCES vendor(id),
    cost            NUMERIC(12,2),
    status          TEXT NOT NULL DEFAULT 'pending',
    scheduled_at    TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ
);

CREATE TABLE quote (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    ticket_id       UUID NOT NULL REFERENCES ticket(id) ON DELETE CASCADE,
    vendor_id       UUID NOT NULL REFERENCES vendor(id),
    amount          NUMERIC(12,2),
    status          TEXT NOT NULL DEFAULT 'received',
    received_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===================== Documents / comms / compliance =======================

CREATE TABLE document (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    type            TEXT,                     -- regolamento|verbale|polizza|contratto|fattura|altro
    title           TEXT,
    storage_key     TEXT NOT NULL,
    version         INT NOT NULL DEFAULT 1,
    pii_tags        TEXT[] NOT NULL DEFAULT '{}',
    expiry_date     DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE communication (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    channel         TEXT NOT NULL CHECK (channel IN ('whatsapp','email','pec','web')),
    direction       TEXT NOT NULL CHECK (direction IN ('in','out')),
    party_ref       TEXT,
    body_ref        TEXT,
    firewall_verdict_id UUID,
    at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE obligation (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    kind            TEXT NOT NULL,            -- insurance|elevator_cert|fire_cert|annual_assembly...
    next_due        DATE,
    lead_days       INT NOT NULL DEFAULT 30,
    status          TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE compliance_alert (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    obligation_id   UUID NOT NULL REFERENCES obligation(id) ON DELETE CASCADE,
    severity        TEXT NOT NULL DEFAULT 'medium',
    raised_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          TEXT NOT NULL DEFAULT 'open'
);

-- ===================== Firewall / review / agent runs =======================

CREATE TABLE firewall_verdict (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    artifact_hash   TEXT NOT NULL,
    verdict         TEXT NOT NULL CHECK (verdict IN ('APPROVE','REVISE','HOLD','BLOCK')),
    layer_scores    JSONB NOT NULL DEFAULT '{}'::jsonb,
    confidence      NUMERIC(4,3),
    autonomy_tier   TEXT,
    signature       TEXT,
    expires_at      TIMESTAMPTZ,
    at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE review_item (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    kind            TEXT NOT NULL,
    priority        TEXT NOT NULL DEFAULT 'normal',
    payload         JSONB NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',
    assignee        UUID REFERENCES admin_user(id),
    sla_due         TIMESTAMPTZ,
    decision        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE agent_run (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    condominium_id  UUID NOT NULL REFERENCES condominium(id) ON DELETE CASCADE,
    agent           TEXT NOT NULL,
    task_id         UUID,
    model           TEXT,
    prompt_version  TEXT,
    inputs          JSONB,
    outputs         JSONB,
    tokens          INT,
    cost            NUMERIC(10,4),
    at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE tool_call (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_run_id    UUID NOT NULL REFERENCES agent_run(id) ON DELETE CASCADE,
    tool            TEXT NOT NULL,
    args            JSONB,
    result          JSONB,
    allowed         BOOLEAN NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------------
-- Row-Level Security: applied to every tenant-scoped table.
-- ---------------------------------------------------------------------------
DO $$
DECLARE t TEXT;
BEGIN
  FOR t IN SELECT unnest(ARRAY[
    'condominium','owner','resident','unit','millesimi_table','assembly','convocation',
    'proxy','resolution','minutes','invoice','charge','payment','collections_case',
    'ticket','work_order','quote','document','communication','obligation','compliance_alert',
    'firewall_verdict','review_item','agent_run'
  ])
  LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', t);
    -- condominium uses id; the rest use condominium_id.
    IF t = 'condominium' THEN
      EXECUTE format($f$CREATE POLICY tenant_isolation ON %I
        USING (id = current_setting('app.current_tenant', true)::uuid);$f$, t);
    ELSE
      EXECUTE format($f$CREATE POLICY tenant_isolation ON %I
        USING (condominium_id = current_setting('app.current_tenant', true)::uuid);$f$, t);
    END IF;
  END LOOP;
END $$;
