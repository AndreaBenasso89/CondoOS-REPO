"use client";

import { ReviewQueue } from "@/components/ReviewQueue";
import { useStore } from "@/lib/sim/store";
import { Badge, PageHeader, TierBadge, timeAgo } from "@/components/ui";

export default function Reviews() {
  const { state } = useStore();
  const decided = state.reviews.filter((r) => r.status !== "pending").slice(0, 10);

  return (
    <div>
      <PageHeader
        title="Coda di revisione"
        subtitle="Ogni messaggio fermato dal Reputation Firewall arriva qui. Niente esce senza che una persona lo veda."
      />
      <ReviewQueue />

      {decided.length > 0 && (
        <>
          <h2 className="mb-3 mt-8 font-serif text-lg font-semibold">Decisioni recenti</h2>
          <div className="card divide-y divide-line p-0">
            {decided.map((r) => (
              <div key={r.id} className="flex items-center justify-between gap-3 px-5 py-3">
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium">{r.title}</div>
                  <div className="text-xs text-ink-faint">{r.decidedBy} · {r.decidedAt ? timeAgo(r.decidedAt) : ""}</div>
                </div>
                <div className="flex items-center gap-2">
                  <TierBadge tier={r.tier} />
                  <Badge tone={r.status === "approved" ? "sage" : r.status === "rejected" ? "red" : "gold"}>
                    {r.status === "approved" ? "approvata" : r.status === "rejected" ? "respinta" : "riassegnata"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
