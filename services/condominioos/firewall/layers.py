"""The eight guard layers of the Reputation Firewall (docs/07 §2).

Each layer implements :meth:`Guard.check` and returns a :class:`LayerResult`. The pipeline runs them
in order; the strongest action wins. Layers are intentionally explicit and testable — the heavy
ML/LLM checks (grounding NLI, tone classifier, risk model) are injected via callables so they can be
stubbed in the skeleton and swapped for real models without touching the pipeline.

Severity ordering for `verdict_hint`: BLOCK > HOLD > REVISE > (pass).
"""

from __future__ import annotations

from typing import Protocol

from condominioos.firewall.contracts import LayerResult, OutboundArtifact, VerdictType

# Banned phrases that imply unfounded legal threats below the legal tier (L5/L6).
BANNED_LEGAL_THREATS = ("vi denuncio", "azione legale immediata", "pignoramento", "decreto ingiuntivo")


class Guard(Protocol):
    name: str

    def check(self, artifact: OutboundArtifact, ctx: GuardContext) -> LayerResult: ...


class GuardContext:
    """Dependencies injected into guards (resolvers for ledger, recipient, risk, etc.)."""

    def __init__(
        self,
        *,
        recipient_unit_resolver=None,   # callable(recipient) -> expected unit_id
        ledger_balance_resolver=None,   # callable(recipient) -> Decimal/float owed
        risk_scorer=None,               # callable(artifact) -> ("low"|"medium"|"high", float)
        grounding_verifier=None,        # callable(claim, citations) -> bool
        tone_scorer=None,               # callable(text) -> float (0..1)
        last_reminder_days=None,        # callable(recipient) -> int | None
        cooldown_days: int = 14,
    ) -> None:
        self.recipient_unit_resolver = recipient_unit_resolver
        self.ledger_balance_resolver = ledger_balance_resolver
        self.risk_scorer = risk_scorer
        self.grounding_verifier = grounding_verifier or (lambda claim, cites: bool(claim.source))
        self.tone_scorer = tone_scorer or (lambda text: 0.95)
        self.last_reminder_days = last_reminder_days
        self.cooldown_days = cooldown_days


# --------------------------------------------------------------------------- L1
class SchemaPolicyGuard:
    name = "L1_schema_policy"

    def check(self, artifact: OutboundArtifact, ctx: GuardContext) -> LayerResult:
        reasons: list[str] = []
        if artifact.kind.value in {"message", "reminder", "vendor_message"} and not artifact.channel:
            reasons.append("missing channel for a communication artifact")
        if artifact.kind.value in {"message", "reminder"} and artifact.recipient is None:
            reasons.append("missing recipient")
        if not artifact.text.strip() and artifact.kind != artifact.kind.FINANCIAL_ACTION:
            reasons.append("empty body")
        passed = not reasons
        return LayerResult(layer=self.name, passed=passed,
                           verdict_hint=None if passed else VerdictType.BLOCK, reasons=reasons)


# --------------------------------------------------------------------------- L2
class GroundingGuard:
    name = "L2_grounding"

    def check(self, artifact: OutboundArtifact, ctx: GuardContext) -> LayerResult:
        if not artifact.claims:
            return LayerResult(layer=self.name, passed=True, score=1.0)
        grounded = [c for c in artifact.claims if ctx.grounding_verifier(c, artifact.citations)]
        coverage = len(grounded) / len(artifact.claims)
        ungrounded = [c.text for c in artifact.claims if c not in grounded]
        if coverage >= 0.999:
            return LayerResult(layer=self.name, passed=True, score=coverage)
        # Some claims unsupported: strip them (REVISE), or HOLD if that guts the message.
        hint = VerdictType.REVISE if coverage >= 0.5 else VerdictType.HOLD
        return LayerResult(layer=self.name, passed=False, score=coverage, verdict_hint=hint,
                           reasons=[f"ungrounded claims: {ungrounded}"],
                           fixes=["remove unsupported claims or attach citations"])


# --------------------------------------------------------------------------- L3
class RecipientPiiGuard:
    name = "L3_pii_recipient"

    def check(self, artifact: OutboundArtifact, ctx: GuardContext) -> LayerResult:
        r = artifact.recipient
        if r is None:
            return LayerResult(layer=self.name, passed=True)
        reasons: list[str] = []
        # Wrong-recipient is a hard BLOCK (top reputational/GDPR risk).
        if ctx.recipient_unit_resolver and r.unit_id is not None:
            expected = ctx.recipient_unit_resolver(r)
            if expected is not None and expected != r.unit_id:
                reasons.append("recipient unit mismatch — refusing to send to wrong unit")
        # Sensitive data over insecure channel.
        if artifact.financials and artifact.channel == "whatsapp" and artifact.financials.iban:
            reasons.append("IBAN over WhatsApp — disallowed channel for this PII")
        passed = not reasons
        return LayerResult(layer=self.name, passed=passed,
                           verdict_hint=None if passed else VerdictType.BLOCK, reasons=reasons)


