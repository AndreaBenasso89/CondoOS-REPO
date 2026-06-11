"use client";

import { useStore } from "@/lib/sim/store";
import { Badge, Money, PageHeader } from "@/components/ui";

export default function Buildings() {
  const { state } = useStore();
  const totalMill = state.units.reduce((s, u) => s + u.millesimi, 0);

  return (
    <div>
      <PageHeader title={state.building.name} subtitle={`${state.building.address} · ${state.building.units} unità · ${totalMill}/1000 millesimi`} />
      <div className="card overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead className="bg-cream-100 text-left text-xs uppercase tracking-wide text-ink-faint">
            <tr>
              <th className="px-5 py-3">Unità</th><th className="px-3 py-3">Piano</th>
              <th className="px-3 py-3">Proprietario</th><th className="px-3 py-3">Residente</th>
              <th className="px-3 py-3">Millesimi</th><th className="px-5 py-3">Saldo</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {state.units.map((u) => (
              <tr key={u.id} className="hover:bg-cream-100/40">
                <td className="px-5 py-3 font-medium">{u.identifier}</td>
                <td className="px-3 py-3 text-ink-soft">{u.floor}</td>
                <td className="px-3 py-3">{u.ownerName}</td>
                <td className="px-3 py-3 text-ink-soft">{u.residentName}</td>
                <td className="px-3 py-3">{u.millesimi}</td>
                <td className="px-5 py-3">{u.balanceEur < 0 ? <Money value={u.balanceEur} /> : <Badge tone="sage">in regola</Badge>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
