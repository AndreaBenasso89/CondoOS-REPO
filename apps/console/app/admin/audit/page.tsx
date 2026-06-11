"use client";

import { ActivityFeed, AuditVerifyBanner } from "@/components/ActivityFeed";
import { PageHeader } from "@/components/ui";

export default function Audit() {
  return (
    <div>
      <PageHeader title="Audit log" subtitle="Registro immutabile e concatenato (hash-chained) di ogni decisione e azione — riproducibile e a prova di manomissione." />
      <div className="mb-4"><AuditVerifyBanner /></div>
      <div className="card p-2"><ActivityFeed showHash /></div>
    </div>
  );
}
