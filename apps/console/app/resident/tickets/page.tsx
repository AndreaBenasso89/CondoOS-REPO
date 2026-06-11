"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { useStore } from "@/lib/sim/store";
import type { Ticket } from "@/lib/sim/types";
import { Badge, PageHeader, timeAgo } from "@/components/ui";

const SEV: Record<Ticket["severity"], { label: string; tone: "neutral" | "gold" | "red" }> = {
  low: { label: "bassa", tone: "neutral" },
  medium: { label: "media", tone: "gold" },
  high: { label: "alta", tone: "gold" },
  emergency: { label: "emergenza", tone: "red" },
};

export default function Tickets() {
  const { persona } = useAuth();
  const { state, reportTicket } = useStore();
  const [desc, setDesc] = useState("");
  const mine = state.tickets.filter((t) => t.unitId === persona?.unitId);

  return (
    <div>
      <PageHeader title="Segnalazioni" subtitle="Apri un ticket: l'agente lo classifica e, se serve, invia un tecnico." />
      <form
        className="card mb-5 flex flex-col gap-3 p-4 sm:flex-row"
        onSubmit={(e) => { e.preventDefault(); if (desc.trim() && persona) { reportTicket(persona, desc); setDesc(""); } }}
      >
        <input className="input" placeholder="Descrivi il problema (es. perdita d'acqua, citofono rotto…)" value={desc} onChange={(e) => setDesc(e.target.value)} />
        <button className="btn-primary shrink-0" type="submit">Invia segnalazione</button>
      </form>

      <div className="card divide-y divide-line p-0">
        {mine.length === 0 && <div className="p-6 text-sm text-ink-faint">Nessuna segnalazione.</div>}
        {mine.map((t) => (
          <div key={t.id} className="flex items-center justify-between gap-3 px-5 py-4">
            <div className="min-w-0">
              <div className="truncate font-medium">{t.description}</div>
              <div className="text-xs text-ink-faint">{t.category} · {timeAgo(t.createdAt)}{t.vendor ? ` · ${t.vendor}` : ""}</div>
            </div>
            <div className="flex items-center gap-2">
              <Badge tone={SEV[t.severity].tone}>{SEV[t.severity].label}</Badge>
              <Badge tone={t.status === "resolved" ? "sage" : t.status === "scheduled" ? "blue" : "neutral"}>{t.status}</Badge>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
