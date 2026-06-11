"""Central configuration. 12-factor: all config from environment (see .env.example)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings. EU-only data residency is assumed by deployment, not toggled here."""

    model_config = SettingsConfigDict(env_prefix="CONDOOS_", env_file=".env", extra="ignore")

    environment: str = Field(default="dev")  # dev | staging | prod
    service_name: str = Field(default="condominioos")

    # Datastores
    database_url: str = Field(default="postgresql+psycopg://condoos:condoos@localhost:5432/condoos")
    audit_database_url: str = Field(
        default="postgresql+psycopg://condoos:condoos@localhost:5432/condoos_audit"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")
    qdrant_url: str = Field(default="http://localhost:6333")
    object_store_endpoint: str = Field(default="http://localhost:9000")
    object_store_bucket: str = Field(default="condoos-documents")

    # Messaging
    nats_url: str = Field(default="nats://localhost:4222")

    # LLM
    anthropic_api_key: str = Field(default="")
    llm_primary_model: str = Field(default="claude-opus-4-8")
    llm_fast_model: str = Field(default="claude-haiku-4-5-20251001")
    llm_eu_region_only: bool = Field(default=True)

    # Governance / safety
    firewall_revise_max_loops: int = Field(default=2)
    default_autonomy_mode: str = Field(default="supervised")  # supervised | ramping | autonomous
    per_task_token_budget: int = Field(default=200_000)
    per_tenant_daily_cost_eur: float = Field(default=5.0)

    # Security
    jwt_audience: str = Field(default="condominioos")
    jwt_issuer: str = Field(default="https://auth.condominioos.eu/")
    verdict_signing_key: str = Field(default="dev-insecure-signing-key-change-me")


@lru_cache
def get_settings() -> Settings:
    return Settings()
