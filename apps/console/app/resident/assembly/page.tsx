"use client";

import { CalendarClock, Check } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { useStore } from "@/lib/sim/store";
import { Badge, Card, PageHeader } from "@/components/ui";

export default function AssemblyPage() {
  const { persona } = useAuth();
  const { state, log } = useStore();
  const a = state.assemblies[0];
  const [rsvp, setRsvp] = useState<"yes" | "proxy" | null>(null);

  if (!a) return <PageHeader title="Assemblea" subtitle="Nessuna assemblea in programma." />;

  const act = (kind: "yes" | "proxy") => {
    setRsvp(kind);
    if (persona) log({ actor: persona.name, actorRole: "resident", action: kind === "yes" ? "Conferma partecipazione assemblea" : "Delega registrata", detail: a.agenda[0], entity: `assembly:${a.id}` });
  };

  return (
    <div>
      <PageHeader title="Assemblea ordinaria" subtitle="Ordine del giorno e conferma di partecipazione." />
      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <Card>
          <div className="label mb-2">Ordine del giorno</div>
          <ol className="space-y-2">
            {a.agenda.map((item, i) => (
              <li key={i} className="flex gap-3 text-sm"><span className="font-semibold text-clay">{i + 1}.</span> {item}</li>
            ))}
          </ol>
        </Card>
        <div className="space-y-4">
          <Card>
            <div className="flex items-center gap-2 text-sm"><CalendarClock size={16} className="text-ink-faint" /> {new Date(a.scheduledAt).toLocaleString("it-IT")}</div>
            <div className="mt-1"><Badge tone="gold">{a.status}</Badge></div>
          </Card>
          <Card>
            <div className="label mb-2">La tua partecipazione</div>
            <div className="flex flex-col gap-2">
              <button className={rsvp === "yes" ? "btn-primary" : "btn-ghost"} onClick={() => act("yes")}>
                {rsvp === "yes" && <Check size={16} />} Parteciperò
              </button>
              <button className={rsvp === "proxy" ? "btn-primary" : "btn-ghost"} onClick={() => act("proxy")}>
                {rsvp === "proxy" && <Check size={16} />} Delego un altro condòmino
              </button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
