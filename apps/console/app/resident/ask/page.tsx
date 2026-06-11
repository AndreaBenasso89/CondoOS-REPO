"use client";

import { Bot, Send, ShieldCheck, User } from "lucide-react";
import { useRef, useState } from "react";
import { useAuth } from "@/lib/auth";
import { useStore } from "@/lib/sim/store";
import type { Conversation } from "@/lib/sim/types";
import { Badge, PageHeader, cn, timeAgo } from "@/components/ui";

const SUGGESTIONS = [
  "Quali sono gli orari del portiere?",
  "Dove va conferita la raccolta differenziata?",
  "Quando è la prossima assemblea?",
  "Non ricordo l'importo del mio saldo",
  "Vorrei inviare una diffida legale",
];

export default function Ask() {
  const { persona } = useAuth();
  const { state, ask } = useStore();
  const [text, setText] = useState("");
  const [activeId, setActiveId] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  const myConvos = state.conversations.filter((c) => c.unitId === persona?.unitId);
  const active: Conversation | undefined = state.conversations.find((c) => c.id === activeId) ?? myConvos[0];

  const submit = (q: string) => {
    if (!q.trim() || !persona) return;
    const id = ask(persona, q, "web");
    setActiveId(id);
    setText("");
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  };

  return (
    <div>
      <PageHeader title="Assistente del condominio" subtitle="Risposte verificate dal Reputation Firewall. Se non sicure, le rivede una persona." />

      <div className="grid gap-5 lg:grid-cols-[1fr_300px]">
        {/* Conversation */}
        <div className="card flex h-[60vh] flex-col p-0">
          <div className="flex-1 space-y-4 overflow-y-auto p-5">
            {!active && (
              <div className="grid h-full place-items-center text-center text-sm text-ink-faint">
                Scrivi una domanda per iniziare.
              </div>
            )}
            {active?.messages.map((m) => (
              <div key={m.id} className={cn("flex gap-3", m.role === "resident" && "flex-row-reverse")}>
                <div className={cn(
                  "grid h-8 w-8 shrink-0 place-items-center rounded-lg",
                  m.role === "agent" ? "bg-clay-50 text-clay-700" : m.role === "operator" ? "bg-blue-50 text-blue-700" : "bg-cream-200 text-ink-soft",
                )}>
                  {m.role === "resident" ? <User size={16} /> : m.role === "operator" ? <ShieldCheck size={16} /> : <Bot size={16} />}
                </div>
                <div className={cn("max-w-[78%] rounded-2xl px-4 py-2.5 text-sm", m.role === "resident" ? "bg-clay text-white" : "bg-cream-100")}>
                  {m.role === "operator" && <div className="mb-1 text-xs font-semibold text-blue-700">Risposta approvata da un operatore</div>}
                  <p className="whitespace-pre-wrap">{m.text}</p>
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {m.citations.map((c, i) => (
                        <span key={i} className="rounded-full bg-white/70 px-2 py-0.5 text-[11px] text-ink-soft">{c.docId} · {c.span}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {active && active.state !== "answered" && (
              <div className="rounded-xl border border-dashed border-line bg-cream-100/60 p-3 text-center text-sm text-ink-soft">
                {active.state === "escalated"
                  ? "La tua richiesta è stata inoltrata a una persona del team. Ti risponderemo a breve."
                  : "Stiamo verificando la risposta prima di inviartela."}
              </div>
            )}
            <div ref={endRef} />
          </div>

          <form className="flex items-center gap-2 border-t border-line p-3" onSubmit={(e) => { e.preventDefault(); submit(text); }}>
            <input className="input" placeholder="Scrivi una domanda…" value={text} onChange={(e) => setText(e.target.value)} />
            <button className="btn-primary" type="submit"><Send size={16} /></button>
          </form>
        </div>

        {/* Side: suggestions + history */}
        <div className="space-y-4">
          <div className="card p-4">
            <div className="label mb-2">Prova a chiedere</div>
            <div className="flex flex-col gap-1.5">
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => submit(s)} className="rounded-lg px-2 py-1.5 text-left text-sm text-ink-soft hover:bg-cream-100">{s}</button>
              ))}
            </div>
          </div>
          <div className="card p-4">
            <div className="label mb-2">Le tue conversazioni</div>
            <div className="flex flex-col gap-1">
              {myConvos.map((c) => (
                <button key={c.id} onClick={() => setActiveId(c.id)} className={cn("flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-left text-sm hover:bg-cream-100", c.id === active?.id && "bg-cream-100")}>
                  <span className="truncate">{c.subject}</span>
                  <Badge tone={c.state === "answered" ? "sage" : "gold"}>{timeAgo(c.updatedAt)}</Badge>
                </button>
              ))}
              {myConvos.length === 0 && <p className="text-sm text-ink-faint">Nessuna ancora.</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
