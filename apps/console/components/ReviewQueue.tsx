"use client";

import { Check, ChevronDown, Pencil, ShieldCheck, X } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { LAYER_LABELS } from "@/lib/sim/engine";
import { useStore } from "@/lib/sim/store";
import type { ReviewItem, ReviewKind } from "@/lib/sim/types";
import { Badge, cn, EmptyState, TierBadge, timeAgo, VerdictBadge } from "./ui";

const KIND_LABEL: Record<ReviewKind, string> = {
  firewall_hold: "Firewall · HOLD",
  escalation: "Escalation",
  collections_approval: "Sollecito",
  convocation_approval: "Convocazione",
};

export function ReviewQueue({ kinds }: { kinds?: ReviewKind[] }) {
  const { state } = useStore();
  let pending = state.reviews.filter((r) => r.status === "pending");
  if (kinds) pending = pending.filter((r) => kinds.includes(r.kind));

  if (pending.length === 0)
    return <EmptyState title="Nessun elemento in coda" hint="Tutto gestito autonomamente dagli agenti." />;

  return (
    <div className="space-y-3">
      {pending.map((r) => (
        <ReviewCard key={r.id} review={r} />
      ))}
    </div>
  );
}

export function ReviewCard({ review: r }: { review: ReviewItem }) {
  const { persona } = useAuth();
  const { decideReview } = useStore();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(r.draftText);
  const canDecide = persona?.role === "operator" || persona?.role === "admin";

  return (
    <div className="card overflow-hidden p-0 animate-fade-up">
      <button onClick={() => setOpen((o) => !o)} className="flex w-full items-center gap-3 px-5 py-4 text-left">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-clay-50 text-clay-700"><ShieldCheck size={18} /></div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="truncate font-medium">{r.title}</span>
            {r.priority === "high" && <Badge tone="red">priorità alta</Badge>}
          </div>
          <div className="mt-0.5 flex flex-wrap items-center gap-1.5 text-xs text-ink-faint">
            <Badge>{KIND_LABEL[r.kind]}</Badge>
            <VerdictBadge verdict={r.verdict} /> <TierBadge tier={r.tier} />
            <span>· confidenza {(r.confidence * 100).toFixed(0)}%</span>
            <span>· {timeAgo(r.createdAt)}</span>
          </div>
        </div>
        <ChevronDown size={18} className={cn("text-ink-faint transition", open && "rotate-180")} />
      </button>

      {open && (
        <div className="space-y-4 border-t border-line bg-cream-100/40 px-5 py-4">
          <div>
            <div className="label mb-1">Destinatario</div>
            <p className="text-sm">{r.recipient}</p>
          </div>

          <div>
            <div className="label mb-1">Bozza {editing && "(modifica)"}</div>
            {editing ? (
              <textarea value={text} onChange={(e) => setText(e.target.value)} rows={6} className="input font-normal" />
            ) : (
              <pre className="whitespace-pre-wrap rounded-xl border border-line bg-white p-3 text-sm">{text}</pre>
            )}
          </div>

          {r.citations.length > 0 && (
            <div>
              <div className="label mb-1">Fonti citate</div>
              <div className="flex flex-wrap gap-1.5">
                {r.citations.map((c, i) => <Badge key={i} tone="blue">{c.docId} · {c.span}</Badge>)}
              </div>
            </div>
          )}

          <div>
            <div className="label mb-1">Controlli Firewall</div>
            <div className="flex flex-wrap gap-1.5">
              {Object.keys(LAYER_LABELS).map((l) => {
                const tripped = r.trippedLayers.includes(l);
                return (
                  <span key={l} className={cn("chip", tripped ? "bg-red-50 text-red-700" : "bg-sage-50 text-sage")}>
                    {tripped ? "✗" : "✓"} {LAYER_LABELS[l]}
                  </span>
                );
              })}
            </div>
            <p className="mt-2 text-sm text-ink-soft">{r.riskNote}</p>
          </div>

          {canDecide ? (
            <div className="flex flex-wrap gap-2 pt-1">
              <button className="btn-primary" onClick={() => decideReview(r.id, "approved", persona!, { editedText: text })}>
                <Check size={16} /> {editing ? "Salva e invia" : "Approva e invia"}
              </button>
              <button className="btn-ghost" onClick={() => setEditing((e) => !e)}>
                <Pencil size={15} /> {editing ? "Annulla modifica" : "Modifica"}
              </button>
              <button className="btn-danger" onClick={() => decideReview(r.id, "rejected", persona!, { note: "Respinto in revisione" })}>
                <X size={16} /> Respingi
              </button>
            </div>
          ) : (
            <p className="rounded-xl bg-cream-100 px-3 py-2 text-sm text-ink-faint">
              In attesa di decisione di Operations / Amministratore. (Stai visualizzando come residente.)
            </p>
          )}
        </div>
      )}
    </div>
  );
}
