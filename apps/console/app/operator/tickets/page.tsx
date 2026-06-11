"use client";

import { useStore } from "@/lib/sim/store";
import type { Ticket } from "@/lib/sim/types";
import { Badge, Money, PageHeader, timeAgo } from "@/components/ui";

const SEV: Record<Ticket["severity"], "neutral" | "gold" | "red"> = { low: "neutral", medium: "gold", high: "gold", emergency: "red" };

export default function OperatorTickets() {
  const { state } = useStore();
  const unitName = (id: string) => state.units.find((u) => u.id === id)?.identifier ?? id;

  return (
    <div>
      <PageHeader title="Interventi" subtitle="Ticket di manutenzione e dispatch dei fornitori." />
      <div className="card overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead className="bg-cream-100 text-left text-xs uppercase tracking-wide text-ink-faint">
            <tr>
              <th className="px-5 py-3">Problema</th><th className="px-3 py-3">Unità</th>
              <th className="px-3 py-3">Gravità</th><th className="px-3 py-3">Stato</th>
              <th className="px-3 py-3">Fornitore</th><th className="px-3 py-3">Costo</th><th className="px-5 py-3">Creato</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {state.tickets.map((t) => (
              <tr key={t.id} className="hover:bg-cream-100/40">
                <td className="px-5 py-3 font-medium">{t.description}</td>
                <td className="px-3 py-3 text-ink-soft">{unitName(t.unitId)}</td>
                <td className="px-3 py-3"><Badge tone={SEV[t.severity]}>{t.severity}</Badge></td>
                <td className="px-3 py-3"><Badge tone={t.status === "resolved" ? "sage" : t.status === "scheduled" ? "blue" : "neutral"}>{t.status}</Badge></td>
                <td className="px-3 py-3 text-ink-soft">{t.vendor ?? "—"}</td>
                <td className="px-3 py-3">{t.costEur ? <Money value={t.costEur} /> : "—"}</td>
                <td className="px-5 py-3 text-ink-faint">{timeAgo(t.createdAt)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
