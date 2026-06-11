"use client";

import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState } from "react";
import { personaById } from "./sim/personas";
import type { Persona } from "./sim/types";

const KEY = "condominioos.session.v1";

interface AuthApi {
  persona: Persona | null;
  ready: boolean;
  login: (id: string) => void;
  switchTo: (id: string) => void; // "view as" — assess any profile without re-login
  logout: () => void;
}

const AuthContext = createContext<AuthApi | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [persona, setPersona] = useState<Persona | null>(null);
  const [ready, setReady] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const id = localStorage.getItem(KEY);
    if (id) setPersona(personaById(id) ?? null);
    setReady(true);
  }, []);

  const set = (id: string | null) => {
    if (id) {
      localStorage.setItem(KEY, id);
      setPersona(personaById(id) ?? null);
    } else {
      localStorage.removeItem(KEY);
      setPersona(null);
    }
  };

  const api: AuthApi = {
    persona,
    ready,
    login: (id) => {
      set(id);
      const p = personaById(id);
      router.push(p ? `/${p.role}` : "/");
    },
    switchTo: (id) => {
      set(id);
      const p = personaById(id);
      router.push(p ? `/${p.role}` : "/");
    },
    logout: () => {
      set(null);
      router.push("/login");
    },
  };

  return <AuthContext.Provider value={api}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
