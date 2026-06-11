"use client";

import { AuthProvider } from "@/lib/auth";
import { StoreProvider } from "@/lib/sim/store";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <StoreProvider>
      <AuthProvider>{children}</AuthProvider>
    </StoreProvider>
  );
}
