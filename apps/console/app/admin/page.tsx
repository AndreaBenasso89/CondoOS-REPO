"use client";

import { AlertTriangle } from "lucide-react";
import Link from "next/link";
import { ActivityFeed } from "@/components/ActivityFeed";
import { useStore } from "@/lib/sim/store";
import { Badge, Money, PageHeader, StatCard } from "@/components/ui";

export default function AdminDashboard() {
  const { state } = useStore();
  const arrears = state.units.reduce((s, u) => s + Math.min(0, u.balanceEur), 0);
  const openAlerts = state.compliance.filter((a) => a.status !== "resolved");
  const pendingApprovals = state.reviews.filter((r) => r.status === "pending");

  return (
    <div>
      <PageHeader title="Amministrazione" subtitle={`${state.building.name} · ${state.building.address}`} />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Unità" value={state.building.units} hint={state.building.plan} />
        <StatCard label="Morosità totale" value={<Money value={arrears} />} hint={`${state.units.filter((u) => u.balanceEur < 0).length} unità a debito`} tone="red" />
        <StatCard label="Scadenze aperte" value={openAlerts.length} hint={`${openAlerts.filter((a) => a.severity === "high").length} ad alta priorità`} tone="gold" />
        <StatCard label="Approvazioni in attesa" value={pendingApprovals.length} hint="da firmare/approvare" tone="gold" />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_1fr]">
        <div>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-serif text-lg font-semibold">Scadenze & compliance</h2>
            <Link href="/admin/compliance" className="text-sm text-clay hover:underline">Tutte →</Link>
          </div>
          <div className="card divide-y divide-line p-0">
            {openAlerts.map((a) => (
              <div key={a.id} className="flex items-center gap-3 px-5 py-3.5">
                <AlertTriangle size={16} className={a.severity === "high" ? "text-red-600" : "text-gold"} />
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-medium">{a.kind}</div>
                  <div className="text-xs text-ink-faint">scadenza {new Date(a.dueDate).toLocaleDateString("it-IT")}</div>
                </div>
                <Badge tone={a.status === "remediating" ? "blue" : "gold"}>{a.status}</Badge>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h2 className="mb-3 font-serif text-lg font-semibold">Attività recente</h2>
          <div className="card p-2"><ActivityFeed limit={8} /></div>
        </div>
      </div>
    </div>
  );
}
