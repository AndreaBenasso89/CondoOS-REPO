"""Database session factory that enforces tenant context (RLS).

Every session opened through :func:`tenant_session` sets ``app.current_tenant`` so PostgreSQL
Row-Level Security policies (db/schema.sql) restrict all queries to the active tenant. Opening a
raw session for tenant data is a bug; CI lints for direct ``Session(engine)`` use outside this module.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from condominioos.common.config import get_settings
from condominioos.common.tenancy import current_tenant

_engine = create_engine(get_settings().database_url, pool_pre_ping=True, future=True)
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False, future=True)


@contextmanager
def tenant_session() -> Iterator[Session]:
    """Yield a session bound to the current tenant; sets the RLS GUC for the transaction."""
    ctx = current_tenant()  # raises if no tenant context — by design
    session = _SessionLocal()
    try:
        session.execute(
            text("SET LOCAL app.current_tenant = :tid"), {"tid": str(ctx.condominium_id)}
        )
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
