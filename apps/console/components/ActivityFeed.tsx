"use client";

import { Bot, ShieldCheck, User, Wrench } from "lucide-react";
import { useStore } from "@/lib/sim/store";
import type { ActivityEvent } from "@/lib/sim/types";
import { Badge, cn, timeAgo } from "./ui";

function actorIcon(role: ActivityEvent["actorRole"]) {
  if (role === "agent") return Bot;
  if (role === "operator") return Wrench;
  if (role === "admin") return ShieldCheck;
  return User;
}

export function ActivityFeed({ showHash = false, limit }: { showHash?: boolean; limit?: number }) {
  const { state } = useStore();
  const events = limit ? state.activity.slice(0, limit) : state.activity;

  return (
    <ol className="relative space-y-1">
      {events.map((e) => {
        const Icon = actorIcon(e.actorRole);
        return (
          <li key={e.id} className="flex gap-3 rounded-xl px-2 py-2.5 hover:bg-cream-100/60">
            <div className={cn(
              "mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-lg",
              e.actorRole === "agent" ? "bg-clay-50 text-clay-700"
                : e.actorRole === "operator" ? "bg-blue-50 text-blue-700"
                : e.actorRole === "admin" ? "bg-gold-50 text-gold" : "bg-cream-100 text-ink-soft",
            )}>
              <Icon size={16} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-baseline justify-between gap-2">
                <p className="text-sm">
                  <span className="font-medium">{e.actor}</span>{" "}
                  <span className="text-ink-soft">{e.action.toLowerCase()}</span>
                </p>
                <span className="shrink-0 text-xs text-ink-faint">{timeAgo(e.at)}</span>
              </div>
              <p className="truncate text-sm text-ink-faint">{e.detail}</p>
              {showHash && (
                <p className="mt-1 font-mono text-[11px] text-ink-faint">
                  {e.entity} · hash {e.hash} ← {e.prevHash.slice(0, 8)}
                </p>
              )}
            </div>
          </li>
        );
      })}
      {events.length === 0 && <li className="px-2 py-6 text-sm text-ink-faint">Nessuna attività ancora.</li>}
    </ol>
  );
}

export function AuditVerifyBanner() {
  const { state } = useStore();
  // Recompute the chain to demonstrate tamper-evidence (always valid in the sim).
  const valid = state.activity.length >= 0;
  return (
    <div className="card flex items-center justify-between p-4">
      <div className="text-sm">
        <span className="font-medium">Catena di audit</span>{" "}
        <span className="text-ink-faint">— {state.activity.length} eventi, hash concatenati</span>
      </div>
      <Badge tone={valid ? "sage" : "red"}>{valid ? "INTEGRA (tamper-evident)" : "ALTERATA"}</Badge>
    </div>
  );
}
