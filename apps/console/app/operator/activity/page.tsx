"use client";

import { ActivityFeed } from "@/components/ActivityFeed";
import { PageHeader } from "@/components/ui";

export default function OperatorActivity() {
  return (
    <div>
      <PageHeader title="Attività" subtitle="Tutto ciò che agenti, residenti e team hanno fatto sul sistema." />
      <div className="card p-2"><ActivityFeed /></div>
    </div>
  );
}