# --------------------------------------------------------------------------- L4
class FinancialIntegrityGuard:
    name = "L4_financial"

    def check(self, artifact: OutboundArtifact, ctx: GuardContext) -> LayerResult:
        f = artifact.financials
        if f is None:
            return LayerResult(layer=self.name, passed=True)
        reasons: list[str] = []
        # Reconciliation gate: amount must equal the ledger balance exactly (no over-collection).
        ledger = f.ledger_balance
        if ctx.ledger_balance_resolver and artifact.recipient is not None:
            ledger = ctx.ledger_balance_resolver(artifact.recipient)
        if ledger is None:
            reasons.append("no reconciled ledger balance — cannot assert an amount owed")
        elif round(float(ledger), 2) != round(float(f.amount), 2):
            reasons.append(f"amount {f.amount} != reconciled balance {ledger} (over/under-collection)")
        # Reminder cadence (anti-harassment).
        if artifact.kind.value == "reminder" and ctx.last_reminder_days and artifact.recipient:
            days = ctx.last_reminder_days(artifact.recipient)
            if days is not None and days < ctx.cooldown_days:
                reasons.append(f"reminder cooldown not elapsed ({days}d < {ctx.cooldown_days}d)")
        passed = not reasons
        return LayerResult(layer=self.name, passed=passed,
                           verdict_hint=None if passed else VerdictType.BLOCK, reasons=reasons)


# --------------------------------------------------------------------------- L5
class LegalSafetyGuard:
    name = "L5_legal"

    def check(self, artifact: OutboundArtifact, ctx: GuardContext) -> LayerResult:
        reasons: list[str] = []
        text = artifact.text.lower()
        # No unfounded legal threats outside the legal tier.
        if artifact.kind.value != "legal_statement":
            for phrase in BANNED_LEGAL_THREATS:
                if phrase in text:
                    reasons.append(f"legal-threat language '{phrase}' outside legal tier")
        # Any explicit legal statement must be human-led.
        if artifact.kind.value == "legal_statement":
            return LayerResult(layer=self.name, passed=False, verdict_hint=VerdictType.HOLD,
                               reasons=["legal statement requires AoR (A0)"])
        # Convocation must carry required legal content (delegated to assemblies validator).
        passed = not reasons
        return LayerResult(layer=self.name, passed=passed,
                           verdict_hint=None if passed else VerdictType.HOLD, reasons=reasons)


# --------------------------------------------------------------------------- L6
class ToneBrandGuard:
    name = "L6_tone"

    def check(self, artifact: OutboundArtifact, ctx: GuardContext) -> LayerResult:
        score = ctx.tone_scorer(artifact.text)
        if score >= 0.7:
            return LayerResult(layer=self.name, passed=True, score=score)
        return LayerResult(layer=self.name, passed=False, score=score, verdict_hint=VerdictType.REVISE,
                           reasons=["tone below brand threshold"],
                           fixes=["rewrite in a professional, empathetic Italian register"])


# --------------------------------------------------------------------------- L7
class RiskScoringGuard:
    name = "L7_risk"

    def check(self, artifact: OutboundArtifact, ctx: GuardContext) -> LayerResult:
        if ctx.risk_scorer is None:
            return LayerResult(layer=self.name, passed=True, score=0.0)
        level, score = ctx.risk_scorer(artifact)
        # Risk never blocks here; it raises the tier in L8 via reasons. High risk → HOLD hint.
        hint = VerdictType.HOLD if level == "high" else None
        return LayerResult(layer=self.name, passed=(level != "high"), score=score,
                           verdict_hint=hint, reasons=[f"risk={level}"])


# L8 (autonomy gate) is implemented in pipeline.py because it consumes the policy + all prior results.

ORDERED_GUARDS: list[Guard] = [
    SchemaPolicyGuard(),
    GroundingGuard(),
    RecipientPiiGuard(),
    FinancialIntegrityGuard(),
    LegalSafetyGuard(),
    ToneBrandGuard(),
    RiskScoringGuard(),
]
