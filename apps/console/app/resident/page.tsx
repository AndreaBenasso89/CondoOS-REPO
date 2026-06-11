"use client";

import { CreditCard, FileText, Gavel, MessageCircle, Wrench } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { useStore } from "@/lib/sim/store";
import { Badge, Card, Money, PageHeader, timeAgo } from "@/components/ui";

const QUICK = [
  { href: "/resident/ask", label: "Fai una domanda", icon: MessageCircle },
  { href: "/resident/tickets", label: "Segnala un guasto", icon: Wrench },
  { href: "/resident/payments", label: "Paga le quote", icon: CreditCard },
  { href: "/resident/documents", label: "Documenti", icon: FileText },
];

export default function ResidentHome() {
  const { persona } = useAuth();
  const { state } = useStore();
  const unit = state.units.find((u) => u.id === persona?.unitId);
  const myConvos = state.conversations.filter((c) => c.unitId === persona?.unitId).slice(0, 4);
  const myTickets = state.tickets.filter((t) => t.unitId === persona?.unitId);
  const assembly = state.assemblies[0];

  return (
    <div>
      <PageHeader title={`Ciao ${persona?.name.split(" ")[0]}`} subtitle={`${unit?.identifier ?? ""} · ${state.building.name}`} />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <div className="label">Saldo del tuo appartamento</div>
          <div className="mt-1 text-3xl font-semibold"><Money value={unit?.balanceEur ?? 0} /></div>
          <div className="mt-1 text-xs text-ink-faint">
            {(unit?.balanceEur ?? 0) < 0 ? "Saldo a debito — puoi regolarizzare dai Pagamenti" : "In regola, grazie!"}
          </div>
        </Card>
        <Card>
          <div className="label">Prossima assemblea</div>
          <div className="mt-1 text-lg font-semibold">{assembly ? new Date(assembly.scheduledAt).toLocaleDateString("it-IT") : "—"}</div>
          <div className="mt-1 text-xs text-ink-faint capitalize">{assembly?.type === "ordinary" ? "ordinaria" : "straordinaria"} · {assembly?.status}</div>
        </Card>
        <Card>
          <div className="label">Le tue segnalazioni aperte</div>
          <div className="mt-1 text-3xl font-semibold">{myTickets.filter((t) => t.status !== "resolved").length}</div>
          <div className="mt-1 text-xs text-ink-faint">su {myTickets.length} totali</div>
        </Card>
      </div>

      <h2 className="mb-3 mt-8 font-serif text-lg font-semibold">Azioni rapide</h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {QUICK.map((q) => (
          <Link key={q.href} href={q.href} className="card flex items-center gap-3 p-4 transition hover:-translate-y-0.5 hover:shadow-lift">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-clay-50 text-clay-700"><q.icon size={20} /></div>
            <span className="font-medium">{q.label}</span>
          </Link>
        ))}
      </div>

      <h2 className="mb-3 mt-8 font-serif text-lg font-semibold">Le tue conversazioni</h2>
      <div className="card divide-y divide-line p-0">
        {myConvos.length === 0 && <div className="p-6 text-sm text-ink-faint">Nessuna conversazione. Prova a fare una domanda all’assistente.</div>}
        {myConvos.map((c) => (
          <Link key={c.id} href="/resident/ask" className="flex items-center justify-between gap-3 px-5 py-3.5 hover:bg-cream-100/60">
            <div className="min-w-0">
              <div className="truncate font-medium">{c.subject}</div>
              <div className="text-xs text-ink-faint">{c.channel} · {timeAgo(c.updatedAt)}</div>
            </div>
            <Badge tone={c.state === "answered" ? "sage" : c.state === "escalated" ? "gold" : "neutral"}>
              {c.state === "answered" ? "Risolta" : c.state === "escalated" ? "In carico a una persona" : "In revisione"}
            </Badge>
          </Link>
        ))}
      </div>
    </div>
  );
}
