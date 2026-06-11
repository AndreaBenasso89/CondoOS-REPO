# 10 — C4 Architecture Diagrams (Mermaid)

C4 model levels 1–3 for CondominioOS. (Level 4/code is the repo itself + docs 13/15.)

---

## Level 1 — System Context

```mermaid
C4Context
  title System Context — CondominioOS
  Person(resident, "Resident / Owner", "Lives in / owns a unit")
  Person(admin, "Amministratore (AoR)", "Licensed legal principal & supervisor")
  Person(ops, "Operations Specialist", "Handles escalations & exceptions")
  Person(vendor, "Vendor", "Plumber, electrician, etc.")

  System(condos, "CondominioOS", "AI-first agentic managed service for small condominiums")

  System_Ext(wa, "WhatsApp Business", "Messaging")
  System_Ext(email, "Email / PEC", "Mail & certified mail")
  System_Ext(bank, "Bank feeds", "MT940 / CBI / CSV")
  System_Ext(llm, "Claude / LLM", "Reasoning & language")
  System_Ext(durc, "Public registries", "DURC / P.IVA / insurance checks")
  System_Ext(esign, "e-Signature", "Qualified signature for minutes")

  Rel(resident, condos, "Asks questions, reports issues, pays", "WhatsApp/Email/Web")
  Rel(admin, condos, "Supervises, approves, signs", "Ops Console")
  Rel(ops, condos, "Resolves escalations", "Ops Console")
  Rel(vendor, condos, "Quotes, schedules, updates", "Email/Web")
  Rel(condos, wa, "Sends/receives messages")
  Rel(condos, email, "Sends/receives mail & PEC")
  Rel(condos, bank, "Imports payments")
  Rel(condos, llm, "Calls models")
  Rel(condos, durc, "Verifies vendor/fiscal data")
  Rel(condos, esign, "Signs minutes/docs")
```

## Level 2 — Containers

```mermaid
C4Container
  title Container Diagram — CondominioOS
  Person(resident, "Resident/Owner")
  Person(staff, "AoR / Ops")

  System_Boundary(c, "CondominioOS") {
    Container(residentPortal, "Resident Portal", "Next.js", "Q&A, docs, payments, tickets")
    Container(adminPortal, "Admin Portal", "Next.js", "Registry, accounting, assemblies")
    Container(opsConsole, "Ops Console", "Next.js", "Review queue, approvals, monitoring")
    Container(gateway, "API Gateway", "FastAPI", "AuthN/Z, routing, rate limit, OpenAPI")
    Container(channels, "Channel Adapters", "FastAPI", "WhatsApp/Email/PEC/Web ACL → events")
    Container(runtime, "Agent Runtime", "LangGraph", "Orchestrator + 12 specialized agents")
    Container(firewall, "Reputation Firewall", "Python", "8-layer outbound gate + signed verdicts")
    Container(notif, "Notification Engine", "Python", "ONLY egress; refuses unsigned verdicts")
    Container(knowledge, "Knowledge/RAG", "Python", "Tenant-scoped retrieval + legal corpus")
    Container(domain, "Domain Services", "FastAPI", "registry/accounting/maintenance/vendors/assemblies/compliance/documents")
    Container(review, "Review Service", "FastAPI", "Human-in-the-loop queue")
    Container(audit, "Audit Service", "FastAPI", "Hash-chained immutable log")
    Container(workflows, "Workflow Workers", "Temporal", "Durable sagas")
    ContainerDb(pg, "PostgreSQL", "DB", "Operational data (RLS)")
    ContainerDb(qd, "Qdrant", "Vector DB", "Per-tenant collections")
    ContainerDb(os, "Object Storage", "S3", "Documents")
    ContainerDb(auddb, "Audit DB", "PostgreSQL", "Append-only")
    ContainerQueue(nats, "NATS JetStream", "Bus", "Domain events")
  }
  System_Ext(llm, "Claude / LLM")

  Rel(resident, residentPortal, "Uses", "HTTPS")
  Rel(staff, adminPortal, "Uses", "HTTPS")
  Rel(staff, opsConsole, "Uses", "HTTPS")
  Rel(residentPortal, gateway, "API", "JSON/HTTPS")
  Rel(adminPortal, gateway, "API")
  Rel(opsConsole, gateway, "API")
  Rel(channels, nats, "Publishes message.received")
  Rel(gateway, nats, "Publishes/consumes")
  Rel(runtime, nats, "Consumes events")
  Rel(runtime, llm, "Calls", "via router")
  Rel(runtime, knowledge, "Retrieves")
  Rel(runtime, domain, "Tool calls")
  Rel(runtime, firewall, "Submits drafts/actions")
  Rel(firewall, notif, "Approved + signed verdict")
  Rel(firewall, review, "HOLD → human")
  Rel(notif, channels, "Send approved")
  Rel(domain, pg, "Reads/writes")
  Rel(knowledge, qd, "Searches")
  Rel(domain, os, "Stores docs")
  Rel(audit, auddb, "Appends")
  Rel(workflows, domain, "Orchestrates")
```

