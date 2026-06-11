"use client";

import { Download, FileText } from "lucide-react";
import { useStore } from "@/lib/sim/store";
import { Badge, PageHeader } from "@/components/ui";

export default function Documents() {
  const { state } = useStore();
  return (
    <div>
      <PageHeader title="Documenti" subtitle="Regolamento, verbali, polizze e contratti del condominio." />
      <div className="card divide-y divide-line p-0">
        {state.documents.map((d) => {
          const expired = d.expiry && new Date(d.expiry) < new Date();
          return (
            <div key={d.id} className="flex items-center gap-3 px-5 py-4">
              <div className="grid h-10 w-10 place-items-center rounded-xl bg-cream-100 text-ink-soft"><FileText size={18} /></div>
              <div className="min-w-0 flex-1">
                <div className="truncate font-medium">{d.title}</div>
                <div className="text-xs text-ink-faint">{d.type}{d.expiry ? ` · scadenza ${new Date(d.expiry).toLocaleDateString("it-IT")}` : ""}</div>
              </div>
              {expired && <Badge tone="red">scaduto</Badge>}
              <button className="btn-ghost"><Download size={15} /> Scarica</button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
