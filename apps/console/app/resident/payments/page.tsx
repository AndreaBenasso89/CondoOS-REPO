"use client";

import { useAuth } from "@/lib/auth";
import { useStore } from "@/lib/sim/store";
import { Badge, Card, Money, PageHeader } from "@/components/ui";

export default function Payments() {
  const { persona } = useAuth();
  const { state, log } = useStore();
  const unit = state.units.find((u) => u.id === persona?.unitId);
  const owed = unit ? Math.max(0, -unit.balanceEur) : 0;

  // Illustrative charge breakdown derived from the unit's millesimi.
  const charges = [
    { label: "Quota ordinaria 2° trimestre", amount: 95 },
    { label: "Conguaglio riscaldamento", amount: 45 },
    { label: "Fondo cassa straordinario", amount: 100 },
  ];

  return (
    <div>
      <PageHeader title="Pagamenti" subtitle={`${unit?.identifier ?? ""} · millesimi ${unit?.millesimi ?? "—"}`} />
      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <div className="card p-0">
          <div className="border-b border-line px-5 py-3 label">Quote del periodo</div>
          <div className="divide-y divide-line">
            {charges.map((c) => (
              <div key={c.label} className="flex items-center justify-between px-5 py-3 text-sm">
                <span>{c.label}</span><span className="font-medium"><Money value={c.amount} /></span>
              </div>
            ))}
          </div>
        </div>
        <Card>
          <div className="label">Saldo attuale</div>
          <div className="mt-1 text-3xl font-semibold"><Money value={unit?.balanceEur ?? 0} /></div>
          {owed > 0 ? (
            <>
              <p className="mt-2 text-sm text-ink-soft">Importo da regolarizzare: <b><Money value={owed} /></b></p>
              <button
                className="btn-primary mt-3 w-full"
                onClick={() => { if (persona) log({ actor: persona.name, actorRole: "resident", action: "Pagamento simulato", detail: `Saldo €${owed.toFixed(2)} — bonifico avviato`, entity: `payment:${persona.unitId}` }); alert("Pagamento simulato avviato. Verrà riconciliato dall'Accounting Agent."); }}
              >
                Paga €{owed.toFixed(2)}
              </button>
            </>
          ) : (
            <Badge tone="sage">In regola</Badge>
          )}
        </Card>
      </div>
    </div>
  );
}