## Level 3 — Component: Agent Runtime

```mermaid
C4Component
  title Component Diagram — Agent Runtime
  Container_Boundary(rt, "Agent Runtime (LangGraph)") {
    Component(graph, "Orchestration Graph", "LangGraph StateGraph", "Nodes, edges, interrupts")
    Component(orch, "Orchestrator Node", "Agent", "Intent classify + route")
    Component(agents, "Specialized Agents x12", "Agent nodes", "Concierge, Maintenance, ... Escalation")
    Component(tools, "Tool Registry", "Governed tools", "Default-deny allowlist per agent")
    Component(router, "LLM Router", "Module", "Model select, budget, failover")
    Component(prompts, "Prompt Registry", "Module", "Versioned prompts")
    Component(mem, "Memory Manager", "Module", "Working/episodic/semantic/procedural")
    Component(rfclient, "Firewall Client", "Module", "Submit drafts/actions")
    Component(ckpt, "Checkpointer", "Persistence", "Durable interrupts for HITL")
  }
  Component_Ext(fw, "Reputation Firewall")
  Component_Ext(kn, "Knowledge/RAG")
  Component_Ext(dom, "Domain Services")
  Component_Ext(llm, "Claude/LLM")

  Rel(graph, orch, "Entry")
  Rel(orch, agents, "Routes to")
  Rel(agents, tools, "Calls (scoped)")
  Rel(agents, router, "Generates via")
  Rel(router, llm, "Invokes")
  Rel(agents, prompts, "Loads prompt vN")
  Rel(agents, mem, "Reads/writes")
  Rel(tools, kn, "knowledge.query")
  Rel(tools, dom, "domain tool calls")
  Rel(agents, rfclient, "Submit outbound/action")
  Rel(rfclient, fw, "Gate")
  Rel(graph, ckpt, "Persist interrupts")
```

## Level 3 — Component: Reputation Firewall

```mermaid
C4Component
  title Component Diagram — Reputation Firewall
  Container_Boundary(fw, "Reputation Firewall") {
    Component(pipe, "Guard Pipeline", "Orchestrates L1..L8")
    Component(l1, "L1 Schema & Policy")
    Component(l2, "L2 Grounding/Hallucination")
    Component(l3, "L3 PII & Recipient")
    Component(l4, "L4 Financial Integrity")
    Component(l5, "L5 Legal Safety")
    Component(l6, "L6 Tone & Brand")
    Component(l7, "L7 Risk Scoring")
    Component(l8, "L8 Confidence & Autonomy Gate")
    Component(verdict, "Verdict Signer", "Signs APPROVE/HOLD/BLOCK/REVISE")
    Component(policy, "Policy Store", "autonomy.yaml, banned-phrases, limits")
  }
  Component_Ext(risk, "Risk Agent")
  Component_Ext(kn, "Knowledge (citations)")
  Component_Ext(ledger, "Accounting (reconcile)")
  Component_Ext(review, "Review Service")
  Component_Ext(notif, "Notification Engine")
  Component_Ext(audit, "Audit Service")

  Rel(pipe, l1, ""); Rel(l1, l2, ""); Rel(l2, l3, ""); Rel(l3, l4, "")
  Rel(l4, l5, ""); Rel(l5, l6, ""); Rel(l6, l7, ""); Rel(l7, l8, "")
  Rel(l2, kn, "Verify citations")
  Rel(l4, ledger, "Reconcile amounts")
  Rel(l7, risk, "Composite score")
  Rel(l8, verdict, "Tier → verdict")
  Rel(pipe, policy, "Reads policy")
  Rel(verdict, notif, "APPROVE")
  Rel(verdict, review, "HOLD")
  Rel(pipe, audit, "Logs all layer scores")
```
