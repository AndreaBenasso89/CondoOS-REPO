"use client";

import { ChevronDown, Eye, LogOut } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { PERSONAS } from "@/lib/sim/personas";
import type { Role } from "@/lib/sim/types";
import { Avatar, Badge, cn } from "./ui";

const ROLE_LABEL: Record<Role, string> = { resident: "Residenti", operator: "Operations", admin: "Amministratore" };
const ROLE_TONE: Record<Role, "clay" | "blue" | "gold"> = { resident: "clay", operator: "blue", admin: "gold" };

// Lets you "view as" any seeded persona to assess every experience without re-login.
export function ProfileSwitcher() {
  const { persona, switchTo, logout } = useAuth();
  const [open, setOpen] = useState(false);
  if (!persona) return null;

  return (
    <div className="relative">
      <button onClick={() => setOpen((o) => !o)} className="flex items-center gap-2 rounded-xl border border-line bg-white px-2.5 py-1.5 hover:bg-cream-100">
        <Avatar name={persona.name} hue={persona.avatarHue} size={30} />
        <div className="hidden text-left sm:block">
          <div className="text-sm font-medium leading-4">{persona.name}</div>
          <div className="text-xs text-ink-faint">{persona.title}</div>
        </div>
        <ChevronDown size={16} className="text-ink-faint" />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute right-0 z-20 mt-2 w-80 overflow-hidden rounded-2xl border border-line bg-white shadow-lift">
            <div className="flex items-center gap-2 border-b border-line bg-cream-100 px-4 py-2.5 text-xs font-semibold text-ink-faint">
              <Eye size={14} /> VISUALIZZA COME — cambia profilo
            </div>
            <div className="max-h-80 overflow-y-auto p-1.5">
              {(["resident", "operator", "admin"] as Role[]).map((role) => (
                <div key={role} className="px-1 py-1">
                  <div className="px-2 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wide text-ink-faint">
                    <Badge tone={ROLE_TONE[role]}>{ROLE_LABEL[role]}</Badge>
                  </div>
                  {PERSONAS.filter((p) => p.role === role).map((p) => (
                    <button
                      key={p.id}
                      onClick={() => { switchTo(p.id); setOpen(false); }}
                      className={cn(
                        "flex w-full items-center gap-3 rounded-xl px-2 py-2 text-left hover:bg-cream-100",
                        p.id === persona.id && "bg-cream-100 ring-1 ring-line",
                      )}
                    >
                      <Avatar name={p.name} hue={p.avatarHue} size={32} />
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium">{p.name}</div>
                        <div className="truncate text-xs text-ink-faint">{p.title}</div>
                      </div>
                    </button>
                  ))}
                </div>
              ))}
            </div>
            <button onClick={logout} className="flex w-full items-center gap-2 border-t border-line px-4 py-3 text-sm text-ink-soft hover:bg-cream-100">
              <LogOut size={15} /> Esci
            </button>
          </div>
        </>
      )}
    </div>
  );
}
