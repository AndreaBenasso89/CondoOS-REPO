"use client";

import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { useStore } from "@/lib/sim/store";
import { Badge, PageHeader } from "@/components/ui";

export default function Compliance() {
  const { state } = useStore();
  return (
    <div>
      <PageHeader title="Scadenze & Compliance" subtitle="Monitoraggio continuo di polizze, certificazioni e adempimenti di legge." />
      <div className="space-y-3">
        {state.compliance.map((a) => {
          const overdue = new Date(a.dueDate) < new Date();
          return (
            <div key={a.id} className="card flex items-center gap-4 p-4">
              {a.status === "resolved"
                ? <CheckCircle2 className="text-sage" size={20} />
                : <AlertTriangle className={a.severity === "high" ? "text-red-600" : "text-gold"} size={20} />}
              <div className="min-w-0 flex-1">
                <div className="font-medium">{a.kind}</div>
                <div className="text-xs text-ink-faint">
                  scadenza {new Date(a.dueDate).toLocaleDateString("it-IT")} {overdue && a.status !== "resolved" ? "· superata" : ""}
                </div>
              </div>
              <Badge tone={a.severity === "high" ? "red" : a.severity === "medium" ? "gold" : "neutral"}>{a.severity}</Badge>
              <Badge tone={a.status === "resolved" ? "sage" : a.status === "remediating" ? "blue" : "gold"}>{a.status}</Badge>
            </div>
          );
        })}
      </div>
    </div>
  );
}
