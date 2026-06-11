"use client";

import { ActivityFeed } from "@/components/ActivityFeed";
import { PageHeader } from "@/components/ui";

export default function AdminActivity() {
  return (
    <div>
      <PageHeader title="Attività" subtitle="Cosa hanno fatto agenti, residenti e team — la stessa cronologia condivisa, visibile a tutti i profili autorizzati." />
      <div className="card p-2"><ActivityFeed /></div>
    </div>
  );
}
