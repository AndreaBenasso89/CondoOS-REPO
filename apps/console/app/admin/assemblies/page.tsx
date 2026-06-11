"use client";

import { ReviewQueue } from "@/components/ReviewQueue";
import { useStore } from "@/lib/sim/store";
import { Badge, Card, PageHeader } from "@/components/ui";

export default function Assemblies() {
  const { state } = useStore();

  return (
    <div>
      <PageHeader title="Assemblee" subtitle="Ciclo di vita assembleare. Le convocazioni richiedono l'approvazione dell'AoR prima dell'invio." />

      <h2 className="mb-3 font-serif text-lg font-semibold">Da approvare</h2>
      <ReviewQueue kinds={["convocation_approval"]} />

      <h2 className="mb-3 mt-8 font-serif text-lg font-semibold">Calendario</h2>
      <div className="space-y-3">
        {state.assemblies.map((a) => (
          <Card key={a.id}>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium capitalize">Assemblea {a.type === "ordinary" ? "ordinaria" : "straordinaria"}</div>
                <div className="text-xs text-ink-faint">{new Date(a.scheduledAt).toLocaleString("it-IT")}</div>
              </div>
              <Badge tone="gold">{a.status}</Badge>
            </div>
            <ol className="mt-3 space-y-1 text-sm text-ink-soft">
              {a.agenda.map((it, i) => <li key={i}>{i + 1}. {it}</li>)}
            </ol>
          </Card>
        ))}
      </div>
    </div>
  );
}
