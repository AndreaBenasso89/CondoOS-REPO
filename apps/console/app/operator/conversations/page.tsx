"use client";

import { Bot, User } from "lucide-react";
import { useState } from "react";
import { useStore } from "@/lib/sim/store";
import { Badge, EmptyState, PageHeader, cn, timeAgo } from "@/components/ui";

export default function Conversations() {
  const { state } = useStore();
  const [activeId, setActiveId] = useState<string | null>(state.conversations[0]?.id ?? null);
  const active = state.conversations.find((c) => c.id === activeId);

  return (
    <div>
      <PageHeader title="Conversazioni" subtitle="Tutte le conversazioni dei residenti del condominio (visibilità completa per Operations)." />
      {state.conversations.length === 0 ? (
        <EmptyState title="Nessuna conversazione" />
      ) : (
        <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
          <div className="card max-h-[64vh] overflow-y-auto p-0">
            {state.conversations.map((c) => (
              <button
                key={c.id} onClick={() => setActiveId(c.id)}
                className={cn("flex w-full flex-col gap-1 border-b border-line px-4 py-3 text-left hover:bg-cream-100/60", c.id === activeId && "bg-cream-100")}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-sm font-medium">{c.residentName}</span>
                  <span className="text-xs text-ink-faint">{timeAgo(c.updatedAt)}</span>
                </div>
                <span className="truncate text-xs text-ink-faint">{c.subject}</span>
                <Badge tone={c.state === "answered" ? "sage" : c.state === "escalated" ? "gold" : "neutral"}>{c.state}</Badge>
              </button>
            ))}
          </div>

          <div className="card p-5">
            {active ? (
              <>
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <div className="font-medium">{active.residentName}</div>
                    <div className="text-xs text-ink-faint">{active.channel} · intent {active.intent}</div>
                  </div>
                  <Badge tone="neutral">{active.state}</Badge>
                </div>
                <div className="space-y-3">
                  {active.messages.map((m) => (
                    <div key={m.id} className={cn("flex gap-3", m.role === "resident" && "flex-row-reverse")}>
                      <div className={cn("grid h-7 w-7 shrink-0 place-items-center rounded-lg", m.role === "resident" ? "bg-cream-200 text-ink-soft" : "bg-clay-50 text-clay-700")}>
                        {m.role === "resident" ? <User size={14} /> : <Bot size={14} />}
                      </div>
                      <div className={cn("max-w-[78%] rounded-2xl px-3.5 py-2 text-sm", m.role === "resident" ? "bg-cream-100" : "bg-clay/10")}>
                        {m.text}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : <p className="text-sm text-ink-faint">Seleziona una conversazione.</p>}
          </div>
        </div>
      )}
    </div>
  );
}
