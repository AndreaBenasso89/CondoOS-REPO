"use client";

import {
  Activity, Building2, CalendarClock, ClipboardList, CreditCard, FileText, Gavel,
  Home, LayoutDashboard, type LucideIcon, MessageCircle, Receipt, RotateCcw, ScrollText,
  ShieldCheck, Wrench,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { useStore } from "@/lib/sim/store";
import type { Role } from "@/lib/sim/types";
import { ProfileSwitcher } from "./ProfileSwitcher";
import { Badge, cn } from "./ui";

type Item = { href: string; label: string; icon: LucideIcon };

const NAV: Record<Role, Item[]> = {
  resident: [
    { href: "/resident", label: "Home", icon: Home },
    { href: "/resident/ask", label: "Assistente", icon: MessageCircle },
    { href: "/resident/documents", label: "Documenti", icon: FileText },
    { href: "/resident/payments", label: "Pagamenti", icon: CreditCard },
    { href: "/resident/tickets", label: "Segnalazioni", icon: Wrench },
    { href: "/resident/assembly", label: "Assemblea", icon: Gavel },
  ],
  operator: [
    { href: "/operator", label: "Dashboard", icon: LayoutDashboard },
    { href: "/operator/reviews", label: "Coda revisione", icon: ShieldCheck },
    { href: "/operator/conversations", label: "Conversazioni", icon: MessageCircle },
    { href: "/operator/tickets", label: "Interventi", icon: Wrench },
    { href: "/operator/activity", label: "Attività", icon: Activity },
  ],
  admin: [
    { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
    { href: "/admin/buildings", label: "Condominio", icon: Building2 },
    { href: "/admin/accounting", label: "Contabilità", icon: Receipt },
    { href: "/admin/assemblies", label: "Assemblee", icon: Gavel },
    { href: "/admin/compliance", label: "Scadenze", icon: CalendarClock },
    { href: "/admin/audit", label: "Audit log", icon: ScrollText },
    { href: "/admin/activity", label: "Attività", icon: Activity },
  ],
};

const ROLE_BADGE: Record<Role, { label: string; tone: "clay" | "blue" | "gold" }> = {
  resident: { label: "Portale Residente", tone: "clay" },
  operator: { label: "Console Operations", tone: "blue" },
  admin: { label: "Portale Amministratore", tone: "gold" },
};

export function Shell({ children }: { children: React.ReactNode }) {
  const { persona } = useAuth();
  const { state, reset } = useStore();
  const pathname = usePathname();
  if (!persona) return null;
  const items = NAV[persona.role];
  const badge = ROLE_BADGE[persona.role];

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-line bg-cream-100/70 p-4 md:flex">
        <div className="flex items-center gap-2 px-2 py-1">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-clay font-serif text-lg font-bold text-white">C</div>
          <div>
            <div className="font-serif text-lg font-semibold leading-4">CondominioOS</div>
            <div className="text-[11px] text-ink-faint">{state.building.name}</div>
          </div>
        </div>

        <div className="mt-4 px-1"><Badge tone={badge.tone}>{badge.label}</Badge></div>

        <nav className="mt-4 flex flex-1 flex-col gap-1">
          {items.map((it) => {
            const active = pathname === it.href || (it.href !== `/${persona.role}` && pathname.startsWith(it.href));
            return (
              <Link
                key={it.href} href={it.href}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition",
                  active ? "bg-white text-ink shadow-soft" : "text-ink-soft hover:bg-white/60",
                )}
              >
                <it.icon size={18} />
                {it.label}
              </Link>
            );
          })}
        </nav>

        <button
          onClick={() => { if (confirm("Ripristinare i dati di test? Tutte le azioni della demo verranno azzerate.")) reset(); }}
          className="mt-2 flex items-center gap-2 rounded-xl px-3 py-2 text-xs text-ink-faint hover:bg-white/60"
        >
          <RotateCcw size={14} /> Ripristina ambiente di test
        </button>
      </aside>

      {/* Main */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex items-center justify-between gap-3 border-b border-line bg-cream/80 px-5 py-3 backdrop-blur">
          <div className="flex items-center gap-2 text-sm text-ink-faint">
            <ClipboardList size={15} />
            <span className="hidden sm:inline">Ambiente di test · dati simulati</span>
          </div>
          <ProfileSwitcher />
        </header>
        <main className="mx-auto w-full max-w-6xl flex-1 px-5 py-7">{children}</main>
      </div>
    </div>
  );
}
