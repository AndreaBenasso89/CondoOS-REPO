# 06 — Security Architecture

Defense-in-depth for a multi-tenant, agentic, GDPR-regulated FinTech/PropTech platform.

---

## 1. Threat model (STRIDE, abridged)

| Threat | Vector | Primary controls |
|---|---|---|
| **Spoofing** | Fake resident on WhatsApp/email; channel impersonation | Channel identity binding, verified onboarding, step-up auth for sensitive actions. |
| **Tampering** | Altered invoices, forged minutes, audit edits | Hash-chained audit, immutable storage versions, signed documents. |
| **Repudiation** | "I never authorized that" | Full audit trail, reproducible agent runs, signed approvals. |
| **Information disclosure** | Cross-tenant leak, PII in prompts, RAG bleed | RLS, per-tenant vector namespaces, PII minimization, output filtering. |
| **Denial of service** | Channel flooding, token-cost bombs | Rate limits, per-tenant budgets, circuit breakers. |
| **Elevation of privilege** | Prompt injection → tool abuse | Tool authz scoping, allowlists, the Reputation Firewall, human gates. |

## 2. Identity, authn & authz

- **Humans:** OIDC (e.g., Auth0/Keycloak), MFA mandatory for AoR/Ops/Compliance; SSO for staff.
- **Residents/owners:** passwordless (magic link / OTP) + channel identity (verified phone/email).
- **Services:** mTLS + short-lived workload identities (SPIFFE-style); no long-lived secrets in code.
- **Authorization:** RBAC + ABAC. Role × tenant × resource. Agents run under a **scoped service
  principal** limited to their bounded context's tools and their task's tenant.
- **Tenant context propagation:** every request/agent-run carries a signed tenant+actor context;
  DB sessions set `SET app.current_tenant` enabling RLS.

## 3. Agent & tool security (the new attack surface)

This is the highest-leverage section for an agentic system.

1. **Tool authorization:** each agent has an explicit **tool allowlist** scoped to its bounded
   context. Tools declare required scopes; the runtime denies out-of-scope calls (default-deny).
2. **Prompt-injection defense:**
   - Untrusted content (emails, docs, WhatsApp, web) is **quarantined and labeled** before reaching a
     model; it is never concatenated as trusted instructions.
   - **Instruction/data separation:** system + developer prompts are signed/templated; external
     content is clearly delimited and treated as data.
   - Tool-call **arguments are validated** against schemas; no free-form shell/SQL from model output.
   - High-impact tools require the Reputation Firewall + human tier regardless of model "intent".
3. **Output handling:** model output is never executed; it is parsed into typed actions, validated,
   then gated.
4. **Budget & loop guards:** per-task token/cost ceilings, max tool calls, recursion/loop detection
   (Orchestrator), kill-switch per agent/tenant.
5. **Data minimization in prompts:** PII-minimizing context assembler — only fields the task needs,
   redacted where possible, with a per-prompt PII budget.
6. **Egress control:** agents have no arbitrary internet/tool access; only registered, audited tools.

## 4. Secrets, keys & crypto

- Secrets in a managed vault (e.g., HashiCorp Vault / cloud KMS); injected at runtime, never in repo
  or images.
- Encryption in transit (TLS 1.3 everywhere) and at rest (DB, object storage, backups).
- Per-tenant data keys for object storage (enables crypto-shredding on erasure).
- Document signing for minutes/official PDFs (qualified e-signature integration for legal validity).

## 5. Network & runtime

- Private VPC; databases not publicly reachable; egress allowlist.
- Service mesh (mTLS, mutual authz) between microservices.
- WAF + rate limiting at the API Gateway; bot/abuse protection on public channels.
- Container hardening: distroless/minimal images, non-root, read-only FS, image signing + scanning,
  SBOM, pinned dependencies.

## 6. GDPR controls (see also doc 07 §GDPR & doc 05 §6–7)

- **Lawful basis** per processing activity (contract, legal obligation, legitimate interest).
- **Data residency:** EU regions only; LLM provider configured for EU/no-train, zero-retention where
  available; DPAs with all sub-processors.
- **Data minimization:** enforced at prompt assembly and logging (no PII in plain telemetry).
- **DSAR tooling:** export & erasure workflows; consent registry; processing register (Art. 30).
- **DPIA:** maintained for the automated decision-making and profiling aspects (collections, risk).
- **Right not to be subject to solely automated decisions** with legal effect: collections T2/T3 and
  any adverse decision require human involvement (already enforced by autonomy tiers).

## 7. Auditing, logging & monitoring

- **Audit (immutable):** hash-chained `audit_event` for every decision/action (doc 05 §4).
- **Observability:** OpenTelemetry traces spanning channel → agent → tool → DB; structured logs with
  tenant+trace ids (PII-scrubbed); metrics & dashboards.
- **Security monitoring:** anomaly detection on tool usage, cross-tenant access attempts, prompt-
  injection signatures, abnormal egress, budget spikes → SIEM + alerts.
- **Tamper evidence:** periodic audit-chain verification job; alerts on break.

## 8. Secure SDLC

- Branch protection, mandatory review, signed commits.
- SAST + dependency scanning + secret scanning in CI; IaC scanning (tfsec/checkov).
- Pre-merge: tests, lint, typecheck, **agent eval gate** (QA Agent rubrics) and **firewall regression
  suite** must pass.
- Staged rollout per tenant (supervised → autonomous) with kill-switch and fast rollback.

## 9. Incident response

- Severity classes (data breach, wrongful communication, financial error, outage).
- Runbooks per class; **wrongful-communication runbook** is first-class (retraction message,
  apology, root-cause, eval case, tenant-level autonomy rollback).
- 72-hour GDPR breach notification process pre-wired; DPO contact and templates ready.

## 10. Security responsibilities mapped to agents

| Concern | Owner |
|---|---|
| Output safety / leakage | Reputation Firewall + Concierge/Document agents |
| Risk scoring of actions | Risk Agent |
| PII detection/redaction | Document Agent + prompt assembler |
| Release safety gate | QA Agent |
| Tenant isolation | Platform (RLS, namespaces) — enforced, not agent-trusted |
