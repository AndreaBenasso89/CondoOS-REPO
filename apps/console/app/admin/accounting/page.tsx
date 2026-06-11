"use client";

import { useStore } from "@/lib/sim/store";
import type { Invoice } from "@/lib/sim/types";
import { Badge, Money, PageHeader, StatCard } from "@/components/ui";

const ST: Record<Invoice["status"], "neutral" | "sage" | "blue" | "gold" | "red"> = {
  extracted: "neutral", validated: "blue", posted: "sage", paid: "sage", anomaly: "red",
};

export default function Accounting() {
  const { state } = useStore();
  const total = state.invoices.reduce((s, i) => s + i.amountGross, 0);
  const anomalies = state.invoices.filter((i) => i.status === "anomaly").length;

  return (
    <div>
      <PageHeader title="Contabilità" subtitle="Fatture passive elaborate dall'Accounting Agent (OCR → validazione → registrazione)." />
      <div className="mb-5 grid gap-4 sm:grid-cols-3">
        <StatCard label="Fatture nel periodo" value={state.invoices.length} />
        <StatCard label="Totale lordo" value={<Money value={total} />} />
        <StatCard label="Anomalie da rivedere" value={anomalies} tone="red" hint={anomalies ? "richiede attenzione" : "nessuna"} />
      </div>
      <div className="card overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead className="bg-cream-100 text-left text-xs uppercase tracking-wide text-ink-faint">
            <tr>
              <th className="px-5 py-3">Fornitore</th><th className="px-3 py-3">Numero</th>
              <th className="px-3 py-3">Conto (CoA)</th><th className="px-3 py-3">Importo</th>
              <th className="px-5 py-3">Stato</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {state.invoices.map((i) => (
              <tr key={i.id} className="hover:bg-cream-100/40">
                <td className="px-5 py-3 font-medium">{i.vendor}</td>
                <td className="px-3 py-3 text-ink-soft">{i.number}</td>
                <td className="px-3 py-3 text-ink-soft">{i.coa}</td>
                <td className="px-3 py-3"><Money value={i.amountGross} /></td>
                <td className="px-5 py-3"><Badge tone={ST[i.status]}>{i.status}</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
