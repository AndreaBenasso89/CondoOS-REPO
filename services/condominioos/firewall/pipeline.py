"""The Reputation Firewall pipeline — runs L1..L8, scores confidence, signs the verdict.

This is the single mandatory gate for all outbound. The Notification Engine refuses any artifact
without an APPROVE verdict whose signature + artifact_hash + expiry validate (docs/07 §8).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

from condominioos.audit import audit_log
from condominioos.common.config import get_settings
from condominioos.common.security import artifact_hash, sign_verdict
from condominioos.common.telemetry import get_logger
from condominioos.firewall.contracts import (
    AutonomyTier,
    FirewallVerdict,
    LayerResult,
    OutboundArtifact,
    VerdictType,
)
from condominioos.firewall.layers import ORDERED_GUARDS, GuardContext

log = get_logger("firewall")

_POLICY_PATH = Path(__file__).parent / "policies" / "autonomy.yaml"

# Severity ranking so the strongest layer action wins.
_SEVERITY = {VerdictType.BLOCK: 3, VerdictType.HOLD: 2, VerdictType.REVISE: 1}


class ReputationFirewall:
    def __init__(self, guard_ctx: GuardContext | None = None) -> None:
        self.guard_ctx = guard_ctx or GuardContext()
        self.policy = yaml.safe_load(_POLICY_PATH.read_text())
        self.settings = get_settings()

    # ---- public API -------------------------------------------------------
    def evaluate(self, artifact: OutboundArtifact, *, agent: str, confidence: float,
                 risk_class: str | None = None) -> FirewallVerdict:
        """Run all layers and return a (possibly signed) verdict over the exact artifact."""
        results = [g.check(artifact, self.guard_ctx) for g in ORDERED_GUARDS]
        strongest = self._strongest_hint(results)
        a_hash = artifact_hash(artifact.model_dump(mode="json"))

        # A blocking layer is terminal.
        if strongest == VerdictType.BLOCK:
            return self._finalize(VerdictType.BLOCK, a_hash, results, confidence, None, agent)

        # L8 autonomy gate: derive the required tier from policy + signals.
        tier = self._autonomy_tier(artifact, results, confidence, risk_class)

        # Decide verdict from layer hints + tier.
        if strongest == VerdictType.HOLD or tier in (AutonomyTier.A0, AutonomyTier.A1):
            verdict = VerdictType.HOLD  # route to human review
        elif strongest == VerdictType.REVISE:
            verdict = VerdictType.REVISE
        else:
            verdict = VerdictType.APPROVE

        return self._finalize(verdict, a_hash, results, confidence, tier, agent)

    # ---- internals --------------------------------------------------------
    def _strongest_hint(self, results: list[LayerResult]) -> VerdictType | None:
        hints = [r.verdict_hint for r in results if r.verdict_hint]
        return max(hints, key=lambda v: _SEVERITY[v]) if hints else None

    def _autonomy_tier(self, artifact: OutboundArtifact, results: list[LayerResult],
                       confidence: float, risk_class: str | None) -> AutonomyTier:
        rc = risk_class or self._infer_risk_class(artifact)
        rule = self.policy["risk_classes"].get(rc, self.policy["risk_classes"]["default"])
        if "min_tier" in rule and rule["min_tier"] == "A0":
            return AutonomyTier.A0
        auto = rule.get("auto_if")
        if auto and self._auto_conditions_met(auto, artifact, results, confidence):
            # Even when auto-eligible, a HOLD/REVISE hint downgrades below A2.
            return AutonomyTier.A2 if self._strongest_hint(results) is None else AutonomyTier.A1
        # Fall to the rule's `else` (or A1 by default).
        return AutonomyTier(rule.get("else", "A1"))

    def _auto_conditions_met(self, cond: dict, artifact: OutboundArtifact,
                             results: list[LayerResult], confidence: float) -> bool:
        if "confidence_gte" in cond and confidence < float(cond["confidence_gte"]):
            return False
        if cond.get("risk") == "low":
            risk = next((r for r in results if r.layer == "L7_risk"), None)
            if risk and not risk.passed:
                return False
        if cond.get("grounded") is True:
            g = next((r for r in results if r.layer == "L2_grounding"), None)
            if g and not g.passed:
                return False
        if cond.get("reconciled") is True:
            f = next((r for r in results if r.layer == "L4_financial"), None)
            if f and not f.passed:
                return False
        return True

    def _infer_risk_class(self, artifact: OutboundArtifact) -> str:
        mapping = {
            "reminder": "collections_T1",
            "convocation": "convocation",
            "legal_statement": "legal_statement",
            "financial_action": "financial_post",
            "vendor_message": "vendor_dispatch",
            "message": "faq_grounded",
        }
        return mapping.get(artifact.kind.value, "default")

    def _finalize(self, verdict: VerdictType, a_hash: str, results: list[LayerResult],
                  confidence: float, tier: AutonomyTier | None, agent: str) -> FirewallVerdict:
        v = FirewallVerdict(verdict=verdict, artifact_hash=a_hash, confidence=confidence,
                            autonomy_tier=tier, layer_results=results)
        # Only APPROVE verdicts are signed for the notification engine to honour.
        if verdict == VerdictType.APPROVE:
            expires = (datetime.now(UTC) + timedelta(minutes=15)).isoformat()
            v.expires_at = expires
            v.signature = sign_verdict(a_hash, verdict.value, expires)
        if verdict == VerdictType.REVISE:
            v.revisions = [fix for r in results for fix in r.fixes]
        # Audit-by-design: every verdict (with all layer scores) is recorded immutably.
        audit_log.append(
            actor=f"agent:{agent}", action="firewall.verdict", entity_ref=a_hash,
            payload={"verdict": verdict.value, "tier": tier.value if tier else None,
                     "confidence": confidence,
                     "layer_scores": {r.layer: r.passed for r in results}},
        )
        log.info("firewall.verdict", agent=agent, verdict=verdict, tier=tier,
                 confidence=confidence, hash=a_hash[:18])
        return v
