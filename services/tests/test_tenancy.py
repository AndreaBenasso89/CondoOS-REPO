"""Tenant isolation guardrails."""

from __future__ import annotations

import uuid

import pytest

from condominioos.agents.tools import ToolNotAllowedError, ToolRegistry
from condominioos.common.tenancy import MissingTenantContextError, current_tenant
from condominioos.knowledge import InMemoryKnowledge


def test_no_tenant_context_raises():
    with pytest.raises(MissingTenantContextError):
        current_tenant()


def test_tool_allowlist_default_deny():
    registry = ToolRegistry()
    scoped = registry.scoped("concierge", allowed=("knowledge.query",))
    with pytest.raises(ToolNotAllowedError):
        scoped.call("ledger.post", fields={})


def test_vector_namespace_is_tenant_derived():
    kn = InMemoryKnowledge()
    a, b = uuid.uuid4(), uuid.uuid4()
    assert kn.collection_for(a) != kn.collection_for(b)
    # A query for tenant A never reads tenant B's seeded chunks.
    kn.seed(kn.collection_for(b), [{"text": "segreto del condominio B", "source": "x", "doc_id": "x"}])
    result = kn.query(a, "segreto del condominio")
    assert result.grounded is False
