"use client";

import { ArrowRight, Building2, type LucideIcon, ShieldCheck, Users, Wrench } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { PERSONAS } from "@/lib/sim/personas";
import type { Role } from "@/lib/sim/types";
import { Avatar, Badge } from "@/components/ui";

const GROUPS: { role: Role; label: string; blurb: string; icon: LucideIcon; tone: "clay" | "blue" | "gold" }[] = [
  { role: "resident", label: "Residenti & Proprietari", blurb: "Fai domande, paga le quote, segnala guasti, consulta documenti.", icon: Users, tone: "clay" },
  { role: "operator", label: "Operations", blurb: "Lavora la coda di revisione e supervisiona gli agenti.", icon: Wrench, tone: "blue" },
  { role: "admin", label: "Amministratore (AoR)", blurb: "Contabilità, assemblee, scadenze, audit dell'intero condominio.", icon: ShieldCheck, tone: "gold" },
];

export default function Login() {
  const { login } = useAuth();
  return (
    <div className="min-h-screen">
      <div className="mx-auto grid min-h-screen max-w-6xl grid-cols-1 gap-10 px-6 py-12 lg:grid-cols-[1.1fr_1.4fr] lg:items-center">
        {/* Brand / pitch */}
        <div className="animate-fade-up">
          <div className="flex items-center gap-2">
            <div className="grid h-11 w-11 place-items-center rounded-2xl bg-clay font-serif text-xl font-bold text-white">C</div>
            <span className="font-serif text-2xl font-semibold">CondominioOS</span>
          </div>
          <h1 className="mt-8 font-serif text-4xl font-semibold leading-tight tracking-tight">
            Il condominio, amministrato dall'AI.<br />Con una persona sempre a garanzia.
          </h1>
          <p className="mt-4 max-w-md text-ink-soft">
            Servizio gestito AI-first per piccoli condomìni. Scegli un profilo per provare le tre
            esperienze: residente, operations e amministratore. Le azioni di un profilo sono visibili
            agli altri — è lo stesso ambiente condiviso.
          </p>
          <div className="mt-6 flex items-center gap-2 text-sm text-ink-faint">
            <Building2 size={16} /> Condominio Via Dante 12 · Milano · ambiente di test
          </div>
        </div>

        {/* Persona picker */}
        <div className="space-y-5">
          {GROUPS.map((g) => (
            <div key={g.role} className="card p-5 animate-fade-up">
              <div className="flex items-center gap-3">
                <div className="grid h-9 w-9 place-items-center rounded-xl bg-cream-100 text-ink-soft"><g.icon size={18} /></div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="font-semibold">{g.label}</h2>
                    <Badge tone={g.tone}>{g.role}</Badge>
                  </div>
                  <p className="text-sm text-ink-faint">{g.blurb}</p>
                </div>
              </div>
              <div className="mt-4 grid gap-2 sm:grid-cols-2">
                {PERSONAS.filter((p) => p.role === g.role).map((p) => (
                  <button
                    key={p.id}
                    onClick={() => login(p.id)}
                    className="group flex items-center gap-3 rounded-xl border border-line bg-white p-3 text-left transition hover:border-clay hover:shadow-soft"
                  >
                    <Avatar name={p.name} hue={p.avatarHue} size={38} />
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-medium">{p.name}</div>
                      <div className="truncate text-xs text-ink-faint">{p.title}</div>
                    </div>
                    <ArrowRight size={16} className="text-ink-faint transition group-hover:translate-x-0.5 group-hover:text-clay" />
                  </button>
                ))}
              </div>
            </div>
          ))}
          <p className="px-1 text-center text-xs text-ink-faint">
            Demo login senza password. Una volta dentro, usa <b>“Visualizza come”</b> in alto a destra
            per passare istantaneamente a un altro profilo.
          </p>
        </div>
      </div>
    </div>
  );
}
