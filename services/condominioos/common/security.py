"""Security primitives: verdict signing (firewall ↔ notification trust) and hashing helpers.

The Notification Engine trusts only artifacts accompanied by a valid, unexpired, signed firewall
verdict whose ``artifact_hash`` matches the exact payload (see docs/07 §8). This module provides the
HMAC signing used for that trust boundary. In production, replace the static key with a KMS-managed
key and consider asymmetric signatures.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from condominioos.common.config import get_settings


def canonical_json(payload: Any) -> str:
    """Deterministic JSON for hashing/signing (sorted keys, no whitespace).

    ``default=str`` makes audit/hashing tolerant of UUID, datetime, Decimal, etc. so a stray
    non-JSON-native value in a payload can never crash the audit log or verdict signing.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      default=str)


def artifact_hash(payload: Any) -> str:
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def sign_verdict(artifact_hash_value: str, verdict: str, expires_at: str) -> str:
    """HMAC-sign a verdict over (artifact_hash, verdict, expiry)."""
    key = get_settings().verdict_signing_key.encode("utf-8")
    msg = f"{artifact_hash_value}|{verdict}|{expires_at}".encode()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def verify_verdict(artifact_hash_value: str, verdict: str, expires_at: str, signature: str) -> bool:
    expected = sign_verdict(artifact_hash_value, verdict, expires_at)
    return hmac.compare_digest(expected, signature)
