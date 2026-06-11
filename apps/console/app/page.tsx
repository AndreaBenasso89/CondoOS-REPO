"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";

export default function Index() {
  const { persona, ready } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (!ready) return;
    router.replace(persona ? `/${persona.role}` : "/login");
  }, [ready, persona, router]);
  return null;
}
