"""CondominioOS — AI-first agentic managed service for small Italian condominiums.

Package layout:
    common/        cross-cutting: config, tenancy, security, telemetry
    db/            SQLAlchemy models, schema, session (RLS-enforced)
    events/        event catalog + bus client (NATS JetStream)
    firewall/      Reputation Firewall — mandatory outbound gate (8 layers)
    notification/  the ONLY egress to channels (verdict-gated)
    llm/           model router + versioned prompt registry
    agents/        agent fleet (BaseAgent + 13 specialized agents)
    runtime/       LangGraph orchestration graph
    knowledge/     RAG retrieval (tenant-scoped)
    domains/       bounded-context services
    audit/         hash-chained immutable audit log
    review/        human-in-the-loop review queue
    gateway/       FastAPI API gateway
    channels/      WhatsApp/Email/PEC/Web adapters (anti-corruption layer)
    evals/         QA evaluation framework
"""

__version__ = "0.1.0"
