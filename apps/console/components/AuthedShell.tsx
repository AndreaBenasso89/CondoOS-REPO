"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import type { Role } from "@/lib/sim/types";
import { Shell } from "./Shell";

// Guards a role area: requires login, and redirects if the active persona's role doesn't match.
export function AuthedShell({ allow, children }: { allow: Role; children: React.ReactNode }) {
  const { persona, ready } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!ready) return;
    if (!persona) router.replace("/login");
    else if (persona.role !== allow) router.replace(`/${persona.role}`);
  }, [ready, persona, allow, router]);

  if (!ready || !persona || persona.role !== allow) {
    return <div className="grid min-h-screen place-items-center text-sm text-ink-faint">Caricamento…</div>;
  }
  return <Shell>{children}</Shell>;
}
