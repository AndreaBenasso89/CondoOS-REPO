"""LLM router — model selection, budget enforcement, and failover.

Selects a model by task class (reasoning vs fast), enforces per-task token budgets, and supports a
degraded "human-only" mode if the provider is unavailable. Claude is the primary provider; the call
site is abstracted so tests run without network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from condominioos.common.config import get_settings
from condominioos.common.telemetry import get_logger

log = get_logger("llm.router")


class TaskClass(StrEnum):
    REASONING = "reasoning"  # planning, drafting, legal-aware text -> primary model
    FAST = "fast"            # classification, extraction -> fast model


@dataclass
class LLMResult:
    text: str
    model: str
    tokens: int
    cost_eur: float


class BudgetExceededError(RuntimeError):
    pass


class LLMRouter:
    def __init__(self, *, offline: bool = False) -> None:
        self.settings = get_settings()
        self.offline = offline or not self.settings.anthropic_api_key
        self._spent_tokens = 0

    def model_for(self, task: TaskClass) -> str:
        return (self.settings.llm_primary_model if task == TaskClass.REASONING
                else self.settings.llm_fast_model)

    async def complete(self, *, system: str, prompt: str, task: TaskClass,
                       max_tokens: int = 1024) -> LLMResult:
        if self._spent_tokens + max_tokens > self.settings.per_task_token_budget:
            raise BudgetExceededError("per-task token budget exceeded")
        model = self.model_for(task)
        if self.offline:
            # Deterministic stub so the skeleton runs end-to-end without a key.
            text = f"[stub:{model}] {prompt[:120]}"
            self._spent_tokens += 32
            return LLMResult(text=text, model=model, tokens=32, cost_eur=0.0)
        # Real call (Anthropic) — wired in Sprint 3; kept abstract here.
        from anthropic import AsyncAnthropic  # local import keeps offline path dependency-free

        client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)
        resp = await client.messages.create(
            model=model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in resp.content if block.type == "text")
        tokens = resp.usage.input_tokens + resp.usage.output_tokens
        self._spent_tokens += tokens
        log.info("llm.complete", model=model, tokens=tokens)
        return LLMResult(text=text, model=model, tokens=tokens, cost_eur=0.0)
