"use client";

import Link from "next/link";
import { ActivityFeed } from "@/components/ActivityFeed";
import { ReviewQueue } from "@/components/ReviewQueue";
import { useStore } from "@/lib/sim/store";
import { PageHeader, StatCard } from "@/components/ui";

export default function OperatorDashboard() {
  const { state } = useStore();
  const pending = state.reviews.filter((r) => r.status === "pending");
  const escalations = pending.filter((r) => r.kind === "escalation");
  const convosToday = state.conversations.length;
  const answered = state.conversations.filter((c) => c.state === "answered").length;
  const autonomy = convosToday ? Math.round((answered / convosToday) * 100) : 0;

  return (
    <div>
      <PageHeader title="Operations" subtitle={`${state.building.name} · supervisione del fleet di agenti`} />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="In coda di revisione" value={pending.length} hint={`${escalations.length} escalation`} tone="gold" />
        <StatCard label="Conversazioni" value={convosToday} hint={`${answered} risolte`} />
        <StatCard label="Autonomia (auto-risolte)" value={`${autonomy}%`} hint="obiettivo 90%+" tone="sage" />
        <StatCard label="Interventi aperti" value={state.tickets.filter((t) => t.status !== "resolved").length} />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-serif text-lg font-semibold">Coda di revisione</h2>
            <Link href="/operator/reviews" className="text-sm text-clay hover:underline">Apri tutto →</Link>
          </div>
          <ReviewQueue />
        </div>
        <div>
          <h2 className="mb-3 font-serif text-lg font-semibold">Attività recente</h2>
          <div className="card p-2"><ActivityFeed limit={8} /></div>
        </div>
      </div>
    </div>
  );
}
