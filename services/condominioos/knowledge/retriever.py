"""Tenant-scoped RAG retriever (docs/05 §5).

Hybrid retrieval over a per-tenant Qdrant collection plus a shared, read-only legal corpus.
Cross-tenant retrieval is impossible by construction: the collection name is derived from the
authenticated tenant id, never from user input. Returns grounded facts + citations + coverage, or an
honest miss.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from condominioos.common.telemetry import get_logger

log = get_logger("knowledge")


class RetrievedCitation(BaseModel):
    doc_id: str
    span: str | None = None


class RetrievedFact(BaseModel):
    text: str
    source: str | None = None


class RetrievalResult(BaseModel):
    grounded: bool
    coverage: float = 0.0
    context: str = ""
    facts: list[RetrievedFact] = Field(default_factory=list)
    citations: list[RetrievedCitation] = Field(default_factory=list)


class KnowledgeRetriever:
    """Abstract retriever; the in-memory impl backs the skeleton, Qdrant backs prod."""

    def collection_for(self, tenant_id: uuid.UUID) -> str:
        return f"kb_tenant_{tenant_id}"

    def query(self, tenant_id: uuid.UUID, question: str, *, min_coverage: float = 0.5) -> RetrievalResult:
        chunks = self._search(self.collection_for(tenant_id), question)
        chunks += self._search("kb_legal_corpus", question)
        if not chunks:
            log.info("knowledge.miss", tenant=str(tenant_id))
            return RetrievalResult(grounded=False, coverage=0.0)
        # Coverage rises with the number of relevant chunks; a single strong hit already grounds.
        coverage = min(1.0, 0.5 + 0.25 * len(chunks))
        facts = [RetrievedFact(text=c["text"], source=c["source"]) for c in chunks]
        cites = [RetrievedCitation(doc_id=c["doc_id"], span=c.get("span")) for c in chunks]
        context = "\n".join(f"- {c['text']} ({c['source']})" for c in chunks)
        return RetrievalResult(grounded=coverage >= min_coverage, coverage=coverage,
                               context=context, facts=facts, citations=cites)

    # In-memory stub corpus; replaced by Qdrant hybrid search in prod.
    def _search(self, collection: str, question: str) -> list[dict]:
        return []


class InMemoryKnowledge(KnowledgeRetriever):
    """Seeded corpus for local dev/tests."""

    def __init__(self, corpus: dict[str, list[dict]] | None = None) -> None:
        self._corpus = corpus or {}

    def seed(self, collection: str, chunks: list[dict]) -> None:
        self._corpus.setdefault(collection, []).extend(chunks)

    def _search(self, collection: str, question: str) -> list[dict]:
        q = question.lower()
        return [c for c in self._corpus.get(collection, [])
                if any(tok in c["text"].lower() for tok in q.split() if len(tok) > 3)][:3]
